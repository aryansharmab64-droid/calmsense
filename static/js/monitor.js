(() => {
  "use strict";
  const root = document.getElementById("monitor");
  if (!root) return;

  const U = root.dataset;
  const $ = (id) => document.getElementById(id);
  const csrf = () => (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || "";
  const fmt = (v, d = 1) => (v === null || v === undefined ? "—" : Number(v).toFixed(d));
  const clock = (iso) => new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });

  let state = null;
  let chart = null;
  let busy = false;

  async function api(url, method = "GET", body = null) {
    const opts = { method, credentials: "same-origin", headers: { Accept: "application/json" } };
    if (method !== "GET") {
      opts.headers["Content-Type"] = "application/json";
      opts.headers["X-CSRFToken"] = csrf();
      opts.body = JSON.stringify(body || {});
    }
    const res = await fetch(url, opts);
    let data;
    try { data = await res.json(); } catch (e) { data = { error: `Unexpected server response (${res.status}).` }; }
    if (!res.ok) {
      const err = new Error(data.error || "Request failed.");
      err.status = res.status;
      err.data = data;
      throw err;
    }
    return data;
  }

  function toast(message, kind = "success") {
    const host = document.querySelector(".toast-container");
    if (!host) return;
    const el = document.createElement("div");
    el.className = "toast cs-toast align-items-center border-0";
    el.setAttribute("role", kind === "error" ? "alert" : "status");
    const wrap = document.createElement("div");
    wrap.className = "d-flex";
    const body = document.createElement("div");
    body.className = "toast-body";
    const icon = document.createElement("i");
    icon.className = "bi me-2 " + (kind === "error" ? "bi-exclamation-circle text-danger" : "bi-check-circle text-success");
    body.append(icon, message);
    const close = document.createElement("button");
    close.type = "button";
    close.className = "btn-close me-2 m-auto";
    close.setAttribute("data-bs-dismiss", "toast");
    close.setAttribute("aria-label", "Close");
    wrap.append(body, close);
    el.append(wrap);
    host.append(el);
    new bootstrap.Toast(el, { delay: 5000 }).show();
    el.addEventListener("hidden.bs.toast", () => el.remove());
  }

  function initChart() {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    chart = new Chart($("liveChart"), {
      type: "line",
      data: {
        labels: [],
        datasets: [
          { label: "Heart rate (BPM)", data: [], borderColor: "#D9534F", backgroundColor: "#D9534F", yAxisID: "y", tension: 0.3, pointRadius: 2, spanGaps: false },
          { label: "HRV (ms)", data: [], borderColor: "#159A9C", backgroundColor: "#159A9C", yAxisID: "y1", tension: 0.3, pointRadius: 2, borderDash: [6, 3], spanGaps: false },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: reduce ? false : { duration: 350 },
        interaction: { mode: "index", intersect: false },
        scales: {
          y: { position: "left", title: { display: true, text: "BPM" } },
          y1: { position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "ms" } },
        },
      },
    });
  }

  const STATUS = {
    running: ["running", "bi-play-circle", "Running"],
    paused: ["paused", "bi-pause-circle", "Paused"],
    stopped: ["stopped", "bi-stop-circle", "Stopped"],
  };

  function render(s) {
    const sim = s.simulation;
    const [cls, icon, text] = STATUS[sim.status] || STATUS.stopped;
    const badge = $("simStatus");
    badge.className = "cs-status " + cls;
    badge.innerHTML = "";
    const i = document.createElement("i");
    i.className = "bi " + icon;
    badge.append(i, " " + text);

    $("btnStart").disabled = sim.status !== "stopped";
    $("btnPause").disabled = sim.status !== "running";
    $("btnResume").disabled = sim.status !== "paused";
    $("btnStop").disabled = sim.status === "stopped";
    if ($("scenario").value !== sim.scenario) $("scenario").value = sim.scenario;
    describeScenario();

    const latest = s.latest;
    ["heart_rate", "hrv_ms", "skin_temp_c", "eda_us", "steps"].forEach((k) => {
      const digits = k === "steps" ? 0 : k === "skin_temp_c" || k === "eda_us" ? 2 : 1;
      $("m-" + k).textContent = latest ? fmt(latest[k], digits) : "—";
    });

    const age = s.latest_age_seconds;
    $("lastAge").textContent = age === null ? "—" : age < 60 ? `${age} s ago` : `${Math.round(age / 60)} min ago`;
    $("runCount").textContent = sim.readings_generated;
    $("totalCount").textContent = s.total_readings;
    $("staleNote").classList.toggle("d-none", !(age === null || (age > 120 && sim.status !== "running")));

    renderTable(s.readings);
    renderChart(s.readings);
  }

  function renderTable(readings) {
    const body = $("readingRows");
    body.innerHTML = "";
    if (!readings.length) {
      body.innerHTML = '<tr><td colspan="6" class="text-muted">No readings yet.</td></tr>';
      return;
    }
    readings.slice(-12).reverse().forEach((r) => {
      const tr = document.createElement("tr");
      const cells = [clock(r.timestamp), fmt(r.heart_rate), fmt(r.hrv_ms), fmt(r.skin_temp_c, 2), fmt(r.eda_us, 2),
        r.is_simulated ? "Simulated" : r.source === "manual" ? "Manual" : "Device/API"];
      cells.forEach((c) => {
        const td = document.createElement("td");
        td.textContent = c;
        tr.append(td);
      });
      body.append(tr);
    });
  }

  function renderChart(readings) {
    $("chartEmpty").classList.toggle("d-none", readings.length > 0);
    $("liveChart").classList.toggle("d-none", readings.length === 0);
    chart.data.labels = readings.map((r) => clock(r.timestamp));
    chart.data.datasets[0].data = readings.map((r) => r.heart_rate);
    chart.data.datasets[1].data = readings.map((r) => r.hrv_ms);
    chart.update();
  }

  function describeScenario() {
    const opt = $("scenario").selectedOptions[0];
    $("scenarioDesc").textContent = opt ? opt.dataset.desc : "";
  }

  async function run(fn, okMessage) {
    if (busy) return;
    busy = true;
    try {
      const result = await fn();
      if (result && result.simulation) { state = result; render(result); }
      if (okMessage) toast(typeof okMessage === "function" ? okMessage(result) : okMessage);
    } catch (e) {
      if (e.status === 401) { window.location.href = U.loginUrl; return; }
      toast(e.message, "error");
    } finally {
      busy = false;
    }
  }

  async function tick() {
    if (document.hidden || busy) return;
    try {
      const running = state && state.simulation.status === "running";
      state = running ? await api(U.pollUrl, "POST") : await api(U.stateUrl);
      render(state);
    } catch (e) {
      if (e.status === 401) window.location.href = U.loginUrl;
    }
  }

  const sim = (action, extra = {}) => api(U.simUrl, "POST", { action, ...extra });

  $("btnStart").addEventListener("click", () => run(() => sim("start", { scenario: $("scenario").value }), "Simulation started (synthetic data)."));
  $("btnPause").addEventListener("click", () => run(() => sim("pause"), "Simulation paused."));
  $("btnResume").addEventListener("click", () => run(() => sim("resume"), "Simulation resumed."));
  $("btnStop").addEventListener("click", () => run(() => sim("stop"), "Simulation stopped."));
  $("scenario").addEventListener("change", () => {
    describeScenario();
    run(() => sim("set_scenario", { scenario: $("scenario").value }), "Scenario changed.");
  });
  $("btnGenerate").addEventListener("click", () =>
    run(() => api(U.generateUrl, "POST", { count: 10 }), "Generated 10 synthetic readings."));
  $("btnReset").addEventListener("click", () => {
    if (!window.confirm("Delete all of your simulated readings? Manually entered readings are kept.")) return;
    run(() => api(U.resetUrl, "POST"), (r) => `Removed ${r.deleted} simulated readings.`);
  });

  $("manualForm").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const errs = $("mfErrors");
    errs.innerHTML = "";
    const payload = { source: "manual" };
    ["heart_rate", "hrv_ms", "skin_temp_c", "eda_us", "steps"].forEach((k) => {
      const v = $("mf-" + k).value.trim();
      if (v !== "") payload[k] = v;
    });
    const t = $("mf-timestamp").value;
    if (t) payload.timestamp = new Date(t).toISOString();
    try {
      await api(U.ingestUrl, "POST", payload);
      toast("Reading saved.");
      $("manualForm").reset();
      state = await api(U.stateUrl);
      render(state);
    } catch (e) {
      const fields = (e.data && e.data.fields) || { error: e.message };
      Object.entries(fields).forEach(([k, msg]) => {
        const li = document.createElement("li");
        li.textContent = `${k}: ${msg}`;
        errs.append(li);
      });
      toast(e.message, "error");
    }
  });

  initChart();
  describeScenario();
  tick();
  setInterval(tick, parseInt(U.pollMs, 10) || 5000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) tick(); });
})();