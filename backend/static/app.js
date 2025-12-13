async function upload() {
  const front = document.getElementById("front").files[0];
  const back = document.getElementById("back").files[0];

  if (!front) {
    alert("Front image is required");
    return;
  }

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
        <img src="/${card.front}" class="preview" />

        <div class="info">
          <h3>${card.identity?.name || "Unknown card"}</h3>
          <p class="meta">
            ${card.identity?.set || ""} • ${card.identity?.number || ""}
          </p>

          <p><strong>Condition:</strong> ${card.condition}</p>
          <p><strong>Estimated price:</strong> $${card.price?.estimated_price ?? "—"}</p>

          <div class="confidence ${confidence < 70 ? "low" : "high"}">
            Confidence: ${confidence}%
          </div>

          ${card.errors.length ? `
            <div class="warning">
              ⚠ ${card.errors.join("<br>")}
            </div>` : ""}
        </div>
      </div>
    `;
  });
}

