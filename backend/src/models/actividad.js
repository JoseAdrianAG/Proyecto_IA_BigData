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
  modulo: {
    type: String,
    required: true
  },
  nivel: {
    type: String,
    required: true
  },
  enunciado: {
    type: String,
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

export default mongoose.model("Actividad", activitySchema, "actividades");
