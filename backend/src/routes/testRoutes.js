import express from "express";
import { authenticateToken } from "../middleware/authMiddleware.js";

const router = express.Router();

router.get("/private", authenticateToken, (req, res) => {
  res.json({
    msg: "Acceso autorizado",
    user: req.user
  });
});

export default router;
