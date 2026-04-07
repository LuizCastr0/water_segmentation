import os

IGNORAR = {"__pycache__", "data"}

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if not d.startswith(".") and d not in IGNORAR]
    level = root.replace(".", "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    for f in files:
        fpath = os.path.join(root, f)
        size = os.path.getsize(fpath)
        size_str = f"{size/1024/1024:.1f}MB" if size > 1024*1024 else f"{size/1024:.0f}KB"
        print(f"{indent}  {f}  ({size_str})")