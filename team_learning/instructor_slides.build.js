const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";            // 13.3 x 7.5
p.author = "team_learning";
p.title = "크롤링 데이터 파이프라인 — 강사용 진행 가이드";

// ── palette ───────────────────────────────────────────────
const DARK = "0E2A3B", DARK2 = "12384E", TEAL = "1C7293", MINT = "02C39A",
      AMBER = "F2A23C", WHITE = "FFFFFF", INK = "1E293B", MUTED = "64748B",
      CODETX = "E6EDF3", CMT = "7FA9BE", CARD = "F1F5F9", HAIR = "E2E8F0", ICE = "CADCFC";
const KR = "Malgun Gothic", MONO = "Consolas";
const W = 13.33, H = 7.5, M = 0.7;
const sh = () => ({ type: "outer", color: "0B1F2C", blur: 9, offset: 3, angle: 90, opacity: 0.18 });

let pageNo = 0;
function light(s){ s.background = { color: WHITE }; }
function dark(s){ s.background = { color: DARK }; }
function foot(s){
  pageNo++;
  s.addText(`team_learning · 강사용`, { x: M, y: H-0.42, w: 5, h: 0.3, fontFace: KR, fontSize: 9, color: MUTED });
  s.addText(String(pageNo), { x: W-1.1, y: H-0.42, w: 0.4, h: 0.3, fontFace: MONO, fontSize: 9, color: MUTED, align: "right" });
}
// lesson chip (mint oval w/ label) + title
function head(s, chipTxt, titleTxt, sub){
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: M, y: 0.5, w: chipTxt.length>3?1.5:1.0, h: 0.42, fill:{color:DARK}, rectRadius:0.21 });
  s.addText(chipTxt, { x: M, y: 0.5, w: chipTxt.length>3?1.5:1.0, h: 0.42, fontFace: MONO, fontSize: 13, bold:true, color: MINT, align:"center", valign:"middle", margin:0 });
  s.addText(titleTxt, { x: M+ (chipTxt.length>3?1.7:1.2), y: 0.42, w: W-M-2.0, h: 0.6, fontFace: KR, fontSize: 27, bold:true, color: INK, valign:"middle" });
  if(sub) s.addText(sub, { x: M, y: 1.15, w: W-2*M, h: 0.4, fontFace: KR, fontSize: 13, color: MUTED });
}
// dark code card with rich runs: lines = array of arrays of {t, c?}
function code(s, x, y, w, h, lines, fs){
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill:{color:DARK}, rectRadius:0.08, shadow: sh() });
  const runs = [];
  lines.forEach((ln, i) => {
    if(ln.length===0){ runs.push({ text:" ", options:{ breakLine:true } }); return; }
    ln.forEach((seg, j) => {
      runs.push({ text: seg.t, options: { color: seg.c||CODETX, breakLine: j===ln.length-1 } });
    });
  });
  s.addText(runs, { x: x+0.22, y: y+0.16, w: w-0.44, h: h-0.32, fontFace: MONO, fontSize: fs||12.5, valign:"top", lineSpacingMultiple:1.06, margin:0 });
}
// callout pill (mint or amber)
function callout(s, x, y, w, h, color, label, body){
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill:{color: color==MINT?"E6FBF5":"FCEFD9"}, line:{color, width:1}, rectRadius:0.08 });
  s.addText([{text: label+"  ", options:{bold:true, color}}, {text: body, options:{color:INK}}],
    { x:x+0.2, y, w:w-0.4, h, fontFace: KR, fontSize: 13, valign:"middle", margin:0 });
}
function card(s, x, y, w, h){
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill:{color:CARD}, rectRadius:0.08 });
}

// ════════ 1. TITLE ════════
{ const s = p.addSlide(); dark(s);
  s.addText("강사용 진행 가이드 · INSTRUCTOR DECK", { x:M, y:1.5, w:11, h:0.4, fontFace:MONO, fontSize:14, color:MINT, charSpacing:2 });
  s.addText("크롤링으로\n데이터 파이프라인 만들기", { x:M, y:2.0, w:11.5, h:2.0, fontFace:KR, fontSize:46, bold:true, color:WHITE, lineSpacingMultiple:1.02 });
  s.addText("KOFIA TDF 크롤러 · team_learning 커리큘럼 (레슨 00–11)", { x:M, y:4.25, w:11.5, h:0.5, fontFace:KR, fontSize:18, color:ICE });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:M, y:5.15, w:7.2, h:0.62, fill:{color:MINT}, rectRadius:0.31 });
  s.addText("로컬에서 만들어  →  클라우드에서 매일 무인 수집", { x:M, y:5.15, w:7.2, h:0.62, fontFace:KR, fontSize:15, bold:true, color:DARK, align:"center", valign:"middle", margin:0 });
  // dot motif
  [0,1,2].forEach(i => s.addShape(p.shapes.OVAL, { x:11.2+i*0.5, y:6.5, w:0.22, h:0.22, fill:{color: i==2?MINT:TEAL} }));
}

// ════════ 2. 이 수업은 ════════
{ const s = p.addSlide(); light(s); head(s, "INTRO", "이 수업은");
  const items = [
    ["대상", "파이썬 기초 문법만 아는 팀원.\n크롤링이 처음이어도 OK."],
    ["목표", "이 크롤러가 어떻게 한 단계씩\n만들어졌는지 직접 만들며 이해."],
    ["결과물", "로컬에서 만든 크롤러가\n클라우드에서 매일 도는 DB."],
  ];
  const cw = (W-2*M-0.6)/3;
  items.forEach((it, i) => {
    const x = M + i*(cw+0.3);
    card(s, x, 1.9, cw, 3.6);
    s.addShape(p.shapes.OVAL, { x:x+0.35, y:2.25, w:0.7, h:0.7, fill:{color:DARK} });
    s.addText(["①","②","③"][i], { x:x+0.35, y:2.25, w:0.7, h:0.7, fontFace:KR, fontSize:22, bold:true, color:MINT, align:"center", valign:"middle", margin:0 });
    s.addText(it[0], { x:x+0.35, y:3.15, w:cw-0.7, h:0.5, fontFace:KR, fontSize:19, bold:true, color:INK });
    s.addText(it[1], { x:x+0.35, y:3.75, w:cw-0.7, h:1.4, fontFace:KR, fontSize:14.5, color:MUTED, lineSpacingMultiple:1.15 });
  });
  foot(s);
}

// ════════ 3. 교육 철학 ════════
{ const s = p.addSlide(); light(s); head(s, "WHY", "교육 철학 — 작게 → 동작 → 정리 → 클라우드");
  const steps = [["작게 시작","한 줄 요청부터"],["동작하는 MVP","한 파일로 끝까지"],["책임별 분리","config·parser·db"],["클라우드 자동화","cron 매일 무인"]];
  const bw = (W-2*M-3*0.45)/4;
  steps.forEach((st,i)=>{
    const x = M + i*(bw+0.45);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y:2.4, w:bw, h:2.4, fill:{color: i==3?DARK:CARD}, rectRadius:0.08 });
    s.addText(String(i+1), { x, y:2.7, w:bw, h:0.7, fontFace:MONO, fontSize:30, bold:true, color: i==3?MINT:TEAL, align:"center", margin:0 });
    s.addText(st[0], { x:x+0.15, y:3.5, w:bw-0.3, h:0.5, fontFace:KR, fontSize:16, bold:true, color: i==3?WHITE:INK, align:"center", margin:0 });
    s.addText(st[1], { x:x+0.15, y:4.0, w:bw-0.3, h:0.6, fontFace:KR, fontSize:12.5, color: i==3?ICE:MUTED, align:"center", margin:0 });
    if(i<3) s.addText("→", { x:x+bw+0.02, y:2.4, w:0.41, h:2.4, fontFace:KR, fontSize:22, bold:true, color:MUTED, align:"center", valign:"middle", margin:0 });
  });
  s.addText("처음부터 멋진 구조를 만들지 않습니다. 동작하는 코드를 정리하며 구조가 나옵니다.", { x:M, y:5.2, w:W-2*M, h:0.5, fontFace:KR, fontSize:14, italic:true, color:MUTED });
  foot(s);
}

// ════════ 4. 아젠다 & 타이밍 ════════
{ const s = p.addSlide(); light(s); head(s, "PLAN", "전체 아젠다 & 권장 시간");
  const rows = [
    [{text:"단계",options:{bold:true,color:WHITE,fill:{color:DARK}}},{text:"내용",options:{bold:true,color:WHITE,fill:{color:DARK}}},{text:"권장",options:{bold:true,color:WHITE,fill:{color:DARK},align:"center"}}],
    ["00–02","환경 · HTTP/응답 · 사이트 관찰(왜 POST)","25분"],
    ["03–05","첫 크롤 → XML 파싱 → SQLite 저장 (라이브 데모)","40분"],
    ["06","한 파일 MVP + 멱등성 ★ (두 번 실행 데모)","20분"],
    ["07–08","config/parser/db 분리 · 테스트(TDD)","25분"],
    ["09","멱등·매일 스냅샷 누적·백필","15분"],
    [{text:"10–11",options:{fill:{color:"E6FBF5"}}},{text:"클라우드 DB 연결 · cron 매일 수집 ★ (실습)",options:{fill:{color:"E6FBF5"}}},{text:"40분",options:{fill:{color:"E6FBF5"}}}],
  ];
  s.addTable(rows, { x:M, y:1.7, w:W-2*M, colW:[1.7, 8.73, 1.5], rowH:0.52, fontFace:KR, fontSize:14, color:INK,
    valign:"middle", border:{pt:0.5,color:HAIR}, align:"left" });
  s.addText("합계 약 2.5–3시간 · 라이브 데모 중심, 학생이 직접 타이핑하게.", { x:M, y:6.35, w:W-2*M, h:0.4, fontFace:KR, fontSize:13, italic:true, color:MUTED });
  foot(s);
}

// ════════ 5. 운영 팁 ════════
{ const s = p.addSlide(); light(s); head(s, "HOW", "강의 운영 팁");
  const tips = [
    ["라이브 데모 중심","강사가 한 줄씩 실행 → 학생이 따라 타이핑. 출력을 함께 본다."],
    ["체크포인트마다 확인","각 레슨 끝 '여기까지 되면 OK' 기준으로 전원 진도 맞추기."],
    ["함정은 미리 경고","proframeWeb 대문자·휴장일 0건·한글 인코딩 등은 터지기 전에 짚기."],
    ["'왜'를 먼저","명령보다 개념. '왜 POST?' '왜 멱등성?'을 먼저 묻고 답하게."],
  ];
  tips.forEach((t,i)=>{
    const y = 1.95 + i*1.18;
    s.addShape(p.shapes.OVAL, { x:M, y, w:0.66, h:0.66, fill:{color:DARK} });
    s.addText(String(i+1), { x:M, y, w:0.66, h:0.66, fontFace:MONO, fontSize:20, bold:true, color:MINT, align:"center", valign:"middle", margin:0 });
    s.addText(t[0], { x:M+0.95, y:y-0.02, w:10.8, h:0.45, fontFace:KR, fontSize:17, bold:true, color:INK, margin:0 });
    s.addText(t[1], { x:M+0.95, y:y+0.42, w:10.8, h:0.55, fontFace:KR, fontSize:13.5, color:MUTED, margin:0 });
  });
  foot(s);
}

// ════════ 6. SECTION Part 1 ════════
{ const s = p.addSlide(); dark(s);
  s.addText("PART 1", { x:M, y:2.5, w:11, h:0.7, fontFace:MONO, fontSize:22, bold:true, color:MINT, charSpacing:3 });
  s.addText("로컬에서 크롤러 만들기", { x:M, y:3.2, w:11.5, h:1.0, fontFace:KR, fontSize:40, bold:true, color:WHITE });
  s.addText("레슨 00–09 · HTTP부터 멱등·자동화까지", { x:M, y:4.4, w:11.5, h:0.5, fontFace:KR, fontSize:17, color:ICE });
}

// ════════ 7. 00–02 개념 ════════
{ const s = p.addSlide(); light(s); head(s, "00–02", "개념: 웹은 데이터를 어떻게 주나");
  s.addText([
    {text:"HTTP = 요청·응답의 대화. ", options:{bold:true,color:INK,breakLine:true}},
    {text:"크롤링 = 브라우저 대신 코드가 그 대화를 한다.", options:{color:MUTED,breakLine:true}},
    {text:" ", options:{breakLine:true}},
    {text:"KOFIA는 화면이 비고 뒤에서 XHR로 데이터를 받아온다", options:{bold:true,color:INK,breakLine:true}},
    {text:"→ 그래서 우리는 그 '뒤의 요청'을 그대로 흉내 낸다 (POST + XML).", options:{color:MUTED}},
  ], { x:M, y:1.9, w:6.6, h:2.6, fontFace:KR, fontSize:15.5, lineSpacingMultiple:1.25, valign:"top" });
  code(s, 7.5, 1.95, 5.1, 3.3, [
    [{t:"# 개발자도구 → Network 탭에서 관찰", c:CMT}],
    [{t:"POST ", c:MINT},{t:"/proframeWeb/XMLSERVICES/"}],
    [],
    [{t:"<pfmSvcName>", c:CMT},{t:"DISFundStdPriceSO"}],
    [{t:"<tmpV30>", c:CMT},{t:"20260610"},{t:" </tmpV30>", c:CMT}],
    [{t:"<tmpV11></tmpV11>", c:CMT},{t:"  ← 비우면 전체"}],
    [],
    [{t:"→ 응답: <selectMeta> 가 펀드 1개", c:MINT}],
  ], 13);
  s.addText("강의 포인트: '왜 GET이 아니라 POST인가'를 학생이 관찰로 깨닫게.", { x:M, y:5.5, w:W-2*M, h:0.4, fontFace:KR, fontSize:13, italic:true, color:MUTED });
  foot(s);
  s.addNotes("타이밍 10분. 데모: 브라우저 F12 Network에서 실제 XHR을 같이 본다. 핵심 질문: 화면은 비었는데 표는 어디서 오나? → XHR → 그래서 POST를 흉내낸다.");
}

// ════════ 8. 03 첫 크롤 ════════
{ const s = p.addSlide(); light(s); head(s, "03", "첫 크롤 — KOFIA에 POST해서 받기");
  code(s, M, 1.9, 7.2, 3.6, [
    [{t:"import requests", c:MINT}],
    [{t:'URL = "https://dis.kofia.or.kr/proframeWeb/XMLSERVICES/"'}],
    [{t:"body = ", c:MINT},{t:'"<message>...DISFundStdPriceSO..."'}],
    [],
    [{t:"r = requests.", c:MINT},{t:"post(URL, data=body.encode(),"}],
    [{t:'           headers={"Content-Type":"application/xml"})'}],
    [{t:'print(r.text.count("<selectMeta>"), "개")', c:MINT}],
    [],
    [{t:"# → 26,000여 펀드를 한 번에 수신", c:CMT}],
  ], 12.5);
  callout(s, 8.6, 2.0, 4.05, 1.5, AMBER, "⚠ 함정", "proframeWeb 의 대문자 W! 소문자면 307→에러로 '0건'.");
  callout(s, 8.6, 3.7, 4.05, 1.5, MINT, "체크포인트", "받은 펀드 수가 출력되면 OK. 0건이면 날짜/대소문자 점검.");
  foot(s);
  s.addNotes("타이밍 10분. 라이브로 crawl_v1.py 실행. 일부러 소문자 proframeweb로 0건을 보여주고 대문자로 고치는 시연이 강력함.");
}

// ════════ 9. 04–05 파싱·저장 ════════
{ const s = p.addSlide(); light(s); head(s, "04–05", "파싱 → 저장");
  s.addText("XML에서 값 뽑기 (parse)", { x:M, y:1.85, w:6, h:0.4, fontFace:KR, fontSize:15, bold:true, color:TEAL });
  code(s, M, 2.25, 6.0, 2.9, [
    [{t:"for el in root.iter():", c:MINT}],
    [{t:'  if local(el.tag)=="selectMeta":'}],
    [{t:"    code = el.find tmpV12   ", c:CMT},{t:"# 펀드코드"}],
    [{t:"    name = el.find tmpV2    ", c:CMT},{t:"# 펀드명"}],
    [{t:"    nav  = el.find tmpV6    ", c:CMT},{t:"# 기준가"}],
    [{t:'  if "TDF" in name: keep()  ', c:MINT},{t:"# TDF만"}],
  ], 12);
  s.addText("SQLite에 저장 (save)", { x:7.1, y:1.85, w:6, h:0.4, fontFace:KR, fontSize:15, bold:true, color:TEAL });
  code(s, 7.1, 2.25, 5.5, 2.9, [
    [{t:"con = sqlite3.", c:MINT},{t:'connect("tdf.db")'}],
    [{t:"con.execute(", c:MINT},{t:'"CREATE TABLE ...")'}],
    [{t:"con.execute(", c:MINT},{t:'"INSERT ... VALUES(?,?)")'}],
    [{t:"con.commit()", c:MINT}],
    [],
    [{t:"# 파일 하나가 곧 DB", c:CMT}],
  ], 12);
  callout(s, M, 5.45, 11.6, 0.95, MINT, "강의 포인트", "여기까지가 '크롤링 → DB 연결'의 로컬 버전. Part 2에서 이게 클라우드 서버 위에서 똑같이 일어난다.");
  foot(s);
}

// ════════ 10. 06 MVP ★ ════════
{ const s = p.addSlide(); light(s); head(s, "06 ★", "한 파일 MVP + 멱등성 (핵심)");
  code(s, M, 1.95, 7.2, 2.9, [
    [{t:"CREATE TABLE tdf_nav (", c:CODETX}],
    [{t:"  fund_code, base_date, nav, aum,"}],
    [{t:"  PRIMARY KEY (fund_code, base_date)", c:MINT},{t:"  # 한 펀드×한 날"}],
    [{t:")"}],
    [{t:"INSERT ... ", c:CODETX},{t:"ON CONFLICT DO UPDATE", c:MINT},{t:"  # = upsert"}],
  ], 13);
  callout(s, M, 5.1, 7.2, 1.2, MINT, "핵심", "PK + upsert = 멱등성. 몇 번 실행해도 중복이 안 쌓인다.");
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:8.6, y:1.95, w:4.05, h:4.35, fill:{color:DARK}, rectRadius:0.08, shadow: sh() });
  s.addText("데모: 두 번 실행", { x:8.8, y:2.2, w:3.65, h:0.45, fontFace:KR, fontSize:16, bold:true, color:MINT, margin:0 });
  s.addText([
    {text:"1차 실행 → 1,950 행", options:{color:CODETX, breakLine:true}},
    {text:"2차 실행 → 1,950 행", options:{color:CODETX, breakLine:true}},
    {text:" ", options:{breakLine:true}},
    {text:"= 행수 그대로!", options:{color:MINT, bold:true, breakLine:true}},
    {text:" ", options:{breakLine:true}},
    {text:"이래서 매일 자동화가", options:{color:ICE, breakLine:true}},
    {text:"안전하다 (재시도 OK).", options:{color:ICE}},
  ], { x:8.8, y:2.8, w:3.65, h:3.3, fontFace:KR, fontSize:15, lineSpacingMultiple:1.2, valign:"top", margin:0 });
  foot(s);
  s.addNotes("타이밍 20분. 가장 중요한 개념 슬라이드. tdf_onefile.py를 두 번 실행해 행수가 그대로임을 보인다. 그다음 PK 줄을 지우고 두 배가 되는 것도 보여주면 멱등성이 각인됨.");
}

// ════════ 11. 07–08 ════════
{ const s = p.addSlide(); light(s); head(s, "07–08", "책임별 분리 · 테스트(TDD)");
  card(s, M, 1.95, 5.85, 4.3);
  s.addText("07 · 리팩터링 — 왜 쪼개나", { x:M+0.3, y:2.2, w:5.3, h:0.45, fontFace:KR, fontSize:16, bold:true, color:INK, margin:0 });
  s.addText([
    {text:"한 파일이 커지면: 변경에 약함·테스트 어려움·재사용 불가", options:{color:MUTED, breakLine:true}},
    {text:" ", options:{breakLine:true}},
    {text:"config", options:{bold:true,color:TEAL}},{text:" (변하기 쉬운 것) · ", options:{color:MUTED}},
    {text:"parsers", options:{bold:true,color:TEAL}},{text:" (순수함수)", options:{color:MUTED, breakLine:true}},
    {text:"db", options:{bold:true,color:TEAL}},{text:" (저장) · ", options:{color:MUTED}},
    {text:"run", options:{bold:true,color:TEAL}},{text:" (지휘자)로 분리", options:{color:MUTED}},
  ], { x:M+0.3, y:2.75, w:5.3, h:3.3, fontFace:KR, fontSize:14, lineSpacingMultiple:1.25, valign:"top", margin:0 });
  card(s, 6.85, 1.95, 5.75, 4.3);
  s.addText("08 · TDD — 순수함수 테스트", { x:7.15, y:2.2, w:5.2, h:0.45, fontFace:KR, fontSize:16, bold:true, color:INK, margin:0 });
  code(s, 7.15, 2.75, 5.15, 2.0, [
    [{t:"def test_parse_number():", c:MINT}],
    [{t:'  assert num("1,927.46")==1927.46'}],
    [{t:'  assert num("")  is None'}],
    [{t:"# 네트워크 없이 픽스처로 검증", c:CMT}],
  ], 11.5);
  s.addText("분리했더니 → 파싱만 떼어 빠르게 시험 가능 (보상)", { x:7.15, y:4.95, w:5.2, h:0.9, fontFace:KR, fontSize:13, color:MUTED, margin:0 });
  foot(s);
}

// ════════ 12. 09 ════════
{ const s = p.addSlide(); light(s); head(s, "09", "멱등 · 매일 스냅샷 누적 · 백필");
  s.addText("매일 실행 = 그날 스냅샷 1장을 시계열로 '추가'", { x:M, y:1.85, w:11.9, h:0.5, fontFace:KR, fontSize:17, bold:true, color:INK });
  const days = ["06-04","06-05","06-08","06-09","06-10"];
  days.forEach((d,i)=>{
    const x = M + i*1.5;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y:2.6, w:1.3, h:1.0, fill:{color: i==4?MINT:CARD}, rectRadius:0.08 });
    s.addText(d, { x, y:2.6, w:1.3, h:1.0, fontFace:MONO, fontSize:14, bold:true, color: i==4?DARK:TEAL, align:"center", valign:"middle", margin:0 });
    if(i<4) s.addText("+", { x:x+1.3, y:2.6, w:0.2, h:1.0, fontFace:KR, fontSize:16, color:MUTED, align:"center", valign:"middle", margin:0 });
  });
  s.addText("전체를 갈아엎는 게 아니라, 날짜가 한 줄씩 늘어 시계열이 된다.", { x:M, y:3.85, w:11.9, h:0.4, fontFace:KR, fontSize:13.5, color:MUTED });
  code(s, M, 4.45, 7.6, 1.5, [
    [{t:"# 과거를 한 번에 채우기 (영업일만, 휴장일 스킵)", c:CMT}],
    [{t:"python -m tdf_crawler.backfill ", c:MINT},{t:"--start 2024-01-01"}],
    [{t:"# 이미 받은 날은 건너뜀 → 중단해도 이어서", c:CMT}],
  ], 12.5);
  callout(s, 8.6, 4.45, 4.05, 1.5, MINT, "왜 중요", "여기서 배운 멱등·백필이 Part 2(클라우드 매일)의 토대.");
  foot(s);
}

// ════════ 13. SECTION Part 2 ════════
{ const s = p.addSlide(); dark(s);
  s.addText("PART 2", { x:M, y:2.4, w:11, h:0.7, fontFace:MONO, fontSize:22, bold:true, color:MINT, charSpacing:3 });
  s.addText("클라우드로 옮겨 매일 돌리기", { x:M, y:3.1, w:12, h:1.0, fontFace:KR, fontSize:38, bold:true, color:WHITE });
  s.addText("레슨 10–11 · 클라우드 DB 연결 → cron 매일 무인 수집", { x:M, y:4.3, w:12, h:0.5, fontFace:KR, fontSize:17, color:ICE });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:M, y:5.1, w:3.4, h:0.5, fill:{color:TEAL}, rectRadius:0.25 });
  s.addText("git은 안다고 가정", { x:M, y:5.1, w:3.4, h:0.5, fontFace:KR, fontSize:13, bold:true, color:WHITE, align:"center", valign:"middle", margin:0 });
}

// ════════ 14. 10 클라우드 DB 연결 ════════
{ const s = p.addSlide(); light(s); head(s, "10", "클라우드 DB — 크롤링 ↔ sqlite 연결 해부");
  const flow = [["fetch","KOFIA 요청"],["parse","XML→값"],["db.upsert","★ 저장"],["tdf.db","sqlite 파일"]];
  const bw=2.6, gap=0.5;
  flow.forEach((f,i)=>{
    const x = M + i*(bw+gap);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y:2.2, w:bw, h:1.35, fill:{color: i>=2?DARK:CARD}, rectRadius:0.08 });
    s.addText(f[0], { x, y:2.4, w:bw, h:0.5, fontFace:MONO, fontSize:16, bold:true, color: i>=2?MINT:TEAL, align:"center", margin:0 });
    s.addText(f[1], { x, y:2.9, w:bw, h:0.45, fontFace:KR, fontSize:13, color: i>=2?ICE:MUTED, align:"center", margin:0 });
    if(i<3) s.addText("→", { x:x+bw, y:2.2, w:gap, h:1.35, fontFace:KR, fontSize:20, bold:true, color:MUTED, align:"center", valign:"middle", margin:0 });
  });
  s.addText([
    {text:"한 번 실행 = (fund_code, base_date) 한 묶음 = 그날 스냅샷 1장", options:{bold:true,color:INK,breakLine:true}},
    {text:"VM의 독립 venv에서 실행 → DB가 '서버 안에' 생성된다 (로컬 환경과 무관).", options:{color:MUTED}},
  ], { x:M, y:4.1, w:11.9, h:1.1, fontFace:KR, fontSize:15, lineSpacingMultiple:1.25 });
  code(s, M, 5.3, 11.9, 1.1, [
    [{t:"ssh user@vm", c:MINT},{t:"  →  git clone … && python3 -m venv .venv && pip install -e ."}],
    [{t:"bash cloud_quickstart/run_week.sh", c:MINT},{t:"   # 1주일 적재 + 검증"}],
  ], 12.5);
  foot(s);
  s.addNotes("두려움 해소 포인트: VM의 venv는 로컬 윈도우 환경을 전혀 안 쓴다. 실제로 GCP VM에서 검증됨.");
}

// ════════ 15. 11 cron ════════
{ const s = p.addSlide(); light(s); head(s, "11", "cron으로 매일 자동 수집");
  s.addText("cron = 리눅스의 '시간표 비서'. crontab 한 줄을 분해해 보자:", { x:M, y:1.85, w:11.9, h:0.45, fontFace:KR, fontSize:15, color:INK });
  code(s, M, 2.45, 11.9, 0.7, [
    [{t:"0 8 * * * ", c:MINT},{t:"cd ~/tdf-crawler && .venv/bin/python -m tdf_crawler.run >> logs/crawl.log"}],
  ], 13);
  const parts = [["0","분"],["8","시"],["*","일"],["*","월"],["*","요일"]];
  parts.forEach((pt,i)=>{
    const x = M + i*1.35;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y:3.45, w:1.15, h:1.0, fill:{color:CARD}, rectRadius:0.08 });
    s.addText(pt[0], { x, y:3.55, w:1.15, h:0.5, fontFace:MONO, fontSize:20, bold:true, color:TEAL, align:"center", margin:0 });
    s.addText(pt[1], { x, y:4.05, w:1.15, h:0.35, fontFace:KR, fontSize:12, color:MUTED, align:"center", margin:0 });
  });
  callout(s, M, 4.75, 11.9, 1.0, MINT, "즉", "매일 08:00(KST)에 크롤러 1회 실행, 로그는 파일로 → 내가 안 켜도 매일 한 장씩 쌓인다.");
  foot(s);
}

// ════════ 16. ★ 시뮬레이션 ════════
{ const s = p.addSlide(); light(s); head(s, "11 ★", "수업 중 '여러 날' 시뮬레이션 (교육장치)");
  s.addText("cron은 본래 하루를 기다려야 보이죠. 날짜를 바꿔 연속 실행해 '매일 쌓임'을 즉석에서 재현:", { x:M, y:1.85, w:11.9, h:0.7, fontFace:KR, fontSize:15, color:INK });
  code(s, M, 2.65, 7.4, 2.0, [
    [{t:"for d in 06-08 06-09 06-10; ", c:MINT},{t:"do"}],
    [{t:"  python -m tdf_crawler.run ", c:CODETX},{t:"--date $d", c:MINT}],
    [{t:"done"}],
    [],
    [{t:"# nav_daily 날짜가 3개로 늘어남!", c:CMT}],
  ], 13);
  callout(s, 7.7, 2.65, 4.95, 0.95, MINT, "효과", "하루 안 기다리고도 '매일 수집'을 수업 안에서 완결.");
  callout(s, 7.7, 3.75, 4.95, 0.9, AMBER, "그다음", "같은 날 또 실행 → 행수 그대로 = 멱등 증명.");
  s.addText("마무리: 진짜 cron 등록 → '내일 날짜가 하나 더 늘었는지 확인'을 숙제로.", { x:M, y:5.0, w:11.9, h:0.5, fontFace:KR, fontSize:14, italic:true, color:MUTED });
  foot(s);
  s.addNotes("이 슬라이드가 11의 핵심 교육장치. --date로 어제·오늘을 연속 적재해 시계열이 자라는 걸 즉석에서 보여준다.");
}

// ════════ 17. cron 실전 + 함정 ════════
{ const s = p.addSlide(); light(s); head(s, "11", "cron 등록 실전 — 순서와 함정");
  code(s, M, 1.95, 7.3, 3.4, [
    [{t:"# 1) cron이 돌릴 명령을 먼저 1회 손검증", c:CMT}],
    [{t:"python -m tdf_crawler.run", c:MINT}],
    [{t:"# 2) 타임존·데몬·로그폴더", c:CMT}],
    [{t:"sudo timedatectl set-timezone Asia/Seoul", c:MINT}],
    [{t:"sudo systemctl enable --now cron", c:MINT}],
    [{t:"# 3) crontab 직접 설치(절대경로)", c:CMT}],
    [{t:'echo "0 8 * * * …run…" | crontab -', c:MINT}],
    [{t:"crontab -l", c:MINT},{t:"   # 등록 확인"}],
  ], 12);
  callout(s, 8.7, 1.95, 3.95, 1.65, AMBER, "⚠ 함정", "set -e 안에서 ( crontab -l | grep…) 쓰면 빈 crontab일 때 grep 실패로 '빈 crontab' 설치됨.");
  callout(s, 8.7, 3.75, 3.95, 1.6, MINT, "해결", 'echo "…" | crontab - 로 직접 설치. 로그는 %를 피해 단일 crawl.log.');
  foot(s);
  s.addNotes("실제로 밟은 함정. walkthrough_gcp_plink.md에 기록. 강사는 crontab -l이 비면 이 함정을 의심하라고 안내.");
}

// ════════ 18. 실제 검증됨 ════════
{ const s = p.addSlide(); light(s); head(s, "PROOF", "실제로 GCP VM에서 검증됨");
  const stats = [["1,950+","수집된 TDF 펀드(클래스)"],["9,757","적재된 nav 행 (5영업일)"],["08:00","매일 KST cron 자동 실행"]];
  const cw=(W-2*M-1.0)/3;
  stats.forEach((st,i)=>{
    const x=M+i*(cw+0.5);
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y:2.1, w:cw, h:2.9, fill:{color: i==2?DARK:CARD}, rectRadius:0.1, shadow: sh() });
    s.addText(st[0], { x, y:2.7, w:cw, h:1.1, fontFace:KR, fontSize:50, bold:true, color: i==2?MINT:TEAL, align:"center", margin:0 });
    s.addText(st[1], { x:x+0.25, y:3.95, w:cw-0.5, h:0.8, fontFace:KR, fontSize:14, color: i==2?ICE:MUTED, align:"center", margin:0 });
  });
  s.addText("Ubuntu VM · Docker 없이 venv 경로 · 코드는 SSH로 직접 업로드 → 1주일 DB 구축 + cron 가동.", { x:M, y:5.4, w:W-2*M, h:0.5, fontFace:KR, fontSize:13.5, italic:true, color:MUTED, align:"center" });
  foot(s);
}

// ════════ 19. 체크포인트 ════════
{ const s = p.addSlide(); light(s); head(s, "CHECK", "단계별 체크포인트 (여기까지 되면 OK)");
  const rows = [
    [{text:"레슨",options:{bold:true,color:WHITE,fill:{color:DARK}}},{text:"학생이 도달해야 할 상태",options:{bold:true,color:WHITE,fill:{color:DARK}}}],
    ["03","POST 응답에서 펀드 수가 출력된다"],
    ["05","tdf.db 파일이 생기고 SELECT로 행이 보인다"],
    ["06","두 번 실행해도 행수가 그대로(멱등)"],
    ["08","pytest 가 통과한다(PASSED)"],
    ["10","VM에서 실행 → data/tdf.db가 '서버에' 생긴다"],
    ["11","crontab -l 에 한 줄, --date 연속 실행으로 날짜가 는다"],
  ];
  s.addTable(rows, { x:M, y:1.75, w:W-2*M, colW:[1.4, 10.53], rowH:0.62, fontFace:KR, fontSize:14.5, color:INK,
    valign:"middle", border:{pt:0.5,color:HAIR} });
  foot(s);
}

// ════════ 20. 함정 모음 ════════
{ const s = p.addSlide(); light(s); head(s, "PITFALL", "흔한 함정 모음 (강사 치트시트)");
  const traps = [
    ["proframeweb (소문자)","대문자 W! → proframeWeb. 아니면 307→에러 0건."],
    ["평일인데 0건","휴장일이면 정상. 전부 0이면 구조 변경 의심."],
    ["한글 출력 깨짐(윈도우)","sys.stdout.reconfigure(encoding='utf-8')"],
    ["VM에 pip 없음","sudo apt install python3-venv python3-pip"],
    ["crontab -l 이 빔","echo \"…\" | crontab - 로 직접 설치(set -e+grep 함정)"],
  ];
  traps.forEach((t,i)=>{
    const y=1.95+i*0.92;
    s.addShape(p.shapes.OVAL, { x:M, y:y+0.05, w:0.32, h:0.32, fill:{color:AMBER} });
    s.addText(t[0], { x:M+0.55, y, w:4.7, h:0.45, fontFace:KR, fontSize:15, bold:true, color:INK, margin:0 });
    s.addText(t[1], { x:5.5, y, w:7.1, h:0.45, fontFace:KR, fontSize:13.5, color:MUTED, margin:0, valign:"middle" });
  });
  foot(s);
}

// ════════ 21. 숙제 & 더 ════════
{ const s = p.addSlide(); light(s); head(s, "NEXT", "숙제 & 더 배우기");
  const items = [
    ["숙제","cron 등록 후 '내일 verify로 날짜 1개 증가' 확인 · exercises 7–9"],
    ["더 깊이","역할별 docs/ (설계자·개발자·운영자·분석가)"],
    ["데이터 사전","docs/schema (ER 다이어그램 + 컬럼 의미)"],
    ["실제 배포 기록","docs/deploy/walkthrough_gcp_plink.md (재현 명령 그대로)"],
  ];
  items.forEach((it,i)=>{
    const y=1.95+i*1.12;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x:M, y, w:2.1, h:0.7, fill:{color:DARK}, rectRadius:0.08 });
    s.addText(it[0], { x:M, y, w:2.1, h:0.7, fontFace:KR, fontSize:14, bold:true, color:MINT, align:"center", valign:"middle", margin:0 });
    s.addText(it[1], { x:M+2.4, y, w:9.7, h:0.7, fontFace:KR, fontSize:14.5, color:INK, valign:"middle", margin:0 });
  });
  foot(s);
}

// ════════ 22. CLOSING ════════
{ const s = p.addSlide(); dark(s);
  s.addText("정리", { x:M, y:1.7, w:11, h:0.5, fontFace:MONO, fontSize:15, color:MINT, charSpacing:3 });
  s.addText("로컬에서 만들어,\n클라우드에서 매일.", { x:M, y:2.3, w:12, h:2.0, fontFace:KR, fontSize:42, bold:true, color:WHITE, lineSpacingMultiple:1.05 });
  s.addText("HTTP → 파싱 → 저장 → 한 파일 MVP → 분리 → 테스트 → 멱등·백필 → 클라우드 DB → cron 매일", { x:M, y:4.6, w:12, h:0.5, fontFace:KR, fontSize:15, color:ICE });
  s.addShape(p.shapes.LINE, { x:M, y:5.4, w:4, h:0, line:{color:TEAL, width:2} });
  s.addText("team_learning · cloud_quickstart · docs/", { x:M, y:5.7, w:12, h:0.4, fontFace:MONO, fontSize:13, color:CMT });
}

p.writeFile({ fileName: "instructor_slides.pptx" }).then(f => console.log("WROTE", f));
