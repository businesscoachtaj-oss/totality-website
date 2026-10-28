// Promo tracker: shared by the website and the Chrome extension.
// Data lives in chrome.storage.local (extension) or localStorage (website), key "zto.tracker".
(() => {
  const KEY = "zto.tracker";
  const hasChrome = typeof chrome !== "undefined" && chrome.storage && chrome.storage.local;
  const Store = {
    async load() {
      if (hasChrome) return new Promise((r) => chrome.storage.local.get(KEY, (o) => r(o[KEY] || null)));
      try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch { return null; }
    },
    async save(d) {
      if (hasChrome) return new Promise((r) => chrome.storage.local.set({ [KEY]: d }, r));
      try { localStorage.setItem(KEY, JSON.stringify(d)); } catch {}
    },
  };
  const $ = (s) => document.getElementById(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const toast = (m) => {
    if (window.ZTO) return ZTO.toast(m);
    const t = document.createElement("div"); t.className = "toast"; t.setAttribute("role", "status"); t.textContent = m;
    document.body.append(t); setTimeout(() => t.remove(), 2200);
  };
  const DAY = 86400000;
  const today = () => new Date(new Date().toDateString());
  const iso = (d) => new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  const uid = () => Math.random().toString(36).slice(2, 10);
  const slugOf = (url) => { try { const u = new URL(url.startsWith("http") ? url : "https://" + url); return u.pathname.split("/").filter(Boolean)[0] || ""; } catch { return ""; } };
  const daysBetween = (a, b) => Math.round((b - a) / DAY);

  let data = { groups: [], posts: [], offers: [], v: 1 };

  // ---- similarity for duplicate wording ----
  const grams = (t) => { const w = t.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter(Boolean); const s = new Set(); for (let i = 0; i < w.length - 2; i++) s.add(w.slice(i, i + 3).join(" ")); return s; };
  const sim = (a, b) => { const A = grams(a), B = grams(b); if (!A.size || !B.size) return 0; let n = 0; A.forEach((g) => B.has(g) && n++); return n / Math.min(A.size, B.size); };

  function groupStatus(g) {
    const posts = data.posts.filter((p) => p.groupId === g.id && p.kind === "promo").sort((a, b) => b.date.localeCompare(a.date));
    const last = posts[0];
    if (g.rule === "none") return { cls: "bad", label: "No promo allowed", last };
    if (g.rule === "pending") return { cls: "", label: "Membership pending", last };
    if (!last) return { cls: "good", label: "Ready", last };
    const gap = daysBetween(new Date(last.date), today());
    if (g.rule === "thread") return { cls: "warn", label: "Once per thread: check for a new thread", last };
    const every = Math.max(0, +g.every || 0);
    if (gap >= every) return { cls: "good", label: "Ready", last };
    return { cls: "warn", label: `Wait ${every - gap} day${every - gap === 1 ? "" : "s"}`, last };
  }

  // ---- rendering ----
  function render() {
    renderToday(); renderGroups(); renderLog(); renderOffers(); fillGroupSelect();
  }
  function fillGroupSelect() {
    const sel = $("pGroup"); const cur = sel.value;
    sel.innerHTML = '<option value="">Choose a group</option>' + data.groups.map((g) => `<option value="${g.id}">${esc(g.name)}</option>`).join("");
    sel.value = cur;
    const os = $("pOffer"); const oc = os.value;
    os.innerHTML = '<option value="">No saved offer</option>' + data.offers.map((o) => `<option value="${o.id}">${esc(o.title)}</option>`).join("");
    os.value = oc;
  }
  function renderToday() {
    const el = $("todayList");
    if (!data.groups.length) { el.innerHTML = '<p class="hint">Add the groups you promote in under "Groups" and they\'ll show here with when you can post next.</p>'; return; }
    const rows = data.groups.map((g) => ({ g, s: groupStatus(g) })).sort((a, b) => (a.s.cls === "good" ? 0 : a.s.cls === "warn" ? 1 : 2) - (b.s.cls === "good" ? 0 : b.s.cls === "warn" ? 1 : 2));
    el.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Group</th><th>Status</th><th>Last promo</th><th>Where to post</th><th></th></tr></thead><tbody>${rows.map(({ g, s }) => `
      <tr><td><strong>${esc(g.name)}</strong>${g.url ? `<br><a href="${esc(g.url)}" target="_blank" rel="noopener">${esc(g.url.replace(/^https?:\/\/(www\.)?/, ""))}</a>` : ""}</td>
      <td><span class="pill ${s.cls}">${esc(s.label)}</span></td>
      <td>${s.last ? `${esc(s.last.date)}<br><span class="hint">${daysBetween(new Date(s.last.date), today())} days ago</span>` : '<span class="hint">never</span>'}</td>
      <td class="hint">${esc(g.where || "")}</td>
      <td><button class="btn ghost small" data-log="${g.id}">Log a post</button></td></tr>`).join("")}</tbody></table></div>`;
    el.querySelectorAll("[data-log]").forEach((b) => b.onclick = () => { showTab("log"); $("pGroup").value = b.dataset.log; $("pKind").value = "promo"; $("pText").focus(); checkLog(); });
  }
  function renderGroups() {
    const el = $("groupList");
    el.innerHTML = data.groups.length ? data.groups.map((g) => `
      <div class="panel" style="padding:14px">
        <div class="row" style="justify-content:space-between"><strong>${esc(g.name)}</strong><div class="row"><button class="btn ghost small" data-edit="${g.id}">Edit</button><button class="btn danger small" data-del="${g.id}">Remove</button></div></div>
        <p class="hint" style="margin:4px 0">${esc(ruleText(g))}${g.where ? " · " + esc(g.where) : ""}</p>
        ${g.notes ? `<p class="hint" style="margin:0;white-space:pre-wrap">${esc(g.notes)}</p>` : ""}
      </div>`).join("") : '<p class="hint">No groups yet.</p>';
    el.querySelectorAll("[data-edit]").forEach((b) => b.onclick = () => editGroup(b.dataset.edit));
    el.querySelectorAll("[data-del]").forEach((b) => b.onclick = () => {
      const g = data.groups.find((x) => x.id === b.dataset.del);
      if (b.dataset.sure) { data.groups = data.groups.filter((x) => x.id !== g.id); persist(); toast("Removed"); }
      else { b.dataset.sure = "1"; b.textContent = "Tap again to remove"; setTimeout(() => { delete b.dataset.sure; b.textContent = "Remove"; }, 3000); }
    });
  }
  const ruleText = (g) => g.rule === "none" ? "No self promotion" : g.rule === "pending" ? "Membership pending" : g.rule === "thread" ? "Once per promo thread" : `Promo every ${g.every || 0} day${+g.every === 1 ? "" : "s"}`;
  function renderLog() {
    const el = $("logList");
    const list = [...data.posts].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 200);
    el.innerHTML = list.length ? `<div class="table-wrap"><table><thead><tr><th>Date</th><th>Group</th><th>Type</th><th>What</th><th></th></tr></thead><tbody>${list.map((p) => {
      const g = data.groups.find((x) => x.id === p.groupId);
      return `<tr><td>${esc(p.date)}</td><td>${esc(g ? g.name : "(removed group)")}</td><td><span class="pill">${esc(p.kind)}</span></td>
      <td>${p.link ? `<a href="${esc(p.link)}" target="_blank" rel="noopener">link</a> · ` : ""}<span class="hint">${esc((p.text || "").slice(0, 140))}${(p.text || "").length > 140 ? "..." : ""}</span></td>
      <td><button class="btn danger small" data-delpost="${p.id}">Delete</button></td></tr>`; }).join("")}</tbody></table></div>` : '<p class="hint">Nothing logged yet.</p>';
    el.querySelectorAll("[data-delpost]").forEach((b) => b.onclick = () => {
      if (b.dataset.sure) { data.posts = data.posts.filter((x) => x.id !== b.dataset.delpost); persist(); }
      else { b.dataset.sure = "1"; b.textContent = "Tap again"; setTimeout(() => { delete b.dataset.sure; b.textContent = "Delete"; }, 3000); }
    });
  }
  function renderOffers() {
    const el = $("offerList");
    el.innerHTML = data.offers.length ? data.offers.map((o) => `
      <div class="panel" style="padding:14px">
        <div class="row" style="justify-content:space-between"><strong>${esc(o.title)}</strong><div class="row"><button class="btn small" data-copyoffer="${o.id}">Copy</button><button class="btn ghost small" data-editoffer="${o.id}">Edit</button><button class="btn danger small" data-deloffer="${o.id}">Remove</button></div></div>
        <p class="hint" style="margin:6px 0 0;white-space:pre-wrap">${esc(o.text)}</p></div>`).join("") : '<p class="hint">Save the offer details you reuse (price, who it\'s for, link) so every post starts from the right facts.</p>';
    el.querySelectorAll("[data-copyoffer]").forEach((b) => b.onclick = () => copy(data.offers.find((o) => o.id === b.dataset.copyoffer).text));
    el.querySelectorAll("[data-editoffer]").forEach((b) => b.onclick = () => { const o = data.offers.find((x) => x.id === b.dataset.editoffer); $("oId").value = o.id; $("oTitle").value = o.title; $("oText").value = o.text; $("oTitle").focus(); });
    el.querySelectorAll("[data-deloffer]").forEach((b) => b.onclick = () => {
      if (b.dataset.sure) { data.offers = data.offers.filter((x) => x.id !== b.dataset.deloffer); persist(); }
      else { b.dataset.sure = "1"; b.textContent = "Tap again"; setTimeout(() => { delete b.dataset.sure; b.textContent = "Remove"; }, 3000); }
    });
  }
  async function copy(t) { try { await navigator.clipboard.writeText(t); toast("Copied"); } catch { toast("Select and copy it"); } }

  // ---- warnings while logging ----
  function checkLog() {
    const out = []; const gid = $("pGroup").value, text = $("pText").value, link = $("pLink").value.trim(), kind = $("pKind").value;
    const g = data.groups.find((x) => x.id === gid);
    if (g) {
      const s = groupStatus(g);
      if (kind === "promo" && s.cls === "bad") out.push(["bad", "This group doesn't allow self promotion."]);
      if (kind === "promo" && /^Wait/.test(s.label)) out.push(["warn", `By your cadence for this group you should ${s.label.toLowerCase()} before the next promo.`]);
      if (g.rule === "thread" && kind === "promo" && link) {
        const same = data.posts.find((p) => p.groupId === gid && p.link && p.link.split("?")[0] === link.split("?")[0]);
        if (same) out.push(["bad", `You already logged a post in this thread on ${same.date}. This group allows one per thread.`]);
      }
      if (link) {
        const sameThread = data.posts.filter((p) => p.link && p.link.split("?")[0] === link.split("?")[0]).sort((a, b) => b.date.localeCompare(a.date))[0];
        if (sameThread && g.rule !== "thread") out.push(["warn", `You already posted in this thread on ${sameThread.date}. Check someone else has replied since, so you're not posting right under your own comment.`]);
      }
      if (text.trim().length > 40) {
        const best = data.posts.filter((p) => p.groupId === gid && p.text).map((p) => ({ p, s: sim(text, p.text) })).sort((a, b) => b.s - a.s)[0];
        if (best && best.s >= 0.5) out.push([best.s >= 0.75 ? "bad" : "warn", `This reads ${Math.round(best.s * 100)}% like your post from ${best.p.date} in this group. Change the opening, the angle and the closing line.`]);
      }
    }
    $("warnings").innerHTML = out.map(([c, t]) => `<p class="notice ${c === "bad" ? "bad" : ""}" style="margin:0">${esc(t)}</p>`).join("");
  }

  // ---- forms ----
  function editGroup(id) {
    const g = data.groups.find((x) => x.id === id) || {};
    $("gId").value = g.id || ""; $("gName").value = g.name || ""; $("gUrl").value = g.url || ""; $("gRule").value = g.rule || "days";
    $("gEvery").value = g.every ?? 1; $("gWhere").value = g.where || ""; $("gNotes").value = g.notes || "";
    showTab("groups"); $("gName").focus(); syncRule();
  }
  const syncRule = () => ($("gEveryWrap").hidden = $("gRule").value !== "days");
  async function persist() { await Store.save(data); render(); }

  function showTab(t) {
    document.querySelectorAll("[data-tab]").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === t));
    document.querySelectorAll("[data-pane]").forEach((p) => (p.hidden = p.dataset.pane !== t));
  }

  async function init() {
    const saved = await Store.load();
    if (saved) data = Object.assign({ groups: [], posts: [], offers: [] }, saved);
    document.querySelectorAll("[data-tab]").forEach((b) => b.onclick = () => showTab(b.dataset.tab));
    $("gRule").onchange = syncRule;
    $("gForm").onsubmit = (e) => {
      e.preventDefault();
      const name = $("gName").value.trim(); if (!name) return;
      const g = { id: $("gId").value || uid(), name, url: $("gUrl").value.trim(), slug: slugOf($("gUrl").value.trim()), rule: $("gRule").value, every: +$("gEvery").value || 0, where: $("gWhere").value.trim(), notes: $("gNotes").value.trim() };
      const i = data.groups.findIndex((x) => x.id === g.id);
      if (i >= 0) data.groups[i] = g; else data.groups.push(g);
      e.target.reset(); $("gId").value = ""; syncRule(); persist(); toast("Group saved");
    };
    $("pDate").value = iso(new Date());
    ["pGroup", "pText", "pLink", "pKind"].forEach((k) => $(k).addEventListener("input", checkLog));
    $("pOffer").onchange = () => { const o = data.offers.find((x) => x.id === $("pOffer").value); if (o && !$("pText").value.trim()) { $("pText").value = o.text; checkLog(); } };
    $("pForm").onsubmit = (e) => {
      e.preventDefault();
      if (!$("pGroup").value) { toast("Choose a group"); return; }
      data.posts.push({ id: uid(), groupId: $("pGroup").value, date: $("pDate").value || iso(new Date()), kind: $("pKind").value, link: $("pLink").value.trim(), text: $("pText").value.trim(), offerId: $("pOffer").value || "" });
      $("pText").value = ""; $("pLink").value = ""; $("warnings").innerHTML = ""; persist(); toast("Logged");
    };
    $("oForm").onsubmit = (e) => {
      e.preventDefault();
      const o = { id: $("oId").value || uid(), title: $("oTitle").value.trim(), text: $("oText").value.trim() };
      if (!o.title || !o.text) return;
      const i = data.offers.findIndex((x) => x.id === o.id);
      if (i >= 0) data.offers[i] = o; else data.offers.push(o);
      e.target.reset(); $("oId").value = ""; persist(); toast("Offer saved");
    };
    $("exportBtn").onclick = () => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
      a.download = `promo-tracker-${iso(new Date())}.json`; document.body.append(a); a.click(); setTimeout(() => a.remove(), 300);
    };
    $("importFile").onchange = () => {
      const f = $("importFile").files[0]; if (!f) return;
      const r = new FileReader();
      r.onload = () => {
        try {
          const d = JSON.parse(r.result);
          if (!Array.isArray(d.groups) || !Array.isArray(d.posts)) throw 0;
          data = Object.assign({ groups: [], posts: [], offers: [] }, d); persist(); toast("Backup loaded");
        } catch { toast("That file isn't a tracker backup"); }
      };
      r.readAsText(f);
    };
    // prefill from extension "log this page" link: ?url=...
    const q = new URLSearchParams(location.search);
    if (q.get("url")) {
      const url = q.get("url"); const slug = slugOf(url);
      const g = data.groups.find((x) => x.slug === slug);
      showTab("log"); $("pLink").value = url;
      if (g) $("pGroup").value = g.id; else { $("gUrl").value = "https://www.skool.com/" + slug; }
    }
    syncRule(); render(); checkLog();
  }
  window.ZTOTracker = { init };
})();
