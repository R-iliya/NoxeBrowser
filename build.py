import PyInstaller.__main__
import os
import shutil
import zipfile

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

# Run PyInstaller
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

# Clear console and notify build completion
os.system('cls' if os.name == 'nt' else 'clear')
print("✅ Build complete!")
print(f"Check your dist folder for {project_name}.exe")

# Ask for version name and create ZIP
print("Enter version name (e.g., v1.0): ")
vname = input(">>").strip()
if vname:
    zip_filename = f"{project_name}_{vname}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        dist_path = "dist"
        for root, dirs, files in os.walk(dist_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_path)
                zipf.write(file_path, arcname)
    print(f"📦 Dist folder zipped as {zip_filename}")
else:
    print("⚠️ No version name entered. Skipping ZIP creation.")
