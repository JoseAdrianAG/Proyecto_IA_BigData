import mongoose from "mongoose";

const userSchema = new mongoose.Schema({
  nombre: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  password: {
    type: String,
    required: true
  },
  rol: {
    type: String,
    enum: ["profesor", "alumno"],
    default: "profesor"
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

export default mongoose.model("Usuario", userSchema, "usuarios");