async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

function downloadTextFile(filename, text, mime = "text/plain") {
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// --- 3D Projected Intelligence Core ---
(function initIntelligenceCore() {
  const canvas = document.getElementById("coreCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const nodes = [];
  for (let i = 0; i < 36; i++) {
    const phi = Math.acos(1 - (2 * (i + 0.5)) / 36);
    const theta = Math.PI * (1 + Math.sqrt(5)) * i;
    nodes.push({ x: Math.sin(phi) * Math.cos(theta), y: Math.sin(phi) * Math.sin(theta), z: Math.cos(phi) });
  }
  let angle = 0;
  function draw() {
    const w = (canvas.width = canvas.clientWidth || 400);
    const h = (canvas.height = canvas.clientHeight || 195);
    ctx.clearRect(0, 0, w, h);
    const cx = w / 2, cy = h / 2, radius = Math.min(w, h) * 0.36;
    angle += 0.008;
    const proj = nodes.map((n) => {
      const rx = n.x * Math.cos(angle) - n.z * Math.sin(angle);
      const rz = n.x * Math.sin(angle) + n.z * Math.cos(angle);
      const scale = 2.4 / (2.4 - rz);
      return { x: cx + rx * radius * scale, y: cy + n.y * radius * scale, z: rz };
    });
    ctx.strokeStyle = "rgba(0, 229, 255, 0.16)";
    ctx.lineWidth = 1;
    for (let i = 0; i < proj.length; i++) {
      for (let j = i + 1; j < proj.length; j++) {
        const dx = proj[i].x - proj[j].x, dy = proj[i].y - proj[j].y;
        if (dx * dx + dy * dy < 2200) {
          ctx.beginPath(); ctx.moveTo(proj[i].x, proj[i].y); ctx.lineTo(proj[j].x, proj[j].y); ctx.stroke();
        }
      }
    }
    proj.forEach((p, idx) => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.z > 0 ? 3.2 : 2.0, 0, Math.PI * 2);
      ctx.fillStyle = idx % 9 === 0 ? "#ff9933" : idx % 3 === 0 ? "#8b5cf6" : "#00e5ff";
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  draw();
})();

function drawLinePlot(canvasId, seriesList, xLabel, yLabel) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !seriesList.length || !seriesList[0].points.length) return;
  const ctx = canvas.getContext("2d");
  const w = (canvas.width = canvas.clientWidth || 640);
  const h = (canvas.height = canvas.clientHeight || 240);
  ctx.clearRect(0, 0, w, h);

  const allPts = seriesList.flatMap((s) => s.points);
  const minX = Math.min(...allPts.map((p) => p.x)), maxX = Math.max(...allPts.map((p) => p.x));
  const minY = Math.min(...allPts.map((p) => p.y)), maxY = Math.max(...allPts.map((p) => p.y));
  const pad = 34, dx = maxX - minX || 1, dy = maxY - minY || 1;

  ctx.strokeStyle = "rgba(157, 176, 206, 0.25)";
  ctx.beginPath(); ctx.moveTo(pad, pad / 2); ctx.lineTo(pad, h - pad); ctx.lineTo(w - pad / 2, h - pad); ctx.stroke();

  seriesList.forEach((s) => {
    ctx.strokeStyle = s.color;
    ctx.lineWidth = s.width || 2;
    ctx.beginPath();
    s.points.forEach((p, i) => {
      const px = pad + ((p.x - minX) / dx) * (w - pad * 1.6);
      const py = h - pad - ((p.y - minY) / dy) * (h - pad * 1.6);
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    });
    ctx.stroke();
  });

  ctx.fillStyle = "#9db0ce";
  ctx.font = "11px monospace";
  ctx.fillText(`${xLabel}: [${minX.toFixed(2)}, ${maxX.toFixed(2)}]  ${yLabel}: [${minY.toFixed(2)}, ${maxY.toFixed(2)}]`, pad + 6, 16);
}

// --- Navigation & Demo Cards ---
function activateSection(secId) {
  document.querySelectorAll(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.section === secId));
  document.querySelectorAll(".section-panel").forEach((p) => p.classList.toggle("active", p.id === `sec-${secId}`));
  if (secId === "ledger") loadHistory();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => activateSection(btn.dataset.section));
});

document.querySelectorAll(".try-demo-btn").forEach((btn) => {
  btn.addEventListener("click", () => activateSection(btn.dataset.target));
});

document.querySelectorAll(".subtabs").forEach((group) => {
  group.querySelectorAll(".subtab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const parent = group.parentElement;
      group.querySelectorAll(".subtab-btn").forEach((b) => b.classList.remove("active"));
      parent.querySelectorAll(".subpanel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`sub-${btn.dataset.sub}`).classList.add("active");
    });
  });
});

async function refreshStatus() {
  try {
    const data = await apiFetch("/api/system/status");
    const backendPill = document.getElementById("backendPill");
    backendPill.textContent = `Backend: ${data.status}`;
    backendPill.className = "pill ok";
    const aiPill = document.getElementById("aiPill");
    aiPill.textContent = `AI (${data.ai_provider.provider}): ${data.ai_provider.status}`;
    aiPill.className = data.ai_provider.status === "CONNECTED" ? "pill ok" : "pill warn";

    document.getElementById("metricExperiments").textContent = data.database.counts.experiments;
    document.getElementById("metricHypotheses").textContent = data.database.counts.hypotheses;
    document.getElementById("metricVerifications").textContent = data.database.counts.verification_runs;
    document.getElementById("metricDatasets").textContent = data.database.counts.datasets ?? 0;
    document.getElementById("metricSources").textContent = data.database.counts.literature_sources;
    document.getElementById("runtimeBadge").textContent = `Py ${data.runtime_versions.python} · SciPy ${data.runtime_versions.scipy}`;
  } catch (err) {
    document.getElementById("backendPill").textContent = `Backend Error: ${err.message}`;
  }
}

// --- MATH LAB ---
document.getElementById("runMathBtn").addEventListener("click", async () => {
  const out = document.getElementById("mathOutput");
  out.textContent = "Computing via SymPy...";
  try {
    const evalRaw = document.getElementById("mathEval").value;
    const payload = {
      expression: document.getElementById("mathExpr").value,
      operation: document.getElementById("mathOp").value,
      variable: document.getElementById("mathVar").value,
      eval_point: evalRaw === "" ? null : Number(evalRaw),
    };
    const data = await apiFetch("/api/math/symbolic", { method: "POST", body: JSON.stringify(payload) });
    out.textContent = JSON.stringify({ experiment_id: data.experiment.id, checksum: data.experiment.input_checksum, result: data.result }, null, 2);
    const pts = data.result.plot_points || [];
    if (pts.length) {
      const series = [{ color: "#00e5ff", points: pts.map((p) => ({ x: p.x, y: p.input_y })) }];
      if (pts[0].result_y !== undefined) series.push({ color: "#ff9933", points: pts.filter((p) => p.result_y !== undefined).map((p) => ({ x: p.x, y: p.result_y })) });
      drawLinePlot("mathCanvas", series, payload.variable, "f(x)");
    }
    refreshStatus();
  } catch (err) { out.textContent = `Error: ${err.message}`; }
});

document.getElementById("runStatsBtn").addEventListener("click", async () => {
  const out = document.getElementById("statsOutput");
  out.textContent = "Running NumPy/SciPy statistical analysis...";
  try {
    const parseNums = (s) => s.split(",").map((v) => Number(v.trim())).filter((v) => !Number.isNaN(v));
    const xVals = parseNums(document.getElementById("statsX").value);
    const yRaw = document.getElementById("statsY").value.trim();
    const yVals = yRaw ? parseNums(yRaw) : null;
    const meanRaw = document.getElementById("statsMean").value.trim();
    const payload = { x_values: xVals, y_values: yVals, hypothesized_mean: meanRaw === "" ? null : Number(meanRaw) };
    const data = await apiFetch("/api/math/statistics", { method: "POST", body: JSON.stringify(payload) });
    out.textContent = JSON.stringify({ experiment_id: data.experiment.id, checksum: data.experiment.input_checksum, result: data.result }, null, 2);
    if (data.result.linear_regression) {
      const pts = data.result.linear_regression.scatter_points;
      drawLinePlot("statsCanvas", [
        { color: "#00e5ff", width: 2, points: pts.map((p) => ({ x: p.x, y: p.y })) },
        { color: "#ff9933", width: 2, points: pts.map((p) => ({ x: p.x, y: p.y_pred })) },
      ], "x", "y");
    }
    refreshStatus();
  } catch (err) { out.textContent = `Error: ${err.message}`; }
});

document.getElementById("runMcBtn").addEventListener("click", async () => {
  const out = document.getElementById("mcOutput");
  out.textContent = "Running deterministic Monte Carlo simulation...";
  try {
    const payload = { samples: Number(document.getElementById("mcSamples").value), seed: Number(document.getElementById("mcSeed").value) };
    const data = await apiFetch("/api/math/monte-carlo-pi", { method: "POST", body: JSON.stringify(payload) });
    out.textContent = JSON.stringify({ experiment_id: data.experiment.id, checksum: data.experiment.input_checksum, result: data.result }, null, 2);
    refreshStatus();
  } catch (err) { out.textContent = `Error: ${err.message}`; }
});

// --- PHYSICS LAB (ALL 5 MODELS) ---
async function runPhysics(endpoint, payload, mapSeries, xLbl, yLbl) {
  const out = document.getElementById("physicsOutput");
  out.textContent = `Running SciPy RK45 solver via ${endpoint}...`;
  try {
    const data = await apiFetch(endpoint, { method: "POST", body: JSON.stringify(payload) });
    drawLinePlot("physicsCanvas", mapSeries(data.result.trajectory), xLbl, yLbl);
    const summary = { ...data.result };
    delete summary.trajectory;
    out.textContent = JSON.stringify({ experiment_id: data.experiment.id, checksum: data.experiment.input_checksum, ...summary }, null, 2);
    refreshStatus();
  } catch (err) { out.textContent = `Error: ${err.message}`; }
}

document.getElementById("runOscBtn").addEventListener("click", () => runPhysics(
  "/api/physics/oscillator",
  {
    mass_kg: Number(document.getElementById("oscMass").value),
    damping_ns_per_m: Number(document.getElementById("oscDamping").value),
    stiffness_n_per_m: Number(document.getElementById("oscStiffness").value),
    x0_m: Number(document.getElementById("oscX0").value),
    duration_s: Number(document.getElementById("oscDur").value),
  },
  (tr) => [
    { color: "#00e5ff", width: 2.5, points: tr.map((p) => ({ x: p.t_s, y: p.x_numerical_m })) },
    { color: "#ff9933", width: 1.5, points: tr.map((p) => ({ x: p.t_s, y: p.x_analytical_m })) },
  ], "t (s)", "x (m)"
));

document.getElementById("runProjBtn").addEventListener("click", () => runPhysics(
  "/api/physics/projectile",
  {
    v0_m_per_s: Number(document.getElementById("projV0").value),
    angle_deg: Number(document.getElementById("projAngle").value),
    mass_kg: Number(document.getElementById("projMass").value),
    drag_coeff: Number(document.getElementById("projCd").value),
  },
  (tr) => [{ color: "#00e5ff", width: 2.5, points: tr.map((p) => ({ x: p.x_m, y: p.y_m })) }], "x (m)", "y (m)"
));

document.getElementById("runDecayBtn").addEventListener("click", () => runPhysics(
  "/api/physics/decay",
  {
    n0: Number(document.getElementById("decN0").value),
    half_life_s: Number(document.getElementById("decHalf").value),
    duration_s: Number(document.getElementById("decDur").value),
  },
  (tr) => [
    { color: "#00e5ff", width: 2.5, points: tr.map((p) => ({ x: p.t_s, y: p.n_numerical })) },
    { color: "#ff9933", width: 1.5, points: tr.map((p) => ({ x: p.t_s, y: p.n_analytical })) },
  ], "t (s)", "N(t)"
));

document.getElementById("runCoolBtn").addEventListener("click", () => runPhysics(
  "/api/physics/cooling",
  {
    t0_c: Number(document.getElementById("coolT0").value),
    t_env_c: Number(document.getElementById("coolTenv").value),
    cooling_k_per_s: Number(document.getElementById("coolK").value),
    duration_s: Number(document.getElementById("coolDur").value),
  },
  (tr) => [
    { color: "#00e5ff", width: 2.5, points: tr.map((p) => ({ x: p.t_s, y: p.temp_numerical_c })) },
    { color: "#ff9933", width: 1.5, points: tr.map((p) => ({ x: p.t_s, y: p.temp_analytical_c })) },
  ], "t (s)", "T (°C)"
));

document.getElementById("runLogBtn").addEventListener("click", () => runPhysics(
  "/api/physics/logistic",
  {
    p0: Number(document.getElementById("logP0").value),
    carrying_capacity_k: Number(document.getElementById("logK").value),
    growth_rate_r: Number(document.getElementById("logR").value),
    duration_t: Number(document.getElementById("logDur").value),
  },
  (tr) => [
    { color: "#00e5ff", width: 2.5, points: tr.map((p) => ({ x: p.t, y: p.p_numerical })) },
    { color: "#ff9933", width: 1.5, points: tr.map((p) => ({ x: p.t, y: p.p_analytical })) },
  ], "t", "P(t)"
));

// --- HYPOTHESIS LAB ---
document.getElementById("createAndVerifyHypBtn").addEventListener("click", async () => {
  const out = document.getElementById("hypOutput");
  out.textContent = "Creating hypothesis and executing real verification run...";
  try {
    const domain = document.getElementById("hypDomain").value;
    const defaultConfigs = {
      physics_oscillator: { mass_kg: 1.0, damping_ns_per_m: 0.4, stiffness_n_per_m: 4.0, x0_m: 1.0, duration_s: 12.0 },
      physics_projectile: { v0_m_per_s: 40.0, angle_deg: 45.0, drag_coeff: 0.47 },
      physics_decay: { n0: 1000.0, half_life_s: 10.0, duration_s: 50.0 },
      physics_cooling: { t0_c: 90.0, t_env_c: 22.0, cooling_k_per_s: 0.05, duration_s: 120.0 },
      physics_logistic: { p0: 10.0, carrying_capacity_k: 1000.0, growth_rate_r: 0.25, duration_t: 40.0 },
      monte_carlo_pi: { samples: 25000, seed: 42 },
    };
    const assumptions = document.getElementById("hypAssumptions").value.split(",").map((s) => s.trim()).filter(Boolean);
    const hyp = await apiFetch("/api/hypotheses", {
      method: "POST",
      body: JSON.stringify({
        title: document.getElementById("hypTitle").value,
        statement: document.getElementById("hypStatement").value,
        assumptions: assumptions.length ? assumptions : ["Explicit computational parameters"],
        falsifiable_prediction: document.getElementById("hypPrediction").value,
        test_domain: domain,
        test_config: defaultConfigs[domain],
        acceptance_criteria: {
          metric: document.getElementById("hypMetric").value,
          operator: document.getElementById("hypOp").value,
          target: Number(document.getElementById("hypTarget").value),
        },
      }),
    });
    const verified = await apiFetch(`/api/hypotheses/${hyp.id}/verify`, { method: "POST", body: JSON.stringify({}) });
    out.textContent = JSON.stringify(verified.verification, null, 2);
    refreshStatus();
  } catch (err) { out.textContent = `Error: ${err.message}`; }
});

// --- CSV DATA ANALYSIS ---
const csvFileInput = document.getElementById("csvFile");
csvFileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => { document.getElementById("csvText").value = reader.result; };
  reader.readAsText(file);
});

document.getElementById("runCsvBtn").addEventListener("click", async () => {
  const out = document.getElementById("csvOutput");
  out.textContent = "Analyzing CSV with Pandas & SciPy...";
  try {
    const file = csvFileInput.files[0];
    const payload = {
      filename: file ? file.name : "sample_dataset.csv",
      csv_text: document.getElementById("csvText").value,
      x_col: document.getElementById("csvXCol").value.trim() || null,
      y_col: document.getElementById("csvYCol").value.trim() || null,
    };
    const data = await apiFetch("/api/datasets/analyze", { method: "POST", body: JSON.stringify(payload) });
    out.textContent = JSON.stringify({ dataset: data.dataset, experiment_id: data.experiment.id, result: data.result }, null, 2);
    if (data.result.linear_regression && data.result.linear_regression.scatter_points.length) {
      const pts = data.result.linear_regression.scatter_points;
      drawLinePlot("csvCanvas", [
        { color: "#00e5ff", width: 2, points: pts.map((p) => ({ x: p.x, y: p.y })) },
        { color: "#ff9933", width: 2, points: pts.map((p) => ({ x: p.x, y: p.y_pred })) },
      ], payload.x_col, payload.y_col);
    }
    refreshStatus();
  } catch (err) { out.textContent = `Error: ${err.message}`; }
});

// --- EXPERIMENT LEDGER + RERUN + MARKDOWN REPORT DOWNLOAD ---
async function loadHistory() {
  const list = document.getElementById("historyList");
  list.innerHTML = "Loading SQLite experiment ledger...";
  try {
    const data = await apiFetch("/api/experiments?limit=20");
    if (!data.experiments.length) {
      list.innerHTML = "<p style='color:var(--text-secondary)'>No experiments recorded yet. Run any demo in Math, Physics, Hypothesis, or Data Analysis first.</p>";
      return;
    }
    list.innerHTML = "";
    data.experiments.forEach((exp) => {
      const div = document.createElement("div");
      div.className = "history-item";
      const info = document.createElement("div");
      info.innerHTML = `<strong>${exp.id}</strong> &middot; <span class="badge">${exp.domain}</span> <span class="badge saffron">${exp.epistemic_label}</span><div style="font-size:0.78rem;color:var(--text-secondary)">${exp.research_question} &middot; SHA256: ${exp.input_checksum.slice(0, 14)}...</div>`;
      const actions = document.createElement("div");
      actions.className = "btn-row";

      const rerunBtn = document.createElement("button");
      rerunBtn.className = "btn-secondary";
      rerunBtn.textContent = "Rerun & Verify";
      rerunBtn.addEventListener("click", async () => {
        const rOut = document.getElementById("rerunOutput");
        rOut.textContent = `Rerunning ${exp.id}...`;
        try {
          const res = await apiFetch(`/api/experiments/${exp.id}/rerun`, { method: "POST" });
          rOut.textContent = JSON.stringify(res, null, 2);
          loadHistory();
          refreshStatus();
        } catch (err) { rOut.textContent = `Rerun failed: ${err.message}`; }
      });

      const repBtn = document.createElement("button");
      repBtn.className = "btn-secondary";
      repBtn.textContent = "Download .md Report";
      repBtn.addEventListener("click", async () => {
        const res = await fetch(`/api/experiments/${exp.id}/report`);
        const md = await res.text();
        document.getElementById("rerunOutput").textContent = md;
        downloadTextFile(`${exp.id}_report.md`, md, "text/markdown");
      });

      actions.appendChild(rerunBtn);
      actions.appendChild(repBtn);
      div.appendChild(info);
      div.appendChild(actions);
      list.appendChild(div);
    });
  } catch (err) { list.innerHTML = `Error loading ledger: ${err.message}`; }
}
document.getElementById("refreshHistoryBtn").addEventListener("click", loadHistory);

// --- LITERATURE + BIBTEX DOWNLOAD ---
document.getElementById("runLitBtn").addEventListener("click", async () => {
  const out = document.getElementById("litOutput");
  out.textContent = "Querying scientific provider...";
  try {
    const data = await apiFetch("/api/literature/search", {
      method: "POST",
      body: JSON.stringify({
        query: document.getElementById("litQuery").value,
        provider: document.getElementById("litProvider").value,
        limit: Number(document.getElementById("litLimit").value),
      }),
    });
    out.textContent = JSON.stringify(data, null, 2);
    refreshStatus();
  } catch (err) { out.textContent = `Error: ${err.message}`; }
});

document.getElementById("exportBibBtn").addEventListener("click", async () => {
  const res = await fetch("/api/literature/export/bibtex");
  const bib = await res.text();
  document.getElementById("litOutput").textContent = bib;
  downloadTextFile("anveshan_library.bib", bib, "application/x-bibtex");
});

// --- AI SYNTHESIS ---
document.getElementById("runAiBtn").addEventListener("click", async () => {
  const out = document.getElementById("aiOutput");
  out.textContent = "Contacting configured AI provider...";
  try {
    const data = await apiFetch("/api/ai/analyze", { method: "POST", body: JSON.stringify({ prompt: document.getElementById("aiPrompt").value }) });
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = `Error: ${err.message}`; }
});

refreshStatus();
