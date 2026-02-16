import PyInstaller.__main__
import os
import shutil
import zipfile

project_name = "NoxeBrowser"
main_script = "main.py"
icon_path = os.path.join("core", "icon.ico")
extra_folders = ["core", "img"]  # folders to copy into dist and zip

# Clean previous builds
for target in ["build", "dist", f"{project_name}.spec"]:
    if os.path.exists(target):
        print(f"🧹 Removing old {target}...")
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)

# Build the executable with PyInstaller
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
    "--collect-submodules=PyQt5.QtWebEngineWidgets",
    "--collect-submodules=PyQt5.QtWebEngineCore",
    "--collect-submodules=PyQt5.QtWebChannel",
    "--exclude-module=tests",
    "--exclude-module=tkinter",
    "--exclude-module=pydoc",
    "--exclude-module=distutils",
    "--strip",
])

# print build success message and instructions
print("\n" + "="*50)
print("✅ Build complete!")
print(f"Check your dist folder for {project_name}.exe")
print("="*50 + "\n")


# Copy extra folders (core and img) into dist for the executable to access, and then create a ZIP of the dist folder for easy distribution.
dist_path = "dist"
for folder in extra_folders:
    src = folder
    dst = os.path.join(dist_path, folder)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"📁 Copied {folder} into dist folder")

# Ask for version name and create ZIP.
print("📁 Enter version name (e.g., v1.0): ")
vname = input(">>").strip()
if vname:
    zip_filename = f"{project_name}_{vname}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk only the dist folder, including copied core and img.
        for root, dirs, files in os.walk(dist_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, dist_path)
                zipf.write(file_path, arcname)
    print(f"📦 Dist folder zipped as {zip_filename}")
else:
    print("⚠️ No version name entered. Skipping ZIP creation.")
