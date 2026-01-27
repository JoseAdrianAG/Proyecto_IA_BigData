import mongoose from "mongoose";

const chatSchema = new mongoose.Schema(
  {
    userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
    title: { type: String, required: true }
  },
  { timestamps: true }
);

export default mongoose.model("Chats", chatSchema, "chats");
