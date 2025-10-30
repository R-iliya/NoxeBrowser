import PyInstaller.__main__
import os
import shutil

project_name = "NoxeBrowser"
main_script = "main.py"
icon_path = os.path.join("core", "icon.ico")

# Clean old builds
for folder in ["build", "dist", f"{project_name}.spec"]:
    if os.path.exists(folder):
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        else:
            os.remove(folder)

PyInstaller.__main__.run([
    main_script,
    "--noconfirm",
    "--windowed",
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

print("\n✅ Build complete!")
print(f"Check your dist folder for {project_name}.exe")
