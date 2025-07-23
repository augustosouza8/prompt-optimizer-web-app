// DEBUG: confirm this file actually loaded
console.log("📦 [Optimizer] content.js loaded");

// The selector ChatGPT currently uses for its Send button
const SEND_BTN_SELECTOR = 'button[data-testid="send-button"]';
const OPT_BTN_ID = 'optimize-prompt-btn';

// 1) Poll every 300ms until we see the Send button on the page
const poll = setInterval(() => {
  const sendBtn = document.querySelector(SEND_BTN_SELECTOR);
  if (!sendBtn) return;
  clearInterval(poll);
  console.log("📦 [Optimizer] Found ChatGPT Send button in DOM");
  injectOptimizeButton(sendBtn);
}, 300);

// 2) Inject our button to the left of Send
function injectOptimizeButton(sendBtn) {
  // prevent double‑inject
  if (document.getElementById(OPT_BTN_ID)) {
    console.log("📦 [Optimizer] Button already injected");
    return;
  }

  console.log("📦 [Optimizer] Injecting Optimize button");
  const btn = document.createElement('button');
  btn.id = OPT_BTN_ID;
  btn.type = 'button';
  btn.innerText = 'Optimize';
  Object.assign(btn.style, {
    marginRight: '8px',
    padding: '0 12px',
    border: '1px solid var(--color-border-primary)',
    borderRadius: '4px',
    background: 'var(--color-bg-secondary)',
    color: 'var(--color-text-primary)',
    fontSize: '14px',
    cursor: 'pointer'
  });

  sendBtn.parentNode.insertBefore(btn, sendBtn);
  btn.addEventListener('click', onOptimizeClick);
}

// 3) Click handler: grab the textarea, call your Groq API, swap in the optimized prompt
async function onOptimizeClick() {
  const textarea = document.querySelector('textarea[placeholder^="Send"]');
  if (!textarea) {
    console.error("📦 [Optimizer] Could not find the input textarea");
    return;
  }

  const original = textarea.value.trim();
  if (!original) {
    console.log("📦 [Optimizer] Input is empty; nothing to optimize");
    return;
  }

  const btn = document.getElementById(OPT_BTN_ID);
  btn.disabled = true;
  btn.innerText = 'Optimizing…';
  console.log("📦 [Optimizer] Sending to Groq API:", original);

  try {
    const res = await fetch('https://api.groq.com/v1/inference', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'your-optimizer-model-name',
        prompt: original
      })
    });

    if (!res.ok) {
      console.error('📦 [Optimizer] API error', res.status, await res.text());
      return;
    }

    const json = await res.json();
    const optimized = json.choices?.[0]?.text?.trim();
    console.log('📦 [Optimizer] Got back:', optimized);

    if (optimized) {
      textarea.value = optimized;
      // move cursor to end
      textarea.setSelectionRange(optimized.length, optimized.length);
    } else {
      console.warn('📦 [Optimizer] No optimized text returned');
    }
  } catch (err) {
    console.error('📦 [Optimizer] Fetch failed:', err);
  } finally {
    btn.disabled = false;
    btn.innerText = 'Optimize';
  }
}
