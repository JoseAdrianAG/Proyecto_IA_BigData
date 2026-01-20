import express from "express";
import Actividad from "../models/actividad.js";
import Chat from "../models/historial.js";
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
    const { ciclo, modulo, nivel } = req.body;

    if (!ciclo || !modulo || !nivel) {
      return res.status(400).json({ error: "Faltan campos obligatorios" });
    }

    const includeSolution = req.user.rol === "profesor";

    const prompt = `
Actúa como un profesor de Formación Profesional en España.

Genera una actividad evaluable para el ciclo formativo de grado superior:
- Ciclo: ${ciclo}
- Módulo profesional: ${modulo}
- Nivel: ${nivel}

La actividad debe:
- Estar alineada con el currículo oficial del BOE y la Conselleria
- Ser adecuada para alumnado de FP
- Incluir contexto, enunciado claro y criterios de evaluación

${includeSolution
  ? "Incluye una solución detallada y razonada."
  : "NO incluyas la solución, solo el enunciado."
}

Responde SIEMPRE en español.
`;


    const sessionId = req.user.id;

    // Guardar mensaje del usuario
    await Chat.create({
      userId: req.user.id,
      sessionId,
      role: "user",
      message: prompt
    });

    // Invocar Agent
    const agentResponse = await invokeAgent(prompt, sessionId, "LIVE");

    // Reconstruir respuesta
    let outputText = "";
    for await (const event of agentResponse.completion) {
      if (event.chunk?.bytes) {
        outputText += new TextDecoder().decode(event.chunk.bytes);
      }
    }

    // Guardar respuesta del Agent
    await Chat.create({
      userId: req.user.id,
      sessionId,
      role: "agent",
      message: outputText
    });

    // Guardar actividad
    const activity = await Actividad.create({
      userId: req.user.id,
      ciclo,
      modulo,
      nivel,
      enunciado: outputText,
      solucion: includeSolution ? outputText : null
    });

    // Respuesta según rol
    if (!includeSolution) {
      return res.json({
        id: activity._id,
        enunciado: activity.enunciado
      });
    }

    res.json(activity);

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error generando actividad con Agent" });
  }
});

export default router;