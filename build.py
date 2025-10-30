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
    "--noupx",  # faster startup
    f"--icon={icon_path}",
    f"--name={project_name}",
    "--add-data=core;core",
    "--add-data=img;img",
    # Hidden imports for PyQt5 WebEngine
    "--hidden-import=PyQt5.QtWebEngineWidgets",
    "--hidden-import=PyQt5.QtWebEngineCore",
    "--hidden-import=PyQt5.QtWebChannel",
    # Only collect essential PyQt5 modules
    "--collect-submodules=PyQt5.QtWidgets",
    "--collect-submodules=PyQt5.QtGui",
    "--collect-submodules=PyQt5.QtCore",
    "--collect-submodules=PyQt5.QtWebEngineWidgets",
    "--collect-submodules=PyQt5.QtWebEngineCore",
    "--collect-submodules=PyQt5.QtWebChannel",
])

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("✅ Build complete!")
clear()

print(f"Check your dist folder for {project_name}.exe")
