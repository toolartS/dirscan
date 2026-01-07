# tscodescan

**tscodescan** adalah *repository artifact generator* berbasis CLI.  
Tool ini dipakai untuk membaca struktur repo, merangkum isinya, dan (jika diminta)
menghasilkan **artifact teks** yang AI-friendly.

Project ini adalah evolusi dari `dirscan`, dengan fokus:
- deterministik
- artifact-first
- CLI sebagai source of truth

---

## Instalasi

```bash
pip install tscodescan
```

Atau mode development (editable):

```bash
git clone https://github.com/toolartS/tscodescan
cd tscodescan
pip install -e .
```

Command yang tersedia:
- `tscodescan`
- `tsc` (alias singkat)

---

## Penggunaan Dasar

### Default Scan (CLI only)

```bash
tsc [path]
```

Output **tidak membuat file**.  
Yang ditampilkan di CLI:

1. Tree struktur repo
2. Summary (komposisi file & bahasa)

Contoh:
```text
.
├── scan
│   └── cli.py
├── README.md
└── setup.py

SUMMARY:
- Python : 3 files
- Markdown : 1 file
```

---

## Mode Artifact (`-i`)

```bash
tsc -i [ID] [path]
```

- **Tanpa konfirmasi**
- Langsung membuat artifact
- Output file disimpan di:

```text
~/storage/downloads/Scan/<repo>/
```

Contoh:
```bash
tsc -i
tsc -i 2 ~/myrepo
```

Hasil:
```text
scan-myrepo.txt
scan-2-myrepo.txt
```

Isi artifact:
- Header repo
- Tree
- Full scan file (dengan ignore default, non-raw)

---

## Diagnose Mode (`-d`)

```bash
tsc -d [path]
```

Digunakan untuk diagnosis repository.

Yang dicek:
- Apakah repo Git
- Noise directory (`.git`, `Scan`)
- Ukuran repo (auto unit: B / KB / MB / GB)

Contoh output:
```text
=== TSCODESCAN DOCTOR ===

✔ Git repository detected
⚠ Noise: .git
⚠ Noise: Scan

Repo size: 1.12 MB
```
---

## Filosofi Desain

- CLI > GUI
- File artifact > chat ephemeral
- Deterministik > heuristik
- Satu command = satu makna

Tool ini **bukan sekadar scanner**, tapi
**alat komunikasi manusia ↔ AI berbasis artifact**.

---

## Lisensi

MIT License

