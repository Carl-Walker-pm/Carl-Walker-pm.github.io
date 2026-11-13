/* Båtsfjord-portalen — morpheme "!" pop-ups. Data: roots.json (fetched when served over http),
   falls back to roots.js (window.ROOTS_DATA) for file:// previews. No external calls. */
(function () {
  "use strict";
  var pop = document.getElementById("rootpop");
  var lastBtn = null, uid = 0;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  var player = null, playingBtn = null;
  function stopAudio() {
    if (player) { player.pause(); player.currentTime = 0; }
    if (playingBtn) { playingBtn.classList.remove("is-playing"); playingBtn.setAttribute("aria-pressed", "false"); }
    playingBtn = null;
  }
  function playBtn(a, scope) {
    var synth = a.kind === "synthetic";
    var b = el("button", "rp-play" + (synth ? " rp-play-synth" : ""));
    b.type = "button";
    b.setAttribute("aria-pressed", "false");
    b.setAttribute("aria-label", "Spill av uttale: " + a.say + (synth ? " (syntetisk stemme)" : " (opptak)"));
    b.appendChild(el("span", "rp-play-i", "")).setAttribute("aria-hidden", "true");
    b.appendChild(el("span", "rp-play-t", a.say));
    b.appendChild(el("span", "rp-play-k", synth ? "syntetisk stemme" : "opptak"));
    b.addEventListener("click", function (ev) {
      ev.stopPropagation();
      if (playingBtn === b) { stopAudio(); return; }
      stopAudio();
      if (!player) { player = new Audio(); player.preload = "auto";
        player.addEventListener("ended", stopAudio); player.addEventListener("error", function () {
          if (playingBtn) playingBtn.classList.add("is-error"); stopAudio(); }); }
      player.src = a.file;
      playingBtn = b; b.classList.add("is-playing"); b.setAttribute("aria-pressed", "true");
      var pr = player.play(); if (pr && pr.catch) pr.catch(function () { stopAudio(); });
    });
    return b;
  }
  function audioRow(list, none) {
    var row = el("div", "rp-audio");
    if (list && list.length) list.forEach(function (a) { row.appendChild(playBtn(a)); });
    else if (none) row.appendChild(el("span", "rp-noaudio", none));
    else return null;
    return row;
  }

  function kind(m) {
    if (m.type === "grammatical") return "gram";
    if (m.type === "unsourced" || m.type === "name") return "none";
    return m.uncertain ? "unc" : "lex";
  }

  function render(data) {
    var labels = data.chain_labels || {};
    document.querySelectorAll(".w[data-w]").forEach(function (span) {
      var word = data.words[span.getAttribute("data-w")];
      if (!word) return;
      span.textContent = "";
      span.classList.add("w-split");
      word.seg.forEach(function (s, i) {
        var m = data.morphemes[s.m];
        var part = el("span", "w-seg w-" + kind(m));
        part.appendChild(el("span", "w-t", s.t));
        var b = el("button", "rk rk-" + kind(m), "!");
        b.type = "button";
        b.setAttribute("aria-haspopup", "dialog");
        b.setAttribute("aria-expanded", "false");
        b.setAttribute("aria-label", "Rot: " + s.t + " (" + span.getAttribute("data-w") + ")");
        b.dataset.m = s.m; b.dataset.t = s.t; b.dataset.word = span.getAttribute("data-w");
        b.addEventListener("click", function (ev) { ev.stopPropagation(); toggle(b, data, labels); });
        part.appendChild(b);
        if (i < word.seg.length - 1) part.appendChild(el("span", "w-dot", "·")).setAttribute("aria-hidden", "true");
        span.appendChild(part);
        if (i < word.seg.length - 1) span.appendChild(document.createElement("wbr"));
      });
    });
  }

  function fill(b, data, labels) {
    var m = data.morphemes[b.dataset.m], w = data.words[b.dataset.word];
    pop.textContent = "";
    pop.className = "rootpop rp-" + kind(m);
    var close = el("button", "rp-x", "×");
    close.type = "button"; close.setAttribute("aria-label", "Lukk");
    close.addEventListener("click", function () { hide(true); });
    pop.appendChild(close);

    var segline = el("p", "rp-word");
    w.seg.forEach(function (s, i) {
      if (i) segline.appendChild(el("span", "rp-dot", "·"));
      segline.appendChild(el("span", s.t === b.dataset.t && s.m === b.dataset.m ? "rp-on" : "", s.t));
    });
    pop.appendChild(segline);
    var wa = audioRow(w.audio, w.audio_none);
    if (wa) { wa.classList.add("rp-audio-word"); wa.insertBefore(el("span", "rp-audio-lab", "Hele navnet:"), wa.firstChild); pop.appendChild(wa); }

    var h = el("h3", "rp-h", m.form); h.id = "rootpop-h"; pop.appendChild(h);
    var tag = { lex: "Rot med kilde", unc: "Usikker · flere syn", gram: "Grammatisk endelse", none: "Ingen etymologi vist" }[kind(m)];
    if (m.loan) tag += " · lånord";
    pop.appendChild(el("p", "rp-tag", tag));
    if (m.gloss) pop.appendChild(el("p", "rp-gloss", "‘" + m.gloss + "’"));
    var ma = audioRow(m.audio, (m.type === "grammatical" || w.audio_none) ? null : m.audio_none);
    if (ma) pop.appendChild(ma);

    if (m.chain && m.chain.length) {
      var ol = el("ol", "rp-chain");
      m.chain.forEach(function (c) {
        var li = el("li");
        var lab = el("span", "rp-lang", labels[c.lang] || c.lang);
        li.appendChild(lab);
        li.appendChild(el("span", "rp-form", c.form));
        if (c.ipa) {
          var ip = el("span", "rp-ipa" + (c.ipa_note ? " rp-ipa-rec" : ""), c.ipa);
          ip.setAttribute("lang", "und-fonipa");
          li.appendChild(ip);
          if (c.ipa_note) li.appendChild(el("span", "rp-ipa-n", c.ipa_note));
        }
        if (c.gloss) li.appendChild(el("span", "rp-g", c.gloss));
        ol.appendChild(li);
      });
      pop.appendChild(ol);
    }
    if (m.variants && m.variants.forms) {
      var vr = el("p", "rp-var");
      vr.appendChild(el("span", "rp-var-h", m.variants.label + ": "));
      vr.appendChild(el("span", "rp-var-f", m.variants.forms.join(" · ")));
      pop.appendChild(vr);
    }
    if (m.note) pop.appendChild(el("p", "rp-note", m.note));
    if (m.sources && m.sources.length) {
      var src = el("p", "rp-src"); src.appendChild(el("span", "rp-src-h", "Kilder: "));
      m.sources.forEach(function (s, i) {
        if (i) src.appendChild(document.createTextNode(" · "));
        var a = el("a", "", s.label); a.href = s.url; a.rel = "noopener"; a.target = "_blank";
        src.appendChild(a);
      });
      pop.appendChild(src);
    }
    var auds = [].concat(w.audio || [], m.audio || []), seen = {};
    if (auds.length) {
      var cr = el("p", "rp-src rp-cred"); cr.appendChild(el("span", "rp-src-h", "Lyd: "));
      auds.forEach(function (a) {
        if (seen[a.file]) return; seen[a.file] = 1;
        if (cr.childNodes.length > 1) cr.appendChild(document.createTextNode(" · "));
        var t = "«" + a.say + "» – " + a.credit;
        var link = a.source || a.credit_url;
        if (link) { var x = el("a", "", t); x.href = link; x.rel = "noopener"; x.target = "_blank"; cr.appendChild(x); }
        else cr.appendChild(document.createTextNode(t));
      });
      pop.appendChild(cr);
    }
  }

  function place(b) {
    if (window.matchMedia("(max-width: 600px)").matches) {
      pop.style.left = pop.style.top = ""; pop.classList.add("rp-sheet"); return;
    }
    pop.classList.remove("rp-sheet");
    var r = b.getBoundingClientRect(), pw = pop.offsetWidth, ph = pop.offsetHeight;
    var vw = document.documentElement.clientWidth, vh = window.innerHeight;
    var left = Math.min(Math.max(12, r.left + r.width / 2 - pw / 2), vw - pw - 12);
    var top = r.bottom + 10;
    if (top + ph > vh - 12 && r.top - ph - 10 > 12) top = r.top - ph - 10;
    pop.style.left = (left + window.scrollX) + "px";
    pop.style.top = (top + window.scrollY) + "px";
  }

  function show(b, data, labels) {
    if (lastBtn) lastBtn.setAttribute("aria-expanded", "false");
    stopAudio();
    fill(b, data, labels);
    pop.hidden = false;
    place(b);
    b.setAttribute("aria-expanded", "true");
    lastBtn = b;
    pop.setAttribute("tabindex", "-1");
    pop.focus({ preventScroll: true });
  }
  function hide(refocus) {
    if (pop.hidden) return;
    stopAudio();
    pop.hidden = true;
    if (lastBtn) { lastBtn.setAttribute("aria-expanded", "false"); if (refocus) lastBtn.focus(); }
    lastBtn = null;
  }
  function toggle(b, data, labels) { if (lastBtn === b && !pop.hidden) hide(true); else show(b, data, labels); }

  document.addEventListener("keydown", function (e) { if (e.key === "Escape") hide(true); });
  document.addEventListener("click", function (e) { if (!pop.hidden && !pop.contains(e.target)) hide(false); });
  window.addEventListener("resize", function () { if (lastBtn && !pop.hidden) place(lastBtn); });

  function start(data) { render(data); window.RootsUI = { open: function (word, i) {
    var bs = document.querySelectorAll('.rk[data-word="' + word + '"]'); if (bs[i || 0]) bs[i || 0].click(); } }; }
  if (location.protocol.indexOf("http") === 0 && window.fetch) {
    fetch("roots.json").then(function (r) { return r.json(); }).then(start)
      .catch(function () { if (window.ROOTS_DATA) start(window.ROOTS_DATA); });
  } else if (window.ROOTS_DATA) start(window.ROOTS_DATA);
})();
