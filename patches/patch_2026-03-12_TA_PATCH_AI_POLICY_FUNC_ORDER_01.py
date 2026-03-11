# PATCH-ID: 2026-03-12-TA-PATCH-AI-POLICY-FUNC-ORDER-01

import os
import shutil

PATCH_ID = "2026-03-12-TA-PATCH-AI-POLICY-FUNC-ORDER-01"


def apply_patch(base_path: str):

    target = os.path.join(base_path, "server", "app.py")

    if not os.path.isfile(target):
        raise FileNotFoundError(target)

    with open(target, "r", encoding="utf-8") as f:
        src = f.read()

    if PATCH_ID in src:
        print("PATCH SKIPPED")
        return

    backup = target + ".bak_" + PATCH_ID
    shutil.copyfile(target, backup)

    guard_func = '''
# PATCH-ID: 2026-03-12-TA-PATCH-AI-POLICY-FUNC-ORDER-01
def _ai_policy_meta(st=None):
    try:
        return st.get("ai_policy_meta", {}) if isinstance(st, dict) else {}
    except Exception:
        return {}
'''

    marker = "if __name__ == \"__main__\":"

    if marker not in src:
        raise RuntimeError("main marker not found")

    new_src = src.replace(marker, guard_func + "\n\n" + marker)

    with open(target, "w", encoding="utf-8") as f:
        f.write(new_src)

    print("PATCH APPLIED:", PATCH_ID)
