const header = document.querySelector("[data-header]");

function syncHeaderState() {
  if (!header) return;
  header.classList.toggle("is-scrolled", window.scrollY > 8);
}

syncHeaderState();
window.addEventListener("scroll", syncHeaderState, { passive: true });
