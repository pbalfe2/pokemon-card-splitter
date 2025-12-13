async function upload() {
  const front = document.getElementById("front").files[0];
  const back = document.getElementById("back").files[0];

  if (!front || !back) {
    alert("Please select both images");
    return;
  }

  const formData = new FormData();
  formData.append("front", front);
  formData.append("back", back);

  document.getElementById("output").textContent = "Uploading...";

  const res = await fetch("/upload/", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  pollJob(data.job_id);
}

async function pollJob(jobId) {
  document.getElementById("output").textContent = "Processing...";

  const interval = setInterval(async () => {
    const res = await fetch(`/jobs/${jobId}`);
    const job = await res.json();

    if (job.status === "completed") {
      clearInterval(interval);
      document.getElementById("output").textContent =
        JSON.stringify(job, null, 2);
    }
  }, 2000);
}
async function generateListing() {
  const output = JSON.parse(document.getElementById("output").textContent);
  const jobId = output ? output.job_id : null;

  if (!jobId) return alert("No job loaded");

  const res = await fetch(`/listings/${jobId}`, { method: "POST" });
  const listing = await res.json();

  document.getElementById("output").textContent =
    JSON.stringify(listing, null, 2);
}
