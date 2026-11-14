const express = require("express");
const {
  register,
  login,
  getMe,
  updateMe,
  logout,
} = require("../controllers/auth");

const router = express.Router();

const { protect } = require("../middleware/auth");

router.post("/register", register);
router.post("/login", login);
router.get("/me", protect, getMe);
router.put("/me", protect, updateMe);
router.get("/logout", protect, logout);

module.exports = router;
