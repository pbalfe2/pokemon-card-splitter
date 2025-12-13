console.log("app.js loaded");

var currentJobId = null;

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM ready");

  var btn = document.getElementById("analyzeBtn");
  if (!btn) {
    console.error("Analyze button not found");
    return;
  }

  btn.addEventListener("click", function () {
    console.log("Analyze button clicked");
    upload();
  });
});

function upload() {
  var frontInput = document.getElementById("front");
  var backInput = document.getElementById("back");
  var output = document.getElementById("output");

  if (!frontInput || !frontInput.files || !frontInput.files[0]) {
    alert("Front image is required");
    return;
  }

  output.innerHTML = "<p>Uploading & analyzing...</p>";

  var formData = new FormData();
  formData.append("front", frontInput.files[0]);

  if (backInput && backInput.files && backInput.files[0]) {
    formData.append("back", backInput.files[0]);
  }

  fetch("/upload/", {
    method: "POST",
    body: formData
  })
    .then(function (res) {
      return res.json();
    })
    .then(function (data) {
      console.log("Upload response:", data);
      currentJobId = data.job_id;
      pollJob();
    })
    .catch(function (err) {
      console.error("Upload failed", err);
      output.innerHTML = "<p style='color:red'>Upload failed</p>";
    });
}

function pollJob() {
  var output = document.getElementById("output");

  var interval = setInterval(function () {
    fetch("/jobs/" + currentJobId)
      .then(function (res) {
        return res.json();
      })
      .then(function (job) {
        console.log("Job status:", job);

        if (job.status === "completed") {
          clearInterval(interval);
          renderResults(job.cards || [], job.front);
        }

        if (job.status === "error") {
          clearInterval(interval);
          output.innerHTML = "<p style='color:red'>Job failed</p>";
        }
      })
      .catch(function (err) {
        console.error("Polling failed", err);
      });
  }, 1500);
}

function renderResults(cards, jobFront) {
  var output = document.getElementById("output");

  if (!cards || !cards.length) {
    output.innerHTML = "<p>No cards detected</p>";
    return;
  }

  output.innerHTML = "";

  var imgPath = "";
  if (jobFront) {
    imgPath = "/data/" + jobFront.replace(/^data\//, "");
  }

  cards.forEach(function (card) {
    var confidence = card.identity?.confidence
      ? Math.round(card.identity.confidence * 100)
      : 0;

    var rarity = card.identity?.rarity || "Unknown";
    var holo = card.identity?.holo ? "Holo" : "Non-Holo";

    var metaHtml =
      '<div class="meta">' +
      '  <span class="badge rarity">' + rarity + '</span>' +
      '  <span class="badge holo">' + holo + '</span>' +
      '</div>';

    output.innerHTML +=
      '<div class="card-block">' +
      '  <div class="card-left">' +
      '    <img src="' + imgPath + '" alt="Card image">' +
      "  </div>" +
      '  <div class="card-right">' +
      "    <h2>" + (card.identity?.name || "Unknown card") + "</h2>" +
      '    <div class="sub">' +
      (card.identity?.set || "") +
      " · " +
      (card.identity?.number || "") +
      "    </div>" +
      metaHtml +
      '    <div class="stats">' +
      '      <div class="stat"><span class="label">Condition</span><span class="value">' +
      (card.condition || "-") +
      "</span></div>" +
      '      <div class="stat"><span class="label">Est. Price</span><span class="value">$' +
      (card.price?.estimated_price ?? "-") +
      "</span></div>" +
      '      <div class="stat"><span class="label">Confidence</span><span class="value">' +
      confidence +
      "%</span></div>" +
      "    </div>" +
      "  </div>" +
      "</div>";
  });
}

