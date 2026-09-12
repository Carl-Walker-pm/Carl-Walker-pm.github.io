/* PurpleShire.uk alpha — shared behaviour */
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
