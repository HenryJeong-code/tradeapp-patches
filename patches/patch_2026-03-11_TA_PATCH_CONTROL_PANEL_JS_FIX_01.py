# PATCH-ID: 2026-03-11-TA-PATCH-CONTROL-PANEL-JS-FIX-01

import os
import re
import shutil
from datetime import datetime

PATCH_ID = "2026-03-11-TA-PATCH-CONTROL-PANEL-JS-FIX-01"


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
        f.write("Action: replace broken setView() block with safe patch-panel aware version\n")

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

    # broken block: setView(...) ~ Coin tabs comment
    pattern = re.compile(
        r'function setView\(view, symbol=null\)\{.*?\n\s*// -------------------------\n\s*// Coin tabs \(Upbit-ish\)',
        re.S
    )

    replacement = """function setView(view, symbol=null){
    const prev = currentView;

    if (prev === "analysis" && view !== "analysis"){
      try{
        window.ViewAnalysis && window.ViewAnalysis.stop && window.ViewAnalysis.stop();
      }catch(_e){}
    }

    currentView = view;
    if (view === "coin") currentSymbol = symbol;

    $$(".view").forEach(v => v.classList.remove("is-active"));

    const map = {
      dashboard:"#view-dashboard",
      analysis:"#view-analysis",
      coin:"#view-coin",
      trades:"#view-trades",
      decisions:"#view-decisions",
      settings:"#view-settings",
      ops:"#view-ops",
      patches:"#view-patches",
      dossier:"#view-dossier"
    };

    const el = $(map[view]);
    if (el) el.classList.add("is-active");

    // sidebar active styles
    $$(".sb-item").forEach(b => b.classList.remove("is-active"));
    if (view === "dashboard"){
      const dashBtn = document.querySelector('.sb-item[data-view="dashboard"]');
      if (dashBtn) dashBtn.classList.add("is-active");
    } else {
      const btn = document.querySelector(`.sb-item[data-view="${view}"]`);
      if (btn) btn.classList.add("is-active");
    }

    // coin list active
    $$(".coin-item").forEach(b => b.classList.remove("is-active"));
    if (view === "coin" && symbol){
      const cbtn = document.querySelector(`.coin-item[data-symbol="${symbol}"]`);
      if (cbtn) cbtn.classList.add("is-active");
    }

    // update hash (SPA)
    try{
      if (view === "coin" && symbol){
        location.hash = `#coin:${symbol}`;
      } else {
        location.hash = `#${view}`;
      }
    }catch(_e){}

    // settings
    if (view === "settings"){
      try{
        window.ViewSettings && window.ViewSettings.bind && window.ViewSettings.bind({ postJson, tick });
      }catch(_e){}
    }

    // ops
    if (view === "ops"){
      try{ window.ViewOpsReport && window.ViewOpsReport.bind && window.ViewOpsReport.bind(); }catch(_e){}
      try{ window.ViewOpsReport && window.ViewOpsReport.refresh && window.ViewOpsReport.refresh(); }catch(_e){}
    }

    // patches
    if (view === "patches"){
      bindPatchViewOnce();
      loadPatchPanel();
    }

    // render current
    renderAll();
  }

  // -------------------------
  // Coin tabs (Upbit-ish)"""

    new_src, count = pattern.subn(replacement, src, count=1)

    if count != 1:
        raise RuntimeError("setView() replacement failed: target block not found exactly once")

    # small safety: if hash whitelist somehow lacks patches, add it
    old_hash = "[ 'dashboard','analysis','trades','decisions','settings','ops','dossier' ]"
    new_hash = "[ 'dashboard','analysis','trades','decisions','settings','ops','patches','dossier' ]"
    if old_hash in new_src and new_hash not in new_src:
        new_src = new_src.replace(old_hash, new_hash)

    backup = target + f".bak.{PATCH_ID}"
    shutil.copyfile(target, backup)

    with open(target, "w", encoding="utf-8") as f:
        f.write(new_src)

    _record_patch(base_path)

    print("PATCH APPLIED:", PATCH_ID)
    print("TARGET:", target)
    print("BACKUP:", backup)
