import express from "express";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import Usuario from "../models/user.js";

const router = express.Router();
router.post("/register", async (req, res) => {
  try {
    const { nombre, email, password } = req.body;

    if (!nombre || !email || !password) {
      return res.status(400).json({ error: "Faltan campos obligatorios" });
    }

    const existingUser = await Usuario.findOne({ email });
    if (existingUser) {
      return res.status(409).json({ error: "El email ya está registrado" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const user = await Usuario.create({
      nombre,
      email,
      password: hashedPassword
    });

    const token = jwt.sign(
      { id: user._id },
      process.env.JWT_SECRET,
      { expiresIn: "8h" }
    );

    res.status(201).json({
      token,
      user: {
        id: user._id,
        nombre: user.nombre,
        email: user.email
      }
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error creando usuario" });
  }
});

router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  // 1. Comprobar usuario
  const user = await Usuario.findOne({ email });
  if (!user) {
    return res.status(401).json({ error: "Credenciales incorrectas" });
  }

  // 2. Comprobar contraseña
  const valid = await bcrypt.compare(password, user.password);
  if (!valid) {
    return res.status(401).json({ error: "Credenciales incorrectas" });
  }

  // 3. Generar JWT
  const token = jwt.sign(
    { id: user._id},
    process.env.JWT_SECRET,
    { expiresIn: "8h" }
  );

  res.json({
    token,
    user: {
      id: user._id,
      nombre: user.nombre,
      email: user.email
    }
  });
});

export default router;