const CoworkingSpace = require("../models/CoworkingSpace.js");
const Reservation = require("../models/Reservation.js");

//@desc     Get all coworkingSpaces
//@route    GET /api/v1/coworkingSpaces
//@access   Public
exports.getCoworkingSpaces = async (req, res, next) => {
  try {
    let query;

    const reqQuery = { ...req.query };

    // Fields to exclude
    const removeFields = ["select", "sort", "page", "limit"];
    removeFields.forEach((param) => delete reqQuery[param]);
    console.log(reqQuery);

    let queryStr = JSON.stringify(reqQuery);
    queryStr = queryStr.replace(
      /\b(gt|gte|lt|lte|in)\b/g,
      (match) => `$${match}`,
    );

    query = CoworkingSpace.find(JSON.parse(queryStr));

    //Sort
    if (req.query.select) {
      const fields = req.query.select.split(",").join(" ");
      query = query.select(fields);
    }
    if (req.query.sort) {
      const sortBy = req.query.sort.split(",").join(" ");
      query = query.sort(sortBy);
    } else {
      query = query.sort("-createdAt");
    }
    // Pagination
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 25;
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;
    const total = await CoworkingSpace.countDocuments();
    query = query.skip(startIndex).limit(limit);

    // Execute query
    const coworkingSpaces = await query;

    // Paginate result
    const pagination = {};
    if (endIndex < total) {
      pagination.next = { page: page + 1, limit };
    }
    if (startIndex > 0) {
      pagination.prev = { page: page - 1, limit };
    }

    res.status(200).json({
      success: true,
      count: coworkingSpaces.length,
      data: coworkingSpaces,
      pagination,
    });
  } catch (err) {
    res.status(400).json({
      success: false,
    });
  }
};

//@desc     Get single coworkingSpace
//@route    GET /api/v1/coworkingSpaces/:id
//@access   Public
exports.getCoworkingSpace = async (req, res, next) => {
  try {
    const coworkingSpace = await CoworkingSpace.findById(req.params.id);

    if (!coworkingSpace) {
      return res.status(400).json({
        success: false,
      });
    }

    res.status(200).json({
      success: true,
      data: coworkingSpace,
    });
  } catch (err) {
    res.status(400).json({
      success: false,
    });
  }
};

//@desc     Create new coworkingSpaces
//@route    POST /api/v1/coworkingSpaces
//@access   Private
exports.createCoworkingSpace = async (req, res, next) => {
  try {
    const coworkingSpace = await CoworkingSpace.create(req.body);
    res.status(201).json({
      success: true,
      data: coworkingSpace,
    });
  } catch (err) {
    let message = err.message;
    res.status(400).json({
      success: false,
      message,
    });
  }
};

//@desc     Update coworkingSpace
//@route    PUT /api/v1/coworkingSpaces/:id
//@access   Private
exports.updateCoworkingSpace = async (req, res, next) => {
  try {
    const coworkingSpace = await CoworkingSpace.findByIdAndUpdate(
      req.params.id,
      req.body,
      {
        new: true,
        runValidators: true,
      },
    );

    if (!coworkingSpace) {
      return res.status(400).json({
        success: false,
      });
    }

    res.status(200).json({
      success: true,
      data: coworkingSpace,
    });
  } catch (err) {
    res.status(400).json({
      success: false,
    });
  }
};

//@desc     Delete coworkingSpaces
//@route    DELETE /api/v1/coworkingSpaces/:id
//@access   Private
exports.deleteCoworkingSpace = async (req, res, next) => {
  try {
    const coworkingSpace = await CoworkingSpace.findById(req.params.id);

    if (!coworkingSpace) {
      return res.status(404).json({
        success: false,
      });
    }
    await Reservation.deleteMany({ coworkingSpace: req.params.id });
    await CoworkingSpace.deleteOne({ _id: req.params.id });

    res.status(200).json({
      success: true,
      data: coworkingSpace,
    });
  } catch (err) {
    res.status(400).json({
      success: false,
    });
  }
};
