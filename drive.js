/* 메뉴별 구글 드라이브 자료 — 와이즈솔루션(wisemanroot) · 오션블루(dev@) 드라이브.
 *
 * 2026-09-22 두 드라이브를 직접 열어 폴더 · 파일 id를 확인해 적었다(scripts/ 에 크롤 기록 없음, 이 파일이 정본).
 * 링크는 계정 번호(/u/0/) 없이 두어, 여는 사람의 권한 있는 계정으로 열린다. 권한이 없으면 드라이브가 요청 화면을 띄운다.
 *
 * DRIVE[pageId]   페이지 상단 「관련 드라이브 자료」 패널
 *   d: 'W' 와이즈 드라이브 · 'O' 오션블루 드라이브
 *   k: 'folder' | 'sheet' | 'file' | 'doc' | 'slides'
 *   guess: true 면 위치를 짐작해 연결한 것(매뉴얼 본문과 폴더 이름이 딱 맞지 않음) — 화면에 (확인 필요) 표시
 * INLINE          본문의 드라이브 경로 문구 옆에 바로가기를 붙인다(문구가 바뀌면 조용히 건너뜀)
 */
(function () {
  var F = function (id) { return 'https://drive.google.com/drive/folders/' + id; };
  var S = function (id, gid) { return 'https://docs.google.com/spreadsheets/d/' + id + '/edit' + (gid ? '#gid=' + gid : ''); };
  var X = function (id) { return 'https://drive.google.com/file/d/' + id + '/view'; };
  var D = function (id) { return 'https://docs.google.com/document/d/' + id + '/edit'; };
  var P = function (id) { return 'https://docs.google.com/presentation/d/' + id + '/edit'; };

  var W = {
    monthly:   F('1OSbtYdYLzt2Dqstc9wxN5KOTCIG4DggK'), // 08. 운영 › 월간 업무
    memo:      F('1UnBcuIshNVWX-PCGx9Q6X5d1WCJg8UOe'), // 08. 운영 › 메모장 모음
    guide3:    F('11hyp9D9ivGAla219ac9MDfzjGgJdMVCM'), // 08. 운영 › [3사] 가이드 문서
    cs:        F('1S6Q_yY8GSd_Iwu3-ChEFFYUL8j5B9tFN'), // 08. 운영 › [CS] 운영
    spam:      F('1D5bXErPDDloje9z2Q6y7HFAAX2GyWQ0d'), // 08. 운영 › 스팸대응센터
    evidence:  F('1H-ye3FF_HOEdsIYl3SPwYCmU3-FN7nbf'), // 08. 운영 › 민원 증빙자료 스크린샷
    todayKT:   F('1vIBpbqYCwhRU6n_czp02nXre32HkAs0J'), // 02. 투데이 › 03.운영 › KT
    todayLG:   F('1yPYtU5OxoGOEsbt-OFPSjL7ubNnvUw74'), // 02. 투데이 › 03.운영 › LG U+
    mindKT:    F('1_BITiqNMeF00U-EoMmaJ6wgOJO_BdzPx'), // 01. 마인드케어 › 03.운영 › KT
    mindLG:    F('1o8J9qCZJH7QdMSYx6EC2MsH2S2N3yUoz'), // 01. 마인드케어 › 03.운영 › LGU
    kitSec:    F('1fBREyYzPiddvxqFwWK72DevsOs_nhkZ_'), // 10. 통신사 관련 › 보안점검 › 고객협력사(KT 보안점검)
    kitForm:   F('1lrOVDaHRrTYa-BE50odUV3A36vYt2bWX'), // 〃 › 제출용 서식
    card:      F('1O5VK4yoVFrUVCnb8tvQkvxpsxO-GR3dl'), // 11. 디자인 › 명함 등 인쇄물
  };

  window.DRIVE = {
    'free-data': [
      { d: 'W', k: 'folder', label: '08. 운영 › 월간 업무', note: '매월 제출한 무료데이터 · 월간 지표 엑셀이 쌓이는 곳', url: W.monthly },
      { d: 'W', k: 'file', label: 'PASS마인드케어 무료데이터 자료_260901.xlsx', note: '최근 제출본 — 다음 달 작성 기준', url: X('1sZeff6uotaERcRCO6MgA5pa1iKPd1U-z') },
      { d: 'W', k: 'file', label: 'LG PASS_투데이_무료회원_데이터_260901.xlsx', note: '최근 제출본', url: X('1HO6koXq1HbK4Uz5XUMhE2NhEZ7hq6tjF') },
      { d: 'O', k: 'sheet', label: '부가서비스 가입자 통계 (오션블루)', note: '헬스케어 유료 · 무료 가입자 원천', url: S('1a3CMOCjWChOW-nnObISdmcCWKAVmUIjC5PIZcVaDbo4') },
    ],
    'lgu-ga': [
      { d: 'W', k: 'file', label: '(와이즈솔루션)서비스 월간 지표_26년 08월.xlsx', note: '아톤에 보낸 최근 월간 지표', url: X('14wJpnEgOAvm9hZiXKEjfpR_qdbiDuZ03') },
      { d: 'W', k: 'folder', label: '08. 운영 › 월간 업무', url: W.monthly },
      { d: 'O', k: 'sheet', label: '2026년 헬스케어 데이터 관리 › LGU+ 전달용 탭', note: '헬스케어 화면별 UV · PV · 체류시간', url: S('1azwDHc2YTYAr80YK-cKyaZ2-AosNK9Fyt-LuAbVCf_c', '1774131877') },
    ],
    'push-mgmt': [
      { d: 'W', k: 'folder', label: '마인드케어 › 03.운영 › 푸시기획', url: F('1wf_UpKGC-X2rQn9bpXKka3PsThXUiir4') },
      { d: 'W', k: 'folder', label: '마인드케어 › KT › PUSH', url: F('1eBGa-fngg7fqT76qcGmmPSG9q71NUiMS') },
      { d: 'W', k: 'folder', label: '마인드케어 › LGU › PUSH', url: F('1TmngljPbnR_OjDUKjcOVRfXsUXMQM32r') },
      { d: 'W', k: 'folder', label: '투데이 › 03.운영 › 푸시기획', url: F('114Nz0GlagQcN27F7eD92I0aoF3PqlYeS') },
      { d: 'W', k: 'folder', label: '투데이 › KT › PUSH', url: F('1LXzS_LsTo5ME-a1pD2TR9qBgeQwnQYYq') },
      { d: 'W', k: 'folder', label: '투데이 › LG U+ › 푸시', url: F('1Afg1eC_uka5edAV-TrWRV990eG5eqsuI') },
      { d: 'W', k: 'folder', label: '08. 운영 › [3사] 가이드 문서', note: 'KT 알림함 개선 등 통신사 PUSH 가이드', url: W.guide3 },
      { d: 'O', k: 'folder', label: '헬스케어 PUSH 연도별 이력 + 입점가이드', url: F('1KtISbGNJOUWfIB50GrBSOE3Yfw5gpSjT') },
    ],
    'telco-check': [
      { d: 'W', k: 'folder', label: '08. 운영 › 메모장 모음', note: '점검 공지 양식 메모장', url: W.memo },
      { d: 'W', k: 'folder', label: '10. 통신사 관련 › 운영 › KT', note: 'KT 부가서비스 점검 요청(20251014) · ZTNA', url: F('1jIWXWxTQuYPDRuZkW3uFfQdGQze1tgcJ') },
      { d: 'W', k: 'folder', label: '10. 통신사 관련 › 운영 › LG U+', note: 'ngCAS 이관 · 약관 현행화 회신 양식', url: F('15-Gt0DHYxJQoDt0xWCnany7VrFYkuFWw') },
      { d: 'O', k: 'doc', label: '통신사 업무 플로우', url: D('12CynZ_g7Oc21pJUUm8ygkzFyX12EIF_CwANtGYYVblA') },
    ],
    'protection-check': [
      { d: 'W', k: 'folder', label: '마인드케어 › KT › 이용자보호', note: '이전 작성 파일 (KT 자가점검 체크리스트)', url: F('1wMGkGp4lL0uwUWUmfcLLgwsWZpLpL1Jt') },
      { d: 'W', k: 'folder', label: '마인드케어 › LGU › 이용자보호', note: '이전 작성 파일 (U+ 반기 현황조사)', url: F('1B8qnH6fve0fZJkhiOqGIHOr0YSr5ERIZ') },
      { d: 'W', k: 'folder', label: '투데이 › KT › 이용자보호', url: F('1ij9-5SZrKQwzAVLJbrfoDXBU70-6pIWS') },
      { d: 'W', k: 'folder', label: '투데이 › LG U+ › 운영', note: '투데이 U+에는 이용자보호 폴더가 따로 없음', url: F('1iyJXNe8XVJaq4pn2iWoO7VzjTju2QRHG'), guess: true },
      { d: 'W', k: 'folder', label: '10. 통신사 관련 › 보안점검 › 고객협력사(KT 보안점검)', note: '연도별 제출본 2022~2026', url: W.kitSec },
      { d: 'W', k: 'folder', label: '고객협력사(KT 보안점검) › 제출용 서식', url: W.kitForm },
      { d: 'W', k: 'sheet', label: '3사 통합 점검 내역(2026)', url: S('1H9W36VWS4fwUV9j-TB7iH5xO8qkUNuRVLoaiSJEhcek') },
    ],
    'event-ops': [
      { d: 'W', k: 'folder', label: '투데이 › 03.운영 › 이벤트 기획', url: F('1IK7N19Qh0mJPe-3ZFFYTb9BZ0bDBOhjo') },
      { d: 'W', k: 'folder', label: '마인드케어 › KT › 이벤트', url: F('1bioxMkNskq9GwCFL5QmJ4BsxZmwsWWeF') },
      { d: 'W', k: 'folder', label: '마인드케어 › LGU › 이벤트 기획', url: F('18JHpvjjqQ8n4tce1D_qp9CGTWA4k2yvX') },
      { d: 'W', k: 'folder', label: '마인드케어 TMS 기존 발송 내역', note: '드라이브상 마인드케어 › LGU 아래에 있음', url: F('179TfHTawS79g1484UsdwWxSGKnemXTdO'), guess: true },
      { d: 'W', k: 'folder', label: '투데이 › KT › TMS', url: F('1asRukpkqmia9h9UlybrdTxzQpaZpkCjC') },
      { d: 'O', k: 'folder', label: '헬스케어 TMS 월별 실행 이력 (2023-11~2025-09) + 결과 지표', url: F('1yXJZtqjBvIf8MKZXQS7vuGDjwJIhutcz') },
      { d: 'O', k: 'folder', label: '헬스케어 엔딩노티 이벤트 이력', url: F('1DQXeRQYIRtXZ6u_NyzhSGliAZOO56JOS') },
      { d: 'O', k: 'folder', label: '행복레터 프로세스 · 디자인 가이드 · 이벤트 결과', url: F('1iI638sOns1u4LuelPBgJGRW0-U-fYLTj') },
      { d: 'O', k: 'folder', label: '헬스케어 KT 이벤트 기획 자료', url: F('1Yb1CoP7d_rFQcYMAVmR9R_gh_1okqb8O') },
      { d: 'O', k: 'folder', label: '헬스케어 U+ 이벤트 관련 자료', url: F('1upNFkm67VH5naAbazymjV4WqYe1AsdFD') },
    ],
    'event-prize': [
      { d: 'W', k: 'folder', label: '투데이 › KT › 이벤트 경품 발송', note: '마케팅비용정산 · 거래명세서', url: F('1Rx0uuKOn49SmjgFEZykrhmd5HCeJJyEd') },
      { d: 'W', k: 'folder', label: '마인드케어 › KT › 이벤트 경품 발송', note: 'SMS 발송 메모장', url: F('1CYDE6RHRViyclNoCxYJPcY7ZLhd5R9Km') },
      { d: 'W', k: 'folder', label: '마인드케어 › LGU › 이벤트 경품 발송', url: F('1DtR_lN38E9km68vLwd97gEcK_llPQlD1') },
      { d: 'O', k: 'folder', label: '경품 발송 도구 (다우경품 발송 리스트)', url: F('1FyCQdrh3Q9FadcJT_QdiRrJM3w0rPmkZ') },
      { d: 'O', k: 'sheet', label: '이벤트 경품 지급 관리', url: S('1hz2xa4pZRHNC7DbUv347-z1aw2nGvn9ZGfjgDw1u7rc') },
      { d: 'O', k: 'folder', label: 'PASS머니 정산 관련', url: F('19wOOYUWc9U5BvdHWZaAH-6MvzU96A1n_') },
    ],
    'health-metrics': [
      { d: 'O', k: 'sheet', label: '부가서비스 가입자 통계 (오션블루)', url: S('1a3CMOCjWChOW-nnObISdmcCWKAVmUIjC5PIZcVaDbo4') },
      { d: 'O', k: 'sheet', label: '크림봇 제휴 광고 데이터 (데일리)', url: S('1ymVDDcWaWtevJkpopjvPgVKtxe1PztBffl97QbkaiyU') },
      { d: 'O', k: 'folder', label: '마케팅 채널별 분류 ([GDN] 배너 · [충전소] 핀크럭스)', url: F('1BjpqgWn0Jsp_esj9Z9HqoTldvesrOlaY') },
    ],
    'settlement': [
      { d: 'O', k: 'folder', label: '빌레터 생활건강 월별 정산내역서', url: F('1MmBoxFXQo50VjWXCisAXsIUxkAFGHs4Z') },
      { d: 'O', k: 'folder', label: 'PASS머니 정산 관련', url: F('19wOOYUWc9U5BvdHWZaAH-6MvzU96A1n_') },
      { d: 'W', k: 'sheet', label: '투데이 | 집계 시트', note: '[비용] 월 합계 탭', url: S('1WSeIPpTEMHFw5Qwmia5y18FpMD7JCwIy8xEG02gzCDA'), guess: true },
      { d: 'W', k: 'folder', label: '마인드케어 › 03.운영 › 제휴마케팅', url: F('1GzhQ-NQBBQFqv7Qdv36ypXqSbdvx-Unh') },
    ],
    'health-content': [
      { d: 'O', k: 'slides', label: '건강뉴스 스크립트 (헬스케어)', url: P('19P6ZrG_wjHI8t2uDkDSycuPc2Dvs99N_DtrefMzhGk8') },
      { d: 'W', k: 'file', label: '퀴즈 등록 양식.xlsx', note: '03. 헬스케어 › 03.운영', url: X('1RpIONK2IeerZ73TyH6gb-Sr2vb0W-NjP') },
      { d: 'W', k: 'folder', label: '03. 헬스케어 › 03.운영', url: F('1aQ7XeI0AYa5JcZQ1-7STFQVeoVmKe5qk') },
    ],
    'qa': [
      { d: 'W', k: 'folder', label: '03. 헬스케어 › 07.QA', url: F('1bEffyg0XGILCA5Kr18cul-pWLL3kuX9m') },
    ],
    'ad-review': [
      { d: 'W', k: 'folder', label: '10. 통신사 관련 › 외부가입창 가이드', url: F('1iOBc4Yk6GOJH4q8C9r3qS-jfkvbB8mUa') },
      { d: 'W', k: 'folder', label: '08. 운영 › [3사] 가이드 문서', note: 'KT GUI · U+ 배너 · SKT 모아보기 가이드', url: W.guide3 },
      { d: 'W', k: 'folder', label: '11. 디자인 › _광고', url: F('1X1bpeg9L43qSSLtehtmFsv3kizOzA-qh') },
      { d: 'O', k: 'folder', label: '[3사] 가이드 · LGU+ 전체 (배너 v2.5/v2.6 · PASS머니 정책서 등)', url: F('1peCBYOxvvToF86Q5CFZEBr71Gtag9KgI') },
    ],
    'cs-inquiry': [
      { d: 'W', k: 'folder', label: '08. 운영 › [CS] 운영', url: W.cs },
      { d: 'W', k: 'file', label: '와이즈서비스_자주하는 질문_통합(KT,U+).xlsx', url: X('1kidSzsmynwe86-Po3aJIyNmGfM5OqtTM') },
      { d: 'W', k: 'file', label: '오션블루_PASS헬스케어_FAQ_250228.xlsx', note: '03. 헬스케어 › 03.운영', url: X('1jn9eKNieTgdvGDBbiPssrjEdO0e8Qy72') },
    ],
    'telco-complaint': [
      { d: 'W', k: 'folder', label: '08. 운영 › 민원 증빙자료 스크린샷', url: W.evidence },
      { d: 'W', k: 'folder', label: '마인드케어 › 03.운영 › 민원사실', url: F('15lkto53Dzkb5Hqo62JXUd1UcdORp8SEd') },
    ],
    'kisa': [
      { d: 'W', k: 'folder', label: '08. 운영 › 스팸대응센터', url: W.spam },
    ],
    'counselor-mgmt': [
      { d: 'W', k: 'folder', label: '마인드케어 › 03.운영 › 상담사 관리', url: F('1saNaK4wEOLkHKVwOzlXV1z3UyQagle1o') },
    ],
  };

  /* 본문 문구 → 바로가기. 첫 번째로 나오는 곳에만 붙인다. */
  window.DRIVE_INLINE = [
    ['드라이브 08.운영 › 월간 업무', W.monthly],
    ['구글 드라이브 › 08.운영 › 메모장 모음', W.memo],
    ['드라이브 › 02.투데이 › 03.운영 › KT › 이벤트 경품 발송', F('1Rx0uuKOn49SmjgFEZykrhmd5HCeJJyEd')],
    ['드라이브(고객협력사 › 제출용 서식)', W.kitForm],
    ['드라이브 › 11. 디자인 › 명함 등 인쇄물', W.card],
  ];
})();
