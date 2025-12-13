let currentJobId = null;

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

  document.getElementById("output").innerHTML = "<p>Analyzing cards…</p>";

  const res = await fetch("/upload/", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  currentJobId = data.job_id;

  pollJob();
}

function pollJob() {
  const interval = setInterval(async () => {
    const res = await fetch(`/jobs/${currentJobId}`);
    const job = await res.json();

    if (job.status === "completed") {
      clearInterval(interval);
      renderResults(job.cards);
    }

    if (job.status === "error") {
      clearInterval(interval);
      document.getElementById("output").innerHTML = "<p>Error processing cards.</p>";
    }
  }, 1500);
}

function renderResults(cards) {
  console.log("renderResults called with:", cards);

  const output = document.getElementById("output");
  output.innerHTML = "";

  if (!cards || !cards.length) {
    output.innerHTML = "<p>No cards detected.</p>";
    return;
  }

  cards.forEach(card => {
    const confidence = Math.round((card.identity?.confidence || 0) * 100);
    const imgPath = "/" + card.front.replace(/^data\//, "");

    output.innerHTML += `
      <div class="card-block">
        <div class="card-left">
          <img src="${imgPath}" alt="Card image"
               onerror="this.src='/static/placeholder.png'">
        </div>

        <div class="card-right">
          <h2>${card.identity?.name || "Unknown card"}</h2>
          <div class="sub">
            ${card.identity?.set || ""} · ${card.identity?.number || ""}
          </div>

          <div class="stats">
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

          <button onclick="generateListing()">Generate eBay Listing</button>
        </div>
      </div>
    `;
  });
}

function generateListing() {
  alert("eBay listing generation hooked and ready.");
}
