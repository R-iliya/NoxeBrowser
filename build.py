import PyInstaller.__main__
import os
import shutil

project_name = "NoxeBrowser"
main_script = "main.py"
icon_path = os.path.join("core", "icon.ico")

# Clean old builds
for target in ["build", "dist", f"{project_name}.spec"]:
    if os.path.exists(target):
        print(f"🧹 Removing old {target}...")
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)

PyInstaller.__main__.run([
    main_script,
    "--noconfirm",
    "--windowed",
    "--onefile",
    "--noupx",
    f"--icon={icon_path}",
    f"--name={project_name}",
    "--add-data=core;core",
    "--add-data=img;img",
    # 💥 Hidden imports to fix WebEngine errors
    "--hidden-import=PyQt5.QtWebEngineWidgets",
    "--hidden-import=PyQt5.QtWebEngineCore",
    "--hidden-import=PyQt5.QtWebEngine",
    "--hidden-import=PyQt5.QtWebChannel",
    "--hidden-import=PyQt5.QtWebEngineCore.QWebEngineProfile",
    "--collect-all=PyQt5",
    "--collect-all=PyQt5.QtWebEngineWidgets",
    "--collect-all=PyQt5.QtWebEngineCore",
    "--collect-all=PyQt5.QtWebEngine",
    "--collect-all=PyQt5.QtNetwork",
    "--collect-all=PyQt5.QtGui",
])

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n✅ Build complete!")
clear()

print(f"Check your dist folder for {project_name}.exe")
