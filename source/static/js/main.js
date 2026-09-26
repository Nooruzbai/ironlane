(() => {
    // Mobile menu
    const toggle = document.querySelector("[data-menu-toggle]");
    const menu = document.getElementById("mobile-menu");
    toggle?.addEventListener("click", () => {
        const open = menu.classList.toggle("hidden") === false;
        toggle.setAttribute("aria-expanded", String(open));
    });
    menu?.querySelectorAll("a").forEach((link) =>
        link.addEventListener("click", () => menu.classList.add("hidden"))
    );

    // Solid header once the page scrolls past the transparent hero
    const header = document.getElementById("site-header");
    if (header?.classList.contains("bg-transparent")) {
        const onScroll = () => {
            const scrolled = window.scrollY > 40;
            header.classList.toggle("bg-asphalt/95", scrolled);
            header.classList.toggle("backdrop-blur", scrolled);
            header.classList.toggle("shadow-lg", scrolled);
        };
        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
    }

    // Count-up animation for stats
    const countUp = (el) => {
        const target = Number(el.dataset.count);
        const start = performance.now();
        const duration = 1400;
        const tick = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            el.textContent = Math.round(target * (1 - Math.pow(1 - progress, 3)));
            if (progress < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    };

    // Scroll reveal
    const targets = document.querySelectorAll(".reveal, [data-count]");
    if (!("IntersectionObserver" in window)) {
        targets.forEach((el) => el.classList.add("active"));
        return;
    }
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                entry.target.classList.add("active");
                if (entry.target.dataset.count) countUp(entry.target);
                observer.unobserve(entry.target);
            });
        },
        { threshold: 0.15 }
    );
    targets.forEach((el) => observer.observe(el));
})();
