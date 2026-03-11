# PATCH-ID: 2026-03-11-TA-PATCH-ENGINE-V1-INIT

import os
from datetime import datetime

PATCH_ID = "2026-03-11-TA-PATCH-ENGINE-V1-INIT"


def apply_patch(base_path):

    patch_meta = os.path.join(base_path, "_patch_meta")

    history_dir = os.path.join(patch_meta, "PATCH_HISTORY")
    tracker_file = os.path.join(patch_meta, "PATCH_TRACKER.md")
    last_patch_file = os.path.join(patch_meta, "LAST_PATCH.md")

    os.makedirs(history_dir, exist_ok=True)

    history_path = os.path.join(history_dir, f"{PATCH_ID}.md")

    with open(history_path, "w", encoding="utf-8") as f:
        f.write(f"# {PATCH_ID}\n")
        f.write(f"Applied: {datetime.now()}\n")

    with open(tracker_file, "a", encoding="utf-8") as f:
        f.write(f"\n- {PATCH_ID}")

    with open(last_patch_file, "w", encoding="utf-8") as f:
        f.write(PATCH_ID)

    print("PATCH APPLIED:", PATCH_ID)
