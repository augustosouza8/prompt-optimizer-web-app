// the file below is a working test of the optimize button the optimizes the user prompt by sending it direct to a Groq model and fetching the result


console.log("🚀 [Optimizer] content_v1.js loaded");

// —— Configuration ——
const GROQ_API_KEY = "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";                // ← Replace with your key
const GROQ_MODEL   = "llama-3.3-70b-versatile";
const SYSTEM_PROMPT = "You are a prompt-engineering expert. The user will give you a simple prompt, and you must rewrite and optimize it for clarity, specificity, and better results. If the user specifies a writing tone (e.g., 'Standard writing tone', 'Technical writing tone'), incorporate that tone into the optimized prompt. If no tone is specified, use a clear, professional tone. Always make the final optimized prompt more specific, actionable, and likely to produce high-quality responses. IMPORTANT: Your response must contain ONLY the final optimized prompt with no additional commentary or explanation."

// —— Selectors & IDs ——
const SEND_BTN_SELECTOR   = 'button[data-testid="send-button"]';
const INPUT_DIV_SELECTOR  = 'div[contenteditable="true"]';
const BTN_ID              = 'optimizer-btn';

// —— 1) Wait for Send button, clear stale text, inject Optimize ——
const poll = setInterval(() => {
  const sendBtn = document.querySelector(SEND_BTN_SELECTOR);
  if (!sendBtn) return;
  clearInterval(poll);

  // a) Clear any leftover text on a fresh chat
  const inputDiv = document.querySelector(INPUT_DIV_SELECTOR);
  if (inputDiv && inputDiv.innerText.trim() !== "") {
    inputDiv.innerText = "";
    inputDiv.dispatchEvent(new Event("input", { bubbles: true }));
    console.log("🚀 [Optimizer] Cleared stale input");
  }

  // b) Inject Optimize button (once)
  if (!document.getElementById(BTN_ID)) {
    console.log("🚀 [Optimizer] Injecting Optimize button");
    const btn = document.createElement("button");
    btn.id = BTN_ID;
    btn.type = "button";
    btn.innerText = "Optimize";
    Object.assign(btn.style, {
      marginRight: "8px",
      padding: "0 12px",
      border: "1px solid var(--color-border-primary)",
      borderRadius: "4px",
      background: "var(--color-bg-secondary)",
      color: "var(--color-text-primary)",
      fontSize: "14px",
      cursor: "pointer"
    });
    sendBtn.parentNode.insertBefore(btn, sendBtn);
    btn.addEventListener("click", onOptimizeClick);
  }
}, 300);


// —— 2) Click handler: fetch the prompt, call Groq, swap in optimized text ——
async function onOptimizeClick() {
  const btn = document.getElementById(BTN_ID);
  btn.disabled = true;
  btn.innerText = "Optimizing…";

  // 2a) Grab the current user prompt
  const inputDiv = document.querySelector(INPUT_DIV_SELECTOR);
  if (!inputDiv) {
    console.error("🚀 [Optimizer] ❌ input div not found");
    showError(btn);
    return;
  }
  const originalPrompt = inputDiv.innerText.trim();
  if (!originalPrompt) {
    console.log("🚀 [Optimizer] Input is empty");
    showError(btn, /* skip restore */ true);
    return;
  }
  console.log("🚀 [Optimizer] Original prompt:", originalPrompt);

  // 2b) Call Groq Chat Completions on the OpenAI-compatible endpoint
  try {
    const response = await fetch(
      "https://api.groq.com/openai/v1/chat/completions",
      {
        method: "POST",
        headers: {
          "Content-Type":  "application/json",
          "Authorization": `Bearer ${GROQ_API_KEY}`
        },
        body: JSON.stringify({
          model:    GROQ_MODEL,
          messages: [
            { role: "system",  content: SYSTEM_PROMPT  },
            { role: "user",    content: originalPrompt }
          ]
        })
      }
    );

    if (!response.ok) {
      console.error("🚀 [Optimizer] API error", response.status, await response.text());
      showError(btn);
      return;
    }

    const data = await response.json();
    const optimized = data.choices?.[0]?.message?.content?.trim();
    console.log("🚀 [Optimizer] Optimized prompt:", optimized);

    if (optimized) {
      // 2c) Replace the contentEditable’s text
      inputDiv.innerText = optimized;
      // 2d) Dispatch an input event so ChatGPT’s UI picks it up
      inputDiv.dispatchEvent(new Event("input", { bubbles: true }));
    } else {
      console.warn("🚀 [Optimizer] No assistant message returned");
      showError(btn);
    }
  } catch (err) {
    console.error("🚀 [Optimizer] Fetch failed:", err);
    showError(btn);
  } finally {
    btn.disabled = false;
    btn.innerText = "Optimize";
  }
}


// —— Helper: flash error state on the button ——
function showError(btn, skipRestore = false) {
  btn.innerText = "Error";
  if (!skipRestore) {
    setTimeout(() => { btn.innerText = "Optimize"; }, 2000);
  }
  btn.disabled = false;
}
