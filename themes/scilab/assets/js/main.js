// SciLab theme JS
const runWhenStylesReady = (handler) => {
  const invoke = () => {
    const exec = () => handler();
    if ('requestAnimationFrame' in window) {
      requestAnimationFrame(() => requestAnimationFrame(exec));
    } else {
      setTimeout(exec, 0);
    }
  };

  const afterFonts = () => {
    const ready = document.fonts && 'ready' in document.fonts
      ? document.fonts.ready
      : Promise.resolve();
    ready.then(invoke);
  };

  if (document.readyState === 'complete') {
    afterFonts();
  } else {
    window.addEventListener('load', afterFonts, { once: true });
  }
};

const initUI = () => {
  /* ===== Mobile navigation ================================================= */
  const toggle = document.getElementById('nav-toggle');
  const menu   = document.getElementById('nav-menu');
  const backdrop = document.getElementById('nav-backdrop');
  const header = document.querySelector('.header');
  const backToTop = document.getElementById('back-to-top');
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const openMenu = () => {
    if (!menu) return;
    menu.classList.add('is-open');
    toggle?.setAttribute('aria-expanded', 'true');
    toggle?.setAttribute('aria-label', 'Close menu');
    if (backdrop) backdrop.hidden = false;
    document.documentElement.style.overflow = 'hidden';
  };
  const closeMenu = () => {
    if (!menu) return;
    menu.classList.remove('is-open');
    toggle?.setAttribute('aria-expanded', 'false');
    toggle?.setAttribute('aria-label', 'Open menu');
    if (backdrop) backdrop.hidden = true;
    document.documentElement.style.overflow = '';
  };
  toggle?.addEventListener('click', () => menu?.classList.contains('is-open') ? closeMenu() : openMenu());
  backdrop?.addEventListener('click', closeMenu);
  menu?.addEventListener('click', (e) => {
    const t = e.target;
    if (t && t.classList?.contains('menu-link')) closeMenu();
  });
  const mq = window.matchMedia('(min-width: 769px)');
  (mq.addEventListener ? mq.addEventListener('change', () => mq.matches && closeMenu())
                       : mq.addListener(() => mq.matches && closeMenu()));

  /* ===== Header + back-to-top behaviour ==================================== */
  const handleScrollState = () => {
    const y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle('is-condensed', y > 10);
    if (backToTop) backToTop.classList.toggle('is-visible', y > 320);
  };
  window.addEventListener('scroll', handleScrollState, { passive: true });
  runWhenStylesReady(() => handleScrollState());

  backToTop?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' });
  });

  /* ===== Reveal on scroll =================================================== */
  const revealTargets = document.querySelectorAll('[data-reveal]');
  if (revealTargets.length) {
    runWhenStylesReady(() => {
      if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries, obs) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('is-revealed');
              obs.unobserve(entry.target);
            }
          });
        }, { threshold: 0.18, rootMargin: '0px 0px -10% 0px' });

        revealTargets.forEach((el) => {
          el.classList.add('reveal');
          observer.observe(el);
        });
      } else {
        revealTargets.forEach((el) => el.classList.add('is-revealed'));
      }
    });
  }

  const hoverCards = document.querySelectorAll('.research-topic, .research-project, .resource-card, .publication-card, .alumni-card, .join-position, .contact-card, .team-card');
  if (hoverCards.length) {
    hoverCards.forEach((card) => {
      card.addEventListener('pointerup', (event) => {
        if (event.pointerType && event.pointerType !== 'mouse') return;
        const active = document.activeElement;
        if (active && card.contains(active) && typeof active.blur === 'function') {
          active.blur();
        }
      });
    });
  }
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initUI);
} else {
  initUI();
}

/* ===========================================================================
   Defer carousel until all stylesheets and fonts are loaded.
   This avoids “Layout was forced before the page was fully loaded.”
   ========================================================================== */
runWhenStylesReady(() => {
  const carousels = document.querySelectorAll('.carousel[data-carousel]');
  if (carousels.length) carousels.forEach(initCarousel);

  function initCarousel(root) {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // If controls already exist in markup, reuse them
    let prev = root.querySelector('.nav-prev');
    let next = root.querySelector('.nav-next');

    const slides = Array.from(root.querySelectorAll('img'));
    if (!slides.length) return;

    // Inject subtle arrows only if missing
    if (!prev) {
      prev = document.createElement('button');
      prev.className = 'nav-btn nav-prev';
      prev.type = 'button';
      prev.setAttribute('aria-label', 'Previous slide');
      prev.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
      root.appendChild(prev);
    }
    if (!next) {
      next = document.createElement('button');
      next.className = 'nav-btn nav-next';
      next.type = 'button';
      next.setAttribute('aria-label', 'Next slide');
      next.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
      root.appendChild(next);
    }

    if (!root.hasAttribute('tabindex')) root.setAttribute('tabindex', '0');

    let index = 0, timer = null;
    const AUTOPLAY_MS = 5000;
    const SWIPE_THRESHOLD = 40;
    let touchStartX = null, touchStartY = null;

    // Initialize first slide as active, set aria-hidden on others
    slides.forEach((el, i) => {
      if (i === 0) {
        el.classList.add('active');
        el.setAttribute('aria-hidden', 'false');
      } else {
        el.classList.remove('active');
        el.setAttribute('aria-hidden', 'true');
      }
    });

    // Two-RAF crossfade so transitions always fire visibly
    const crossfadeTo = (i) => {
      const targetIndex = (i + slides.length) % slides.length;
      if (index === targetIndex) return;
      const current = slides[index];
      const nextEl  = slides[targetIndex];

      // 1) fade-in next
      nextEl.classList.add('active');
      nextEl.setAttribute('aria-hidden', 'false');

      // 2) then fade-out previous in the next paint
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          current.classList.remove('active');
          current.setAttribute('aria-hidden', 'true');
          index = targetIndex;
        });
      });
    };

    const nextSlide = () => crossfadeTo(index + 1);
    const prevSlide = () => crossfadeTo(index - 1);

    const start = () => {
      stop();
      // Only autoplay if user hasn't requested reduced motion
      if (slides.length > 1 && !prefersReducedMotion) {
        timer = setInterval(nextSlide, AUTOPLAY_MS);
      }
    };
    const stop  = () => { if (timer) { clearInterval(timer); timer = null; } };

    next.addEventListener('click', () => { nextSlide(); start(); });
    prev.addEventListener('click', () => { prevSlide(); start(); });

    root.addEventListener('mouseenter', stop);
    root.addEventListener('mouseleave', start);
    root.addEventListener('focusin', stop);
    root.addEventListener('focusout', (e) => { if (!root.contains(e.relatedTarget)) start(); });

    root.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); nextSlide(); start(); }
      if (e.key === 'ArrowLeft')  { e.preventDefault(); prevSlide(); start(); }
    });

    root.addEventListener('touchstart', (e) => {
      if (!e.touches || e.touches.length !== 1) return;
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
      stop();
    }, { passive: true });
    root.addEventListener('touchend', (e) => {
      if (touchStartX === null) { start(); return; }
      const dx = (e.changedTouches[0].clientX) - touchStartX;
      const dy = (e.changedTouches[0].clientY) - touchStartY;
      if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > SWIPE_THRESHOLD) dx < 0 ? nextSlide() : prevSlide();
      touchStartX = touchStartY = null;
      start();
    }, { passive: true });

    if (slides.length > 1) start(); else { prev.style.display = 'none'; next.style.display = 'none'; }
  }
});

/* Fallback active-state by URL (in case templates fail) */
document.addEventListener('DOMContentLoaded', function () {
  var here = location.pathname.replace(/\/+$/, '');
  document.querySelectorAll('.menu-link').forEach(function (a) {
    var href = (a.getAttribute('href') || '').replace(location.origin, '').replace(/\/+$/, '');
    if (href && href === here) {
      a.classList.add('active');
      a.setAttribute('aria-current', 'page');
    }
  });
});
