import express from "express";
import { authenticateToken } from "../middleware/authMiddleware.js";
import Mensajes from "../models/mensajes.js"

const router = express.Router();

// GET historial completo de un usuario
router.get("/chats/:chatId/mensajes", authenticateToken, async (req, res) => {
  try {
    const mensajes = await Mensajes.find({
      chatId: req.params.chatId,
      userId: req.user.id
    })
      .sort({ createdAt: 1 })
      .select("role message createdAt")
      .lean();

    res.json(mensajes);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error recuperando mensajes" });
  }
});

export default router;