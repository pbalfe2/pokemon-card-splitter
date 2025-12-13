function toggleBackUpload(cb) {
    document.getElementById("backUpload").style.display = cb.checked ? "block" : "none";
}

function showLoading() {
    document.getElementById("loadingOverlay").style.display = "flex";
}
