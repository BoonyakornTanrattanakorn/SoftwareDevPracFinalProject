const mongoose = require("mongoose");

const SettingSchema = new mongoose.Schema({
  maxReservations: {
    type: Number,
    required: [true, "Please add a maximum number of reservations"],
    min: [1, "Maximum number of reservations must be at least 1"],
    validate: {
      validator: Number.isInteger,
      message: "Maximum number of reservations must be an integer",
    },
    default: 3,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// Get the system settings (there is only one document), create it with default values if it does not exist
SettingSchema.statics.getSettings = async function () {
  let settings = await this.findOne();
  if (!settings) {
    settings = await this.create({});
  }
  return settings;
};

module.exports = mongoose.model("Setting", SettingSchema);