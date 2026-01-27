import mongoose from "mongoose";

const activitySchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true
  },
  ciclo: {
    type: String,
    required: true,
    enum: ["DAM", "DAW", "ASIX"]
  },
  curso: {
    type: Number,
    required: true,
    enum: [1, 2]
  },
  nivel: {
    type: String,
    required: true
  },
  enunciado: {
    type: String,
    required: true
  },
  solucion: {
    type: String,
    default: null
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

export default mongoose.model("Actividad", activitySchema, "actividades");