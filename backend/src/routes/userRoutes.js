import express from "express";
import Usuario from "../models/user.js";
import bcrypt from "bcrypt";
import { authenticateToken } from "../middleware/authMiddleware.js";

const router = express.Router();

/**
 * PUT /update-profile
 * Actualiza el perfil del usuario (nombre, email, avatar)
 */
router.put("/update", authenticateToken, async (req, res) => {
  try {
    const { nombre, email, avatar } = req.body;

    // Validar campos obligatorios
    if (!nombre || !email) {
      return res.status(400).json({ error: "Faltan campos obligatorios" });
    }

    // Buscar usuario autenticado
    const user = await Usuario.findById(req.user.id);
    if (!user) {
      return res.status(404).json({ error: "Usuario no encontrado" });
    }

    // Verificar si el email ya está en uso por otro usuario
    if (email !== user.email) {
      const emailExists = await Usuario.findOne({ 
        email, 
        _id: { $ne: req.user.id } 
      });
      if (emailExists) {
        return res.status(400).json({ error: "El email ya está en uso" });
      }
    }

    // Actualizar campos
    const updateData = {
      nombre,
      email
    };
    
    if (avatar) {
      updateData.avatar = avatar;
    }

    const updatedUser = await Usuario.findByIdAndUpdate(
      req.user.id,
      { $set: updateData },
      { new: true, runValidators: true }
    ).select("-password");

    res.json({
      message: "Perfil actualizado correctamente",
      user: updatedUser
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error al actualizar el perfil" });
  }
});

/**
 * PUT /change-password
 * Cambia la contraseña del usuario autenticado
 */
router.put("/cambiar-password", authenticateToken, async (req, res) => {
  try {
    const { currentPassword, newPassword } = req.body;

    // Validar campos obligatorios
    if (!currentPassword || !newPassword) {
      return res.status(400).json({ error: "Faltan campos obligatorios" });
    }

    // Buscar usuario
    const user = await Usuario.findById(req.user.id);
    if (!user) {
      return res.status(404).json({ error: "Usuario no encontrado" });
    }

    // Verificar contraseña actual
    const isPasswordValid = await bcrypt.compare(currentPassword, user.password);
    if (!isPasswordValid) {
      return res.status(400).json({ error: "Contraseña actual incorrecta" });
    }

    // Encriptar nueva contraseña
    const hashedPassword = await bcrypt.hash(newPassword, 10);

    // Actualizar contraseña
    await Usuario.findByIdAndUpdate(req.user.id, { 
      password: hashedPassword 
    });

    res.json({ 
      message: "Contraseña actualizada correctamente" 
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error al cambiar la contraseña" });
  }
});

router.get("/perfil", authenticateToken, async (req, res) => {
  try {
    const user = await Usuario.findById(req.user.id).select("-password");
    
    if (!user) {
      return res.status(404).json({ error: "Usuario no encontrado" });
    }

    res.json({ user });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Error al obtener el perfil" });
  }
});

export default router;