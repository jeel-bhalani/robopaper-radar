const PAGE_SIZE = 10;
let offset = 0;

// Short helper: find an element by its id
const $ = (id) => document.getElementById(id);

// Make text safe before putting it into HTML (protects against XSS)
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

// Call our API and return the JSON, or throw an error
async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

// ---------- Stats, topic dropdown, charts ----------
async function loadStats() {
  // Run 3 requests at the same time
  const [topics, days, authors] = await Promise.all([
    getJSON("/topics"),
    getJSON("/stats/papers-per-day"),
    getJSON("/authors/top?limit=1"),
  ]);

  const total = days.reduce((sum, d) => sum + d.paper_count, 0);
  $("stat-papers").textContent = total;
  $("stat-topics").textContent = topics.length;
  $("stat-author").textContent = authors[0]?.name ?? "–";

  // Fill the topic dropdown
  for (const t of topics) {
    const option = document.createElement("option");
    option.value = t.name;
    option.textContent = `${t.name} (${t.paper_count})`;
    $("topic").appendChild(option);
  }

  // Charts
  Chart.defaults.color = "#9aa4b2";
  new Chart($("topicChart"), {
    type: "bar",
    data: {
      labels: topics.map((t) => t.name),
      datasets: [{ data: topics.map((t) => t.paper_count), backgroundColor: "#4f9cf9" }],
    },
    options: { indexAxis: "y", plugins: { legend: { display: false } } },
  });
  new Chart($("dayChart"), {
    type: "line",
    data: {
      labels: days.map((d) => d.day),
      datasets: [{ data: days.map((d) => d.paper_count), borderColor: "#4f9cf9", tension: 0.3 }],
    },
    options: { plugins: { legend: { display: false } } },
  });
}

// ---------- One paper as HTML ----------
function paperCard(p) {
  const authors = p.authors.length > 3
    ? p.authors.slice(0, 3).join(", ") + " et al."
    : p.authors.join(", ");
  const date = p.published_at
    ? new Date(p.published_at).toLocaleDateString("en-GB")
    : "";
  const topics = p.topics
    .map((t) => `<span class="badge">${escapeHtml(t)}</span>`)
    .join("");
  const difficulty = p.difficulty
    ? `<span class="difficulty" title="Difficulty ${p.difficulty}/5">${"●".repeat(p.difficulty)}${"○".repeat(5 - p.difficulty)}</span>`
    : "";
  const summary = p.ai_summary
    ? escapeHtml(p.ai_summary)
    : "<em>No AI summary yet</em>";

  return `
    <article class="paper">
      <h3><a href="${escapeHtml(p.url)}" target="_blank" rel="noopener">${escapeHtml(p.title)}</a></h3>
      <p class="meta">${escapeHtml(authors)} · ${date} ${difficulty}</p>
      <div class="badges">${topics}</div>
      <p class="summary">${summary}</p>
    </article>`;
}

// ---------- Paper list with filters and pages ----------
async function loadPapers() {
  const params = new URLSearchParams({ limit: PAGE_SIZE, offset });
  const search = $("search").value.trim();
  if (search) params.set("search", search);
  if ($("topic").value) params.set("topic", $("topic").value);
  if ($("difficulty").value) params.set("difficulty", $("difficulty").value);

  $("message").textContent = "Loading...";
  try {
    const papers = await getJSON(`/papers?${params}`);
    $("papers").innerHTML = papers.map(paperCard).join("");
    $("message").textContent = papers.length ? "" : "No papers found.";
    $("page-info").textContent = `Page ${offset / PAGE_SIZE + 1}`;
    $("prev").disabled = offset === 0;
    $("next").disabled = papers.length < PAGE_SIZE;
  } catch (error) {
    $("papers").innerHTML = "";
    $("message").textContent = `Could not load papers (${error.message}). Is the API running?`;
  }
}

// ---------- Events: react to the user ----------
let searchTimer;
$("search").addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => { offset = 0; loadPapers(); }, 300);
});
$("topic").addEventListener("change", () => { offset = 0; loadPapers(); });
$("difficulty").addEventListener("change", () => { offset = 0; loadPapers(); });
$("prev").addEventListener("click", () => { offset -= PAGE_SIZE; loadPapers(); window.scrollTo(0, 0); });
$("next").addEventListener("click", () => { offset += PAGE_SIZE; loadPapers(); window.scrollTo(0, 0); });

// ---------- Industry news ----------
async function loadNews() {
  try {
    const news = await getJSON("/news?limit=8");
    $("news").innerHTML = news.length
      ? news.map((n) =>
          `<li><a href="${escapeHtml(n.url)}" target="_blank" rel="noopener">${escapeHtml(n.title)}</a></li>`
        ).join("")
      : "<li><em>No news yet. Run scrape_news.py</em></li>";
  } catch (error) {
    $("news").innerHTML = "<li><em>Could not load news.</em></li>";
  }
}

// ---------- Start ----------
loadStats().catch((error) => console.error("Stats failed:", error));
loadPapers();
loadNews();