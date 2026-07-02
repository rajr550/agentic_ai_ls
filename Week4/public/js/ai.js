// ===== Finance Tracker — AI Module =====
// Async helper to call the Gemini API through our server proxy.

async function askAI(prompt) {
  try {
    const res = await fetch("/api/ai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Server responded with ${res.status}`);
    }

    const data = await res.json();

    if (data.error) {
      throw new Error(data.error);
    }

    return data.reply;
  } catch (error) {
    console.error("AI Error:", error);
    throw error;
  }
}
