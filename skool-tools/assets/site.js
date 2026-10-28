// Shared header, footer and small helpers for the Zero to Operator tools.
(function () {
  const JOIN = "https://www.skool.com/tbd-5276/about";
  const pages = [
    ["members.html", "Member dashboard"],
    ["health.html", "Group health check"],
    ["formatter.html", "Lesson formatter"],
    ["tracker.html", "Promo tracker"],
  ];
  const here = location.pathname.split("/").pop() || "index.html";

  const header = document.createElement("header");
  header.className = "top wrap";
  header.innerHTML =
    '<a class="brand" href="index.html"><img src="img/op-wave.png" alt=""><span>Tools for Skool owners<small>by Zero to Operator</small></span></a>' +
    '<nav class="tools" aria-label="Tools">' +
    pages.map(([href, name]) => `<a href="${href}"${href === here ? ' aria-current="page"' : ""}>${name}</a>`).join("") +
    "</nav>";
  document.body.prepend(header);

  const footer = document.createElement("footer");
  footer.className = "site wrap";
  footer.innerHTML =
    '<div class="cta"><img src="img/op-welcome.png" alt=""><div>' +
    "<p><strong>Made by Zero to Operator</strong>, a free Skool community where business owners learn to start, build and run their business with Claude as the team.</p>" +
    `<a class="btn" href="${JOIN}" target="_blank" rel="noopener">Join Zero to Operator free</a></div></div>` +
    "<p>Free to use. Everything runs in your browser: nothing you paste or upload is sent anywhere or stored on a server.</p>" +
    "<p>Independent tools. Not made by, affiliated with or endorsed by Skool or Anthropic. Skool is a trademark of its owner.</p>";
  document.body.append(footer);

  window.ZTO = {
    JOIN,
    toast(msg) {
      const t = document.createElement("div");
      t.className = "toast";
      t.setAttribute("role", "status");
      t.textContent = msg;
      document.body.append(t);
      setTimeout(() => t.remove(), 2200);
    },
    esc(s) {
      return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    },
    async copyText(text) {
      try { await navigator.clipboard.writeText(text); ZTO.toast("Copied"); return true; }
      catch { ZTO.toast("Select the text and copy it"); return false; }
    },
    store: {
      get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } },
      set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch { return false; } },
    },
    download(name, text, type = "application/json") {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([text], { type }));
      a.download = name;
      document.body.append(a);
      a.click();
      setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
    },
  };
})();
