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
      <div class="card">
        <div class="image-wrapper">
          <img src="/${card.front}" alt="Card image" />
        </div>

        <div class="info">
          <h2>${card.identity?.name || "Unknown card"}</h2>

          <div class="meta">
            ${card.identity?.set || ""} • ${card.identity?.number || ""}
          </div>

          <div class="details">
            <div><strong>Condition:</strong> ${card.condition}</div>
            <div><strong>Estimated price:</strong> $${card.price?.estimated_price ?? "—"}</div>
          </div>

          <div class="confidence ${confidence >= 80 ? "high" : "medium"}">
            Confidence: ${confidence}%
          </div>

          ${card.errors.length ? `
            <div class="warning">
              ⚠ ${card.errors.join("<br>")}
            </div>
          ` : ""}
        </div>
      </div>
    `;
  });
}


