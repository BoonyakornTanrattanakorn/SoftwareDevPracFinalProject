const User = require("../models/User");
const CoworkingSpace = require("../models/CoworkingSpace");

//@desc     Get my favourite co-working spaces
//@route    GET /api/v1/favourites
//@access   Private
exports.getFavourites = async (req, res, next) => {
  try {
    const user = await User.findById(req.user.id).populate({
      path: "favourites",
      select: "name address tel openTime closeTime",
    });

    res.status(200).json({
      success: true,
      count: user.favourites.length,
      data: user.favourites,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ success: false, message: "Cannot find favourite list" });
  }
};

//@desc     Add a co-working space to my favourite list
//@route    POST /api/v1/favourites/:coworkingSpaceId
//@access   Private
exports.addFavourite = async (req, res, next) => {
  try {
    const coworkingSpace = await CoworkingSpace.findById(
      req.params.coworkingSpaceId,
    );

    if (!coworkingSpace) {
      return res.status(404).json({
        success: false,
        message: `No co-working space with the id of ${req.params.coworkingSpaceId}`,
      });
    }

    // Do not add the same co-working space twice
    const alreadyAdded = req.user.favourites.some(
      (id) => id.toString() === coworkingSpace.id,
    );
    if (alreadyAdded) {
      return res.status(400).json({
        success: false,
        message: `Co-working space ${coworkingSpace.id} is already in your favourite list`,
      });
    }

    const user = await User.findByIdAndUpdate(
      req.user.id,
      { $addToSet: { favourites: coworkingSpace._id } },
      { new: true },
    );

    res.status(201).json({
      success: true,
      count: user.favourites.length,
      data: user.favourites,
    });
  } catch (error) {
    console.log(error);
    if (error.name === "CastError") {
      return res
        .status(400)
        .json({ success: false, message: "Invalid co-working space id" });
    }
    return res
      .status(500)
      .json({ success: false, message: "Cannot add favourite" });
  }
};

//@desc     Remove a co-working space from my favourite list
//@route    DELETE /api/v1/favourites/:coworkingSpaceId
//@access   Private
exports.removeFavourite = async (req, res, next) => {
  try {
    const inList = req.user.favourites.some(
      (id) => id.toString() === req.params.coworkingSpaceId,
    );
    if (!inList) {
      return res.status(404).json({
        success: false,
        message: `Co-working space ${req.params.coworkingSpaceId} is not in your favourite list`,
      });
    }

    const user = await User.findByIdAndUpdate(
      req.user.id,
      { $pull: { favourites: req.params.coworkingSpaceId } },
      { new: true },
    );

    res.status(200).json({
      success: true,
      count: user.favourites.length,
      data: user.favourites,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ success: false, message: "Cannot remove favourite" });
  }
};