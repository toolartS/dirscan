
import argparse
import os
import datetime
from collections import Counter
from pathlib import Path

IGNORE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "build", "dist",
    ".egg-info", ".mypy_cache", ".pytest_cache"
}

SOURCE_EXTS = {
    ".py", ".js", ".ts", ".html", ".css", ".md",
    ".json", ".yml", ".yaml", ".toml", ".ini", ".sh"
}

BINARY_EXTS = {".zip", ".tar", ".gz", ".whl", ".apk", ".exe", ".bin"}

def human_size(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

def build_tree(root):
    lines = []
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        level = base.replace(root, "").count(os.sep)
        indent = "  " * level
        lines.append(f"{indent}{os.path.basename(base) or base}/")
        for f in files:
            lines.append(f"{indent}  {f}")
    return "\n".join(lines)

def analyze_repo(root):
    counter = Counter()
    total = 0
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            ext = Path(f).suffix.lower() or "noext"
            counter[ext] += 1
            total += 1
    return counter, total

def infer_identity(counter):
    if counter.get(".py", 0) > 0:
        return "Python Package"
    if counter.get(".html", 0) + counter.get(".css", 0) > 5:
        return "Web Project"
    return "Source Code Repository"

def diagnose_repo(root):
    out = []
    if (Path(root) / ".git").exists():
        out.append("✔ Git repository detected")
    else:
        out.append("✖ Not a git repository")

    for d in ["build", "dist", ".venv", ".git"]:
        if (Path(root) / d).exists():
            out.append(f"⚠ Noise: {d}")

    size = sum(
        f.stat().st_size
        for f in Path(root).rglob("*")
        if f.is_file() and ".git" not in f.parts
    )
    out.append(f"Repo size: {human_size(size)}")
    return "\n".join(out)

def collect_files(root, raw=False):
    files = []
    for base, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in fs:
            p = Path(base) / f
            if p.suffix.lower() in BINARY_EXTS:
                continue
            if not raw and p.suffix.lower() not in SOURCE_EXTS:
                continue
            files.append(p)
    return files

def write_artifact(root, repo, tree, summary, diagnose, files, raw, idtag):
    outdir = Path.home() / "storage" / "downloads" / "Scan" / repo
    outdir.mkdir(parents=True, exist_ok=True)

    name = "scan"
    if raw:
        name += "-raw"
    if idtag:
        name += f"-{idtag}"
    name += f"-{repo}.txt"

    out = outdir / name
    with out.open("w", errors="ignore") as o:
        o.write("========================================\n")
        o.write(f"ARTIFACT: {repo}\n")
        o.write(f"MODE: {'raw' if raw else 'standard'}\n")
        o.write(f"GENERATED: {datetime.datetime.now()}\n")
        o.write("========================================\n\n")

        o.write("TREE\n-----\n")
        o.write(tree + "\n\n")

        o.write("SUMMARY\n-------\n")
        o.write(summary + "\n\n")

        o.write("DIAGNOSE\n--------\n")
        o.write(diagnose + "\n\n")

        o.write("CONTEXT (SOURCE)\n----------------\n")
        for f in files:
            o.write(f"\n=== {f.relative_to(root)} ===\n")
            try:
                o.write(f.read_text(errors="ignore"))
            except Exception:
                o.write("[READ ERROR]\n")

    print(f"[OK] Artifact created: {out}")

def main():
    p = argparse.ArgumentParser("tsc")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("-i", nargs="?", const=True)
    p.add_argument("-r", action="store_true")
    args = p.parse_args()

    root = os.path.abspath(args.path)
    repo = os.path.basename(root)

    tree = build_tree(root)
    counter, total = analyze_repo(root)
    identity = infer_identity(counter)

    summary = (
        "# =============================================\n"
        "# TSCODESCAN SUMMARY\n"
        "# =============================================\n\n"
        "Identity:\n"
        f"- {identity}\n\n"
        "Language Composition:\n"
        + "\n".join(
            f"- {k:8} : {v} files ({int(v/total*100)}%)"
            for k, v in counter.most_common()
        )
        + "\n\nDocumentation Signals:\n"
        "- README.md\n"
        "- Instalasi\n"
        "- Penggunaan Dasar\n"
        "- Filosofi Desain\n"
        "- Lisensi"
    )

    diagnose = diagnose_repo(root)

    if not args.i:
        print(tree)
        print(summary)
        print("\nDIAGNOSE:")
        print(diagnose)
        return

    files = collect_files(root, raw=args.r)
    idtag = None if args.i is True else args.i
    write_artifact(root, repo, tree, summary, diagnose, files, args.r, idtag)

if __name__ == "__main__":
    main()
