// Booru tag autocompletion for Dataset Tag Editor (standalone).
// Compatible with the tag database of DominikDoom/a1111-sd-webui-tagcomplete:
// it reads the same CSV format (<name>,<type>,<postCount>,"<aliases>") served by
// /dte/tagcomplete/tags.csv and attaches to the same caption textareas the
// original extension targets (Caption of Selected Image, Interrogate Result,
// Edit Caption, Edit Tags). Self-contained: no a1111 / gradioApp-shim needed
// beyond the gradioApp() helper already defined in 00_init.js.
(function () {
    "use strict";

    var TARGET_IDS = ["dte_caption", "dte_interrogate", "dte_edit_caption", "dte_edit_tags"];
    var TYPE_CLASS = { 0: "tac-type-0", 1: "tac-type-1", 3: "tac-type-3", 4: "tac-type-4", 5: "tac-type-5" };

    var cfg = { enabled: true, maxResults: 20, searchAlias: true, replaceUnderscores: true, appendComma: true };
    var tags = [];
    var loaded = false, loading = null, loadFailed = false;
    var attached = new WeakSet();
    var popup = null, results = [], activeIndex = -1, activeTa = null, skipNextInput = false;

    function app() { return (typeof gradioApp === "function") ? gradioApp() : document; }

    // ---- data loading -------------------------------------------------------
    function loadData() {
        if (loaded) return Promise.resolve();
        if (loading) return loading;
        loading = Promise.all([
            fetch("dte/tagcomplete/config").then(function (r) { return r.json(); }),
            fetch("dte/tagcomplete/tags.csv").then(function (r) { return r.text(); })
        ]).then(function (res) {
            cfg = Object.assign(cfg, res[0] || {});
            tags = parseCsv(res[1] || "");
            loaded = true; loading = null;
        }).catch(function () { loading = null; loadFailed = true; });
        return loading;
    }

    function parseCsv(text) {
        var out = [];
        if (!text) return out;
        var lines = text.split(/\r?\n/);
        var re = /^([^,]+),(\d+),(\d+)(?:,"([^"]*)")?/;
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            if (!line) continue;
            var m = re.exec(line);
            if (!m) continue;
            var name = m[1];
            out.push({
                name: name,
                lower: name.toLowerCase(),
                type: parseInt(m[2], 10) || 0,
                count: parseInt(m[3], 10) || 0,
                aliases: m[4] ? m[4].toLowerCase().split(",").filter(Boolean) : []
            });
        }
        return out;
    }

    // ---- search -------------------------------------------------------------
    function search(query) {
        var q = query.trim().toLowerCase().replace(/\s+/g, "_");
        if (!q) return [];
        var res = [];
        var max = cfg.maxResults || 20;
        for (var i = 0; i < tags.length; i++) {
            var t = tags[i];
            var score = -1, matched = t.name;
            if (t.lower.indexOf(q) === 0) score = 0;
            else if (t.lower.indexOf(q) !== -1) score = 1;
            else if (cfg.searchAlias) {
                for (var j = 0; j < t.aliases.length; j++) {
                    var a = t.aliases[j];
                    if (a.indexOf(q) === 0) { score = 2; matched = t.name + " \u2190 " + a; break; }
                    if (a.indexOf(q) !== -1 && score < 0) { score = 3; matched = t.name + " \u2190 " + a; }
                }
            }
            if (score >= 0) res.push({ tag: t, score: score, label: matched });
        }
        res.sort(function (a, b) { return a.score - b.score || b.tag.count - a.tag.count; });
        return res.slice(0, max);
    }

    // ---- current tag word around the caret ----------------------------------
    function tagWord(ta) {
        var caret = ta.selectionStart || 0;
        var before = ta.value.slice(0, caret);
        var start = Math.max(before.lastIndexOf(","), before.lastIndexOf("\n")) + 1;
        return { text: before.slice(start), start: start, end: caret };
    }

    // ---- popup --------------------------------------------------------------
    function ensurePopup() {
        if (popup) return popup;
        injectStyle();
        popup = document.createElement("div");
        popup.id = "dte-tagcomplete-popup";
        popup.className = "dte-tac-popup";
        popup.style.display = "none";
        document.body.appendChild(popup);
        window.addEventListener("scroll", hidePopup, true);
        window.addEventListener("resize", hidePopup);
        return popup;
    }

    function renderPopup() {
        var p = ensurePopup();
        p.innerHTML = "";
        results.forEach(function (r, i) {
            var div = document.createElement("div");
            div.className = "dte-tac-item " + (TYPE_CLASS[r.tag.type] || "tac-type-0") + (i === activeIndex ? " active" : "");
            var name = document.createElement("span");
            name.className = "dte-tac-name";
            name.textContent = r.label;
            var count = document.createElement("span");
            count.className = "dte-tac-count";
            count.textContent = formatCount(r.tag.count);
            div.appendChild(name); div.appendChild(count);
            div.addEventListener("mousedown", function (e) { e.preventDefault(); insertResult(i); });
            div.addEventListener("mouseenter", function () { setActive(i); });
            p.appendChild(div);
        });
    }

    function formatCount(n) {
        if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
        if (n >= 1e3) return (n / 1e3).toFixed(1) + "k";
        return String(n);
    }

    function positionPopup(ta) {
        var rect = ta.getBoundingClientRect();
        var p = ensurePopup();
        p.style.display = "block";
        p.style.left = Math.max(4, rect.left) + "px";
        p.style.width = Math.max(240, rect.width) + "px";
        var ph = p.offsetHeight || 220;
        var top = rect.bottom + 2;
        if (top + ph > window.innerHeight - 4) top = Math.max(4, rect.top - ph - 2);
        p.style.top = top + "px";
    }

    function showPopup(ta) {
        activeTa = ta;
        renderPopup();
        positionPopup(ta);
    }

    function hidePopup() {
        if (popup) popup.style.display = "none";
        results = []; activeIndex = -1; activeTa = null;
    }

    function setActive(i) {
        activeIndex = i;
        if (!popup) return;
        var items = popup.children;
        for (var k = 0; k < items.length; k++) items[k].classList.toggle("active", k === i);
        if (items[i] && items[i].scrollIntoView) items[i].scrollIntoView({ block: "nearest" });
    }

    function refresh(ta) {
        if (!cfg.enabled || !loaded || !tags.length) { hidePopup(); return; }
        if (document.activeElement !== ta) { hidePopup(); return; }
        var w = tagWord(ta);
        if (!w.text.trim()) { hidePopup(); return; }
        results = search(w.text);
        if (!results.length) { hidePopup(); return; }
        activeIndex = 0;
        showPopup(ta);
    }

    // ---- insertion ----------------------------------------------------------
    function insertResult(i) {
        var ta = activeTa;
        if (!ta || !results[i]) return;
        var t = results[i].tag;
        var text = cfg.replaceUnderscores ? t.name.replace(/_/g, " ") : t.name;
        text = text.replace(/\(/g, "\\(").replace(/\)/g, "\\)");
        if (cfg.appendComma) text += ", ";
        var w = tagWord(ta);
        var after = ta.value.slice(w.end);
        ta.value = ta.value.slice(0, w.start) + text + after;
        var caret = w.start + text.length;
        ta.setSelectionRange(caret, caret);
        skipNextInput = true;
        ta.dispatchEvent(new Event("input", { bubbles: true }));
        ta.focus();
        hidePopup();
    }

    // ---- textarea wiring ----------------------------------------------------
    function attach(ta) {
        if (!ta || attached.has(ta)) return;
        attached.add(ta);
        var timer = null;
        ta.addEventListener("focus", function () { loadData(); });
        ta.addEventListener("input", function () {
            if (skipNextInput) { skipNextInput = false; return; }
            clearTimeout(timer);
            timer = setTimeout(function () {
                loadData().then(function () { if (!loadFailed) refresh(ta); });
            }, 90);
        });
        ta.addEventListener("keydown", function (e) {
            if (!popup || popup.style.display === "none" || !results.length) return;
            if (e.key === "ArrowDown") { e.preventDefault(); e.stopPropagation(); setActive((activeIndex + 1) % results.length); }
            else if (e.key === "ArrowUp") { e.preventDefault(); e.stopPropagation(); setActive((activeIndex - 1 + results.length) % results.length); }
            else if (e.key === "Enter" || e.key === "Tab") { e.preventDefault(); e.stopPropagation(); insertResult(activeIndex >= 0 ? activeIndex : 0); }
            else if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); hidePopup(); }
        });
        ta.addEventListener("blur", function () { setTimeout(function () { if (activeTa === ta) hidePopup(); }, 150); });
    }

    function attachAll() {
        var root = app();
        TARGET_IDS.forEach(function (id) {
            var el = root.getElementById ? root.getElementById(id) : document.getElementById(id);
            if (!el) return;
            var ta = el.tagName === "TEXTAREA" ? el : el.querySelector("textarea");
            if (ta) attach(ta);
        });
    }

    // ---- styles -------------------------------------------------------------
    function injectStyle() {
        if (document.getElementById("dte-tac-style")) return;
        var st = document.createElement("style");
        st.id = "dte-tac-style";
        st.textContent = [
            ".dte-tac-popup{position:fixed;z-index:100000;max-height:240px;overflow-y:auto;",
            "  background:#1f2937;border:1px solid #4b5563;border-radius:6px;",
            "  box-shadow:0 6px 18px rgba(0,0,0,.45);font-size:13px;font-family:ui-monospace,monospace;}",
            ".dte-tac-item{display:flex;justify-content:space-between;gap:10px;padding:3px 10px;cursor:pointer;white-space:nowrap;}",
            ".dte-tac-item.active{background:#374151;}",
            ".dte-tac-count{color:#9ca3af;font-size:11px;}",
            ".tac-type-0 .dte-tac-name{color:#87cefa;}",
            ".tac-type-1 .dte-tac-name{color:#f0a0a0;}",
            ".tac-type-3 .dte-tac-name{color:#c084fc;}",
            ".tac-type-4 .dte-tac-name{color:#6ee76e;}",
            ".tac-type-5 .dte-tac-name{color:#f0c060;}",
            ".dark .dte-tac-popup{background:#111827;border-color:#374151;}",
            ":root:not(.dark) .dte-tac-popup{background:#ffffff;border-color:#d1d5db;color:#111827;}",
            ":root:not(.dark) .dte-tac-item.active{background:#e5e7eb;}",
            ":root:not(.dark) .tac-type-0 .dte-tac-name{color:#0369a1;}",
            ":root:not(.dark) .tac-type-1 .dte-tac-name{color:#b91c1c;}",
            ":root:not(.dark) .tac-type-3 .dte-tac-name{color:#7e22ce;}",
            ":root:not(.dark) .tac-type-4 .dte-tac-name{color:#15803d;}",
            ":root:not(.dark) .tac-type-5 .dte-tac-name{color:#b45309;}"
        ].join("\n");
        document.head.appendChild(st);
    }

    // ---- bootstrap ----------------------------------------------------------
    function init() {
        attachAll();
        var obs = new MutationObserver(function () { attachAll(); });
        obs.observe(app(), { childList: true, subtree: true });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    // expose for debugging / tests
    window.dteTagComplete = { search: function (q) { return search(q); }, reload: function () { loaded = false; loadFailed = false; return loadData(); }, config: function () { return cfg; }, count: function () { return tags.length; } };
})();
