const $ = (id) => document.getElementById(id);

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

const formatDate = (value) =>
  value ? new Date(value).toLocaleString("en-GB") : "–";

async function loadQuality() {
  try {
    const response = await fetch("/quality");
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    const report = await response.json();

    // Summary + checks
    const passed = report.checks.filter((c) => c.status === "ok").length;
    $("summary").textContent = `${passed} of ${report.checks.length} checks passed`;
    $("checks").innerHTML = report.checks.map((c) => `
      <li class="check ${c.status}">
        <span>${c.status === "ok" ? "✅" : "⚠️"}</span>
        <div><strong>${escapeHtml(c.name)}</strong><br><small>${escapeHtml(c.detail)}</small></div>
      </li>`).join("");

    // Numbers
    $("q-total").textContent = report.stats.total_papers;
    $("q-ai").textContent = report.stats.ai_processed;
    $("q-pending").textContent = report.stats.ai_pending;
    $("q-news").textContent = report.news.news_count;

    // Difficulty chart
    Chart.defaults.color = "#9aa4b2";
    new Chart($("difficultyChart"), {
      type: "bar",
      data: {
        labels: report.difficulty.map((d) => `Level ${d.difficulty}`),
        datasets: [{ data: report.difficulty.map((d) => d.paper_count), backgroundColor: "#4f9cf9" }],
      },
      options: { plugins: { legend: { display: false } } },
    });

    // Runs table
    $("runs").innerHTML = report.recent_runs.length
      ? report.recent_runs.map((run) => `
          <tr>
            <td>${run.id}</td>
            <td>${formatDate(run.started_at)}</td>
            <td class="status-${escapeHtml(run.status)}">${escapeHtml(run.status)}</td>
            <td>${run.new_papers ?? "–"}</td>
            <td>${run.ai_processed ?? "–"} / ${run.ai_failed ?? "–"}</td>
            <td>${run.new_news ?? "–"}</td>
          </tr>`).join("")
      : `<tr><td colspan="6">No runs yet</td></tr>`;
  } catch (error) {
    $("summary").textContent = `Could not load the report (${error.message}). Is the API running?`;
  }
}

loadQuality();