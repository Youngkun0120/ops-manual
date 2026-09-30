/* =========================================================================
   상세 업무 처리 탭 — 실행 센터(ops-center.html)를 이 페이지 안에 띄운다.
   실행 센터가 ①업무 유형 ②서비스 ③통신사 ④스킬 선택과 실행 안내를 모두 가진다.
   (2026-09-28 교체: 이전의 카드 목록 버전은 실행 센터로 대체됐다.)

   부모 주소 #/ops/<유형>/<서비스>/<통신사>/<스킬> → 실행 센터의 #/... 로 그대로 넘긴다.
   실행 센터는 높이가 바뀔 때 parent 로 {type:'ops-model-height'} 를 보낸다.
   ========================================================================= */
(function () {
  var SRC = 'ops-center.html';
  var VER = '20260928-01b';   /* 실행 센터를 바꾸면 올린다 — 브라우저 캐시에 남은 옛 파일을 쓰지 않게 */
  var MIN_H = 760;

  window.renderOps = function () {
    var sub = location.hash.replace(/^#\/?/, '').split('/').slice(1).join('/');
    var src = SRC + '?embed=1&v=' + VER + (sub ? '#/' + sub : '');
    return '<iframe id="opsFrame" class="ops-frame" src="' + src + '" title="상세 업무 처리 실행 센터"' +
      ' style="height:' + MIN_H + 'px"></iframe>' +
      '<div class="ops-frame-foot">' +
        '<span>실행 센터가 이 화면 안에서 돌아갑니다. 화면이 좁으면 ' +
        '<a class="ops-link" href="' + SRC + '?v=' + VER + (sub ? '#/' + sub : '') + '" target="_blank" rel="noopener">새 창으로 열기 ↗</a></span>' +
      '</div>';
  };

  window.addEventListener('message', function (e) {
    if (!e.data) return;
    if (e.data.type === 'ops-scroll-top') {            /* 실행 센터의 「메인으로 가기」 */
      var c = document.getElementById('content');
      if (c) c.scrollTop = 0;
      window.scrollTo(0, 0);
      return;
    }
    if (e.data.type !== 'ops-model-height') return;
    var f = document.getElementById('opsFrame');
    if (f) f.style.height = Math.max(MIN_H, e.data.height + 24) + 'px';
  });
})();
