document.addEventListener("DOMContentLoaded", () => {
  // Show server-rendered toasts
  document.querySelectorAll(".toast").forEach((el) => {
    const t = new bootstrap.Toast(el);
    t.show();
  });

  // Sidebar: collapse on desktop, slide-in on mobile
  const toggle = document.getElementById("sidebarToggle");
  if (toggle) {
    const KEY = "cs.sidebar.collapsed";
    const mobile = () => window.matchMedia("(max-width: 991px)").matches;
    try {
      if (!mobile() && localStorage.getItem(KEY) === "1") {
        document.body.classList.add("sidebar-collapsed");
      }
    } catch (e) { /* storage unavailable */ }

    toggle.addEventListener("click", () => {
      if (mobile()) {
        document.body.classList.toggle("sidebar-open");
      } else {
        const collapsed = document.body.classList.toggle("sidebar-collapsed");
        try { localStorage.setItem(KEY, collapsed ? "1" : "0"); } catch (e) {}
      }
    });
  }
});