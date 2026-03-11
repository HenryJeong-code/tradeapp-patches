# PATCH-ID: 2026-03-12-TA-PATCH-STATUS-AI-POLICY-GUARD-02

import os
import shutil
from datetime import datetime

PATCH_ID = "2026-03-12-TA-PATCH-STATUS-AI-POLICY-GUARD-02"


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
        f.write("Target: server/app.py\n")
        f.write("Action: guard ai_policy_meta to prevent /status NameError 500\n")

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
    target = os.path.join(base_path, "server", "app.py")

    if not os.path.isfile(target):
        raise FileNotFoundError(f"target not found: {target}")

    with open(target, "r", encoding="utf-8") as f:
        src = f.read()

    marker = "# PATCH-ID: 2026-03-12-TA-PATCH-STATUS-AI-POLICY-GUARD-02"
    if marker in src:
        print("PATCH SKIPPED: already applied", PATCH_ID)
        return

    backup = target + f".bak.{PATCH_ID}"
    shutil.copyfile(target, backup)

    guard = """# PATCH-ID: 2026-03-12-TA-PATCH-STATUS-AI-POLICY-GUARD-02
try:
    ai_policy_meta
except NameError:
    ai_policy_meta = {}

"""

    new_src = guard + src

    with open(target, "w", encoding="utf-8") as f:
        f.write(new_src)

    _record_patch(base_path)

    print("PATCH APPLIED:", PATCH_ID)
    print("TARGET:", target)
    print("BACKUP:", backup)
