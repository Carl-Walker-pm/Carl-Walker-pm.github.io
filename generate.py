#!/usr/bin/env python3
"""Generate the PurpleShire.uk alpha static site from projects.json.

Usage: python3 generate.py
Outputs under purpleshireuk/ (maps 1:1 to the repo path served at
https://carl-walker-pm.github.io/purpleshireuk/).
"""

import html
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "purpleshireuk")
PROJECTS_DIR = os.path.join(OUT, "projects")
ASSETS_DIR = os.path.join(OUT, "assets")

STYLE_CSS = r"""/* PurpleShire.uk alpha — shared stylesheet */
:root {
  --bg: #12101a;
  --bg-soft: #1a1626;
  --card: #201b31;
  --card-border: #3a2f5c;
  --accent: #9d7bff;
  --accent-soft: #c9b6ff;
  --text: #ece7fa;
  --muted: #a99fc4;
  --badge: #6d5bd0;
  --radius: 14px;
  --maxw: 1080px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  line-height: 1.6;
}

.wrap {
  max-width: var(--maxw);
  margin: 0 auto;
  padding: 0 1.25rem;
}

/* Header */
.site-header {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: 1.25rem 0;
  border-bottom: 1px solid var(--card-border);
}
.wordmark {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: .02em;
  color: var(--text);
  text-decoration: none;
}
.wordmark .dot { color: var(--accent); }
.badge-alpha {
  background: var(--badge);
  color: #fff;
  font-size: .7rem;
  font-weight: 700;
  letter-spacing: .12em;
  padding: .25rem .6rem;
  border-radius: 999px;
}

/* Hero */
.hero {
  padding: 4rem 0 2.5rem;
}
.hero h1 {
  font-size: 2.4rem;
  line-height: 1.15;
  margin: 0 0 .75rem;
}
.hero .lede {
  font-size: 1.15rem;
  color: var(--muted);
  max-width: 42rem;
}
.hero .status-pill {
  display: inline-block;
  margin-top: 1rem;
  background: rgba(157, 123, 255, .12);
  border: 1px solid var(--card-border);
  color: var(--accent-soft);
  font-size: .85rem;
  padding: .35rem .85rem;
  border-radius: 999px;
}

/* Sections */
.section { padding: 2rem 0; }
.section h2 { font-size: 1.6rem; margin: 0 0 .25rem; }
.section-intro { color: var(--muted); margin: 0 0 1.5rem; }

.cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
.card {
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: var(--radius);
  padding: 1.35rem;
  text-decoration: none;
  color: inherit;
  transition: border-color .15s ease, transform .15s ease;
}
a.card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}
.card h3 { margin: 0 0 .4rem; font-size: 1.2rem; }
.card .tagline { color: var(--accent-soft); font-size: .95rem; margin: 0 0 .7rem; }
.card .status { font-size: .8rem; color: var(--muted); }
.card .status::before { content: "● "; color: var(--accent); }

/* Breadcrumb */
.breadcrumb { padding: 1.25rem 0 0; font-size: .9rem; }
.breadcrumb a { color: var(--accent-soft); text-decoration: none; }
.breadcrumb a:hover { text-decoration: underline; }

/* Prose */
.prose { max-width: 46rem; }
.prose h2 { margin-top: 2.5rem; }
ul.ticks { list-style: none; padding: 0; }
ul.ticks li { padding: .35rem 0 .35rem 1.75rem; position: relative; }
ul.ticks li::before { content: "✦"; color: var(--accent); position: absolute; left: 0; }

/* Buttons */
.btn {
  display: inline-block;
  background: var(--accent);
  color: #14101f;
  font-weight: 700;
  padding: .7rem 1.4rem;
  border-radius: var(--radius);
  text-decoration: none;
}
.btn:hover { background: var(--accent-soft); }

/* Contact form */
.contact-box {
  background: var(--bg-soft);
  border: 1px solid var(--card-border);
  border-radius: var(--radius);
  padding: 1.75rem;
  max-width: 38rem;
  margin-top: 1rem;
}
.contact-box label { display: block; font-weight: 600; margin: .9rem 0 .3rem; }
.contact-box label:first-child { margin-top: 0; }
.contact-box input[type="text"],
.contact-box input[type="email"],
.contact-box textarea {
  width: 100%;
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  color: var(--text);
  padding: .65rem .8rem;
  font-size: 1rem;
  font-family: inherit;
}
.contact-box textarea { min-height: 7rem; resize: vertical; }
.contact-box button {
  margin-top: 1.1rem;
  background: var(--accent);
  color: #14101f;
  font-weight: 700;
  font-size: 1rem;
  border: 0;
  border-radius: var(--radius);
  padding: .7rem 1.6rem;
  cursor: pointer;
}
.contact-box button:hover { background: var(--accent-soft); }
.contact-box button[disabled] { opacity: .6; cursor: default; }
.form-note { font-size: .85rem; color: var(--muted); margin-top: .9rem; }
.form-ok { color: #9df0b6; font-size: 1.05rem; }
.form-err { color: #ff9d9d; }

/* Footer */
.site-footer {
  margin-top: 3.5rem;
  padding: 1.75rem 0 2.5rem;
  border-top: 1px solid var(--card-border);
  color: var(--muted);
  font-size: .9rem;
}

/* Larger screens */
@media (min-width: 700px) {
  .hero h1 { font-size: 3rem; }
  .cards { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 1050px) {
  .cards { grid-template-columns: repeat(3, 1fr); }
}
"""

SITE_JS = r"""/* PurpleShire.uk alpha — shared behaviour */
(function () {
  "use strict";

  /* Current year in footer */
  var yearEl = document.getElementById("year");
  if (yearEl) { yearEl.textContent = String(new Date().getFullYear()); }

  /* Smooth scroll for in-page anchors */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener("click", function (ev) {
      var target = document.getElementById(a.getAttribute("href").slice(1));
      if (target) {
        ev.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  /* AJAX contact form (intercept only forms marked data-ajax) */
  var form = document.querySelector("form[data-ajax]");
  if (!form) { return; }

  var wrap = form.parentElement;
  var endpoint = form.getAttribute("action");
  var projectName = form.getAttribute("data-project") || "Website";
  var email = form.getAttribute("data-email");

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var btn = form.querySelector('button[type="submit"]');
    var name = form.elements.namedItem("name").value.trim();
    var sender = form.elements.namedItem("email").value.trim();
    var message = form.elements.namedItem("message").value.trim();
    if (!name || !sender || !message) { return; }

    btn.disabled = true;
    btn.textContent = "Sending…";

    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify({
        name: name,
        email: sender,
        message: message,
        _subject: "[PurpleShire.uk] " + projectName + " — new website message",
        _template: "table",
        _honey: "",
        _autoresponse: "Thanks for reaching out about " + projectName +
          " — we will get back to you soon. — PurpleShire.uk"
      })
    }).then(function (res) {
      if (!res.ok) { throw new Error("HTTP " + res.status); }
      return res.json();
    }).then(function () {
      wrap.innerHTML = '<p class="form-ok"><strong>Thanks — your message is on its way.</strong><br>' +
        "We reply from our Gmail.</p>";
    }).catch(function () {
      var fallback = email
        ? ' or write to us directly at <a href="mailto:' + email + '">' + email + "</a>"
        : "";
      wrap.innerHTML = '<p class="form-err">Sorry — something went wrong sending your message. ' +
        "Please try again later" + fallback + ".</p>";
    });
  });
})();
"""


def esc(s):
    return html.escape(s, quote=True)


def header(name, depth):
    """depth: 0 for hub (purpleshireuk/), 1 for project landings."""
    prefix = "../" if depth else ""
    return (
        '<header class="site-header wrap">\n'
        '  <a class="wordmark" href="%sindex.html">PurpleShire<span class="dot">.</span>uk</a>\n'
        '  <span class="badge-alpha">ALPHA</span>\n'
        "</header>" % prefix
    )


def footer(name, depth):
    prefix = "../" if depth else ""
    return (
        '<footer class="site-footer">\n'
        '  <div class="wrap">\n'
        '    <p>© <span id="year"></span> PurpleShire.uk — alpha version. '
        '<a href="%sindex.html" style="color: var(--accent-soft);">Back to the platform</a></p>\n'
        "  </div>\n"
        "</footer>\n"
        '<script src="%sassets/site.js"></script>' % (prefix, prefix)
    )


def page_shell(title, body, depth):
    prefix = "../" if depth else ""
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n"
        '<link rel="stylesheet" href="%sassets/style.css">\n'
        "</head>\n"
        "<body>\n%s\n</body>\n</html>\n" % (esc(title), prefix, body)
    )


def contact_section(project, email, depth):
    """Contact form: AJAX when JS is on, plain POST via <noscript> otherwise."""
    subject = "[PurpleShire.uk] %s — new website message" % project["name"]
    autoresponse = (
        "Thanks for reaching out about %s — we will get back to you soon. — PurpleShire.uk"
        % project["name"]
    )
    hidden = (
        '<input type="hidden" name="_subject" value="%s">\n'
        '<input type="hidden" name="_template" value="table">\n'
        '<input type="hidden" name="_honey" value="">\n'
        '<input type="hidden" name="_autoresponse" value="%s">\n'
        '<input type="hidden" name="_captcha" value="false">'
        % (esc(subject), esc(autoresponse))
    )
    return (
        '<section class="section" id="contact">\n'
        '<div class="wrap prose">\n'
        "<h2>Contact</h2>\n"
        '<p>Questions about %s? Send us a message — we reply from our Gmail.</p>\n'
        '<div class="contact-box">\n'
        # JS path: posts to the AJAX endpoint, intercepted by site.js
        '<form method="post" data-ajax '
        'action="https://formsubmit.co/ajax/%s" data-email="%s" data-project="%s">\n'
        "%s\n"
        '<label for="cf-name">Name</label>\n'
        '<input type="text" id="cf-name" name="name" required autocomplete="name">\n'
        '<label for="cf-email">Email</label>\n'
        '<input type="email" id="cf-email" name="email" required autocomplete="email">\n'
        '<label for="cf-msg">Message</label>\n'
        '<textarea id="cf-msg" name="message" required></textarea>\n'
        '<button type="submit">Send message</button>\n'
        '<p class="form-note">Or email us directly: '
        '<a href="mailto:%s" style="color: var(--accent-soft);">%s</a></p>\n'
        "</form>\n"
        # noscript path: classic POST to the same inbox
        "<noscript>\n"
        '<form method="post" action="https://formsubmit.co/%s">\n'
        "%s\n"
        '<label for="cf-name-ns">Name</label>\n'
        '<input type="text" id="cf-name-ns" name="name" required autocomplete="name">\n'
        '<label for="cf-email-ns">Email</label>\n'
        '<input type="email" id="cf-email-ns" name="email" required autocomplete="email">\n'
        '<label for="cf-msg-ns">Message</label>\n'
        '<textarea id="cf-msg-ns" name="message" required></textarea>\n'
        '<button type="submit">Send message</button>\n'
        "</form>\n"
        "</noscript>\n"
        "</div>\n"
        "</div>\n"
        "</section>"
        % (
            esc(project["name"]),
            email,
            email,
            esc(project["name"]),
            hidden,
            email,
            email,
            email,
            hidden,
        )
    )


def landing(project, site):
    email = site["contactEmail"]
    about = "\n".join("<p>%s</p>" % esc(p) for p in project["about"])
    highlights = "\n".join(
        "<li>%s</li>" % esc(h) for h in project.get("highlights", [])
    )
    external = ""
    ext = project.get("external")
    if ext:
        external = (
            '<p><a class="btn" href="%s" rel="noopener">%s →</a></p>\n'
            % (esc(ext["url"], ), esc(ext["label"]))
        )
    body = (
        header(site["name"], 1)
        + '<nav class="breadcrumb wrap"><a href="../index.html">← PurpleShire.uk</a></nav>\n'
        + '<section class="hero wrap">\n'
        "<h1>%s</h1>\n"
        '<p class="lede">%s</p>\n'
        '<span class="status-pill">%s</span>\n'
        "</section>\n"
        '<section class="section"><div class="wrap prose">\n'
        "<h2>About</h2>\n%s\n"
        "<h2>Highlights</h2>\n<ul class=\"ticks\">\n%s\n</ul>\n%s"
        "</div></section>\n"
        % (esc(project["name"]), esc(project["tagline"]), esc(project["status"]), about, highlights, external)
        + contact_section(project, email, 1)
        + footer(site["name"], 1)
    )
    return page_shell("%s — PurpleShire.uk" % project["name"], body, 1)


def hub(data):
    site = data["site"]
    sections = data["sections"]
    projects = data["projects"]
    cards = {}
    for p in projects:
        card = (
            '<a class="card" href="projects/%s/">\n'
            "<h3>%s</h3>\n"
            '<p class="tagline">%s</p>\n'
            '<p class="status">%s</p>\n'
            "</a>" % (p["slug"], esc(p["name"]), esc(p["tagline"]), esc(p["status"]))
        )
        cards.setdefault(p["section"], []).append(card)
    sec_html = ""
    for s in sections:
        intro = '<p class="section-intro">%s</p>\n' % esc(site["liafIntro"]) if s["id"] == "liaf" else ""
        sec_html += (
            '<section class="section" id="%s"><div class="wrap">\n'
            "<h2>%s</h2>\n%s"
            '<div class="cards">\n%s\n</div>\n'
            "</div></section>\n" % (s["id"], esc(s["title"]), intro, "\n".join(cards.get(s["id"], [])))
        )
    body = (
        header(site["name"], 0)
        + '<section class="hero wrap">\n'
        "<h1>%s</h1>\n"
        '<p class="lede">%s</p>\n'
        "</section>\n" % (esc(site["heroHeading"]), esc(site["heroSub"]))
        + sec_html
        + footer(site["name"], 0)
    )
    return page_shell(site["hubTitle"], body, 0)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", os.path.relpath(path, BASE))


def main():
    with open(os.path.join(BASE, "projects.json"), encoding="utf-8") as f:
        data = json.load(f)
    write(os.path.join(OUT, "index.html"), hub(data))
    write(os.path.join(ASSETS_DIR, "style.css"), STYLE_CSS)
    write(os.path.join(ASSETS_DIR, "site.js"), SITE_JS)
    for p in data["projects"]:
        write(os.path.join(PROJECTS_DIR, p["slug"], "index.html"), landing(p, data["site"]))
    print("done: %d landings" % len(data["projects"]))


if __name__ == "__main__":
    main()
