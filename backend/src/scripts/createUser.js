import mongoose from "mongoose";
import bcrypt from "bcrypt";
import dotenv from "dotenv";
import User from "../models/user.js";

dotenv.config();

await mongoose.connect("mongodb://localhost:27018/proyectoIA");

const passwordHash = await bcrypt.hash("1234", 10);

await User.create({
  nombre: "Prueba Adrian",
  email: "prueba@gmail.com",
  password: passwordHash
});

console.log("Usuario creado correctamente");
process.exit();
