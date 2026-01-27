import mongoose from "mongoose";

const messageSchema = new mongoose.Schema(
  {
    chatId: { type: mongoose.Schema.Types.ObjectId, ref: "Chat", required: true },
    userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    role: { type: String, enum: ["user", "agent"], required: true },
    message: { type: String, required: true }
  },
  { timestamps: true }
);

export default mongoose.model("Mensajes", messageSchema, "mensajes");
