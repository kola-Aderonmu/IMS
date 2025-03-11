document.addEventListener("DOMContentLoaded", () => {
  const progress = document.querySelector(".progress");
  const status = document.querySelector(".status");
  const messages = [
    "Initializing System...",
    "Loading Components...",
    "Preparing Dashboard...",
    "Almost Ready...",
  ];

  let currentProgress = 0;
  const interval = setInterval(() => {
    if (currentProgress >= 100) {
      clearInterval(interval);
      status.textContent = "Welcome!";
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 500);
      return;
    }

    currentProgress += 1;
    progress.style.width = `${currentProgress}%`;

    // Update status message based on progress
    if (currentProgress < 30) status.textContent = messages[0];
    else if (currentProgress < 60) status.textContent = messages[1];
    else if (currentProgress < 85) status.textContent = messages[2];
    else status.textContent = messages[3];
  }, 30);
});
