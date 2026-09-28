#!/usr/bin/env python3
"""index.html 에 1depth 탭(업무 매뉴얼 / 상세 업무 처리)을 넣는다.

기획자가 새 index.html 을 주면 patch-drive.py 와 함께 다시 돌린다.
여러 번 돌려도 한 번만 들어간다.
"""
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'index.html'
MARK = '/* ops.js patch */'

CSS = MARK + '''
.tabbar{display:flex;gap:4px;padding:0 0 0 4px;border-bottom:1px solid var(--border);background:var(--bg);position:sticky;top:0;z-index:6}
.tabbar button{
  appearance:none;background:none;border:0;border-bottom:2px solid transparent;margin-bottom:-1px;
  padding:12px 14px;font:inherit;font-size:13.5px;font-weight:600;color:var(--ink-faint);cursor:pointer;
}
.tabbar button:hover{color:var(--ink-muted)}
.tabbar button.on{color:var(--accent-ink);border-bottom-color:var(--accent)}
.ops-picker{border:1px solid var(--border);border-radius:14px;background:var(--surface);padding:6px 16px;margin-bottom:22px}
.ops-row{display:flex;gap:14px;align-items:flex-start;padding:12px 0;border-bottom:1px solid var(--border)}
.ops-row:last-child{border-bottom:0}
.ops-row-label{flex:0 0 116px;font-size:12.5px;font-weight:600;color:var(--ink-muted);padding-top:5px;display:flex;gap:7px;align-items:center}
.ops-row-label .depth{
  display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:50%;
  background:var(--accent-soft);color:var(--accent-ink);font-size:11px;font-family:'IBM Plex Mono',monospace
}
.ops-chips{display:flex;flex-wrap:wrap;gap:6px}
.ops-chip{
  appearance:none;display:inline-flex;align-items:center;gap:6px;padding:6px 11px;border-radius:999px;
  border:1px solid var(--border-strong);background:var(--surface-2);color:var(--ink);
  font:inherit;font-size:12.5px;cursor:pointer
}
.ops-chip:hover{border-color:var(--accent)}
.ops-chip .n{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--ink-faint)}
.ops-chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
.ops-chip.on .n{color:rgba(255,255,255,.75)}
.ops-chip.empty{opacity:.45}
.ops-result-head{display:flex;justify-content:space-between;align-items:baseline;margin:0 0 10px;font-size:12px;color:var(--ink-faint)}
.ops-result-head b{color:var(--ink-muted);font-size:13px}
.ops-cards{display:flex;flex-direction:column;gap:12px}
.ops-card{border:1px solid var(--border);border-radius:14px;background:var(--surface);padding:16px 18px}
.ops-card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.ops-card-name{font-size:15.5px;font-weight:700}
.ops-card-scope{font-size:12px;color:var(--ink-faint);margin-top:3px}
.ops-tag{flex:0 0 auto;font-size:11px;font-weight:600;padding:4px 9px;border-radius:999px;background:var(--surface-2);border:1px solid var(--border);color:var(--ink-faint)}
.ops-tag.on{background:var(--accent-soft);border-color:var(--accent-soft-border);color:var(--accent-ink)}
.ops-what{font-size:13.5px;color:var(--ink-muted);line-height:1.65;margin:10px 0 14px}
.ops-field{display:flex;align-items:center;gap:8px;margin-bottom:7px;flex-wrap:wrap}
.ops-field-k{flex:0 0 74px;font-size:11.5px;font-weight:600;color:var(--ink-faint)}
.ops-id,.ops-ask{
  font-family:'IBM Plex Mono',monospace;font-size:12.5px;padding:6px 10px;border-radius:8px;
  background:var(--surface-2);border:1px solid var(--border);color:var(--ink);word-break:break-all
}
.ops-ask{font-family:inherit}
.ops-copy{appearance:none;border:1px solid var(--border-strong);background:var(--surface);color:var(--ink-muted);border-radius:8px;padding:5px 10px;font:inherit;font-size:11.5px;cursor:pointer}
.ops-copy:hover{border-color:var(--accent);color:var(--accent-ink)}
.ops-copy.done{background:var(--accent-soft);border-color:var(--accent-soft-border);color:var(--accent-ink)}
.ops-foot{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin-top:12px;padding-top:12px;border-top:1px solid var(--border);font-size:12px}
.ops-note{color:var(--ink-faint)}
.ops-link{color:var(--accent-ink);cursor:pointer;text-decoration:none;font-weight:600}
.ops-link:hover{text-decoration:underline}
.ops-embed{margin:14px 0 4px;border:1px solid var(--border);border-radius:12px;overflow:hidden;background:var(--surface-2)}
.ops-embed-head{display:flex;gap:10px;align-items:baseline;padding:9px 12px;border-bottom:1px solid var(--border);font-size:12px;color:var(--ink-faint)}
.ops-embed-head b{font-size:12.5px;color:var(--ink-muted)}
.ops-embed-head span{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ops-embed iframe{display:block;width:100%;height:560px;border:0;background:var(--surface)}
@media (max-width:860px){.ops-embed iframe{height:420px}}
.ops-frame{display:block;width:100%;border:0;background:var(--surface);border-radius:14px}
.ops-frame-foot{margin-top:10px;font-size:12px;color:var(--ink-faint)}
body.ops-mode .content{padding-top:10px}
body.ops-mode .sidebar{display:none}
@media (max-width:860px){.ops-row{flex-direction:column;gap:6px}.ops-row-label{padding-top:0}}
@media print{.tabbar{display:none!important}}
</style>'''

TABBAR = '''    <div class="tabbar" id="tabbar">
      <button data-tab="manual" onclick="navigate('home')">업무 매뉴얼</button>
      <button data-tab="ops" onclick="location.hash='#/ops/-/-/-'">상세 업무 처리</button>
    </div>
'''

ROUTE_OLD = '''function renderRoute(id){
  var ok = id==='home' || !!findPage(id);'''
ROUTE_NEW = '''function renderRoute(id){
  /* ops.js patch — 상세 업무 처리 탭 */
  var isOps = id.split('/')[0]==='ops';
  document.body.classList.toggle('ops-mode', isOps);
  document.querySelectorAll('#tabbar button').forEach(function(b){
    b.classList.toggle('on', b.getAttribute('data-tab')===(isOps?'ops':'manual'));
  });
  if(isOps){
    document.getElementById('pageBody').innerHTML = renderOps();
    document.getElementById('content').scrollTop = 0;
    window.scrollTo(0,0);
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('scrim').classList.remove('open');
    return;
  }
  var ok = id==='home' || !!findPage(id);'''

HASH_OLD = '''function currentIdFromHash(){
  var h = location.hash.replace(/^#\\/?/,'');
  return h || 'home';
}'''
HASH_NEW = '''function currentIdFromHash(){
  var h = location.hash.replace(/^#\\/?/,'');
  if(h.split('/')[0]==='ops') return h;   /* ops.js patch */
  return h || 'home';
}'''


def main():
    s = HTML.read_text(encoding='utf-8')
    if MARK in s:
        print('이미 적용돼 있음 — 건너뜀')
        return
    assert s.count('</style>') == 1
    s = s.replace('</style>', CSS, 1)

    old_bar = '''    <div class="content" id="content">'''
    assert old_bar in s
    s = s.replace(old_bar, TABBAR + old_bar, 1)

    assert '<script src="shots.js"></script>' in s
    s = s.replace('<script src="shots.js"></script>', '<script src="shots.js"></script>\n<script src="ops.js"></script>', 1)

    assert ROUTE_OLD in s
    s = s.replace(ROUTE_OLD, ROUTE_NEW, 1)
    assert HASH_OLD in s
    s = s.replace(HASH_OLD, HASH_NEW, 1)

    HTML.write_text(s, encoding='utf-8')
    print('탭 · 상세 업무 처리 화면 적용 완료')


if __name__ == '__main__':
    main()
