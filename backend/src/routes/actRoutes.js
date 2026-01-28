import express from "express";
import Actividad from "../models/actividad.js";
import Chat from "../models/chat.js";
import Mensajes from "../models/mensajes.js";
import { authenticateToken } from "../middleware/authMiddleware.js";
import { invokeAgent } from "../services/agenteService.js";

const router = express.Router();

/**
 * POST /generate-ia
 * Genera una actividad usando Amazon Bedrock Agent
 * - Alumno: solo enunciado
 * - Profesor: enunciado + solución
 */
router.post("/generate-ia", authenticateToken, async (req, res) => {
  try {
    const { ciclo, curso, nivel, solucion, userPrompt, chatId } = req.body;

    if (!ciclo || !curso || !nivel || !solucion || !userPrompt) {
      return res.status(400).json({ error: "Faltan campos obligatorios" });
    }

    // 1️⃣ Crear o reutilizar chat
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

    // 2️⃣ Guardar mensaje del usuario
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


    // 4️⃣ Invocar Agent (1 chat = 1 sesión)
    const agentResponse = await invokeAgent(
      prompt,
      chat._id.toString(),
      "LIVE"
    );

    // 5️⃣ Reconstruir respuesta
    let outputText = "";
    for await (const event of agentResponse.completion) {
      if (event.chunk?.bytes) {
        outputText += new TextDecoder().decode(event.chunk.bytes);
      }
    }

    // 6️⃣ Guardar mensaje del agente
    await Mensajes.create({
      chatId: chat._id,
      userId: req.user.id,
      role: "agent",
      message: outputText
    });

    // 7️⃣ Guardar actividad
    const activity = await Actividad.create({
      userId: req.user.id,
      ciclo,
      curso,
      nivel,
      enunciado: outputText,
      solucion
    });

    // 8️⃣ Respuesta
    res.json({
      chatId: chat._id,
      activity
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error generando actividad con Agent" });
  }
});

/**
 * POST /generate
 * Mock generator (NO Agent) — for testing frontend
 */
router.post("/generate", authenticateToken, async (req, res) => {
  try {
    const { ciclo, curso, nivel, solucion, userPrompt, chatId } = req.body;

    if (!ciclo || !curso || !nivel || !solucion || !userPrompt) {
      return res.status(400).json({ error: "Faltan campos obligatorios" });
    }

    // 1️⃣ Create or reuse chat
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

    // 2️⃣ Save user message
    await Mensajes.create({
      chatId: chat._id,
      userId: req.user.id,
      role: "user",
      message: userPrompt
    });

    // 3️⃣ MOCK AI RESPONSE (fixed content)
    const mockResponse = `
EXAMEN DE ${ciclo} - ${curso} (${nivel})

1. Explica la diferencia entre '==' e 'is' en Python.
2. ¿Qué es una lista por comprensión? Da un ejemplo.
3. Explica qué es una función y cómo se define.
4. ¿Qué es un diccionario y para qué se utiliza?

${solucion === "si" ? `
SOLUCIÓN:

1. '==' compara valores, 'is' compara referencias.
2. Una lista por comprensión permite crear listas de forma concisa.
3. Una función es un bloque de código reutilizable.
4. Un diccionario almacena pares clave-valor.
` : ""}
`.trim();

    // 4️⃣ Save agent message (mock)
    await Mensajes.create({
      chatId: chat._id,
      userId: req.user.id,
      role: "agent",
      message: mockResponse
    });

    // 5️⃣ Save activity
    const activity = await Actividad.create({
      userId: req.user.id,
      ciclo,
      curso,
      nivel,
      enunciado: mockResponse,
      solucion
    });

    // 6️⃣ Response (same structure as /generate-ia)
    res.json({
      chatId: chat._id,
      activity
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error generando actividad (mock)" });
  }
});


export default router;