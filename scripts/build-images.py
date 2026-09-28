#!/usr/bin/env python3
"""매뉴얼 참고 화면 이미지 빌드.

~/Downloads/manual_images_rename/{메뉴}_{NN}.png + _네이밍_매핑표.csv
  → img/{page-id}_{NN}.jpg  (고객 개인정보 영역은 불투명 박스로 가림, 긴 변 2000px 이하)
  → shots.js                (window.SHOTS = {page-id: [{src, cap}]})

다시 돌리면 img/ 와 shots.js 를 통째로 새로 만든다.
"""
import csv, json, os, sys, unicodedata
from pathlib import Path
from PIL import Image, ImageDraw

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else '~/Downloads/manual_images_rename').expanduser()
OUT = Path(__file__).resolve().parent.parent
IMG = OUT / 'img'

# 파일명 접두어 → index.html NAV 의 페이지 id
PAGE = {
    '서비스QA': 'qa', '푸시마케팅관리': 'push-mgmt', '무료가입자통계공유': 'free-data',
    'LGU_GA실적전달': 'lgu-ga', '통신사점검대응': 'telco-check', '이용자보호점검': 'protection-check',
    '통신사민원대응': 'telco-complaint', '가입사실내역확인': 'sub-fact-check', 'CS민원지원': 'cs-inquiry',
    '마케팅이미지검수': 'ad-review', '이벤트기획': 'event-ops', '이벤트당첨자상품발송': 'event-prize',
    '헬스케어마케팅실적집계': 'health-metrics', '제휴정산업무': 'settlement',
    '헬스케어콘텐츠기획': 'health-content', '월간문자발송': 'monthly-sms',
    '1대1마음상담관리': 'mindcare-counsel', '인건비정산업무': 'counselor-mgmt',
}

# 고객 개인정보 가림 영역. 좌표는 (기준폭, 기준높이) 화면에서 잰 값이고 원본 크기에 맞춰 늘린다.
MASKS = {
    '가입사실내역확인_01': ((1037, 1400), [(325, 245, 690, 315), (330, 505, 695, 575), (125, 1090, 485, 1155)]),
    '가입사실내역확인_02': ((1400, 674), [(225, 340, 705, 415)]),
    '가입사실내역확인_03': ((1317, 1400), [(255, 265, 750, 340)]),
    'CS민원지원_01': ((1400, 752), [(98, 170, 185, 191), (215, 226, 390, 260), (468, 226, 554, 260)]),
    '이벤트기획_01': ((1400, 652), [(468, 553, 585, 652)]),
    '이벤트당첨자상품발송_01': ((1400, 708), [(688, 522, 812, 708)]),
    '1대1마음상담관리_03': ((1400, 752), [(462, 192, 1225, 290), (462, 334, 1225, 503)]),
    '1대1마음상담관리_04': ((1400, 1185), [(655, 0, 1380, 125), (352, 276, 1375, 920)]),
}
MAX_SIDE = 2000


def nfc(s):
    return unicodedata.normalize('NFC', s)


def main():
    caps = {}
    with open(SRC / '_네이밍_매핑표.csv', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            caps[nfc(row['새 파일명'])] = row['내용'].strip()

    IMG.mkdir(exist_ok=True)
    for old in IMG.iterdir():
        old.unlink()

    shots, unknown = {}, []
    for raw in sorted(os.listdir(SRC)):
        name = nfc(raw)
        stem, ext = os.path.splitext(name)
        if ext.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
            continue
        prefix, _, no = stem.rpartition('_')
        page = PAGE.get(prefix)
        if not page or not no.isdigit():
            unknown.append(name)
            continue

        im = Image.open(SRC / raw).convert('RGB')
        if stem in MASKS:
            (bw, bh), boxes = MASKS[stem]
            sx, sy = im.width / bw, im.height / bh
            d = ImageDraw.Draw(im)
            for x0, y0, x1, y1 in boxes:
                d.rectangle([x0 * sx, y0 * sy, x1 * sx, y1 * sy], fill=(96, 104, 116))
        if max(im.size) > MAX_SIDE:
            im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)

        out = f'{page}_{int(no):02d}.jpg'
        im.save(IMG / out, 'JPEG', quality=86, optimize=True)
        shots.setdefault(page, []).append({'no': int(no), 'src': 'img/' + out, 'cap': caps.get(name, ''),
                                           'masked': stem in MASKS})

    for page in shots:
        shots[page].sort(key=lambda s: s['no'])
        for s in shots[page]:
            del s['no']

    (OUT / 'shots.js').write_text(
        '/* build-images.py 가 만든다 — 직접 고치지 말 것 */\nwindow.SHOTS = '
        + json.dumps(shots, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')

    total = sum(len(v) for v in shots.values())
    print(f'{total}장 → {len(shots)}개 메뉴, 가림 {sum(s["masked"] for v in shots.values() for s in v)}장')
    missing = [m for m in MASKS if not any(s['src'].startswith('img/' + PAGE[m.rpartition("_")[0]]) for s in shots.get(PAGE[m.rpartition("_")[0]], []))]
    if unknown:
        print('메뉴를 못 찾은 파일:', unknown)
    if missing:
        print('가림 대상인데 파일이 없음:', missing)


if __name__ == '__main__':
    main()
