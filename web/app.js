const form = document.querySelector("#message-form");
const input = document.querySelector("#message-input");
const sendButton = document.querySelector("#send-button");
const conversation = document.querySelector("#conversation");
const clearButton = document.querySelector("#clear-chat");

const fields = {
  apiStatus: document.querySelector("#api-status"),
  kbStatus: document.querySelector("#kb-status"),
  intent: document.querySelector("#intent-value"),
  source: document.querySelector("#source-value"),
  confidence: document.querySelector("#confidence-value"),
  review: document.querySelector("#review-value"),
  checklists: document.querySelector("#checklist-sources"),
  normative: document.querySelector("#normative-sources"),
  protocols: document.querySelector("#protocol-sources"),
};

const sourceLabels = {
  qa: "Perguntas e respostas",
  corrected: "Resposta corrigida",
  checklist: "Checklist operacional",
  historical: "Base histórica",
  normative: "Base normativa",
  fallback: "Contato SEPLAN",
};

function removeEmptyState() {
  const empty = conversation.querySelector(".empty-state");
  if (empty) {
    empty.remove();
  }
}

function addMessage(role, text) {
  removeEmptyState();
  const node = document.createElement("article");
  node.className = `message ${role}`;
  const label = role === "user" ? "Cidadão" : "Agente";
  node.innerHTML = `<small>${label}</small>${escapeHtml(text)}`;
  conversation.appendChild(node);
  conversation.scrollTop = conversation.scrollHeight;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setList(element, values) {
  element.innerHTML = "";
  if (!values || values.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Sem fonte específica nesta resposta.";
    element.appendChild(li);
    return;
  }

  values.forEach((value) => {
    const li = document.createElement("li");
    li.textContent = value;
    element.appendChild(li);
  });
}

function updateInspector(data) {
  fields.intent.textContent = data.detected_intent || "-";
  fields.source.textContent = sourceLabels[data.answer_source] || data.answer_source || "-";
  fields.confidence.textContent = typeof data.confidence_score === "number"
    ? `${Math.round(data.confidence_score * 100)}%`
    : "-";
  fields.review.textContent = data.needs_human_review ? "sim" : "não";
  fields.review.className = data.needs_human_review ? "warn" : "good";
  setList(fields.checklists, data.source_checklists);
  setList(fields.normative, data.source_normative);
  setList(fields.protocols, data.source_protocols);
}

async function sendMessage(message) {
  sendButton.disabled = true;
  sendButton.textContent = "Enviando";
  addMessage("user", message);

  try {
    const response = await fetch("/agent/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        channel: "whatsapp",
        phone_number: "+5547999999999",
        message,
      }),
    });

    if (!response.ok) {
      throw new Error(`Erro HTTP ${response.status}`);
    }

    const data = await response.json();
    addMessage("agent", data.response_text);
    updateInspector(data);
  } catch (error) {
    addMessage("agent", "Não consegui consultar o backend agora. Verifique se a API está rodando.");
    fields.apiStatus.textContent = "erro";
    fields.apiStatus.className = "bad";
  } finally {
    sendButton.disabled = false;
    sendButton.textContent = "Enviar";
  }
}

async function loadStatus() {
  try {
    const [healthResponse, knowledgeResponse] = await Promise.all([
      fetch("/health"),
      fetch("/agent/knowledge"),
    ]);
    fields.apiStatus.textContent = healthResponse.ok ? "online" : "erro";
    fields.apiStatus.className = healthResponse.ok ? "good" : "bad";

    if (knowledgeResponse.ok) {
      const knowledge = await knowledgeResponse.json();
      const total = Object.values(knowledge.sources || {}).reduce((sum, value) => sum + value, 0);
      fields.kbStatus.textContent = `${total} itens`;
      fields.kbStatus.className = "good";
    } else {
      fields.kbStatus.textContent = "erro";
      fields.kbStatus.className = "bad";
    }
  } catch {
    fields.apiStatus.textContent = "offline";
    fields.apiStatus.className = "bad";
    fields.kbStatus.textContent = "offline";
    fields.kbStatus.className = "bad";
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) {
    input.focus();
    return;
  }
  input.value = "";
  sendMessage(message);
});

document.querySelectorAll(".prompt-button").forEach((button) => {
  button.addEventListener("click", () => {
    const message = button.dataset.message || "";
    input.value = message;
    input.focus();
  });
});

clearButton.addEventListener("click", () => {
  conversation.innerHTML = `
    <div class="empty-state">
      <strong>Digite uma pergunta da SEPLAN.</strong>
      <span>O agente responde usando base normativa, checklists, histórico e respostas corrigidas.</span>
    </div>
  `;
  updateInspector({
    detected_intent: "-",
    answer_source: "-",
    confidence_score: null,
    needs_human_review: false,
    source_checklists: [],
    source_normative: [],
    source_protocols: [],
  });
});

loadStatus();
