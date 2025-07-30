// the file below is a working test of the optimize button with a pre fixed message to see the optimize button working
// it basically fetches what's written on ChatGPT chatbox and replaces it with the fixed message "That is just a text to make sure that we are able to correctly fetch the content from ChatGPT chatbox and replace it with this dummy message"


console.log("🚀 [StubOptimizer] content_v1.js loaded");

// Selectors & IDs
const SEND_BTN_SELECTOR   = 'button[data-testid="send-button"]';
const INPUT_DIV_SELECTOR  = 'div[contenteditable="true"]';
const BTN_ID              = 'stub-optimizer-btn';

const poll = setInterval(() => {
  const sendBtn = document.querySelector(SEND_BTN_SELECTOR);
  if (!sendBtn) return;
  clearInterval(poll);

  // 1) Clear any pre-existing text in the prompt box
  const inputDiv = document.querySelector(INPUT_DIV_SELECTOR);
  if (inputDiv && inputDiv.innerText.trim() !== "") {
    console.log("🚀 [StubOptimizer] Clearing stale input");
    inputDiv.innerText = "";
    inputDiv.dispatchEvent(new Event("input", { bubbles: true }));
  }

  // 2) Inject our Optimize button (once)
  if (!document.getElementById(BTN_ID)) {
    console.log("🚀 [StubOptimizer] Found send-button – injecting Optimize button");
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


// A stub “optimizer” that pretends to call Groq
function stubOptimize(promptText) {
  console.log("🚀 [StubOptimizer] stubOptimize received:", promptText);
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(
        "That is just a text to make sure that we are able to correctly fetch the content from ChatGPT chatbox and replace it with this dummy message"
      );
    }, 500);
  });
}


// Click handler: grab prompt, run stub, swap in dummy text
async function onOptimizeClick() {
  const btn = document.getElementById(BTN_ID);
  btn.disabled = true;
  btn.innerText = "Optimizing…";

  // Grab the current prompt text
  const inputDiv = document.querySelector(INPUT_DIV_SELECTOR);
  if (!inputDiv) {
    console.error("🚀 [StubOptimizer] ❌ input div not found");
    btn.innerText = "Error";
    setTimeout(() => (btn.innerText = "Optimize"), 2000);
    btn.disabled = false;
    return;
  }
  const originalPrompt = inputDiv.innerText.trim();
  console.log("🚀 [StubOptimizer] Original prompt:", originalPrompt);

  // Run our stub instead of a real API call
  try {
    const optimized = await stubOptimize(originalPrompt);
    console.log("🚀 [StubOptimizer] Stub returned:", optimized);

    // Replace the contentEditable’s text
    inputDiv.innerText = optimized;
    // Dispatch an input event so React notices
    inputDiv.dispatchEvent(new Event("input", { bubbles: true }));
  } catch (err) {
    console.error("🚀 [StubOptimizer] Stub failed:", err);
    btn.innerText = "Error";
    setTimeout(() => (btn.innerText = "Optimize"), 2000);
  } finally {
    btn.disabled = false;
    btn.innerText = "Optimize";
  }
}
