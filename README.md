# Gonggi: Recess — kanji / hanzi stroke data

Stroke centerlines that the game's handwriting (name tags, dictation notebook, chalkboard) uses to write Chinese characters.

| File | Characters | Source |
|---|---|---|
| `hanzi-ja.bytes` | 7,070 (Japanese forms) | AnimCJK `graphicsJa.txt` |
| `hanzi-zh.bytes` | 8,001 (Simplified Chinese forms) | AnimCJK `graphicsZhHans.txt` |
| `hanzi-more.bytes` | 818 (Traditional and rare characters missing from both files above) | Make Me a Hanzi `graphics.txt` |

## What was changed

Made by `build_hanzi.py` from AnimCJK (https://github.com/parsimonhi/animCJK), commit `3e1253b341cc7be14c3540bb3c045e6163557777`, and Make Me a Hanzi (https://github.com/skishore/makemeahanzi), commit `bddc96d41bef78427ed0e034e9f7e31d71fd1b92`:

- kept only the stroke centerlines (`medians`), dropped the outlines (`strokes`)
- from Make Me a Hanzi, kept only characters missing from both AnimCJK files
- kept only BMP CJK ideographs (U+4E00–9FFF, U+3400–4DBF, U+F900–FAFF) and 々〆〇
- scaled coordinates from the 1024 box (y up, bottom −124) to 0..1 and quantized to 8 bits, removed repeated points
- packed into a small binary format (described at the top of `build_hanzi.py`); each file starts with a notice saying the same

Rebuild: `python build_hanzi.py <animCJK folder> <makemeahanzi folder> [--animcjk-commit C] [--mmah-commit C]`

## License

The original `graphics*.txt` files are derived from the Arphic PL KaitiM / UKai fonts, and are licensed under the **Arphic Public License** (`ARPHICPL.TXT`). These modified files are released under the same license, free of charge to everyone.

AnimCJK: Copyright 2016-2026 FM&SH. Make Me a Hanzi: Shaunak Kishore. Arphic fonts: Copyright (C) 1999 Arphic Technology Co., Ltd.

The game itself is a separate work and is not covered by this license.
