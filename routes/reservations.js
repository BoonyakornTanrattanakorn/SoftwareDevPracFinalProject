const express = require("express");
const {
  getReservations,
  getReservation,
  addReservation,
  updateReservation,
  deleteReservation,
  exportReservations,
} = require("../controllers/reservations");
const router = express.Router({ mergeParams: true });

const { protect, authorize } = require("../middleware/auth");

router
  .route("/")
  .get(protect, getReservations)
  .post(protect, authorize("admin", "user"), addReservation);
// Must be before "/:id", otherwise "export" is treated as a reservation id
router.route("/export").get(protect, authorize("admin"), exportReservations);
router
  .route("/:id")
  .get(protect, getReservation)
  .put(protect, authorize('admin', 'user'), updateReservation)
  .delete(protect, authorize('admin', 'user'), deleteReservation);

module.exports = router;
