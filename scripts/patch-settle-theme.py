#!/usr/bin/env python3
"""settlement-workbench.html 의 색·글꼴을 매뉴얼·실행 센터와 같게 맞춘다.

워크벤치는 파란색 계열 + Pretendard 로 따로 만들어져 있었다.
변수 이름(--brand, --panel …)은 그대로 두고 값만 매뉴얼 토큰으로 바꾸므로
나머지 CSS·화면 코드는 손대지 않는다. 라이트/다크 모두 맞춘다.
새 워크벤치 파일을 받으면 이 스크립트를 다시 돌린다.
"""
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'settlement-workbench.html'
MARK = '/* 매뉴얼·실행 센터와 같은 토큰 */'

LIGHT_OLD = ':root{--bg:#f2f5f8;--panel:#fff;--ink:#1c2a35;--muted:#5f7282;--line:#dbe3ea;--brand:#0a67a0;--brand2:#0d4f7a;--soft:#e9f2f8;--ok:#1d8049;--okbg:#e4f3ea;--warn:#a86400;--warnbg:#fff3de;--err:#bf3526;--errbg:#fdeae8;--wk:#f7f9fb;--input:#fff}'
LIGHT_NEW = (MARK + '\n'
             ':root{--bg:#f4f6f8;--panel:#ffffff;--ink:#1a2230;--muted:#5c6675;--line:#e1e5ea;'
             '--brand:#0f5c56;--brand2:#0a3f3b;--soft:#e3f1ee;--ok:#2f7d55;--okbg:#e6f2ea;'
             '--warn:#a5540d;--warnbg:#fbf1e4;--err:#a3311f;--errbg:#fbeeec;--wk:#eef1f4;--input:#ffffff;'
             "--mono:'IBM Plex Mono',ui-monospace,Consolas,monospace}")

DARK_VALS = ('--bg:#12161c;--panel:#181d25;--ink:#e7ebf0;--muted:#a3adba;--line:#2a313c;'
             '--brand:#4fc9bc;--brand2:#bdf0e7;--soft:#173330;--ok:#6fd4a0;--okbg:#16301f;'
             '--warn:#e3a765;--warnbg:#2e2415;--err:#e08674;--errbg:#2c1a17;--wk:#1f2530;--input:#12161c')

DARK1_OLD = '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#111820;--panel:#18222c;--ink:#e3ebf1;--muted:#98abba;--line:#2c3a47;--brand:#4aa6dd;--brand2:#7cc0ea;--soft:#1d2e3c;--ok:#5cc98a;--okbg:#17301f;--warn:#f0b24f;--warnbg:#33280f;--err:#ff8a7a;--errbg:#3a1b17;--wk:#1c2731;--input:#101820}}'
DARK1_NEW = '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){' + DARK_VALS + '}}'

DARK2_OLD = ':root[data-theme="dark"]{--bg:#111820;--panel:#18222c;--ink:#e3ebf1;--muted:#98abba;--line:#2c3a47;--brand:#4aa6dd;--brand2:#7cc0ea;--soft:#1d2e3c;--ok:#5cc98a;--okbg:#17301f;--warn:#f0b24f;--warnbg:#33280f;--err:#ff8a7a;--errbg:#3a1b17;--wk:#1c2731;--input:#101820}'
DARK2_NEW = ':root[data-theme="dark"]{' + DARK_VALS + '}'

FONT_OLD = 'body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.6 "Pretendard","Malgun Gothic","Apple SD Gothic Neo",system-ui,sans-serif}'
FONT_NEW = ("body{margin:0;background:var(--bg);color:var(--ink);"
            "font:14px/1.6 'Noto Sans KR','IBM Plex Sans KR',-apple-system,BlinkMacSystemFont,system-ui,sans-serif;"
            "-webkit-font-smoothing:antialiased}\n"
            "h1,h2,h3{font-family:'IBM Plex Sans KR','Noto Sans KR',sans-serif}\n"
            "code,kbd,samp,.mono{font-family:var(--mono)}")

LINK_OLD = '<meta name="viewport" content="width=device-width, initial-scale=1">'
LINK_NEW = (LINK_OLD + '\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700'
            '&family=Noto+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">')

REPL = [(LIGHT_OLD, LIGHT_NEW), (DARK1_OLD, DARK1_NEW), (DARK2_OLD, DARK2_NEW),
        (FONT_OLD, FONT_NEW), (LINK_OLD, LINK_NEW)]


def main():
    s = HTML.read_text(encoding='utf-8')
    if MARK in s:
        print('이미 적용돼 있음 — 건너뜀')
        return
    for old, new in REPL:
        assert s.count(old) == 1, f'기준 문구를 한 번만 찾지 못함: {old[:60]!r}'
        s = s.replace(old, new, 1)
    HTML.write_text(s, encoding='utf-8')
    print('색·글꼴을 매뉴얼 기준으로 맞춤')


if __name__ == '__main__':
    main()
