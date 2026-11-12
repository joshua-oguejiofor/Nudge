// Fade out flash messages after 3 seconds
setTimeout(function () {
  document.querySelectorAll('.alert').forEach(function (msg) {
    msg.style.opacity = '0';
    setTimeout(() => msg.remove(), 800);
  });
}, 3000);

// Mobile menu toggle (only exists on pages that have the navbar)
function toggleMenu() {
  const navLinks = document.getElementById('navLinks');
  const menuToggle = document.getElementById('menuToggle');
  if (!navLinks || !menuToggle) return;
  navLinks.classList.toggle('active');
  menuToggle.classList.toggle('active');
}
