__version__ = "0.2.0"

def scan_debug_errors(root):
    import os, re

    pattern = re.compile(r"([\w./-]+)[: ]+(line )?(\d+)", re.I)
    results = []

    for name in os.listdir(root):
        if "error" in name.lower() and name.endswith((".log", ".txt")):
            path = os.path.join(root, name)
            try:
                for line in open(path, errors="ignore"):
                    m = pattern.search(line)
                    if m:
                        results.append({
                            "source": name,
                            "file": m.group(1),
                            "line": int(m.group(3)),
                            "raw": line.strip()
                        })
            except:
                pass

    return results

import os, sys, argparse, platform
from datetime import datetime

DEFAULT_EXT = {".txt",".md",".py",".php",".js",".html",".css",".json",".sql"}
DEFAULT_EXCLUDE = {".git","node_modules","vendor","__pycache__"}

def get_scan_workspace(repo):
    base = os.path.join(get_download_dir(), "Scan")
    path = os.path.join(base, repo)
    os.makedirs(path, exist_ok=True)
    return path

def get_download_dir():

    # Detect Termux explicitly
    if os.path.exists("/data/data/com.termux"):
        return os.path.expanduser("~/storage/downloads")

    system = platform.system().lower()

    if system == "linux":
        return os.path.expanduser("~/Downloads")

    if system == "windows":
        return os.path.join(os.environ.get("USERPROFILE", ""), "Downloads")

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
    p = argparse.ArgumentParser(prog="tscodescan")
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
    p.add_argument("--state", nargs="?", const="current", help="State snapshot")
    p.add_argument("--debug", action="store_true", help="Detect runtime errors and generate debug receipt")
    args = p.parse_args()

    # =========================
    # DEBUG MODE (exclusive)
    # =========================
    if args.debug:

        root = os.getcwd()
        repo = os.path.basename(root)
        errors = scan_debug_errors(root)

        if not errors:
            print("[OK] No runtime errors detected")
            return

        out_dir = get_scan_workspace(repo)
        out_file = os.path.join(out_dir, f"debug-{repo}.txt")

        with open(out_file, "w", encoding="utf-8", errors="ignore") as out:
            out.write("=== TSCODESCAN DEBUG RECEIPT ===\n")
            out.write(f"Repo    : {repo}\n")
            out.write(f"Path    : {root}\n")
            out.write(f"Created : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.write("\n----------------------------------\n")

            for e in errors:
                out.write("\n[ERROR]\n")
                out.write(f"Source : {e['source']}\n")
                out.write(f"Line   : {e['raw']}\n")

                try:
                    target = os.path.join(root, e["file"])
                    lines = open(target, errors="ignore").read().splitlines()
                    ln = e["line"] - 1
                    start = max(0, ln - 10)
                    end = min(len(lines), ln + 10)

                    out.write("\n[CONTEXT]\n")
                    for i in range(start, end):
                        mark = ">>" if i == ln else "  "
                        out.write(f"{mark} {i+1}: {lines[i]}\n")
                except:
                    out.write("[CONTEXT UNAVAILABLE]\n")

        print("[OK] Debug receipt generated")
        print("[OUTPUT]", out_file)
        return


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

    name = args.name or f"tscodescan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    repo = os.path.basename(root)
    out_dir = get_scan_workspace(repo)

    if args.state:
        if args.state == "current":
            out_file = os.path.join(out_dir, f"state-{repo}.txt")
        else:
            out_file = os.path.join(out_dir, f"state-{args.state}-{repo}.txt")
    else:
        out_file = os.path.join(out_dir, f"{repo}.txt")


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

    print("[OK] tscodescan completed")
    print("[OUTPUT]", out_file)

if __name__ == "__main__":
    main()