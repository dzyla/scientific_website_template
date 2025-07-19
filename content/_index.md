---
title: "Bio Lab"
---

<section class="hero">
  <div class="hero-image">
    <img src="{{ "images/lab.jpg" | relURL }}" alt="Bio Lab">
  </div>
  <h1>Welcome to Bio Lab</h1>
  <p>
    We are a cutting-edge biophysics laboratory dedicated to unraveling the
    complexities of biological systems through innovative research and
    interdisciplinary collaboration.
  </p>
</section>

<section class="news">
  <h2>Latest News</h2>
  {{ $news :=  where site.RegularPages "Section" "news" |  first 3 }}
  {{ if $news }}
  <ul>
    {{ range $news }}
    <li>
      <a href="{{ .Permalink }}">{{ .Title }}</a> - {{ .Date.Format "Jan 2, 2006" }}
    </li>
    {{ end }}
  </ul>
  {{ else }}
  <p>Stay tuned for updates!</p>
  {{ end }}
</section>

<section class="join-us">
  <h2>Join Our Team</h2>
  <p>
    We are always looking for talented and motivated individuals to join our
    team. If you are passionate about [mention your research area] and have a
    strong background in [relevant fields], please contact us.
  </p>
  <a href="/contact" class="button">Contact Us</a>
</section>

<section class="lab-work">
  <h2>Our Work</h2>
  <p>
    Our research focuses on [briefly describe the lab's main research focus,
    e.g., "understanding the structural basis of viral infection using
    cryo-electron microscopy"]. We employ a variety of techniques, including
    [list key techniques], to address fundamental questions in [research area].
  </p>
</section>

