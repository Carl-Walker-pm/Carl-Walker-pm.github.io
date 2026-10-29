/* =====================================================================
   CORE WIDGET 1 — ON AIR seconds counter
   Broadcast Hub, purpleshire.uk project.
   ---------------------------------------------------------------------
   HOW TO CONNECT IT TO ANY SCREEN (.html):
     Add this one line before </body>:
       <script src="onair-widget.js"></script>
     (Use the path relative to the page. Same file on every screen.)
   WHY IT NEVER STOPS AND NEVER RESETS:
     The counter is NOT a timer that counts up in memory. It is derived
     from the wall clock: elapsed = now - ON_AIR_START. Changing screens,
     reloading, or a throttled background tab cannot reset or drift it —
     on every tick it recomputes from the clock. That is what makes it
     core: it runs as long as the broadcast's start moment exists.
   ON_AIR_START: the moment the broadcast was switched on,
     2026-10-28 20:12:55 PDT (2026-10-29T03:12:55Z), Kirill's order.
   ===================================================================== */
(function () {
  "use strict";

  var ON_AIR_START = 1793243575; // Unix seconds, 2026-10-29T03:12:55Z

  // Public handle so future widgets can connect to the same core.
  window.__onAir = {
    startEpoch: ON_AIR_START,
    elapsed: function () {
      return Math.max(0, Math.floor(Date.now() / 1000) - ON_AIR_START);
    }
  };

  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function hms(total) {
    var h = Math.floor(total / 3600);
    var m = Math.floor((total % 3600) / 60);
    var s = total % 60;
    return pad(h) + ":" + pad(m) + ":" + pad(s);
  }

  var css = [
    "#onair-core{position:fixed;top:14px;right:14px;z-index:10000;",
    "background:rgba(10,8,24,.88);border:1px solid #f472b6;",
    "border-radius:12px;padding:10px 14px;color:#fff;",
    "font-family:ui-monospace,Menlo,Consolas,monospace;",
    "text-align:right;box-shadow:0 4px 24px rgba(0,0,0,.45);}",
    "#onair-core .onair-top{display:flex;align-items:center;gap:8px;",
    "justify-content:flex-end;font-size:12px;font-weight:700;",
    "letter-spacing:.18em;color:#f472b6;}",
    "#onair-core .onair-dot{width:9px;height:9px;border-radius:50%;",
    "background:#f472b6;box-shadow:0 0 10px #f472b6;",
    "animation:onair-pulse 1.6s infinite;}",
    "@keyframes onair-pulse{0%,100%{opacity:1}50%{opacity:.35}}",
    "#onair-core .onair-sec{font-size:26px;font-weight:700;",
    "line-height:1.25;font-variant-numeric:tabular-nums;}",
    "#onair-core .onair-sec small{font-size:13px;color:#9a93c4;",
    "font-weight:400;letter-spacing:.08em;}",
    "#onair-core .onair-hms{font-size:12px;color:#9a93c4;",
    "font-variant-numeric:tabular-nums;}"
  ].join("");

  function build() {
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);

    var box = document.createElement("div");
    box.id = "onair-core";
    box.innerHTML =
      '<div class="onair-top"><span class="onair-dot"></span>ON AIR</div>' +
      '<div class="onair-sec"><span id="onair-sec-num">0</span> <small>seconds</small></div>' +
      '<div class="onair-hms" id="onair-hms-num">00:00:00</div>';
    document.body.appendChild(box);

    var secEl = document.getElementById("onair-sec-num");
    var hmsEl = document.getElementById("onair-hms-num");

    function tick() {
      var total = window.__onAir.elapsed();
      secEl.textContent = total.toLocaleString("en-US");
      hmsEl.textContent = hms(total);
    }
    tick();
    setInterval(tick, 1000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
