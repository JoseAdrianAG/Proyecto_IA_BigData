import mongoose from "mongoose";

const chatSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  sessionId: { type: String, required: true },
  role: { type: String, enum: ["user", "agent"], required: true },
  message: { type: String, required: true },
  activityId: { type: mongoose.Schema.Types.ObjectId, ref: "Activity" },
  createdAt: { type: Date, default: Date.now }
});

export default mongoose.model("Historial", chatSchema, "historiales_chat");