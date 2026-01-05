import os, sys, argparse, platform
from datetime import datetime

DEFAULT_EXT = {".txt",".md",".py",".php",".js",".html",".css",".json",".sql"}
DEFAULT_EXCLUDE = {".git","node_modules","vendor","__pycache__"}

def get_download_dir():
    system = platform.system().lower()
    if "android" in system:
        return os.path.expanduser("~/storage/downloads")
    if system == "linux":
        return os.path.expanduser("~/Downloads")
    if system == "windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    return os.getcwd()

def build_tree(root, exclude):
    lines = []
    dir_count = file_count = 0

    def walk(path, prefix=""):
        nonlocal dir_count, file_count
        try:
            items = sorted(os.listdir(path))
        except PermissionError:
            return

        for i, name in enumerate(items):
            if name in exclude:
                continue
            full = os.path.join(path, name)
            connector = "└── " if i == len(items)-1 else "├── "
            if os.path.isdir(full) and not os.path.islink(full):
                dir_count += 1
                lines.append(prefix + connector + name)
                walk(full, prefix + ("    " if i == len(items)-1 else "│   "))
            else:
                file_count += 1
                if os.path.islink(full):
                    lines.append(prefix + connector + f"{name} -> {os.readlink(full)}")
                else:
                    lines.append(prefix + connector + name)

    lines.append(".")
    walk(root)
    lines.append(f"\n{dir_count} directories, {file_count} files")
    return "\n".join(lines)

def scan_files(root, exts, exclude):
    for r, d, f in os.walk(root):
        d[:] = [x for x in d if x not in exclude]
        for file in f:
            if file.startswith("dirscan_"):
                continue
            ext = os.path.splitext(file)[1].lower()
            if ext in exts:
                yield os.path.join(r, file)

def main():
    p = argparse.ArgumentParser(prog="dirscan")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--ext")
    p.add_argument("--exclude")
    p.add_argument("--name")
    p.add_argument("--to")
    p.add_argument("--cwd", action="store_true")
    p.add_argument("--tree", action="store_true")
    p.add_argument("--tree-f", action="store_true")
    p.add_argument("--summary", action="store_true")
    p.add_argument("--grep")
    p.add_argument("--markdown", action="store_true")
    args = p.parse_args()

    root = os.path.abspath(args.path)
    exts = set(f".{x.strip()}" for x in args.ext.split(",")) if args.ext else DEFAULT_EXT
    exclude = set(args.exclude.split(",")) if args.exclude else DEFAULT_EXCLUDE

    # TREE CLI MODE
    if args.tree:
        print(build_tree(root, exclude))
        return

    # GREP MODE
    if args.grep:
        for f in scan_files(root, exts, exclude):
            try:
                if args.grep in open(f, errors="ignore").read():
                    print(os.path.relpath(f, root))
            except:
                pass
        return

    # OUTPUT PATH
    out_dir = os.getcwd() if args.cwd else (args.to or get_download_dir())
    os.makedirs(out_dir, exist_ok=True)

    name = args.name or f"dirscan_{os.path.basename(root)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    out_file = os.path.join(out_dir, name)

    with open(out_file, "w", encoding="utf-8", errors="ignore") as out:
        out.write("=== PROJECT TREE ===\n")
        out.write(root + "\n\n")
        out.write(build_tree(root, exclude))
        out.write("\n\n=== FILE CONTENTS ===\n\n")

        for f in scan_files(root, exts, exclude):
            out.write(f"\n=== FILE: {os.path.relpath(f, root)} ===\n")
            try:
                content = open(f, errors="ignore").read()
                out.write(f"```{os.path.splitext(f)[1][1:]}```\n" if args.markdown else "")
                out.write(content)
                out.write("\n```" if args.markdown else "")
            except:
                out.write("[ERROR READING FILE]\n")

    print("[OK] dirscan completed")
    print("[OUTPUT]", out_file)

if __name__ == "__main__":
    main()
