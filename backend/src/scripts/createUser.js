import mongoose from "mongoose";
import bcrypt from "bcrypt";
import dotenv from "dotenv";
import user from "../models/user.js";

dotenv.config();

await mongoose.connect("mongodb://localhost:27018/proyectoIA");

const passwordHash = await bcrypt.hash("1234", 10);

await user.create({
  nombre: "Prueba Alumno",
  email: "adrian@gmail.com",
  rol: "alumno",
  password: passwordHash
});

console.log("Usuario creado correctamente");
process.exit();