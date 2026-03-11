# PATCH-ID: 2026-03-12-TA-PATCH-LIST-FILTER-01

import os
import shutil
from datetime import datetime

PATCH_ID = "2026-03-12-TA-PATCH-LIST-FILTER-01"


def _record_patch(base_path: str):
    patch_meta = os.path.join(base_path, "_patch_meta")
    history_dir = os.path.join(patch_meta, "PATCH_HISTORY")
    tracker_file = os.path.join(patch_meta, "PATCH_TRACKER.md")
    last_patch_file = os.path.join(patch_meta, "LAST_PATCH.md")

    os.makedirs(history_dir, exist_ok=True)

    history_path = os.path.join(history_dir, f"{PATCH_ID}.md")
    with open(history_path, "w", encoding="utf-8") as f:
        f.write(f"# {PATCH_ID}\n")
        f.write(f"Applied: {datetime.now()}\n")
        f.write("Target: server/static/js/front/app_main.js\n")
        f.write("Action: hide already-applied patches from patch list UI using recent patch history + LAST badge normalization\n")

    existing = ""
    if os.path.isfile(tracker_file):
        with open(tracker_file, "r", encoding="utf-8") as f:
            existing = f.read()

    line = f"- {PATCH_ID}"
    if line not in existing:
        with open(tracker_file, "a", encoding="utf-8") as f:
            if existing and not existing.endswith("\n"):
                f.write("\n")
            f.write(line + "\n")

    with open(last_patch_file, "w", encoding="utf-8") as f:
        f.write(PATCH_ID)


def apply_patch(base_path: str):
    target = os.path.join(base_path, "server", "static", "js", "front", "app_main.js")

    if not os.path.isfile(target):
        raise FileNotFoundError(f"target not found: {target}")

    with open(target, "r", encoding="utf-8") as f:
        src = f.read()

    marker = "// PATCH-ID: 2026-03-12-TA-PATCH-LIST-FILTER-01"
    if marker in src:
        print("PATCH SKIPPED: already applied", PATCH_ID)
        return

    injection = r"""

// PATCH-ID: 2026-03-12-TA-PATCH-LIST-FILTER-01
(function(){
  function _patchNormBase(name){
    let s = String(name || "").trim();
    if (!s) return "";

    s = s.replace(/^patch_/i, "");
    s = s.replace(/\.(patch\.)?py$/i, "");
    s = s.replace(/\.md$/i, "");
    s = s.replace(/^PATCH_NOTES_/i, "");

    // keep date part, normalize separators afterwards
    if (/^\d{4}-\d{2}-\d{2}[_-]/.test(s)) {
      s = s.slice(0, 10) + "-" + s.slice(11);
    }

    s = s.replace(/_/g, "-");
    s = s.replace(/-+/g, "-");
    s = s.replace(/^-+|-+$/g, "");
    return s.toUpperCase();
  }

  function _patchAppliedSet(){
    const out = new Set();

    // LAST badge text
    try {
      const badges = Array.from(document.querySelectorAll("body *"));
      badges.forEach(el => {
        const t = (el.textContent || "").trim();
        if (!t) return;
        const m = t.match(/LAST:\s*([A-Z0-9\-_]+)/i);
        if (m && m[1]) out.add(_patchNormBase(m[1]));
      });
    } catch(_e){}

    // recent patch history rows
    try {
      const rows = document.querySelectorAll("#patchHistoryBody tr");
      rows.forEach(tr => {
        const td = tr.querySelector("td");
        if (!td) return;
        const t = (td.textContent || "").trim();
        if (!t) return;
        out.add(_patchNormBase(t));
      });
    } catch(_e){}

    return out;
  }

  function _patchFilterListRows(){
    const tbody = document.querySelector("#patchListBody");
    if (!tbody) return;

    const applied = _patchAppliedSet();
    const rows = Array.from(tbody.querySelectorAll("tr"));
    let visible = 0;

    rows.forEach(tr => {
      const first = tr.querySelector("td");
      if (!first) return;

      const filename = (first.textContent || "").trim();
      if (!filename) return;

      const norm = _patchNormBase(filename);
      const isApplied = applied.has(norm);

      tr.style.display = isApplied ? "none" : "";
      if (!isApplied) visible += 1;
    });

    const oldEmpty = document.querySelector("#patchListFilteredEmpty");
    if (oldEmpty) oldEmpty.remove();

    if (rows.length > 0 and visible == 0):
      pass
  }

  function _patchEnsureEmptyState(){
    const tbody = document.querySelector("#patchListBody");
    if (!tbody) return;

    const rows = Array.from(tbody.querySelectorAll("tr"));
    const visibleRows = rows.filter(tr => tr.style.display !== "none");

    let oldEmpty = document.querySelector("#patchListFilteredEmpty");
    if (oldEmpty) oldEmpty.remove();

    if (rows.length > 0 && visibleRows.length === 0) {
      const tr = document.createElement("tr");
      tr.id = "patchListFilteredEmpty";
      tr.innerHTML = '<td colspan="3" style="padding:14px 12px; color:#7b7b7b;">이미 적용된 패치만 있어 표시할 항목이 없습니다.</td>';
      tbody.appendChild(tr);
    }
  }

  function applyPatchListFilter(){
    try {
      _patchFilterListRows();
      _patchEnsureEmptyState();
    } catch (e) {
      console.warn("[patch-list-filter] failed:", e);
    }
  }

  function wrapPatchPanelLoader(){
    try {
      if (window.__patchListFilterWrapped) return;
      window.__patchListFilterWrapped = true;

      if (typeof window.loadPatchPanel === "function") {
        const orig = window.loadPatchPanel;
        window.loadPatchPanel = async function(){
          const result = await orig.apply(this, arguments);
          setTimeout(applyPatchListFilter, 0);
          return result;
        };
      }
    } catch (e) {
      console.warn("[patch-list-filter] wrap failed:", e);
    }
  }

  function watchPatchDom(){
    try {
      if (window.__patchListFilterObserver) return;

      const listBody = document.querySelector("#patchListBody");
      const histBody = document.querySelector("#patchHistoryBody");
      if (!listBody && !histBody) return;

      const observer = new MutationObserver(function(){
        applyPatchListFilter();
      });

      if (listBody) observer.observe(listBody, { childList: true, subtree: true });
      if (histBody) observer.observe(histBody, { childList: true, subtree: true });

      window.__patchListFilterObserver = observer;
    } catch (e) {
      console.warn("[patch-list-filter] observer failed:", e);
    }
  }

  function bootPatchListFilter(){
    wrapPatchPanelLoader();
    watchPatchDom();
    setTimeout(applyPatchListFilter, 0);
    setTimeout(applyPatchListFilter, 150);
    setTimeout(applyPatchListFilter, 600);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootPatchListFilter);
  } else {
    bootPatchListFilter();
  }

  window.applyPatchListFilter = applyPatchListFilter;
})();
"""

    # fix accidental python-like fragment safeguard
    injection = injection.replace(
        """    if (rows.length > 0 and visible == 0):
      pass
""",
        ""
    )

    backup = target + f".bak.{PATCH_ID}"
    shutil.copyfile(target, backup)

    new_src = src.rstrip() + "\n" + injection + "\n"

    with open(target, "w", encoding="utf-8") as f:
        f.write(new_src)

    _record_patch(base_path)

    print("PATCH APPLIED:", PATCH_ID)
    print("TARGET:", target)
    print("BACKUP:", backup)
