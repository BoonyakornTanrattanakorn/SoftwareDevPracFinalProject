const Reservation = require("../models/Reservation");
const CoworkingSpace = require("../models/CoworkingSpace");

const MAX_RESERVATIONS = 3;

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

    // If the user is not an admin, then have reservations count limit.
    const count = await Reservation.countDocuments({ user: req.user.id });
    if (count >= MAX_RESERVATIONS && req.user.role !== "admin") {
      return res.status(400).json({
        success: false,
        message: `The user with ID ${req.user.id} has already made ${MAX_RESERVATIONS} reservations`,
      });
    }

    // Create the reservation
    const reservation = await Reservation.create({
      reservationDate: req.body.reservationDate,
      coworkingSpace: req.params.coworkingSpaceId,
      user: req.user.id,
    });

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
    if (req.body.reservationDate)
      updates.reservationDate = req.body.reservationDate;
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
