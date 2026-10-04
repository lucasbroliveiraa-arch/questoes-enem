// Configuração: em dev, o backend roda em outra porta (uvicorn na 8000).
// Se o frontend for servido pelo próprio FastAPI no futuro, troque para "".
const API_BASE = "http://localhost:8000";

let state = {
  areas: new Set(),
  anos: new Set(),
  keyword: "",
  page: 1,
  total: 0,
  current: null,
  answered: false,
  selected: null,
};

function loadStatsCache() {
  // cache local só para não piscar "0/0" antes do primeiro fetch de /api/stats
  try {
    const raw = localStorage.getItem("enem_stats_cache");
    return raw ? JSON.parse(raw) : { total_answered: 0, total_correct: 0 };
  } catch (e) {
    return { total_answered: 0, total_correct: 0 };
  }
}
let statsCache = loadStatsCache();

function letter(i) { return ["A", "B", "C", "D", "E"][i]; }

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s || "";
  return d.innerHTML;
}

function buildQuery(pageSize) {
  const params = new URLSearchParams();
  state.areas.forEach(a => params.append("area", a));
  state.anos.forEach(y => params.append("year", y));
  if (state.keyword) params.set("q", state.keyword);
  params.set("page", state.page);
  params.set("page_size", pageSize);
  return params.toString();
}

function showApiError() {
  document.getElementById("sheet").innerHTML =
    `<div class="empty">Não foi possível carregar as questões.<br>Confira se a API está rodando em ${API_BASE} e recarregue a página.</div>`;
  document.getElementById("prevBtn").disabled = true;
  document.getElementById("nextBtn").disabled = true;
  document.getElementById("randBtn").disabled = true;
}

async function loadFilters() {
  try {
    const resp = await fetch(`${API_BASE}/api/questions/filters`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    state.areas = new Set(data.areas);
    state.anos = new Set(data.years);
    buildChips(document.getElementById("areaChips"), data.areas, state.areas);
    buildChips(document.getElementById("anoChips"), data.years, state.anos, v => String(v));    
  } catch (e) {
    showApiError();
  }
}

function buildChips(container, values, activeSet, formatFn) {
  container.innerHTML = "";
  values.forEach(v => {
    const c = document.createElement("button");
    c.className = "chip" + (activeSet.has(v) ? " active" : "");
    c.textContent = formatFn ? formatFn(v) : v;
    c.onclick = () => {
      if (activeSet.has(v)) activeSet.delete(v); else activeSet.add(v);
      c.classList.toggle("active");
    };
    container.appendChild(c);
  });
}

async function fetchStats() {
  try {
    const resp = await fetch(`${API_BASE}/api/stats`);
    const data = await resp.json();
    statsCache = { total_answered: data.total_answered, total_correct: data.total_correct };
    localStorage.setItem("enem_stats_cache", JSON.stringify(statsCache));
  } catch (e) { /* segue com o cache local se a API estiver fora */ }
}

async function loadQuestion() {
  const sheet = document.getElementById("sheet");
  const query = buildQuery(1);
  let data;

  try {
    const resp = await fetch(`${API_BASE}/api/questions?${query}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    data = await resp.json();
  } catch (e) {
    showApiError();
    return;
  }
  
  state.total = data.total;
  state.current = data.items[0] || null;
  state.answered = false;
  state.selected = null;
  renderCounter();

  document.getElementById("prevBtn").disabled = state.page <= 1;
  document.getElementById("nextBtn").disabled = state.page >= state.total;
  document.getElementById("randBtn").disabled = state.total === 0;

  if (!state.current) {
    sheet.innerHTML = '<div class="empty">Nenhuma questão encontrada com esse filtro.<br>Tente remover alguma área/ano ou trocar a palavra-chave.</div>';
    return;
  }

  renderQuestion(state.current);
}

function renderCounter() {
  document.getElementById("counter").textContent = state.total
    ? `${state.page} / ${state.total}  ·  ${statsCache.total_correct}/${statsCache.total_answered} acertos`
    : "";
}

function looksLikeImagePath(s) {
  return /\.(png|jpe?g|webp|gif)$/i.test(s) || s.includes('-images/');
}

function renderQuestion(q) {
  const sheet = document.getElementById("sheet");
  let html = "";
  html += `<div class="meta">ENEM ${q.year} &middot; ${escapeHtml(q.area)}</div>`;
  html += `<div class="qnum">Questão ${q.number}</div>`;
  html += '<hr class="hr">';

  if (q.images && q.images.length > 0) {
    html += '<div class="qimgs">';
    q.images.forEach(src => {
      html += `<img src="${API_BASE}${src}" alt="Imagem da questão ${q.number}" loading="lazy">`;
    });
    html += '</div>';
  }

  if (q.context && q.context.trim()) {
    html += `<div class="ctx">${escapeHtml(q.context)}</div>`;
  }

  html += `<div class="qtext">${escapeHtml(q.statement)}</div>`;
  html += '<div class="feedback" id="feedback"></div>';
  
  const options = [q.option_a, q.option_b, q.option_c, q.option_d, q.option_e];
  const validOptions = options.filter(alt => alt && alt.trim() && !looksLikeImagePath(alt));
  
  html += '<div class="alts" id="alts">';
  
  if (validOptions.length === 0) {
    html += '<p style="font-style:italic;color:var(--ink-soft);">Alternativas não disponíveis para esta questão.</p>';
  }
  
  options.forEach((alt, i) => {
    if (!alt || !alt.trim() || looksLikeImagePath(alt)) return;
    html += `<div class="alt" data-i="${i}"><div class="bubble">${letter(i)}</div><div class="alt-text">${escapeHtml(alt)}</div></div>`;
  });
  
  html += '</div>';
  html += '<div class="actions"><button class="btn btn-primary" id="confirmBtn" disabled>Confirmar resposta</button></div>';
  
  sheet.innerHTML = html;

  document.querySelectorAll(".alt").forEach(el => {
    el.addEventListener("click", () => {
      if (state.answered) return;
      document.querySelectorAll(".alt").forEach(o => o.classList.remove("selected"));
      el.classList.add("selected");
      state.selected = parseInt(el.dataset.i, 10);
      document.getElementById("confirmBtn").disabled = false;
    });
  });

  document.getElementById("confirmBtn").addEventListener("click", confirmAnswer);
}

async function confirmAnswer() {
  if (state.selected === null || state.answered || !state.current) return;
  state.answered = true;

  const resp = await fetch(`${API_BASE}/api/answers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question_id: state.current.id,
      selected_option: letter(state.selected),
    }),
  });
  const result = await resp.json();
  const correctIdx = ["A", "B", "C", "D", "E"].indexOf(result.correct_answer);

  document.querySelectorAll(".alt").forEach((el) => {
    const i = parseInt(el.dataset.i, 10);
    if (i === correctIdx) el.classList.add("correct");
    if (i === state.selected && i !== correctIdx) el.classList.add("wrong");
  });

  const fb = document.getElementById("feedback");
  fb.classList.add("show", result.is_correct ? "ok" : "bad");
  fb.textContent = result.is_correct
    ? `Certa! Resposta: ${result.correct_answer}`
    : `Errada. Resposta certa: ${result.correct_answer}`;

  await fetchStats();
  renderCounter();
}

document.getElementById("toggleFilters").addEventListener("click", () => {
  document.getElementById("panel").classList.toggle("open");
});
document.getElementById("apply").addEventListener("click", () => {
  state.keyword = document.getElementById("keyword").value.trim();
  state.page = 1;
  loadQuestion();
  document.getElementById("panel").classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
});
document.getElementById("prevBtn").addEventListener("click", () => {
  if (state.page > 1) { state.page -= 1; loadQuestion(); window.scrollTo({ top: 0, behavior: "smooth" }); }
});
document.getElementById("nextBtn").addEventListener("click", () => {
  if (state.page < state.total) { state.page += 1; loadQuestion(); window.scrollTo({ top: 0, behavior: "smooth" }); }
});
document.getElementById("randBtn").addEventListener("click", () => {
  if (state.total > 0) {
    state.page = 1 + Math.floor(Math.random() * state.total);
    loadQuestion();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
});

(async function init() {
  await loadFilters();
  await fetchStats();
  renderCounter();
  await loadQuestion();
})();
