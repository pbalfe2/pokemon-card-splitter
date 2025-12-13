async function upload() {
  const front = document.getElementById("front").files[0];
  const back = document.getElementById("back").files[0];

  if (!front) {
    alert("Front image is required");
    return;
  }

  // 👇 FIX 4 — disable listing button during processing
  document.getElementById("generateListing").disabled = true;

  const formData = new FormData();
  formData.append("front", front);
  if (back) formData.append("back", back);

  const res = await fetch("/upload/", { method: "POST", body: formData });
  const data = await res.json();

  if (!data.job_id) {
    alert("Upload failed");
    return;
  }

  pollJob(data.job_id);
}

async function pollJob(jobId) {
  const output = document.getElementById("output");

  output.innerHTML = `
    <div class="status queued">Queued…</div>
  `;

  const interval = setInterval(async () => {
    const res = await fetch(`/jobs/${jobId}`);
    if (!res.ok) {
      clearInterval(interval);
      output.innerHTML = `<div class="error">Job failed or not found</div>`;
      return;
    }

    const job = await res.json();

    if (job.status === "processing") {
      output.innerHTML = `<div class="status processing">Analyzing cards…</div>`;
    }

if (job.status === "completed") {
  clearInterval(interval);

  renderResults(job.cards);

  // 👇 FIX 4 — enable listing button now that analysis is done
  document.getElementById("generateListing").disabled = false;
}


    if (job.status === "failed") {
      clearInterval(interval);
      output.innerHTML = `<div class="error">${job.error}</div>`;
    }
  }, 1500);
}

function renderResults(cards) {
  const output = document.getElementById("output");
  output.innerHTML = "";

  cards.forEach(card => {
    const confidence = Math.round((card.identity?.confidence || 0) * 100);

    output.innerHTML += `
      <div class="card-block">

        <div class="card-left">
          <img src="/${card.front}" alt="Card image">
        </div>

        <div class="card-right">
          <div class="card-header">
            <h2>${card.identity?.name || "Unknown card"}</h2>
            <div class="card-sub">
              ${card.identity?.set || ""} · ${card.identity?.number || ""}
            </div>
          </div>

          <div class="card-stats">
            <div class="stat">
              <span class="label">Condition</span>
              <span class="value">${card.condition}</span>
            </div>

            <div class="stat">
              <span class="label">Est. Price</span>
              <span class="value">$${card.price?.estimated_price ?? "—"}</span>
            </div>

            <div class="stat">
              <span class="label">Confidence</span>
              <span class="value ${confidence >= 80 ? "good" : "warn"}">
                ${confidence}%
              </span>
            </div>
          </div>

          <div class="card-actions">
            <button onclick="generateListing()">Generate eBay Listing</button>
          </div>
        </div>

      </div>
    `;
  });
}



