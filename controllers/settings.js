const Setting = require("../models/Setting");

//@desc     Get system settings (max active reservations per user)
//@route    GET /api/v1/settings
//@access   Private (admin)
exports.getSettings = async (req, res, next) => {
  try {
    const settings = await Setting.getSettings();

    res.status(200).json({
      success: true,
      data: settings,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ success: false, message: "Cannot get settings" });
  }
};

//@desc     Update max active reservations per user
//@route    PUT /api/v1/settings
//@access   Private (admin)
exports.updateSettings = async (req, res, next) => {
  try {
    const { maxReservations } = req.body;

    // maxReservations must be a whole number of at least 1
    if (!Number.isInteger(maxReservations) || maxReservations < 1) {
      return res.status(400).json({
        success: false,
        message: "Please provide maxReservations as an integer of at least 1",
      });
    }

    const settings = await Setting.getSettings();
    settings.maxReservations = maxReservations;
    settings.updatedAt = Date.now();
    await settings.save();

    res.status(200).json({
      success: true,
      data: settings,
    });
  } catch (error) {
    console.log(error);
    return res
      .status(500)
      .json({ success: false, message: "Cannot update settings" });
  }
};