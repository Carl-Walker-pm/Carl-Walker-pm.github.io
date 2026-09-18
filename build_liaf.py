#!/usr/bin/env python3
"""Build LIAF project landings from Kirill's ORIGINAL designs (sources/*.html).

For each of the 13 LIAF projects with an original in sources/, writes
  purpleshireuk/projects/<slug>/index.html            (EN, from sources/)
  purpleshireuk/ru/projects/<slug>/index.html         (RU, from ru-sources/)

The original design is kept 100% intact (markup, styles, scripts, CDNs).
Injected platform chrome, all classes prefixed `psuk-` so they can never
clash with the original's CSS:

  1. Analytics placeholder comment in <head> (standing rule).
  2. Slim PurpleShire top bar as the first element in <body>
     (position:sticky so it never covers the original design, z-index high):
     EN: "← PurpleShire.uk" -> ../../index.html,  "RU" pill -> ../../ru/projects/<slug>/index.html
     RU: "← PurpleShire.uk" -> ../../index.html,  "EN" pill -> ../../projects/<slug>/index.html
  3. Contact section before </body>: heading + short line + form wired
     exactly like generate.py's contact_section (FormSubmit AJAX + <noscript>
     fallback, carl.walker.pm@gmail.com).

demo.html in each project dir stays untouched.

The 3 LIAF projects WITHOUT originals (praw-mutual, lunar-mall, aed-project)
are owned by generate.py (landing()/landing_ru()). generate.py must NOT write
the 13 slugs below (clobber guard) — same convention as ru/index.html.

Usage: python3 build_liaf.py        # builds EN + RU
"""

import html
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "purpleshireuk")
RU_OUT = os.path.join(BASE, "purpleshireuk", "ru")

# slug -> source file stem. The 3 LIAF projects without originals are NOT here.
ORIGINAL_SLUGS = {
    "aura-botanica": "aura-botanica",
    "aurelius": "aurelius",
    "future-proof-travel": "future-proof-travel",
    "kinetic": "kinetic",
    "lumina": "lumina",
    "proso": "proso",
    "selene": "selene",
    "softhouse": "softhouse",
    "synthetix": "synthetix",
    "tao-school": "tao-school",
    "unity-travel": "unity-travel",
    "vantage": "vantage",
    "velocity": "velocity",
}

ANALYTICS_PLACEHOLDER = """<!-- ANALYTICS PLACEHOLDER
  GA4, Microsoft Clarity, and PostHog snippets go here.
  Standing rule: every page keeps its analytics counters.
  build_liaf.py preserves this comment verbatim on every build. -->"""

TOPBAR_CSS = """
<style>
.psuk-topbar{position:sticky;top:0;z-index:99999;display:flex;align-items:center;justify-content:space-between;
  background:rgba(14,11,24,.94);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
  border-bottom:1px solid #3a2f5c;padding:0 16px;height:44px;box-sizing:border-box;
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.psuk-topbar-back{color:#c9b6ff!important;text-decoration:none!important;font-size:13px;font-weight:600;line-height:1}
.psuk-topbar-back:hover{color:#fff!important}
.psuk-topbar-lang{color:#14101f!important;background:#9d7bff;text-decoration:none!important;
  font-size:12px;font-weight:800;letter-spacing:.08em;padding:7px 16px;border-radius:999px;line-height:1}
.psuk-topbar-lang:hover{background:#c9b6ff}
</style>
"""

CONTACT_CSS = """
<style>
.psuk-contact{background:#14101f;border-top:2px solid #3a2f5c;padding:3rem 1.25rem;
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#ece7fa}
.psuk-contact-inner{max-width:38rem;margin:0 auto}
.psuk-contact-title{margin:0 0 .5rem;font-size:1.6rem;color:#ece7fa}
.psuk-contact-sub{margin:0 0 1.25rem;color:#a99fc4;font-size:1rem}
.psuk-contact-form label{display:block;font-size:13px;font-weight:600;color:#ece7fa;margin:10px 0 4px}
.psuk-contact-form input,.psuk-contact-form textarea{display:block;width:100%;box-sizing:border-box;
  background:#201b31;border:1px solid #3a2f5c;border-radius:8px;color:#ece7fa;
  padding:10px 12px;font-size:15px;font-family:inherit}
.psuk-contact-form input:focus,.psuk-contact-form textarea:focus{outline:none;border-color:#9d7bff}
.psuk-contact-form textarea{resize:vertical;min-height:110px}
.psuk-contact-form button{margin-top:16px;background:#9d7bff;color:#14101f;border:0;border-radius:10px;
  font-weight:700;font-size:15px;padding:12px 26px;cursor:pointer}
.psuk-contact-form button:hover{background:#c9b6ff}
.psuk-contact-note{font-size:13px;color:#a99fc4;margin:14px 0 0}
.psuk-contact-note a{color:#c9b6ff}
.psuk-contact-status{font-size:14px;margin:10px 0 0;min-height:1.2em}
.psuk-contact-status.psuk-ok{color:#9df0b6}
.psuk-contact-status.psuk-err{color:#ff9d9d}
</style>
"""

CONTACT_JS = """
<script>
(function(){
  "use strict";
  var form=document.querySelector("form[data-psuk-ajax]");
  if(!form)return;
  form.addEventListener("submit",function(e){
    e.preventDefault();
    var email=form.getAttribute("data-psuk-email"),project=form.getAttribute("data-psuk-project");
    var name=form.elements.name.value.trim(),sender=form.elements.email.value.trim(),msg=form.elements.message.value.trim();
    var status=form.querySelector(".psuk-contact-status");
    var btn=form.querySelector('button[type="submit"]');
    status.className="psuk-contact-status";status.textContent="";
    if(!name||!sender||!msg){status.classList.add("psuk-err");status.textContent=form.getAttribute("data-psuk-incomplete");return;}
    btn.disabled=true;btn.textContent=form.getAttribute("data-psuk-sending");
    fetch("https://formsubmit.co/ajax/"+email,{
      method:"POST",headers:{"Content-Type":"application/json","Accept":"application/json"},
      body:JSON.stringify({name:name,email:sender,message:msg,
        _subject:"[PurpleShire.uk] "+project+" \\u2014 new website message",
        _template:"table",_honey:"",
        _autoresponse:form.getAttribute("data-psuk-autoresponse")})
    }).then(function(r){if(!r.ok)throw new Error("http "+r.status);return r.json();})
    .then(function(){
      form.innerHTML='<p class="psuk-contact-status psuk-ok">'+form.getAttribute("data-psuk-thanks")+"</p>";
    })
    .catch(function(){
      status.classList.add("psuk-err");
      status.innerHTML=form.getAttribute("data-psuk-failed");
      btn.disabled=false;btn.textContent=form.getAttribute("data-psuk-send");
    });
  });
})();
</script>
"""


def topbar(slug, lang):
    """Slim platform bar, first element in <body>."""
    if lang == "ru":
        lang_pill = '<a class="psuk-topbar-lang" href="../../projects/%s/index.html">EN</a>' % slug
    else:
        lang_pill = '<a class="psuk-topbar-lang" href="../../ru/projects/%s/index.html">RU</a>' % slug
    return (
        TOPBAR_CSS
        + '<div class="psuk-topbar">\n'
        + '  <a class="psuk-topbar-back" href="../../index.html">&larr; PurpleShire.uk</a>\n'
        + "  %s\n" % lang_pill
        + "</div>\n"
    )


def contact_section(name, email, lang):
    """Contact section before </body>, FormSubmit wiring identical to generate.py."""
    if lang == "ru":
        title, sub = "Контакты", "Вопросы о %s? Напишите нам — отвечаем с нашего Gmail." % name
        l_name, l_email, l_msg = "Имя", "Email", "Сообщение"
        send, sending = "Отправить", "Отправка…"
        incomplete = "Заполните, пожалуйста, все поля."
        thanks = "Спасибо! Ваше сообщение отправлено. Мы отвечаем с нашего Gmail."
        failed = "Что-то пошло не так. Попробуйте ещё раз или напишите на"
        autoresponse = (
            "Спасибо за обращение по %s — мы скоро ответим. — PurpleShire.uk" % name
        )
        note = "Или напишите напрямую:"
    else:
        title, sub = "Contact", "Questions about %s? Send us a message — we reply from our Gmail." % name
        l_name, l_email, l_msg = "Name", "Email", "Message"
        send, sending = "Send message", "Sending…"
        incomplete = "Please fill in all fields."
        thanks = "Thank you! Your message is on its way. We reply from our Gmail."
        failed = "Sorry — something went wrong. Please try again or write to"
        autoresponse = (
            "Thanks for reaching out about %s — we will get back to you soon. — PurpleShire.uk" % name
        )
        note = "Or email us directly:"

    def esc(s):
        return html.escape(s, quote=True)

    hidden = (
        '<input type="hidden" name="_subject" value="%s">\n'
        '<input type="hidden" name="_template" value="table">\n'
        '<input type="hidden" name="_honey" value="">\n'
        '<input type="hidden" name="_autoresponse" value="%s">\n'
        '<input type="hidden" name="_captcha" value="false">'
        % (esc("[PurpleShire.uk] %s — new website message" % name), esc(autoresponse))
    )
    failed_html = esc(failed) + ' <a href="mailto:%s">%s</a>.' % (esc(email), esc(email))
    form = (
        '<form class="psuk-contact-form" method="post" data-psuk-ajax '
        'action="https://formsubmit.co/ajax/%s" data-psuk-email="%s" data-psuk-project="%s" '
        'data-psuk-incomplete="%s" data-psuk-sending="%s" data-psuk-send="%s" '
        'data-psuk-autoresponse="%s" data-psuk-thanks="%s" data-psuk-failed="%s">\n'
        "%s\n"
        '<label>%s<input type="text" name="name" required autocomplete="name"></label>\n'
        '<label>%s<input type="email" name="email" required autocomplete="email"></label>\n'
        '<label>%s<textarea name="message" required></textarea></label>\n'
        '<button type="submit">%s</button>\n'
        '<p class="psuk-contact-note">%s <a href="mailto:%s">%s</a></p>\n'
        '<p class="psuk-contact-status"></p>\n'
        "</form>\n"
        "<noscript>\n"
        '<form class="psuk-contact-form" method="post" action="https://formsubmit.co/%s">\n'
        "%s\n"
        '<label>%s<input type="text" name="name" required autocomplete="name"></label>\n'
        '<label>%s<input type="email" name="email" required autocomplete="email"></label>\n'
        '<label>%s<textarea name="message" required></textarea></label>\n'
        '<button type="submit">%s</button>\n'
        "</form>\n"
        "</noscript>\n"
        % (
            esc(email), esc(email), esc(name),
            esc(incomplete), esc(sending), esc(send),
            esc(autoresponse), esc(thanks), esc(failed_html),
            hidden,
            esc(l_name), esc(l_email), esc(l_msg), esc(send),
            esc(note), esc(email), esc(email),
            esc(email),
            hidden,
            esc(l_name), esc(l_email), esc(l_msg), esc(send),
        )
    )
    return (
        CONTACT_CSS
        + '<section class="psuk-contact">\n<div class="psuk-contact-inner">\n'
        + "<h2 class=\"psuk-contact-title\">%s</h2>\n" % esc(title)
        + '<p class="psuk-contact-sub">%s</p>\n' % esc(sub)
        + form
        + "</div>\n</section>\n"
        + CONTACT_JS
    )


def build_one(slug, name, email, src_path, dest_path, lang):
    with open(src_path, encoding="utf-8") as f:
        page = f.read()

    if lang == "ru":
        # translated originals carry lang="en" — flip the document language
        page = re.sub(r'<html([^>]*)>', lambda m: "<html" + m.group(1).replace('lang="en"', 'lang="ru"'),
                      page, count=1, flags=re.IGNORECASE)
        if 'lang="ru"' not in page.lower():
            page = re.sub(r"<html", '<html lang="ru"', page, count=1, flags=re.IGNORECASE)

    # 1. analytics placeholder right after <head>
    m = re.search(r"<head[^>]*>", page, flags=re.IGNORECASE)
    if not m:
        raise ValueError("%s: no <head> found" % src_path)
    page = page[: m.end()] + "\n" + ANALYTICS_PLACEHOLDER + page[m.end():]

    # 2. top bar as first element in <body>
    m = re.search(r"<body[^>]*>", page, flags=re.IGNORECASE)
    if not m:
        raise ValueError("%s: no <body> found" % src_path)
    page = page[: m.end()] + "\n" + topbar(slug, lang) + page[m.end():]

    # 3. contact section before </body>
    idx = page.lower().rfind("</body>")
    if idx == -1:
        raise ValueError("%s: no </body> found" % src_path)
    page = page[:idx] + contact_section(name, email, lang) + page[idx:]

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote", os.path.relpath(dest_path, BASE))


def main():
    with open(os.path.join(BASE, "projects.json"), encoding="utf-8") as f:
        data = json.load(f)
    email = data["site"]["contactEmail"]
    names = {p["slug"]: p["name"] for p in data["projects"]}

    for slug, stem in sorted(ORIGINAL_SLUGS.items()):
        name = names[slug]
        # EN from Kirill's original
        build_one(slug, name, email,
                  os.path.join(BASE, "sources", stem + ".html"),
                  os.path.join(OUT, "projects", slug, "index.html"),
                  "en")
        # RU from the translated original
        ru_src = os.path.join(BASE, "ru-sources", stem + ".html")
        if not os.path.isfile(ru_src):
            print("SKIP RU (no translated source yet):", slug)
            continue
        build_one(slug, name, email,
                  ru_src,
                  os.path.join(RU_OUT, "projects", slug, "index.html"),
                  "ru")
    print("done")


if __name__ == "__main__":
    main()
