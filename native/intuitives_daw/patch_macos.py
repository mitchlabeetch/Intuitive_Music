import os
import sys

path = 'intlib/lib/path/macos.py'
if not os.path.exists(path):
    print(f"File not found: {path}")
    sys.exit(1)

with open(path, 'r') as f:
    content = f.read()

old_block = """    INSTALL_PREFIX = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            *(['..'] * 3),
        ),
    )"""

new_block = """    is_frozen = getattr(sys, 'frozen', False)
    if is_frozen and "Contents/MacOS" in sys.executable:
        # PyInstaller .app bundle
        # sys.executable is .../Contents/MacOS/Intuitives
        # Resources are in .../Contents/Resources
        INSTALL_PREFIX = os.path.abspath(
            os.path.join(
                os.path.dirname(sys.executable),
                "..",
                "Resources"
            )
        )
    else:
        # PyInstaller one-dir or other frozen modes not in .app bundle
        INSTALL_PREFIX = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                *(['..'] * 3),
            ),
        )"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(path, 'w') as f:
        f.write(content)
    print("Updated macos.py")
else:
    print("Could not find block to replace")
    # Print content for debugging
    print(content)
    sys.exit(1)
