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
  document.getElementById("output").textContent = "Processing job " + jobId;

  const interval = setInterval(async () => {
    const res = await fetch(`/jobs/${jobId}`);

    if (!res.ok) {
      clearInterval(interval);
      document.getElementById("output").textContent =
        "Job not found or failed";
      return;
    }

    const job = await res.json();

    if (job.status === "completed") {
      clearInterval(interval);
      document.getElementById("output").textContent =
        JSON.stringify(job, null, 2);
    }
  }, 2000);
}
