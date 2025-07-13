// static/js/darkmode.js
document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("modeToggle");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
        });
    }
});
// Ensure the toggle button exists before adding the event listener
// This prevents errors if the button is not present in the HTML