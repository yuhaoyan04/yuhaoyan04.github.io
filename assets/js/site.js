(() => {
  document.documentElement.classList.add("js");
  const root = document.documentElement;
  const header = document.querySelector("[data-header]");
  const nav = document.querySelector("#site-nav");
  const navToggle = document.querySelector(".nav-toggle");
  const themeToggle = document.querySelector(".theme-toggle");
  const themeMeta = document.querySelector('meta[name="theme-color"]');

  const preferredTheme = () => {
    const stored = localStorage.getItem("yuhao-theme");
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const applyTheme = (theme) => {
    root.dataset.theme = theme;
    themeMeta?.setAttribute("content", theme === "dark" ? "#121916" : "#f4f1e9");
    if (themeToggle) {
      themeToggle.setAttribute("aria-label", theme === "dark" ? "切换到亮色主题" : "切换到暗色主题");
      themeToggle.setAttribute("title", theme === "dark" ? "切换到亮色主题" : "切换到暗色主题");
    }
  };

  applyTheme(preferredTheme());

  themeToggle?.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem("yuhao-theme", next);
    applyTheme(next);
  });

  const closeNav = () => {
    nav?.classList.remove("open");
    navToggle?.setAttribute("aria-expanded", "false");
  };

  navToggle?.addEventListener("click", () => {
    const open = !nav?.classList.contains("open");
    nav?.classList.toggle("open", open);
    navToggle.setAttribute("aria-expanded", String(open));
  });

  nav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeNav));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeNav();
  });

  const updateHeader = () => header?.classList.toggle("scrolled", window.scrollY > 12);
  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });

  const revealItems = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    revealItems.forEach((item) => item.classList.add("visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -36px" },
  );

  revealItems.forEach((item) => observer.observe(item));
})();
