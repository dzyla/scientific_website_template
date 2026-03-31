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
    window.addEventListener('load', afterFonts);
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

  /* ===== Reading progress bar ============================================== */
  const progressBar = document.getElementById('reading-progress');
  if (progressBar) {
    const updateProgress = () => {
      const scrolled = window.scrollY;
      const total = document.body.scrollHeight - window.innerHeight;
      if (total > 200) {
        progressBar.classList.add('is-active');
        progressBar.style.width = Math.min(100, (scrolled / total) * 100) + '%';
      }
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    updateProgress();
  }

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

  /* ===== Scroll reveal via IntersectionObserver ============================ */
  const revealTargets = document.querySelectorAll('[data-reveal]');
  if (revealTargets.length) {
    if (!prefersReducedMotion && 'IntersectionObserver' in window) {
      revealTargets.forEach(el => el.classList.add('will-reveal'));
      const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed');
            revealObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
      revealTargets.forEach(el => revealObserver.observe(el));
    } else {
      revealTargets.forEach(el => el.classList.add('is-revealed'));
    }
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
    // Explicitly opt-in to animation even if OS has reduced motion
    root.setAttribute('data-animate', 'always');

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

    // Initialize first slide as active
    slides.forEach((el, i) => i === 0 ? el.classList.add('active') : el.classList.remove('active'));

    // Two-RAF crossfade so transitions always fire visibly
    const crossfadeTo = (i) => {
      const targetIndex = (i + slides.length) % slides.length;
      if (index === targetIndex) return;
      const current = slides[index];
      const nextEl  = slides[targetIndex];

      // 1) fade-in next
      nextEl.classList.add('active');

      // 2) then fade-out previous in the next paint
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          current.classList.remove('active');
          index = targetIndex;
        });
      });
    };

    const nextSlide = () => crossfadeTo(index + 1);
    const prevSlide = () => crossfadeTo(index - 1);

    const start = () => { stop(); if (slides.length > 1) timer = setInterval(nextSlide, AUTOPLAY_MS); };
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

/* ===========================================================================
   Dark Mode Toggle
   ========================================================================== */
(() => {
  const toggle = document.getElementById('theme-toggle');
  const root = document.documentElement;
  const STORAGE_KEY = 'theme-preference';

  const getTheme = () => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return saved;
    return 'light';
  };

  const setTheme = (theme) => {
    root.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
  };

  // Initialize
  setTheme(getTheme());

  // Listen for toggle
  toggle?.addEventListener('click', () => {
    const current = root.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    setTheme(next);
  });

  // Listen for system changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });
})();

/* ===========================================================================
   Email Obfuscation
   ========================================================================== */
const initEmailObfuscation = () => {
  document.querySelectorAll('.__cf_email__').forEach(el => {
    try {
      const email = atob(el.dataset.cfemail);
      const display = el.dataset.display || email;

      if (el.tagName === 'A') {
        el.href = 'mailto:' + email;
        if (el.innerHTML.includes('[email]')) {
          el.innerHTML = el.innerHTML.replace('[email]', email);
        }
        el.removeAttribute('data-cfemail');
        el.removeAttribute('data-display');
        el.classList.remove('__cf_email__');
      } else {
        const a = document.createElement('a');
        a.href = 'mailto:' + email;
        a.textContent = display;
        a.className = el.className;
        a.classList.remove('__cf_email__');
        el.replaceWith(a);
      }
    } catch (e) {
      console.error('Email obfuscation failed', e);
    }
  });
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initEmailObfuscation);
} else {
  initEmailObfuscation();
}

/* ===========================================================================
   Copy Citation
   =========================================================================== */
const initCitationCopy = () => {
  document.querySelectorAll('.pub-copy-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const text = btn.dataset.citation;
      if (!text) return;
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        // Fallback for older browsers
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.cssText = 'position:fixed;opacity:0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      const label = btn.querySelector('.pub-copy-label');
      btn.classList.add('is-copied');
      if (label) label.textContent = 'Copied!';
      setTimeout(() => {
        btn.classList.remove('is-copied');
        if (label) label.textContent = 'Cite';
      }, 2000);
    });
  });
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initCitationCopy);
} else {
  initCitationCopy();
}
