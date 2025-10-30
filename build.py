import PyInstaller.__main__
import os
import shutil
import sys

# === CONFIG ===
project_name = "NoxeBrowser"
main_script = "main.py"
icon_path = os.path.join("core", "icon.ico")
use_onefile = False  # ⬅️ Set to True for single EXE (slower startup)
use_upx = True       # ⬅️ Compress binaries if UPX is installed
upx_path = r"C:\upx"  # ⬅️ Change to your UPX folder if available

# === CLEAN OLD BUILDS ===
for target in ["build", "dist", f"{project_name}.spec"]:
    if os.path.exists(target):
        print(f"🧹 Removing old {target}...")
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)

# === BUILD OPTIONS ===
options = [
    main_script,
    "--noconfirm",
    "--windowed",
    f"--icon={icon_path}",
    f"--name={project_name}",
    "--add-data=core;core",
    "--add-data=img;img",
    "--hidden-import=PyQt5.QtWebEngineWidgets",
    "--hidden-import=PyQt5.QtWebEngineCore",
    "--hidden-import=PyQt5.QtWebEngine",
    "--hidden-import=PyQt5.QtWebChannel",
    "--collect-all=PyQt5",
    "--collect-all=PyQt5.QtWebEngineWidgets",
    "--collect-all=PyQt5.QtWebEngineCore",
    "--collect-all=PyQt5.QtWebEngine",
    "--collect-all=PyQt5.QtNetwork",
    "--collect-all=PyQt5.QtGui",
]

# === Optional flags ===
if use_onefile:
    options.append("--onefile")

if use_upx and os.path.exists(upx_path):
    options.append(f"--upx-dir={upx_path}")

# === RUN PYINSTALLER ===
print("🚀 Building", project_name, "...\n")
PyInstaller.__main__.run(options)

# === POST-BUILD INFO ===
exe_path = os.path.join("dist", f"{project_name}.exe" if use_onefile else project_name)
print("\n✅ Build complete!")
print(f"📁 Output: {os.path.abspath(exe_path)}")
print(f"⚙️ Mode: {'Single-file (slower startup)' if use_onefile else 'Folder (fast startup)'}")
if use_upx and not os.path.exists(upx_path):
    print("⚠️ UPX not found — skipping compression.")
