/* Replace broken images with clean, generated placeholders.
 *
 * The dataset stores remote thumbnail URLs (Google / Bing image caches) that can
 * expire or be blocked. When one fails to load we draw an SVG card showing the
 * course subject and platform instead of a broken-image icon. Header buttons fall
 * back to a text label. Loaded in <head> with a capturing listener so it also
 * catches errors that fire before the page finishes loading.
 */
(function () {
  var PALETTE = ["#2563eb", "#7c3aed", "#db2777", "#ea580c", "#16a34a",
                 "#0891b2", "#4f46e5", "#ca8a04", "#dc2626", "#0d9488"];

  function hash(text) {
    var h = 0;
    for (var i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) >>> 0;
    return h;
  }

  function escapeXml(text) {
    return String(text).replace(/[<>&"']/g, function (c) {
      return { "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;", "'": "&apos;" }[c];
    });
  }

  function courseCard(subject, platform) {
    subject = (subject || "Course").trim().toUpperCase();
    platform = (platform || "").trim();
    var c1 = PALETTE[hash(subject) % PALETTE.length];
    var c2 = PALETTE[(hash(subject) + 3) % PALETTE.length];
    var size = subject.length > 22 ? 22 : 28;
    var svg =
      '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200">' +
      '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">' +
      '<stop offset="0" stop-color="' + c1 + '"/><stop offset="1" stop-color="' + c2 + '"/>' +
      '</linearGradient></defs>' +
      '<rect width="400" height="200" fill="url(#g)"/>' +
      '<circle cx="345" cy="40" r="70" fill="#ffffff" opacity="0.08"/>' +
      '<circle cx="40" cy="190" r="60" fill="#ffffff" opacity="0.08"/>' +
      '<text x="200" y="98" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" ' +
      'font-size="' + size + '" font-weight="700" fill="#ffffff">' + escapeXml(subject) + '</text>' +
      (platform ? '<text x="200" y="134" text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif" ' +
        'font-size="16" fill="#ffffff" opacity="0.9">' + escapeXml(platform.toUpperCase()) + '</text>' : '') +
      '</svg>';
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  }

  function navButton(img) {
    var label = document.createElement("span");
    label.textContent = img.getAttribute("data-label") || "Open";
    label.style.cssText = "display:inline-block;width:" + (img.width || 120) + "px;line-height:" +
      (img.height || 50) + "px;background:#111827;color:#fff;border-radius:8px;" +
      "font-weight:600;font-size:15px;text-align:center;";
    img.replaceWith(label);
  }

  window.addEventListener("error", function (event) {
    var img = event.target;
    if (!img || img.tagName !== "IMG" || img.dataset.fallbackDone) return;
    img.dataset.fallbackDone = "1";
    if (img.hasAttribute("data-label")) {
      navButton(img);
    } else {
      img.src = courseCard(img.getAttribute("data-subject"), img.getAttribute("data-platform"));
    }
  }, true);
})();
