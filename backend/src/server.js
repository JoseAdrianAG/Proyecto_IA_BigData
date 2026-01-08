import express from "express";
import dotenv from "dotenv";
import mongoose from "mongoose";
import authRoutes from "./routes/authRoutes.js";
import testRoutes from "./routes/testRoutes.js";
import actRoutes from "./routes/actRoutes.js";

dotenv.config();

const app = express();
app.use(express.json());

//Rutas
app.use("/api/auth", authRoutes);
app.use("/api/test", testRoutes)
app.use("/api/actividades", actRoutes);

app.get("/", (req, res) => {
  res.send("Servidor conectado correctamente ✔️");
});

mongoose.connect(process.env.MONGO_URI)
  .then(() => {
    app.listen(3000, () => {
      console.log("Servidor escuchando en http://localhost/3000:");
    });
  });
