// ===== Smart Task Planner — Node.js Backend =====
// Serves the frontend and proxies Gemini API calls to keep the API key secret.

import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Load environment variables from .env
dotenv.config();

// Resolve __dirname for ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ===== Gemini API Setup =====
const API_KEY = process.env.API_KEY;

if (!API_KEY || API_KEY === "YOUR_API_KEY_HERE") {
  console.error("\n❌  Missing API key!");
  console.error("   Open Week3/.env and replace YOUR_API_KEY_HERE with your Gemini API key.");
  console.error("   Get one free at: https://aistudio.google.com/\n");
  process.exit(1);
}

const ai = new GoogleGenAI({ apiKey: API_KEY });

// ===== Generate Tasks via Gemini =====
async function generateTasks(goal) {
  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: `You are a professional project planner. The user wants to achieve the following goal:

"${goal}"

Break this goal down into a clear, actionable step-by-step plan. Return 6 to 10 tasks. Each task should have:
- A concise task name (action-oriented, starting with a verb)
- A priority level (High, Medium, or Low)
- An estimated time to complete (e.g., "30 mins", "2 hours", "1 day")

Order the tasks chronologically — the first task should be done first.`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "OBJECT",
          properties: {
            tasks: {
              type: "ARRAY",
              items: {
                type: "OBJECT",
                properties: {
                  task_name: { type: "STRING" },
                  priority: { type: "STRING" },
                  estimated_time: { type: "STRING" },
                },
              },
            },
          },
        },
      },
    });

    const data = JSON.parse(response.text);
    return { success: true, tasks: data.tasks };
  } catch (error) {
    console.error("Gemini API Error:", error.message);
    return {
      success: false,
      error: error.message || "Failed to generate tasks. Please try again.",
    };
  }
}

// ===== MIME Types for Static File Serving =====
const MIME_TYPES = {
  ".html": "text/html",
  ".css": "text/css",
  ".js": "application/javascript",
  ".json": "application/json",
  ".png": "image/png",
  ".ico": "image/x-icon",
};

// ===== HTTP Server =====
const PORT = 3000;

const server = http.createServer(async (req, res) => {
  // --- CORS & JSON headers helper ---
  const sendJSON = (statusCode, data) => {
    res.writeHead(statusCode, { "Content-Type": "application/json" });
    res.end(JSON.stringify(data));
  };

  // --- POST /generate — Gemini API proxy ---
  if (req.method === "POST" && req.url === "/generate") {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", async () => {
      try {
        const { goal } = JSON.parse(body);

        if (!goal || !goal.trim()) {
          return sendJSON(400, { success: false, error: "Goal cannot be empty." });
        }

        console.log(`\n🎯 Goal received: "${goal}"`);
        console.log("⏳ Calling Gemini API...");

        const result = await generateTasks(goal.trim());

        if (result.success) {
          console.log(`✅ Generated ${result.tasks.length} tasks successfully.`);
        } else {
          console.log(`❌ Error: ${result.error}`);
        }

        sendJSON(result.success ? 200 : 500, result);
      } catch (err) {
        sendJSON(400, { success: false, error: "Invalid request format." });
      }
    });
    return;
  }

  // --- Static file serving ---
  let filePath = req.url === "/" ? "/index.html" : req.url;
  filePath = path.join(__dirname, filePath);

  const ext = path.extname(filePath);
  const contentType = MIME_TYPES[ext] || "application/octet-stream";

  try {
    const content = fs.readFileSync(filePath);
    res.writeHead(200, { "Content-Type": contentType });
    res.end(content);
  } catch {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("404 Not Found");
  }
});

server.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════╗
║   🧠  Smart Task Planner is running!         ║
║                                               ║
║   Open in browser:  http://localhost:${PORT}     ║
║   Press Ctrl+C to stop the server             ║
╚═══════════════════════════════════════════════╝
  `);
});
