// ui/static/main.js

const popup = document.getElementById("popup");
const toggleBtn = document.getElementById("testbed-toggle");
const liveBadge = document.getElementById("live-badge");

let lastAttackKey = "";     // prevent popup spamming
let lastKnownFile = "";     // track latest file

function notifyBlue(msg){
  popup.innerText = msg;
  popup.style.background = "#1a73e8";
  popup.classList.add("show");
  setTimeout(()=>popup.classList.remove("show"), 2200);
}

function notifyRed(msg){
  popup.innerText = msg;
  popup.style.background = "#d32f2f";
  popup.classList.add("show");
  setTimeout(()=>popup.classList.remove("show"), 2600);
}

function setLive(on){
  if(on){
    liveBadge.classList.remove("hidden");
    toggleBtn.innerText = "ON";
    toggleBtn.classList.remove("btn-off");
    toggleBtn.classList.add("btn-on");
  }else{
    liveBadge.classList.add("hidden");
    toggleBtn.innerText = "OFF";
    toggleBtn.classList.remove("btn-on");
    toggleBtn.classList.add("btn-off");
    lastAttackKey = "";
  }
}

// Toggle testbed
toggleBtn.onclick = async ()=>{
  const on = toggleBtn.innerText === "ON";
  if(on){
    await fetch("/api/testbed/stop", {method:"POST"});
    notifyBlue("Testbed stopped");
    setLive(false);
    return;
  }

  // Start: use uploaded scenario path if available
  const scenarioPath = document.getElementById("scenario-file").dataset.path || "scenarios/default_scenario.json";
  const res = await fetch("/api/testbed/start", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({scenario_path: scenarioPath})
  });
  const j = await res.json();
  if(!j.ok) return notifyRed(j.error || "Cannot start testbed");

  notifyBlue("Testbed started");
  setLive(true);
};

// Upload scenario
document.getElementById("scenario-upload").onclick = async ()=>{
  const f = document.getElementById("scenario-file").files[0];
  if(!f) return notifyBlue("Choose scenario first");
  const fd = new FormData(); fd.append("file", f);

  const res = await fetch("/api/scenario/upload", {method:"POST", body: fd});
  const j = await res.json();

  if(j.ok){
    document.getElementById("scenario-file").dataset.path = j.path;
    notifyBlue("Scenario uploaded");
  }else{
    notifyRed(j.error || "Upload failed");
  }
};

// Update status every 1.2s (show LIVE badge properly)
setInterval(async ()=>{
  try{
    const st = await (await fetch("/api/testbed/status")).json();
    setLive(!!st.running);
  }catch(e){}
}, 1200);

// Poll last file every 1s and render tables
setInterval(async ()=>{
  try{
    const st = await (await fetch("/api/testbed/status")).json();
    if(!st.running) return;

    // get files
    const filesRes = await (await fetch("/api/testbed/files")).json();
    const files = filesRes.files || [];
    if(!files.length) return;

    // latest file
    const latest = files[files.length - 1].path;
    lastKnownFile = latest;

    // load file
    const data = await (await fetch("/api/testbed/load",{
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({path: latest})
    })).json();

    if(!data.ok) return;

    const rows = data.rows || [];

    // split by sensor name (network, auth, device)
    renderTable("monitor-network", rows.filter(r=>r.sensor==="network"));
    renderTable("monitor-auth", rows.filter(r=>r.sensor==="auth"));
    renderTable("monitor-device", rows.filter(r=>r.sensor==="device"));

  }catch(e){}
}, 1000);

function renderTable(id, rows){
  const t = document.getElementById(id);
  t.innerHTML = "";

  if(!rows.length){
    t.innerHTML = "<tr><td>No data</td></tr>";
    return;
  }

  const cols = Object.keys(rows[0].values || {});
  const header = "<thead><tr><th>Time</th>" + cols.map(c=>`<th>${c}</th>`).join("") + "</tr></thead>";

  // show last 25 rows to keep UI fast
  const slice = rows.slice(-25).reverse();


  const body = "<tbody>" + slice.map(r=>{
    const evt = r.values?.event ?? "Normal";
    const isAttack = evt !== "Normal";

    // red popup once per new attack type/time
    if(isAttack){
      const key = id + "_" + evt + "_" + r.timestamp;
      if(key !== lastAttackKey){
        lastAttackKey = key;
        notifyRed("⚠ Attack Detected: " + evt);
      }
    }

    const cls = isAttack ? "attack-row" : "";
    return `<tr class="${cls}">
      <td>${new Date(r.timestamp*1000).toLocaleTimeString()}</td>
      ${cols.map(c=>`<td>${r.values[c]}</td>`).join("")}
    </tr>`;
  }).join("") + "</tbody>";

  t.innerHTML = header + body;
}
