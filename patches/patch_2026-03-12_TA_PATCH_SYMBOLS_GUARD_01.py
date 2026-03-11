# PATCH-ID: 2026-03-12-TA-PATCH-SYMBOLS-GUARD-01

import os
import shutil

PATCH_ID = "2026-03-12-TA-PATCH-SYMBOLS-GUARD-01"


def apply_patch(base_path: str):

    target = os.path.join(base_path,"server","static","js","front","app_main.js")

    if not os.path.isfile(target):
        raise FileNotFoundError(target)

    with open(target,"r",encoding="utf-8") as f:
        src = f.read()

    if PATCH_ID in src:
        print("PATCH SKIPPED")
        return

    backup = target + ".bak_" + PATCH_ID
    shutil.copyfile(target,backup)

    src = src.replace(
        "symbols.forEach(",
        "(Array.isArray(symbols)?symbols:[]).forEach("
    )

    with open(target,"w",encoding="utf-8") as f:
        f.write(src)

    print("PATCH APPLIED:",PATCH_ID)
