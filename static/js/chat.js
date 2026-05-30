// ── État global ────────────────────────────────────────────────────────────────
let lang = 'fr';

const SUGGESTIONS = {
  fr: [
    "C'est quoi WeeFizz ?",
    "Comment démarrer ?",
    "Comment mesurer ma taille ?",
    "Comment mesurer mon poids ?",
    "Qu'est-ce que la silhouette ?",
    "Différence photo vs manuel ?",
    "Pourquoi mon âge ?",
    "Les données sont-elles sécurisées ?",
    "Comment lire mes résultats ?",
    "J'ai un problème technique",
  ],
  en: [
    "What is WeeFizz?",
    "How do I start?",
    "How to measure my height?",
    "How to measure my weight?",
    "What is silhouette?",
    "Photo vs manual — difference?",
    "Why do you need my age?",
    "Is my data secure?",
    "How do I read my results?",
    "I have a technical problem",
  ],
};

const WELCOME = {
  fr: "Bonjour ! 👋 Je suis l'assistant WeeFizz.\n\nJe suis là pour vous aider à comprendre le formulaire de recommandation de taille. Posez-moi vos questions ou choisissez un sujet ci-dessous.",
  en: "Hello! 👋 I'm the WeeFizz assistant.\n\nI'm here to help you understand the size recommendation form. Ask me anything or choose a topic below.",
};

const PLACEHOLDER = {
  fr: "Posez votre question...",
  en: "Ask your question...",
};

const SUG_LABEL = {
  fr: "Questions fréquentes :",
  en: "Frequently asked questions:",
};

const EMAIL_BTN = {
  fr: "✉️ Envoyer ma question par e-mail",
  en: "✉️ Send my question by email",
};

// ── Helpers DOM ────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

function scrollBottom() {
  const msgs = $('messages');
  msgs.scrollTop = msgs.scrollHeight;
}

// ── Langue ────────────────────────────────────────────────────────────────────
function setLang(l) {
  lang = l;
  document.querySelectorAll('.lang-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.lang === l);
  });
  $('user-input').placeholder = PLACEHOLDER[l];
  $('sug-label').textContent = SUG_LABEL[l];
  renderSuggestions();
}

// ── Suggestions ────────────────────────────────────────────────────────────────
function renderSuggestions() {
  const chips = $('chips');
  chips.innerHTML = '';
  SUGGESTIONS[lang].forEach(s => {
    const btn = document.createElement('button');
    btn.className = 'chip';
    btn.textContent = s;
    btn.onclick = () => handleUserMessage(s);
    chips.appendChild(btn);
  });
}

// ── Typing indicator ───────────────────────────────────────────────────────────
function showTyping() {
  const msgs = $('messages');
  const div = document.createElement('div');
  div.className = 'msg bot';
  div.id = 'typing-indicator';
  div.innerHTML = `
    <div class="avatar">W</div>
    <div class="bubble">
      <div class="typing-wrap">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
    </div>`;
  msgs.appendChild(div);
  scrollBottom();
}

function removeTyping() {
  const el = $('typing-indicator');
  if (el) el.remove();
}

// ── Ajouter un message ────────────────────────────────────────────────────────
function addMessage(text, who, emailAddress = null) {
  const msgs = $('messages');
  const div = document.createElement('div');
  div.className = `msg ${who}`;

  if (who === 'bot') {
    // Convertir les listes à puces texte en HTML propre
    const formatted = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>');

    let emailHtml = '';
    if (emailAddress) {
      const subject = encodeURIComponent(
        lang === 'fr' ? 'Question WeeFizz' : 'WeeFizz Question'
      );
      emailHtml = `<br><a
        class="email-btn"
        href="mailto:${emailAddress}?subject=${subject}"
        target="_blank"
      >${EMAIL_BTN[lang]}</a>`;
    }

    div.innerHTML = `
      <div class="avatar">W</div>
      <div class="bubble">${formatted}${emailHtml}</div>`;
  } else {
    div.innerHTML = `<div class="bubble">${text}</div>`;
  }

  msgs.appendChild(div);
  scrollBottom();
}

// ── Envoi de message ──────────────────────────────────────────────────────────
async function handleUserMessage(text) {
  if (!text.trim()) return;

  // Affiche le message utilisateur
  addMessage(text, 'user');
  $('user-input').value = '';

  // Typing indicator
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, lang }),
    });

    const data = await res.json();
    removeTyping();

    // Légère pause pour un effet naturel
    await new Promise(r => setTimeout(r, 150));
    addMessage(data.answer, 'bot', data.email || null);

  } catch (err) {
    removeTyping();
    const errMsg = {
      fr: "Une erreur est survenue. Veuillez réessayer.",
      en: "An error occurred. Please try again.",
    };
    addMessage(errMsg[lang], 'bot');
  }
}

function sendMessage() {
  handleUserMessage($('user-input').value.trim());
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Message de bienvenue
  setTimeout(() => addMessage(WELCOME[lang], 'bot'), 400);

  // Suggestions initiales
  renderSuggestions();

  // Placeholder
  $('user-input').placeholder = PLACEHOLDER[lang];
  $('sug-label').textContent = SUG_LABEL[lang];

  // Focus input
  $('user-input').focus();
});