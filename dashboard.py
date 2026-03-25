import json
from pathlib import Path
from typing import Any

from lib import Subject, YtlDatum


def semester_sort_key(value: str) -> tuple[int, int, str]:
    year_text, season = value.split(maxsplit=1)
    season_order = {"kevät": 0, "syksy": 1}
    return (int(year_text), season_order.get(season, 99), season)


def build_dashboard_payload(subjects: list[Subject], ytl_results: list[YtlDatum]) -> dict[str, Any]:
    subject_order = [subject.name for subject in subjects]
    semesters = sorted({row.semester for row in ytl_results}, key=semester_sort_key)
    ytl_grades = ["L", "E", "M", "C", "B", "A"]

    subjects_payload: dict[str, Any] = {}
    for subject_name in subject_order:
        subject_rows = [row for row in ytl_results if row.subject == subject_name]
        by_grade: dict[str, dict[str, float]] = {grade: {} for grade in ytl_grades}
        for row in subject_rows:
            by_grade[row.grade][row.semester] = float(row.value)

        available_semesters = sorted({row.semester for row in subject_rows}, key=semester_sort_key)
        latest_semester = available_semesters[-1] if available_semesters else None
        latest_thresholds = (
            {row.grade: float(row.value) for row in subject_rows if row.semester == latest_semester}
            if latest_semester
            else {}
        )

        subjects_payload[subject_name] = {
            "grades": by_grade,
            "availability": {
                "semesters": available_semesters,
                "latest_semester": latest_semester,
                "semester_count": len(available_semesters),
            },
            "latest_thresholds": latest_thresholds,
        }

    return {
        "subjects": subjects_payload,
        "subject_order": subject_order,
        "semesters": semesters,
        "ytl_grades": ytl_grades,
    }


def render_dashboard_html(payload: dict[str, Any], generated_at: str) -> str:
    payload_json = json.dumps(payload, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>YO_graph</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --bg: #f5f1e8;
      --panel: #fffaf3;
      --line: #decfb8;
      --ink: #201a14;
      --muted: #6e665d;
      --accent: #165d8a;
      --accent-2: #b6592b;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--bg);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 18px 18px 28px;
    }}
    h1, h2, h3, p {{ margin: 0; }}
    .topbar {{
      display: grid;
      gap: 8px;
      margin-bottom: 12px;
    }}
    .topbar-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .topbar h1 {{
      font-size: 1.2rem;
      font-weight: 650;
      letter-spacing: -0.02em;
    }}
    .topbar-copy {{
      color: var(--muted);
      font-size: 0.93rem;
      line-height: 1.45;
      max-width: 68ch;
    }}
    .panel {{
      background: rgba(255, 250, 243, 0.92);
      border: 1px solid rgba(222, 207, 184, 0.85);
      border-radius: 18px;
      box-shadow: 0 6px 18px rgba(70, 52, 28, 0.05);
    }}
    .toolbar {{
      padding: 0;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .control {{
      display: grid;
      gap: 4px;
    }}
    label {{
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--muted);
    }}
    select {{
      border: 1px solid rgba(222, 207, 184, 0.95);
      border-radius: 10px;
      background: white;
      padding: 8px 10px;
      font: inherit;
      color: inherit;
    }}
    .content {{
      display: block;
    }}
    .chart-panel {{
      padding: 14px 16px 12px;
      display: grid;
      gap: 10px;
    }}
    .chart-wrap {{
      min-height: min(76vh, 720px);
    }}
    .note {{
      color: var(--muted);
      line-height: 1.5;
    }}
    .mono {{
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
    }}
    @media (max-width: 720px) {{
      .topbar-row {{
        flex-direction: column;
        align-items: stretch;
      }}
      .control {{
        width: 100%;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="topbar">
      <div class="topbar-row">
        <h1>YO_graph</h1>
        <div class="toolbar">
          <div class="control">
            <label for="subject-select">Subject</label>
            <select id="subject-select"></select>
          </div>
        </div>
      </div>
      <p class="topbar-copy">Official YTL matriculation exam thresholds, normalized by each subject’s maximum score.</p>
    </section>
    <section class="content">
      <section class="panel chart-panel">
        <div>
          <h2 id="chart-title"></h2>
          <p id="chart-subtitle" class="note"></p>
        </div>
        <div class="chart-wrap">
          <canvas id="chart"></canvas>
        </div>
      </section>
    </section>
  </main>
  <script id="dashboard-data" type="application/json">{payload_json}</script>
  <script>
    const generatedAt = {json.dumps(generated_at, ensure_ascii=False)};
    const payload = JSON.parse(document.getElementById("dashboard-data").textContent);
    const subjectSelect = document.getElementById("subject-select");
    const chartTitle = document.getElementById("chart-title");
    const chartSubtitle = document.getElementById("chart-subtitle");

    for (const subject of payload.subject_order) {{
      subjectSelect.add(new Option(subject, subject));
    }}

    const colors = ["#165d8a", "#b6592b", "#25724d", "#7b4f9d", "#b79000", "#5a5f66"];
    const chart = new Chart(document.getElementById("chart"), {{
      type: "line",
      data: {{ labels: [], datasets: [] }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        interaction: {{ mode: "nearest", intersect: false }},
        scales: {{
          y: {{
            beginAtZero: true,
            max: 1,
            ticks: {{
              callback: (value) => Number.isFinite(value) ? value.toFixed(2).replace(/\\.00$/, "") : value
            }}
          }}
        }}
      }}
    }});

    function makeDataset(label, valuesBySemester, labels, color) {{
      return {{
        label,
        data: labels.map((semester) => valuesBySemester[semester] ?? null),
        borderColor: color,
        backgroundColor: color,
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        spanGaps: false,
        tension: 0.18,
      }};
    }}

    function updateChart() {{
      const subjectData = payload.subjects[subjectSelect.value];
      const labels = subjectData.availability.semesters;

      const datasets = payload.ytl_grades.map((grade, index) =>
        makeDataset(grade, subjectData.grades[grade], labels, colors[index % colors.length])
      );
      chartTitle.textContent = subjectSelect.value;
      chartSubtitle.textContent = `Official normalized thresholds across ${{subjectData.availability.semester_count}} semesters. Updated ${{generatedAt}}.`;

      chart.data.labels = labels;
      chart.data.datasets = datasets.filter((dataset) => dataset.data.some((value) => value !== null));
      chart.update();
    }}

    subjectSelect.addEventListener("change", updateChart);

    subjectSelect.value = payload.subject_order[0];
    updateChart();
  </script>
</body>
</html>
"""


def save_dashboard_html(path: str | Path, payload: dict[str, Any], generated_at: str) -> Path:
    output_path = Path(path)
    output_path.write_text(render_dashboard_html(payload, generated_at), encoding="utf-8")
    return output_path
