import express from "express";
import { authenticateToken } from "../middleware/authMiddleware.js";
import Chat from "../models/historial.js";

const router = express.Router();

// GET historial completo de un usuario
router.get("/chat", authenticateToken, async (req, res) => {
  try {
    const { sessionId } = req.query; // opcional: filtrar por sesión

    const query = { userId: req.user.id };
    if (sessionId) query.sessionId = sessionId;

    const chats = await Chat.find(query)
      .sort({ createdAt: 1 }) // orden cronológico
      .select("-__v")         // opcional: quitar __v
      .lean();

    res.json(chats);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error recuperando historial de chats" });
  }
});

export default router;