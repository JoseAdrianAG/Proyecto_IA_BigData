import express from "express";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import User from "../models/user.js";

const router = express.Router();

router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  // 1. Comprobar usuario
  const user = await User.findOne({ email });
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
    { id: user._id, rol: user.rol },
    process.env.JWT_SECRET,
    { expiresIn: "8h" }
  );

  res.json({
    token,
    user: {
      id: user._id,
      nombre: user.nombre,
      email: user.email,
      rol: user.rol
    }
  });
});

export default router;