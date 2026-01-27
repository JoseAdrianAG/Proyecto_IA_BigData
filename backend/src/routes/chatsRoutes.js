import express from "express";
import { authenticateToken } from "../middleware/authMiddleware.js";
import Chat from "../models/chat.js";
import Message from "../models/mensajes.js";

const router = express.Router();

// GET historial completo de un usuario
router.get("/chats", authenticateToken, async (req, res) => {
  try {
    const chats = await Chat.find({ userId: req.user.id })
      .sort({ createdAt: -1 }) // más recientes primero
      .select("_id title createdAt")
      .lean();

    res.json(
      chats.map(c => ({
        id: c._id.toString(),
        title: c.title,
        createdAt: c.createdAt
      }))
    );
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error recuperando chats" });
  }
});

router.put("/chats/:chatId", authenticateToken, async (req, res) => {
  try {
    const { title } = req.body;

    if (!title || title.trim() === "") {
      return res.status(400).json({ error: "Título requerido" });
    }

    const chat = await Chat.findOneAndUpdate(
      { _id: req.params.chatId, userId: req.user.id },
      { title },
      { new: true }
    );

    if (!chat) {
      return res.status(404).json({ error: "Chat no encontrado" });
    }

    res.json({
      id: chat._id,
      title: chat.title
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error actualizando chat" });
  }
});

router.delete("/chats/:chatId", authenticateToken, async (req, res) => {
  try {
    const chat = await Chat.findOneAndDelete({
      _id: req.params.chatId,
      userId: req.user.id
    });

    if (!chat) {
      return res.status(404).json({ error: "Chat no encontrado" });
    }

    await Message.deleteMany({ chatId: chat._id });

    res.json({ success: true });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error borrando chat" });
  }
});

export default router;