(() => {
  // CDN failed: show hidden content instead of leaving it invisible
  if (!window.Vue) {
    document.querySelectorAll(".reveal").forEach((el) => el.classList.add("active"));
    document
      .querySelectorAll("[v-count-up]")
      .forEach((el) => (el.textContent = el.getAttribute("v-count-up")));
    return;
  }
  const { createApp, ref, onMounted, onBeforeUnmount } = Vue;

  // Django owns {{ }}, so Vue templates use [[ ]].
  const delimiters = ["[[", "]]"];

  // Header: mobile menu + solid header once the page scrolls past the hero
  const header = document.getElementById("site-header");
  if (header) {
    createApp({
      delimiters,
      setup() {
        const menuOpen = ref(false);
        const scrolled = ref(false);
        const onScroll = () => (scrolled.value = window.scrollY > 40);
        const closeMenuOnLink = (event) => {
          if (event.target.closest("a")) menuOpen.value = false;
        };
        onMounted(() => {
          window.addEventListener("scroll", onScroll, { passive: true });
          onScroll();
        });
        onBeforeUnmount(() => window.removeEventListener("scroll", onScroll));
        return { menuOpen, scrolled, closeMenuOnLink };
      },
    }).mount(header);
  }

  // Page content: only mounted where the template opts in with data-vue
  const main = document.querySelector("main[data-vue]");
  if (!main) return;

  const countUp = (el, target) => {
    const start = performance.now();
    const duration = 1400;
    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - progress, 3)));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  // Run once when an element scrolls into view (immediately without IntersectionObserver)
  const hasObserver = "IntersectionObserver" in window;
  const callbacks = new WeakMap();
  const observer =
    hasObserver &&
    new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          observer.unobserve(entry.target);
          callbacks.get(entry.target)?.();
          callbacks.delete(entry.target);
        });
      },
      { threshold: 0.15 },
    );
  const onVisible = (el, callback) => {
    if (!hasObserver) return callback();
    callbacks.set(el, callback);
    observer.observe(el);
  };
  const stopWatching = (el) => {
    if (!hasObserver) return;
    observer.unobserve(el);
    callbacks.delete(el);
  };

  createApp({ delimiters })
    // <div v-reveal class="reveal">: fades in on scroll
    .directive("reveal", {
      mounted: (el) => onVisible(el, () => el.classList.add("active")),
      beforeUnmount: stopWatching,
    })
    // <span v-count-up="98">0</span>: counts up on scroll
    .directive("count-up", {
      mounted: (el, { value }) => onVisible(el, () => countUp(el, Number(value))),
      beforeUnmount: stopWatching,
    })
    .mount(main);
})();
