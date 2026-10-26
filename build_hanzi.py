# 한자 손글씨 획 자료 짓기: AnimCJK·Make Me a Hanzi의 graphics 파일에서 획 중심선(medians)만 뽑아 HandFont가 읽는 작은 파일로.
# 사용: python Tools/handfont/build_hanzi.py <animCJK 폴더> <makemeahanzi 폴더> [--animcjk-commit C] [--mmah-commit C]
#   animCJK 폴더에는 graphicsJa.txt · graphicsZhHans.txt, makemeahanzi 폴더에는 graphics.txt가 있어야 한다.
#   폴더가 git 저장소면 커밋을 스스로 읽는다.
# 결과: (game) Assets/Resources/HandFont/
#   hanzi-ja.bytes   일본어 꼴 (AnimCJK svgsJa)
#   hanzi-zh.bytes   간체 꼴 (AnimCJK svgsZhHans)
#   hanzi-more.bytes 위 둘에 없는 글자만 (Make Me a Hanzi: 간체·번체)
#
# 원본 graphics 파일은 Arphic Public License(APL)다. 결과 파일은 그 "고친 것"이라 APL을 따르고,
# 파일 머리에 무엇을 언제 고쳤는지 적는다(APL 2a). 공개 자리와 라이선스 글은 같은 폴더의 README.md.
#
# 꼴 (little endian):
#   "HFZ1", u16 머리글 길이, 머리글(UTF-8), u16 글자 수 n,
#   u16 글자[n] (오름차순), u32 자리[n] (글자 자료 시작, 자료 묶음 안에서), 자료 묶음
#   글자 자료: u8 획 수, 획마다 u8 점 수, 점마다 u8 x, u8 y (0..255 = 칸 0..1, y 위쪽)

import argparse
import json
import os
import struct
import subprocess
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'Assets', 'Resources', 'HandFont')


def wanted(c):
    """HandFont가 이 자료로 그릴 글자: BMP 한자(통합·확장 A·호환)와 々〆〇. 가나·부수·획 조각은 뺀다."""
    o = ord(c)
    return (0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF or 0xF900 <= o <= 0xFAFF
            or c in '々〆〇')


def q(v):
    return max(0, min(255, round(v * 255)))


def glyph(medians):
    # 두 자료 모두 1024 칸, y 위쪽, 아래 끝이 -124
    b = bytearray([len(medians)])
    for m in medians:
        pts = [(q(x / 1024), q((y + 124) / 1024)) for x, y in m]
        # 8비트로 줄여 겹친 점은 뺀다
        out = [pts[0]] + [p for i, p in enumerate(pts[1:]) if p != pts[i]]
        if len(out) == 1:
            out.append(out[0])
        b.append(len(out))
        for x, y in out:
            b += bytes((x, y))
    return bytes(b)


def read(path):
    chars = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            c = d['character']
            if len(c) == 1 and wanted(c):
                chars[c] = glyph(d['medians'])
    return chars


def write(chars, out_name, source):
    keys = sorted(chars, key=ord)
    notice = (f"Stroke centerlines (medians) for {len(keys)} characters, taken from {source} "
              f"and modified by NangmanGames on {date.today().isoformat()}: outlines dropped, "
              f"coordinates scaled to 0..1 and quantized to 8 bits, repeated points removed, packed into this binary format. "
              f"Licensed under the Arphic Public License (see ARPHICPL.TXT).").encode('utf-8')
    blob = bytearray()
    offsets = []
    for c in keys:
        offsets.append(len(blob))
        blob += chars[c]
    data = bytearray(b'HFZ1')
    data += struct.pack('<H', len(notice)) + notice
    data += struct.pack('<H', len(keys))
    data += b''.join(struct.pack('<H', ord(c)) for c in keys)
    data += b''.join(struct.pack('<I', o) for o in offsets)
    data += blob
    with open(os.path.join(OUT, out_name), 'wb') as f:
        f.write(data)
    print(f'{out_name}: {len(keys)} chars, {len(data) / 1024:.0f} KB')


def commit_of(folder, given):
    if given:
        return given
    if os.path.isdir(os.path.join(folder, '.git')):
        return subprocess.run(['git', '-C', folder, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    return 'unknown'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('animcjk')
    ap.add_argument('mmah')
    ap.add_argument('--animcjk-commit')
    ap.add_argument('--mmah-commit')
    a = ap.parse_args()
    ac = commit_of(a.animcjk, a.animcjk_commit)
    mc = commit_of(a.mmah, a.mmah_commit)
    os.makedirs(OUT, exist_ok=True)

    ja = read(os.path.join(a.animcjk, 'graphicsJa.txt'))
    zh = read(os.path.join(a.animcjk, 'graphicsZhHans.txt'))
    more = {c: g for c, g in read(os.path.join(a.mmah, 'graphics.txt')).items() if c not in ja and c not in zh}
    anim = f'AnimCJK (https://github.com/parsimonhi/animCJK, commit {ac})'
    write(ja, 'hanzi-ja.bytes', f'{anim} graphicsJa.txt (Japanese forms)')
    write(zh, 'hanzi-zh.bytes', f'{anim} graphicsZhHans.txt (Simplified Chinese forms)')
    write(more, 'hanzi-more.bytes', f'Make Me a Hanzi (https://github.com/skishore/makemeahanzi, commit {mc}) graphics.txt, '
                                    f'only characters missing from the two AnimCJK files')


if __name__ == '__main__':
    main()
