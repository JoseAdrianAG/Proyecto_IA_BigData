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

  //Comprobar usuario
  const user = await Usuario.findOne({ email });
  if (!user) {
    return res.status(401).json({ error: "Credenciales incorrectas" });
  }

  //Comprobar contraseña
  const valid = await bcrypt.compare(password, user.password);
  if (!valid) {
    return res.status(401).json({ error: "Credenciales incorrectas" });
  }

  //Generar JWT
  const token = jwt.sign(
    { id: user._id },
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


router.put("/update-profile", async (req, res) => {
  try {
    const { id, nombre, email } = req.body;

    const updatedUser = await Usuario.findByIdAndUpdate(
      id,
      { nombre, email },
      { new: true }
    );

    if (!updatedUser) return res.status(404).json({ error: "Usuario no encontrado" });

    res.json({
      message: "Perfil actualizado",
      user: { id: updatedUser._id, nombre: updatedUser.nombre, email: updatedUser.email }
    });
  } catch (error) {
    res.status(500).json({ error: "Error al actualizar perfil" });
  }
});

router.put("/change-password", async (req, res) => {
  try {
    const { id, oldPassword, newPassword } = req.body;

    const user = await Usuario.findById(id);
    if (!user) {
      return res.status(404).json({ error: "Usuario no encontrado" });
    }

    const valid = await bcrypt.compare(oldPassword, user.password);
    if (!valid) {
      return res.status(401).json({ error: "Contraseña actual incorrecta" });
    }

    user.password = await bcrypt.hash(newPassword, 10);
    await user.save();

    return res.status(200).json({
      message: "Contraseña actualizada correctamente"
    });

  } catch (error) {
    console.error("Change password error:", error);
    return res.status(500).json({
      error: "Error al cambiar contraseña"
    });
  }
});


export default router;