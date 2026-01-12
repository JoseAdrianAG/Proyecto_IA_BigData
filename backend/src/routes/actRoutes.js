import express from "express";
import Actividad from "../models/actividad.js";
import { authenticateToken } from "../middleware/authMiddleware.js";
import { authorizeRoles } from "../middleware/roleMiddleware.js";

const router = express.Router();

// Crear actividad
router.post("/", authenticateToken, async (req, res) => {
  const { ciclo, modulo, nivel, enunciado } = req.body;

  if (!ciclo || !modulo || !nivel || !enunciado) {
    return res.status(400).json({ error: "Faltan campos obligatorios" });
  }

  const act = await Actividad.create({
    userId: req.user.id,
    ciclo,
    modulo,
    nivel,
    enunciado
  });

  res.status(201).json(act);
});

export default router;

// Historial de actividades del usuario
router.get("/", authenticateToken, async (req, res) => {
  const acts = await Actividad.find({ userId: req.user.id })
    .sort({ createdAt: -1 });

  res.json(acts);
});

// Crear actividad (todos)
router.post(
  "/",
  authenticateToken,
  authorizeRoles("profesor", "alumno"),
  async (req, res) => {
    res.json({solution: "Ejercicio creado"})
  }
);

// Ver solución (solo profesores)
router.get(
  "/:id/solution",
  authenticateToken,
  authorizeRoles("profesor"),
  async (req, res) => {
    res.json({ solution: "Solución completa del ejercicio" });
  }
);

router.post(
  "/generate",
  authenticateToken,
  authorizeRoles("profesor", "alumno"),
  async (req, res) => {
    const { ciclo, modulo, nivel } = req.body;

    const enunciado = `Actividad de ${modulo} para ${ciclo} (${nivel})`;
    const solucion = `Solución detallada de la actividad`;

    const act = await Actividad.create({
      userId: req.user.id,
      ciclo,
      modulo,
      nivel,
      enunciado,
      solucion: req.user.rol === "profesor" ? solucion : null
    });

    // 🔐 Respuesta según rol
    if (req.user.rol === "alumno") {
      return res.json({
        id: act._id,
        enunciado: act.enunciado
      });
    }

    res.json(act);
  }
);