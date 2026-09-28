"""index.html 에 드라이브 자료 연결(drive.js)을 붙인다. 여러 번 돌려도 한 번만 들어간다.

    python3 scripts/patch-drive.py

기획자가 새 index.html 을 주면: 이미지 패치(build-images 관련 3군데)와 함께 이것도 다시 돌린다.
"""
import re, sys, pathlib
p = pathlib.Path(__file__).resolve().parent.parent / "index.html"
s = p.read_text()
MARK = "/* drive.js patch */"
if MARK in s:
    print("이미 패치됨"); sys.exit(0)

# 1) 스크립트 로드
a = '<script src="shots.js"></script>'
assert a in s, "shots.js 태그가 없음 — 이미지 패치부터"
s = s.replace(a, a + '\n<script src="drive.js"></script>', 1)

# 2) CSS
css = MARK + """
.drive-box{margin:16px 0 4px;border:1px solid var(--border);border-radius:12px;background:var(--surface);overflow:hidden}
.drive-box .dh{display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:10px 14px;border-bottom:1px solid var(--border);background:var(--surface-2,var(--bg))}
.drive-box .dh b{font-size:13px}
.drive-box .dh span{font-size:11.5px;color:var(--ink-faint)}
.drive-box ul{list-style:none;margin:0;padding:4px 0}
.drive-box li{display:grid;grid-template-columns:74px 1fr;gap:10px;align-items:baseline;padding:6px 14px}
.drive-box li+li{border-top:1px dashed var(--border)}
.drive-box .who{font-size:11px;font-weight:700;padding:1px 7px;border-radius:999px;text-align:center;white-space:nowrap}
.drive-box .who.W{background:var(--accent-soft);color:var(--accent-ink);border:1px solid var(--accent-soft-border)}
.drive-box .who.O{background:var(--warn-soft);color:var(--warn);border:1px solid var(--warn-soft-border)}
.drive-box a{font-size:13px;font-weight:600;color:var(--ink);text-decoration:none}
.drive-box a:hover{color:var(--accent);text-decoration:underline}
.drive-box .kind{font-size:10.5px;color:var(--ink-faint);margin-left:6px}
.drive-box .note{display:block;font-size:12px;color:var(--ink-muted);margin-top:1px}
.drive-box .guess{font-size:10.5px;font-weight:700;color:var(--warn);margin-left:6px}
"""
i = s.index("</style>")
s = s[:i] + css + s[i:]

# 3) 렌더 함수 + renderPage 연결
fn = MARK + """
var DRIVE_KIND = {folder:'폴더', sheet:'시트', file:'파일', doc:'문서', slides:'슬라이드'};
function renderDrive(pageId){
  var list = (window.DRIVE||{})[pageId];
  if(!list || !list.length) return '';
  return '<div class="drive-box"><div class="dh"><b>관련 드라이브 자료</b><span>와이즈 = wisemanroot · 오션블루 = dev@ 드라이브 · 권한이 있는 계정으로 열림</span></div><ul>'+
    list.map(function(x){
      return '<li><span class="who '+x.d+'">'+(x.d==='W'?'와이즈':'오션블루')+'</span><span>'+
        '<a href="'+x.url+'" target="_blank" rel="noopener">'+x.label+'</a><span class="kind">'+(DRIVE_KIND[x.k]||'')+'</span>'+
        (x.guess?'<span class="guess">위치 확인 필요</span>':'')+
        (x.note?'<span class="note">'+x.note+'</span>':'')+'</span></li>';
    }).join('')+'</ul></div>';
}
function linkDriveInline(html){
  (window.DRIVE_INLINE||[]).forEach(function(r){
    var i = html.indexOf(r[0]);
    if(i<0) return;
    html = html.slice(0, i+r[0].length) + L(r[1], '드라이브') + html.slice(i+r[0].length);
  });
  return html;
}
"""
a = "function renderPage(pageId){"
assert a in s
s = s.replace(a, fn + a, 1)
a = "    (isRef?'':renderActions(entry))+\n"
assert a in s
s = s.replace(a, a + "    (isRef?'':renderDrive(pageId))+\n", 1)
a = "    '<div style=\"margin-top:10px\">'+renderPageBody(entry.refs)+'</div>';"
assert a in s
s = s.replace(a, "    '<div style=\"margin-top:10px\">'+linkDriveInline(renderPageBody(entry.refs))+'</div>';", 1)

p.write_text(s)
print("패치 완료")
