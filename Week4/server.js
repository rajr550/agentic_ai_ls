// ===== Finance Tracker — Server =====
// Express server that serves static files and proxies Gemini API calls.

import express from "express";
import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";
import { fileURLToPath } from "node:url";
import path from "node:path";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ===== Validate API Key =====
const API_KEY = process.env.GEMINI_API_KEY;

if (!API_KEY || API_KEY === "your-key-here" || API_KEY === "YOUR_API_KEY_HERE") {
  console.error("\n❌  Missing Gemini API key!");
  console.error("   Open Week4/.env and set your GEMINI_API_KEY.");
  console.error("   Get one free at: https://aistudio.google.com/\n");
  process.exit(1);
}

const ai = new GoogleGenAI({ apiKey: API_KEY });

// ===== Express Setup =====
const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// ===== AI Endpoint =====
app.post("/api/ai", async (req, res) => {
  try {
    const { prompt } = req.body;

    if (!prompt || !prompt.trim()) {
      return res.status(400).json({ error: "Prompt is required." });
    }

    console.log(`\n🤖 AI request: "${prompt.substring(0, 80)}..."`);

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
    });

    const reply = response.text;
    console.log(`✅ AI responded (${reply.length} chars)`);

    res.json({ reply });
  } catch (error) {
    console.error("❌ Gemini API Error:", error.message);
    res.status(500).json({
      error: "Failed to get AI response. Please try again.",
    });
  }
});

// ===== Start Server =====
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════╗
║   💰  Finance Tracker is running!                ║
║                                                  ║
║   Open in browser:  http://localhost:${PORT}        ║
║   Press Ctrl+C to stop the server                ║
╚══════════════════════════════════════════════════╝
  `);
});
