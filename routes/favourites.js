const express = require("express");
const {
  getFavourites,
  addFavourite,
  removeFavourite,
} = require("../controllers/favourites");

const router = express.Router();

const { protect } = require("../middleware/auth");

router.route("/").get(protect, getFavourites);
router
  .route("/:coworkingSpaceId")
  .post(protect, addFavourite)
  .delete(protect, removeFavourite);

module.exports = router;
