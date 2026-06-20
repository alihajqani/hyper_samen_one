"""Package هایپرمارکت ثامن into a one-folder executable with PyInstaller.

One-folder (not one-file) so the bundled logo/font are inside the app, while the
runtime files the operator manages — ``.env``, the inventory ``.xlsx``, and the
daily ``YYYYMMDD.log`` files — sit next to the executable.

Usage:
    python tools/build_exe.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "hyper_samen_one"


def _add_data(src: str, dest: str) -> str:
    sep = ";" if os.name == "nt" else ":"
    return f"{(ROOT / src)}{sep}{dest}"


def build() -> int:
    sys.path.insert(0, str(ROOT))
    from app.__version__ import __version__

    datas = [
        _add_data("data/logo.png", "data"),
        _add_data("app/frontend/assets", "app/frontend/assets"),
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(ROOT / "main.py"),
        "--name", APP_NAME,
        "--noconfirm", "--clean",
        "--windowed",
        "--distpath", str(ROOT / "dist"),
        "--workpath", str(ROOT / "build"),
        "--specpath", str(ROOT / "build"),
    ]
    for d in datas:
        cmd += ["--add-data", d]

    icon = ROOT / "data" / "app.ico"
    if icon.exists():
        cmd += ["--icon", str(icon)]

    print(f"ساخت نسخهٔ {__version__} برای {sys.platform} …")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        return result.returncode

    out = ROOT / "dist" / APP_NAME
    # Provide a starter .env next to the binary if none exists.
    example = ROOT / ".env.example"
    target_env = out / ".env"
    if example.exists() and not target_env.exists():
        shutil.copy(example, target_env)

    print("\nساخت با موفقیت انجام شد.")
    print(f"خروجی: {out}")
    print("یادآوری: فایل .env را کنار فایل اجرایی پر کنید و فایل موجودی را در پوشهٔ data قرار دهید.")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
