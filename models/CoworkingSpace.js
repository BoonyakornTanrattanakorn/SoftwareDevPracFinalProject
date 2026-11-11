const mongoose = require("mongoose");

const CoworkingSpaceSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, "Please add a name"],
      unique: true,
      trim: true,
      maxlength: [50, "Name can not be more than 50 characters"],
    },
    address: { type: String, required: [true, "Please add an address"] },
    tel: { type: String, required: [true, "Please add a telephone number"] },
    openTime: {
      type: String,
      required: [true, "Please add an open time"],
      match: [/^([01]\d|2[0-3]):[0-5]\d$/, "Use HH:mm format, e.g. 08:00"],
    },
    closeTime: {
      type: String,
      required: [true, "Please add a close time"],
      match: [/^([01]\d|2[0-3]):[0-5]\d$/, "Use HH:mm format, e.g. 20:00"],
    },
  },
  {
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  },
);

// Reverse populate with virtuals
CoworkingSpaceSchema.virtual("reservations", {
  ref: "Reservation",
  localField: "_id",
  foreignField: "coworkingSpace",
  justOne: false,
});

module.exports = mongoose.model("Hospital", HospitalSchema);
