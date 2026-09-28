#!/usr/bin/env python3
"""models/ 폴더의 업무 자동화 모델 HTML을 훑어 models.js 를 만든다.

파일 이름은 ops.js 의 스킬 ID와 같아야 한다 (예: models/telco-push-copy.html).
ID 가 ops.js 에 없으면 경고만 하고 목록에는 넣는다.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / 'models'
OPS = ROOT / 'ops.js'


def main():
    MODELS.mkdir(exist_ok=True)
    known = set(re.findall(r"^\s*id:\s*'([^']+)'", OPS.read_text(encoding='utf-8'), re.M))

    pages = {}
    for f in sorted(MODELS.glob('*.html')):
        sid = f.stem
        title = ''
        m = re.search(r'<title[^>]*>(.*?)</title>', f.read_text(encoding='utf-8', errors='ignore'), re.S)
        if m:
            title = re.sub(r'\s+', ' ', m.group(1)).strip()
        pages[sid] = {'src': f'models/{f.name}', 'title': title,
                      'kb': round(f.stat().st_size / 1024)}
        if sid not in known:
            print(f'  ! {f.name} — ops.js 에 없는 ID (카드 없이 파일만 존재)', file=sys.stderr)

    (ROOT / 'models.js').write_text(
        '/* build-models.py 가 만든다 — 직접 고치지 말 것 */\nwindow.MODEL_PAGES = '
        + json.dumps(pages, ensure_ascii=False, indent=1) + ';\n', encoding='utf-8')

    missing = sorted(known - set(pages))
    print(f'모델 페이지 {len(pages)}개 연결')
    if missing:
        print('아직 HTML 이 없는 스킬:', ', '.join(missing))


if __name__ == '__main__':
    main()
