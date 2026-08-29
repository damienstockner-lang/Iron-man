#!/usr/bin/env python3
import sys
import os
import zipfile
import shutil

def build():
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    # Create zipapp bundle
    bundle_path = os.path.join(dist_dir, "friday.pyz")
    with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write("friday_assistant/__main__.py", "__main__.py")
        for root, dirs, files in os.walk("friday_assistant"):
            for file in files:
                if file.endswith('.pyc') or '__pycache__' in root:
                    continue
                filepath = os.path.join(root, file)
                arcname = filepath
                zf.write(filepath, arcname)
    
    # Create standalone launcher
    launcher = os.path.join(dist_dir, "friday")
    with open(launcher, 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('import sys\n')
        f.write('sys.path.insert(0, ".")\n')
        f.write('from friday_assistant.cli import main\n')
        f.write('sys.exit(main())\n')
    os.chmod(launcher, 0o755)
    
    print(f"Build complete: {bundle_path}")
    print(f"Launcher: {launcher}")
    print("\nTo install:")
    print("  cp dist/friday /usr/local/bin/friday")
    print("  pip install -r requirements.txt")
    print("\nOr run directly:")
    print("  python3 dist/friday.pyz --help")

if __name__ == "__main__":
    build()
