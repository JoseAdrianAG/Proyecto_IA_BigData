import express from "express";
import Actividad from "../models/actividad.js";
import Chat from "../models/chat.js";
import Mensajes from "../models/mensajes.js";
import { authenticateToken } from "../middleware/authMiddleware.js";
import { invokeAgent } from "../services/agenteService.js";

const router = express.Router();

router.post("/generate-ia", authenticateToken, async (req, res) => {
  try {
    const { ciclo, curso, nivel, solucion, userPrompt, chatId } = req.body;

    if (!ciclo || !curso || !nivel || !solucion || !userPrompt) {
      return res.status(400).json({ error: "Faltan campos obligatorios" });
    }

    //Crear o reutilizar chat
    let chat;

    if (chatId) {
      chat = await Chat.findOne({ _id: chatId, userId: req.user.id });
      if (!chat) {
        return res.status(404).json({ error: "Chat no encontrado" });
      }
    } else {
      chat = await Chat.create({
        userId: req.user.id,
        title: `${ciclo} - ${curso} (${nivel})`
      });
    }

    //Guardar mensaje del usuario
    await Mensajes.create({
      chatId: chat._id,
      userId: req.user.id,
      role: "user",
      message: userPrompt
    });

    const prompt = `
        Rol del usuario: ${req.user.rol}
          
        Ciclo: ${ciclo}
        Curso: ${curso}
        Nivel: ${nivel}
        Solución: ${solucion}
          
        ${userPrompt}
        Si la solución es si, SI incluyes la solución.
        Si la solución es no, NO incluyes la solución.
        Responde siempre en español
        Contesta siempre, no pidas mas informacion, si no te indican temas escogelos tu aleatoriamente
        `;


    //Invocar Agent
    const agentResponse = await invokeAgent(
      prompt,
      chat._id.toString(),
      "LIVE"
    );

    //Reconstruir respuesta
    let outputText = "";
    for await (const event of agentResponse.completion) {
      if (event.chunk?.bytes) {
        outputText += new TextDecoder().decode(event.chunk.bytes);
      }
    }

    //Guardar mensaje del agente
    await Mensajes.create({
      chatId: chat._id,
      userId: req.user.id,
      role: "agent",
      message: outputText
    });

    //Guardar actividad
    const activity = await Actividad.create({
      userId: req.user.id,
      ciclo,
      curso,
      nivel,
      enunciado: outputText,
      solucion
    });

    //Respuesta
    res.json({
      chatId: chat._id,
      activity
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error generando actividad con Agent" });
  }
});

export default router;