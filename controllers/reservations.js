const Reservation = require("../models/Reservation");
const CoworkingSpace = require("../models/CoworkingSpace");

const Setting = require("../models/Setting");
const { findThaiPublicHoliday } = require("../utils/holidays");
const { sendReservationConfirmation } = require("../utils/email");
const { toCsv } = require("../utils/csv");

// Start of today (00:00 server time), reservations from this point on are "active"
const startOfToday = () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return today;
};

// Check the date against the Thai public holiday API (in real time)
// Return { status, message } if the reservation must be rejected, otherwise null
const checkPublicHoliday = async (date) => {
  try {
    const holiday = await findThaiPublicHoliday(date);
    if (holiday) {
      return {
        status: 400,
        message: `Cannot reserve on ${holiday.date.iso.slice(0, 10)} because it is a Thai public holiday (${holiday.name})`,
      };
    }
    return null;
  } catch (err) {
    console.log(`Holiday API error: ${err.message}`);
    return {
      status: 503,
      message:
        "Cannot check Thai public holidays right now, please try again later",
    };
  }
};

// @desc    Get all reservations
//@route    GET /api/v1/reservations
//@access   Public
exports.getReservations = async (req, res, next) => {
  let query;

  if (req.user.role !== "admin") {
    // General users can see only their reservations
    query = Reservation.find({ user: req.user.id }).populate({
      path: "coworkingSpace",
      select: "name address tel openTime closeTime",
    });
  } else {
    // Admin can see all reservations
    if (req.params.coworkingSpaceId) {
      console.log(req.params.coworkingSpaceId);
      query = Reservation.find({
        coworkingSpace: req.params.coworkingSpaceId,
      }).populate({
        path: "coworkingSpace",
        select: "name address tel openTime closeTime",
      });
    } else {
      query = Reservation.find().populate({
        path: "coworkingSpace",
        select: "name address tel openTime closeTime",
      });
    }
  }
  try {
    const reservations = await query;

    res.status(200).json({
      success: true,
      count: reservations.length,
      data: reservations,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ success: false, message: "Cannot find Reservation" });
  }
};

// @desc    Get a reservation
//@route    GET /api/v1/reservations/:id
//@access   Public
exports.getReservation = async (req, res, next) => {
  try {
    const reservation = await Reservation.findById(req.params.id).populate({
      path: "coworkingSpace",
      select: "name address tel openTime closeTime",
    });

    if (!reservation) {
      return res.status(404).json({
        success: false,
        message: `No reservation with the id of ${req.params.id}`,
      });
    }

    if (req.user.role !== "admin" && reservation.user.toString() !== req.user.id) {
      // Don't allow a user to read other user reservations
      return res.status(401).json({
        success: false,
        message: `User ${req.user.id} is not authorized to view this reservation`,
      });
    }

    res.status(200).json({
      success: true,
      data: reservation,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ success: false, message: "Cannot find Reservation" });
  }
};

// @desc    Add an reservation
//@route    POST /api/v1/coworkingSpaces/:coworkingSpaceId/reservations
//@access   Private
exports.addReservation = async (req, res, next) => {
  try {
    const coworkingSpace = await CoworkingSpace.findById(
      req.params.coworkingSpaceId,
    );

    if (!coworkingSpace) {
      return res.status(404).json({
        success: false,
        message: `No coworkingSpace with the id of ${req.params.coworkingSpaceId}`,
      });
    }

    // date is required
    if (!req.body.reservationDate) {
      return res
        .status(400)
        .json({ success: false, message: "Please provide a reservationDate" });
    }

    // Reservation date must be a valid date and not in the past
    const reservationDate = new Date(req.body.reservationDate);
    if (isNaN(reservationDate)) {
      return res
        .status(400)
        .json({ success: false, message: "Date string is invalid" });
    }
    if (reservationDate < startOfToday()) {
      return res.status(400).json({
        success: false,
        message: "Reservation date cannot be in the past",
      });
    }

    // If the user is not an admin, limit the number of active reservations
    // (the limit is configured by the admin in the settings)
    const { maxReservations } = await Setting.getSettings();
    const count = await Reservation.countDocuments({
      user: req.user.id,
      reservationDate: { $gte: startOfToday() },
    });
    if (count >= maxReservations && req.user.role !== "admin") {
      return res.status(400).json({
        success: false,
        message: `The user with ID ${req.user.id} has already made ${maxReservations} active reservations`,
      });
    }

    // Reservation date must not be a Thai public holiday
    const holidayError = await checkPublicHoliday(reservationDate);
    if (holidayError) {
      return res
        .status(holidayError.status)
        .json({ success: false, message: holidayError.message });
    }

    // Create the reservation
    const reservation = await Reservation.create({
      reservationDate: req.body.reservationDate,
      coworkingSpace: req.params.coworkingSpaceId,
      user: req.user.id,
    });

    // Send the confirmation email through Resend
    // (not awaited, so the response is not delayed; a failed email is only logged)
    sendReservationConfirmation(req.user, reservation, coworkingSpace)
      .then(() => console.log(`Confirmation email sent to ${req.user.email}`))
      .catch((err) =>
        console.log(`Cannot send confirmation email: ${err.message}`),
      );

    res.status(201).json({
      success: true,
      data: reservation,
    });
  } catch (error) {
    if (error.name == "ValidationError" || error.name === "CastError") {
      return res
        .status(400)
        .json({ success: false, message: "Date string is invalid" });
    }
    return res
      .status(500)
      .json({ success: false, message: "Cannot create Reservation" });
  }
};

// @desc    Update an reservation
//@route    PUT /api/v1/reservations/:id
//@access   Private
exports.updateReservation = async (req, res, next) => {
  try {
    let reservation = await Reservation.findById(req.params.id);

    if (!reservation) {
      return res.status(404).json({
        success: false,
        message: `No reservation with the id of ${req.params.id}`,
      });
    }

    // Make sure user is the reservation owner
    if (
      reservation.user.toString() !== req.user.id &&
      req.user.role !== "admin"
    ) {
      return res.status(401).json({
        success: false,
        message: `User ${req.user.id} is not authorized to update this reservation`,
      });
    }

    const updates = {};
    if (req.body.reservationDate) {
      // New date must be a valid date and not in the past
      const reservationDate = new Date(req.body.reservationDate);
      if (isNaN(reservationDate)) {
        return res
          .status(400)
          .json({ success: false, message: "Date string is invalid" });
      }
      if (reservationDate < startOfToday()) {
        return res.status(400).json({
          success: false,
          message: "Reservation date cannot be in the past",
        });
      }
      // New date must not be a Thai public holiday
      const holidayError = await checkPublicHoliday(reservationDate);
      if (holidayError) {
        return res
          .status(holidayError.status)
          .json({ success: false, message: holidayError.message });
      }
      updates.reservationDate = req.body.reservationDate;
    }
    if (req.body.coworkingSpace) {
      const space = await CoworkingSpace.findById(req.body.coworkingSpace);
      if (!space)
        return res.status(404).json({
          success: false,
          message: `No co-working space with the id of ${req.body.coworkingSpace}`,
        });
      updates.coworkingSpace = req.body.coworkingSpace;
    }
    reservation = await Reservation.findByIdAndUpdate(req.params.id, updates, {
      new: true,
      runValidators: true,
    });

    res.status(200).json({
      success: true,
      data: reservation,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ success: false, message: "Cannot update Reservation" });
  }
};

// @desc    Delete an reservation
//@route    DELETE /api/v1/reservations/:id
//@access   Private
exports.deleteReservation = async (req, res, next) => {
  try {
    const reservation = await Reservation.findById(req.params.id);

    if (!reservation) {
      return res.status(404).json({
        success: false,
        message: `No reservation with the id of ${req.params.id}`,
      });
    }

    // Make sure user is the reservation owner
    if (
      reservation.user.toString() !== req.user.id &&
      req.user.role !== "admin"
    ) {
      return res.status(401).json({
        success: false,
        message: `User ${req.user.id} is not authorized to delete this reservation`,
      });
    }

    await reservation.deleteOne();

    res.status(200).json({
      success: true,
      data: reservation,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ success: false, message: "Cannot delete Reservation" });
  }
};


// @desc    Export reservations within a date range as a CSV file
//@route    GET /api/v1/reservations/export?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
//@access   Private (admin)
exports.exportReservations = async (req, res, next) => {
  try {
    const { startDate, endDate } = req.query;
    const datePattern = /^\d{4}-\d{2}-\d{2}$/;

    if (!startDate || !endDate) {
      return res.status(400).json({
        success: false,
        message: "Please provide startDate and endDate (YYYY-MM-DD)",
      });
    }

    // Reservation date as YYYY-MM-DD in Thailand time
    const thaiDate = (date) =>
      new Date(date.getTime() + 7 * 60 * 60 * 1000).toISOString().slice(0, 10);

    // The range covers whole days in Thailand time (UTC+7), both ends included
    const start = new Date(`${startDate}T00:00:00.000+07:00`);
    const end = new Date(`${endDate}T23:59:59.999+07:00`);
    if (
      !datePattern.test(startDate) ||
      !datePattern.test(endDate) ||
      isNaN(start) ||
      isNaN(end) ||
      thaiDate(start) !== startDate || // e.g. 2027-02-30 is not a real date
      thaiDate(end) !== endDate
    ) {
      return res.status(400).json({
        success: false,
        message: "startDate and endDate must be valid dates in YYYY-MM-DD format",
      });
    }
    if (start > end) {
      return res.status(400).json({
        success: false,
        message: "startDate must be on or before endDate",
      });
    }

    const filter = { reservationDate: { $gte: start, $lte: end } };
    // /api/v1/coworkingspaces/:coworkingSpaceId/reservations/export only exports that space
    if (req.params.coworkingSpaceId) {
      filter.coworkingSpace = req.params.coworkingSpaceId;
    }

    const reservations = await Reservation.find(filter)
      .populate({ path: "user", select: "name email tel" })
      .populate({
        path: "coworkingSpace",
        select: "name address tel openTime closeTime",
      })
      .sort("reservationDate");

    const header = [
      "reservationId",
      "reservationDate",
      "userName",
      "userEmail",
      "userTel",
      "coworkingSpaceName",
      "coworkingSpaceAddress",
      "coworkingSpaceTel",
      "openTime",
      "closeTime",
      "createdAt",
    ];
    const rows = reservations.map((r) => [
      r._id,
      thaiDate(r.reservationDate),
      r.user ? r.user.name : "",
      r.user ? r.user.email : "",
      r.user ? r.user.tel : "",
      r.coworkingSpace ? r.coworkingSpace.name : "",
      r.coworkingSpace ? r.coworkingSpace.address : "",
      r.coworkingSpace ? r.coworkingSpace.tel : "",
      r.coworkingSpace ? r.coworkingSpace.openTime : "",
      r.coworkingSpace ? r.coworkingSpace.closeTime : "",
      r.createdAt ? r.createdAt.toISOString() : "",
    ]);

    res
      .status(200)
      .set("Content-Type", "text/csv; charset=utf-8")
      .attachment(`reservations_${startDate}_to_${endDate}.csv`)
      .send(toCsv(header, rows));
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ success: false, message: "Cannot export reservations" });
  }
};
