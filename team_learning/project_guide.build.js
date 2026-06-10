const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";
p.author = "team_learning";
p.title = "TDF 크롤링→DB 적재 프로젝트 — 전체 가이드(따라하기)";

const DARK="0E2A3B", TEAL="1C7293", MINT="02C39A", AMBER="F2A23C", WHITE="FFFFFF",
      INK="1E293B", MUTED="64748B", CODETX="E6EDF3", CMT="7FA9BE", CARD="F1F5F9",
      HAIR="E2E8F0", ICE="CADCFC";
const KR="Malgun Gothic", MONO="Consolas";
const W=13.33, H=7.5, M=0.7;
const sh=()=>({type:"outer",color:"0B1F2C",blur:9,offset:3,angle:90,opacity:0.18});
let pageNo=0;
const light=s=>s.background={color:WHITE};
const dark=s=>s.background={color:DARK};
function foot(s){ pageNo++;
  s.addText("TDF 프로젝트 가이드 · 따라하기", {x:M,y:H-0.42,w:6,h:0.3,fontFace:KR,fontSize:9,color:MUTED});
  s.addText(String(pageNo),{x:W-1.1,y:H-0.42,w:0.4,h:0.3,fontFace:MONO,fontSize:9,color:MUTED,align:"right"});
}
function head(s, chip, title, sub){
  const cw = chip.length>4?1.75:1.25;
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:M,y:0.5,w:cw,h:0.42,fill:{color:DARK},rectRadius:0.21});
  s.addText(chip,{x:M,y:0.5,w:cw,h:0.42,fontFace:MONO,fontSize:13,bold:true,color:MINT,align:"center",valign:"middle",margin:0});
  s.addText(title,{x:M+cw+0.2,y:0.42,w:W-M-cw-0.9,h:0.6,fontFace:KR,fontSize:26,bold:true,color:INK,valign:"middle"});
  if(sub) s.addText(sub,{x:M,y:1.16,w:W-2*M,h:0.4,fontFace:KR,fontSize:13,color:MUTED});
}
function code(s,x,y,w,h,lines,fs){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:DARK},rectRadius:0.08,shadow:sh()});
  const runs=[];
  lines.forEach(ln=>{
    if(ln.length===0){runs.push({text:" ",options:{breakLine:true}});return;}
    ln.forEach((seg,j)=>runs.push({text:seg.t,options:{color:seg.c||CODETX,breakLine:j===ln.length-1}}));
  });
  s.addText(runs,{x:x+0.22,y:y+0.16,w:w-0.44,h:h-0.32,fontFace:MONO,fontSize:fs||12.5,valign:"top",lineSpacingMultiple:1.06,margin:0});
}
function callout(s,x,y,w,h,color,label,body){
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:color==MINT?"E6FBF5":"FCEFD9"},line:{color,width:1},rectRadius:0.08});
  s.addText([{text:label+"  ",options:{bold:true,color}},{text:body,options:{color:INK}}],
    {x:x+0.2,y,w:w-0.4,h,fontFace:KR,fontSize:13,valign:"middle",margin:0});
}
const card=(s,x,y,w,h,c)=>s.addShape(p.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:c||CARD},rectRadius:0.08});
function section(num, kicker, title, sub){
  const s=p.addSlide(); dark(s);
  s.addShape(p.shapes.OVAL,{x:M,y:2.3,w:1.5,h:1.5,fill:{color:TEAL}});
  s.addText(num,{x:M,y:2.3,w:1.5,h:1.5,fontFace:KR,fontSize:46,bold:true,color:WHITE,align:"center",valign:"middle",margin:0});
  s.addText(kicker,{x:M+1.9,y:2.45,w:10,h:0.5,fontFace:MONO,fontSize:15,color:MINT,charSpacing:2});
  s.addText(title,{x:M+1.9,y:2.95,w:10.5,h:1.0,fontFace:KR,fontSize:34,bold:true,color:WHITE});
  if(sub) s.addText(sub,{x:M+1.9,y:4.05,w:10.5,h:0.5,fontFace:KR,fontSize:15,color:ICE});
  return s;
}

// ═══ 1. TITLE ═══
{ const s=p.addSlide(); dark(s);
  s.addText("학생용 따라하기 가이드 · PROJECT GUIDE",{x:M,y:1.45,w:11,h:0.4,fontFace:MONO,fontSize:14,color:MINT,charSpacing:2});
  s.addText("증권 TDF 크롤링 →\nSQLite DB 적재 프로젝트",{x:M,y:1.95,w:12,h:2.0,fontFace:KR,fontSize:44,bold:true,color:WHITE,lineSpacingMultiple:1.02});
  s.addText("데이터 소스 찾기부터 코드 작성·업로드·클라우드 매일 자동화까지, 전 과정을 따라 만든다",
    {x:M,y:4.25,w:12,h:0.5,fontFace:KR,fontSize:17,color:ICE});
  s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:M,y:5.15,w:9.4,h:0.62,fill:{color:MINT},rectRadius:0.31});
  s.addText("KOFIA 공시  →  파싱  →  SQLite  →  매일 cron  →  클라우드 DB",
    {x:M,y:5.15,w:9.4,h:0.62,fontFace:KR,fontSize:15,bold:true,color:DARK,align:"center",valign:"middle",margin:0});
}

// ═══ 2. 무엇을 만드나 ═══
{ const s=p.addSlide(); light(s); head(s,"GOAL","무엇을 만드나");
  s.addText("국내 TDF(은퇴목표 펀드)의 기준가·설정액·순자산·보수를 매일 KOFIA에서 수집해 SQLite에 시계열로 쌓는다.",
    {x:M,y:1.85,w:11.9,h:0.7,fontFace:KR,fontSize:16,color:INK,lineSpacingMultiple:1.2});
  const flow=[["KOFIA 공시","데이터 출처"],["크롤러","받기·파싱"],["SQLite","적재(시계열)"],["cron·클라우드","매일 무인"]];
  const bw=2.6,gap=0.5;
  flow.forEach((f,i)=>{const x=M+i*(bw+gap);
    card(s,x,2.75,bw,1.4, i==3?DARK:CARD);
    s.addText(f[0],{x,y:2.95,w:bw,h:0.5,fontFace:KR,fontSize:16,bold:true,color:i==3?MINT:TEAL,align:"center",margin:0});
    s.addText(f[1],{x,y:3.5,w:bw,h:0.45,fontFace:KR,fontSize:13,color:i==3?ICE:MUTED,align:"center",margin:0});
    if(i<3) s.addText("→",{x:x+bw,y:2.75,w:gap,h:1.4,fontFace:KR,fontSize:20,bold:true,color:MUTED,align:"center",valign:"middle",margin:0});
  });
  callout(s,M,4.6,11.9,1.0,MINT,"최종 결과","클라우드 VM에서 매일 08:00 자동으로 한 날치가 쌓이는 살아있는 데이터 DB.");
  foot(s);
}

// ═══ 3. 전체 여정 (roadmap) ═══
{ const s=p.addSlide(); light(s); head(s,"ROADMAP","전체 여정 — 5단계");
  const ph=[["①","데이터 소스 찾기","KOFIA 실제 엔드포인트·요청 형식 파악"],
            ["②","크롤러 작성","받기(fetch) → 파싱(parse) → TDF 필터"],
            ["③","DB 적재","스키마 설계 + 멱등 upsert"],
            ["④","자동화·과거 누적","매일 실행 + backfill + 테스트"],
            ["⑤","클라우드 배포","코드 업로드 → VM 실행 → cron 매일"]];
  ph.forEach((q,i)=>{const y=1.85+i*0.92;
    s.addShape(p.shapes.OVAL,{x:M,y:y,w:0.62,h:0.62,fill:{color:i==4?MINT:DARK}});
    s.addText(q[0],{x:M,y:y,w:0.62,h:0.62,fontFace:KR,fontSize:20,bold:true,color:i==4?DARK:MINT,align:"center",valign:"middle",margin:0});
    s.addText(q[1],{x:M+0.9,y:y-0.02,w:4.6,h:0.45,fontFace:KR,fontSize:17,bold:true,color:INK,valign:"middle",margin:0});
    s.addText(q[2],{x:M+5.5,y:y,w:6.6,h:0.6,fontFace:KR,fontSize:14,color:MUTED,valign:"middle",margin:0});
  });
  foot(s);
}

// ═══ 4. 준비물 ═══
{ const s=p.addSlide(); light(s); head(s,"SETUP","준비물 (5분)");
  s.addText("코어는 표준 라이브러리 + requests 뿐. 무겁지 않다.",{x:M,y:1.85,w:11.9,h:0.4,fontFace:KR,fontSize:15,color:INK});
  code(s,M,2.35,7.4,2.5,[
    [{t:"python --version",c:MINT},{t:"   # 3.10+"}],
    [{t:"pip install requests",c:MINT},{t:"   # 받기"}],
    [{t:"pip install pytest",c:MINT},{t:"     # 테스트(선택)"}],
    [],
    [{t:"# sqlite3·xml 은 파이썬 내장 → 설치 불필요",c:CMT}],
  ],13);
  callout(s,8.6,2.35,4.05,1.1,MINT,"클라우드용","VM(리눅스) · SSH 접속 · git 또는 scp (Part ⑤)");
  callout(s,8.6,3.6,4.05,1.25,AMBER,"윈도우 팁","한글 출력 깨지면 sys.stdout.reconfigure(encoding='utf-8')");
  foot(s);
}

// ═══ 5. 프로젝트 구조 미리보기 ═══
{ const s=p.addSlide(); light(s); head(s,"MAP","프로젝트 구조 미리보기");
  s.addText("우리가 만들 목표 모양. 책임별로 파일이 나뉜다(왜 나누는지는 ④에서).",{x:M,y:1.85,w:11.9,h:0.4,fontFace:KR,fontSize:14,color:MUTED});
  code(s,M,2.3,6.7,4.2,[
    [{t:"tdf_crawler/",c:MINT}],
    [{t:"  config.py     ",c:CODETX},{t:"# 엔드포인트·컬럼맵",c:CMT}],
    [{t:"  fetchers/     ",c:CODETX},{t:"# 받기(POST)",c:CMT}],
    [{t:"  parsers.py    ",c:CODETX},{t:"# XML→레코드(순수)",c:CMT}],
    [{t:"  discovery.py  ",c:CODETX},{t:"# TDF 필터",c:CMT}],
    [{t:"  db.py         ",c:CODETX},{t:"# 스키마·upsert",c:CMT}],
    [{t:"  run.py        ",c:CODETX},{t:"# 일일 실행 CLI",c:CMT}],
    [{t:"  backfill.py   ",c:CODETX},{t:"# 과거 누적",c:CMT}],
  ],12.5);
  const right=[["tests/","픽스처 기반 테스트"],["cloud_quickstart/","1주일 클라우드 빌드"],["docs/","역할별·스키마 문서"],["data/tdf.db","결과 DB(시계열)"]];
  right.forEach((r,i)=>{const y=2.35+i*1.0;
    card(s,7.7,y,4.95,0.82);
    s.addText(r[0],{x:7.9,y:y,w:2.2,h:0.82,fontFace:MONO,fontSize:13,bold:true,color:TEAL,valign:"middle",margin:0});
    s.addText(r[1],{x:9.9,y:y,w:2.6,h:0.82,fontFace:KR,fontSize:12.5,color:MUTED,valign:"middle",margin:0});
  });
  foot(s);
}

// ═══ 6. SECTION ① ═══
section("①","PHASE 1 · 데이터 소스 찾기","어디서·어떻게 데이터를 받나","KOFIA 공시 사이트의 실제 요청을 관찰한다");

// ═══ 7. 실제 엔드포인트 ═══
{ const s=p.addSlide(); light(s); head(s,"①","KOFIA 실제 엔드포인트 파악");
  s.addText("브라우저 개발자도구(F12) → Network 에서 화면이 보내는 실제 POST를 관찰한다.",{x:M,y:1.85,w:11.9,h:0.4,fontFace:KR,fontSize:14,color:INK});
  code(s,M,2.3,7.4,3.3,[
    [{t:"POST ",c:MINT},{t:"https://dis.kofia.or.kr/proframeWeb/XMLSERVICES/"}],
    [],
    [{t:"<pfmSvcName>",c:CMT},{t:"DISFundStdPriceSO"},{t:"</pfmSvcName>",c:CMT}],
    [{t:"<tmpV30>",c:CMT},{t:"20260610"},{t:"</tmpV30>",c:CMT},{t:"  # 날짜"}],
    [{t:"<tmpV11></tmpV11>",c:CMT},{t:"          # 운용사(빈값=전체)"}],
    [],
    [{t:"→ 응답: <selectMeta> 가 펀드 1개, tmpV6=기준가…",c:MINT}],
  ],12.5);
  callout(s,8.7,2.3,3.95,1.55,AMBER,"⚠ 핵심 함정","proframeWeb 의 대문자 W! 소문자는 죽은 주소 → 307→에러로 '0건'.");
  callout(s,8.7,4.05,3.95,1.55,MINT,"배운 점","GET이 아니라 POST+XML. 빈 운용사로 전체 2.6만 펀드를 한 번에.");
  foot(s);
}

// ═══ 8. SECTION ② ═══
section("②","PHASE 2 · 크롤러 작성","받기 → 파싱 → 필터","요청을 흉내 내고, 응답에서 값을 뽑고, TDF만 남긴다");

// ═══ 9. fetch ═══
{ const s=p.addSlide(); light(s); head(s,"②-a","받기 (fetch) — POST 요청");
  code(s,M,1.95,11.9,2.7,[
    [{t:"import requests",c:MINT}],
    [{t:'body = f"""<message><proframeHeader>'},{t:"...DISFundStdPriceSO...",c:CMT},{t:'</proframeHeader>'}],
    [{t:'  <DISCondFuncDTO><tmpV30>{date}</tmpV30><tmpV11></tmpV11></DISCondFuncDTO></message>"""'}],
    [{t:"r = requests.post",c:MINT},{t:'(URL, data=body.encode("utf-8"),'}],
    [{t:'                  headers={"Content-Type":"application/xml; charset=UTF-8"})'}],
  ],12);
  callout(s,M,4.95,11.9,0.95,MINT,"포인트","본문은 .encode('utf-8')로 보낸다(한글 안전). 실제 코드는 fetchers/http_fetcher.py·base.py.");
  foot(s);
}

// ═══ 10. parse ═══
{ const s=p.addSlide(); light(s); head(s,"②-b","파싱 (parse) — XML→레코드 (순수함수)");
  code(s,M,1.95,7.4,3.5,[
    [{t:"from xml.etree import ElementTree as ET",c:MINT}],
    [{t:"root = ET.fromstring(xml_bytes)"}],
    [{t:"for el in root.iter():",c:MINT}],
    [{t:'  if local(el.tag)=="selectMeta":'}],
    [{t:"    code = el/tmpV12   ",c:CMT},{t:"# 펀드코드"}],
    [{t:"    name = el/tmpV2    ",c:CMT},{t:"# 펀드명"}],
    [{t:"    nav  = el/tmpV6    ",c:CMT},{t:"# 기준가(원)"}],
    [{t:"    aum  = el/tmpV5    ",c:CMT},{t:"# 설정액(백만원)"}],
  ],12);
  callout(s,8.7,1.95,3.95,1.6,MINT,"왜 순수함수","네트워크·DB 없이 bytes→레코드. 저장된 응답(픽스처)으로 테스트 가능.");
  callout(s,8.7,3.7,3.95,1.75,AMBER,"위치 매핑","tmpV1..N 의 의미는 config.py 한 곳에. KOFIA가 바뀌면 거기만 수정.");
  foot(s);
}

// ═══ 11. discovery ═══
{ const s=p.addSlide(); light(s); head(s,"②-c","TDF만 골라내기 (discovery)");
  code(s,M,1.95,7.4,2.3,[
    [{t:"def is_tdf(fund):",c:MINT}],
    [{t:'  kw = ("TDF","TARGET DATE","타겟데이트")'}],
    [{t:"  return any(k in fund.name.upper() ",c:MINT},{t:"for k in kw)"}],
    [],
    [{t:"# 전체 2.6만 → TDF 약 1,950개로 압축",c:CMT}],
  ],12.5);
  callout(s,8.7,1.95,3.95,2.3,MINT,"배운 점","간단한 이름 키워드 필터가 곧 'TDF 탐색'. 실제: discovery.py");
  s.addText("이제 받기·파싱·필터가 갖춰졌다 → 저장(③)으로.",{x:M,y:4.55,w:11.9,h:0.5,fontFace:KR,fontSize:14,italic:true,color:MUTED});
  foot(s);
}

// ═══ 12. SECTION ③ ═══
section("③","PHASE 3 · DB 적재","SQLite에 시계열로 쌓기","스키마를 정하고, 중복 없이 매일 한 장씩 누적");

// ═══ 13. 스키마 ═══
{ const s=p.addSlide(); light(s); head(s,"③-a","스키마 설계 — 키는 (펀드 × 날짜)");
  const tbl=[["funds","펀드 정보(코드·이름·운용사·만기연도)"],
             ["nav_daily","기준가·설정액·순자산  (일별)"],
             ["flows_daily","순유입 = 설정액 증감  (파생)"],
             ["fees","합성총보수·운용·판매보수  (월별)"],
             ["crawl_runs","실행 로그(상태·건수)"]];
  tbl.forEach((t,i)=>{const y=1.95+i*0.82;
    card(s,M,y,11.9,0.68, i==0?CARD:CARD);
    s.addText(t[0],{x:M+0.25,y:y,w:2.6,h:0.68,fontFace:MONO,fontSize:14,bold:true,color:TEAL,valign:"middle",margin:0});
    s.addText(t[1],{x:M+3.0,y:y,w:8.6,h:0.68,fontFace:KR,fontSize:14,color:INK,valign:"middle",margin:0});
  });
  callout(s,M,6.1,11.9,0.7,MINT,"공통 키","측정 3종은 PRIMARY KEY (fund_code, base_date) — 펀드 한 개 × 날짜 한 개 = 한 행.");
  foot(s);
}

// ═══ 14. 멱등 upsert ═══
{ const s=p.addSlide(); light(s); head(s,"③-b","멱등 upsert — 매일 안전하게 ★");
  code(s,M,1.95,7.4,2.7,[
    [{t:"INSERT INTO nav_daily ",c:CODETX},{t:"(...) VALUES (...)"}],
    [{t:"ON CONFLICT",c:MINT},{t:"(fund_code, base_date)"}],
    [{t:"DO UPDATE SET ",c:MINT},{t:"nav=excluded.nav, ..."}],
    [],
    [{t:"# 같은 키면 덮어쓰기 → 중복 0",c:CMT}],
  ],12.5);
  callout(s,8.7,1.95,3.95,2.7,MINT,"멱등성","몇 번 실행해도 행수 그대로. 재시도·매일 실행이 안전해지는 핵심. 실제: db.py");
  s.addText("→ 같은 날 두 번 돌려도, 실패 후 다시 돌려도 데이터가 망가지지 않는다.",{x:M,y:5.0,w:11.9,h:0.5,fontFace:KR,fontSize:14,italic:true,color:MUTED});
  foot(s);
}

// ═══ 15. 로컬 실행 ═══
{ const s=p.addSlide(); light(s); head(s,"③-c","로컬에서 실행 & 확인");
  code(s,M,1.95,11.9,2.5,[
    [{t:"pip install -e .",c:MINT},{t:"                         # 패키지 설치"}],
    [{t:"python -m tdf_crawler.run ",c:MINT},{t:"--date 2026-06-10   # 그날 수집·적재"}],
    [],
    [{t:'python -c "import sqlite3; print(sqlite3.connect(',c:MINT},{t:"'data/tdf.db')"}],
    [{t:"   .execute('SELECT COUNT(*) FROM nav_daily').fetchone())",c:CODETX},{t:'"'}],
  ],12);
  callout(s,M,4.75,11.9,1.0,MINT,"체크포인트","data/tdf.db 가 생기고 nav_daily 행수가 출력되면 ③ 성공. (한 번 실행=그날 스냅샷 1장)");
  foot(s);
}

// ═══ 16. SECTION ④ ═══
section("④","PHASE 4 · 자동화 & 과거 누적","매일·과거를 안전하게","backfill로 과거를 채우고, 테스트로 안전망을 친다");

// ═══ 17. backfill ═══
{ const s=p.addSlide(); light(s); head(s,"④-a","과거 전체 누적 (backfill)");
  code(s,M,1.95,11.9,1.9,[
    [{t:"python -m tdf_crawler.backfill ",c:MINT},{t:"--start 2024-01-01"}],
    [{t:"# 영업일만 수집 · 휴장일 자동 스킵 · 이미 받은 날은 건너뜀(resume)",c:CMT}],
    [{t:"# 과거→현재 순으로 적재 후 순유입(Δ설정액) 일괄 재계산",c:CMT}],
  ],12.5);
  const days=["06-04","06-05","06-08","06-09","06-10"];
  days.forEach((d,i)=>{const x=M+i*1.45;
    card(s,x,4.2,1.25,0.9,i==4?MINT:CARD);
    s.addText(d,{x,y:4.2,w:1.25,h:0.9,fontFace:MONO,fontSize:13,bold:true,color:i==4?DARK:TEAL,align:"center",valign:"middle",margin:0});
    if(i<4) s.addText("+",{x:x+1.25,y:4.2,w:0.2,h:0.9,fontFace:KR,fontSize:15,color:MUTED,align:"center",valign:"middle",margin:0});
  });
  callout(s,8.0,4.2,4.6,0.9,MINT,"누적","날짜가 한 줄씩 늘어 시계열이 된다(덮어쓰기 아님).");
  foot(s);
}

// ═══ 18. 테스트 ═══
{ const s=p.addSlide(); light(s); head(s,"④-b","테스트로 안전망 (TDD)");
  code(s,M,1.95,7.4,2.5,[
    [{t:"python -m pytest -q",c:MINT}],
    [{t:"  ......................  50 passed",c:CODETX}],
    [],
    [{t:"# 픽스처(저장된 응답)로 네트워크 없이 검증",c:CMT}],
    [{t:"# 순수 파서 덕분에 빠르고 안정적",c:CMT}],
  ],12.5);
  callout(s,8.7,1.95,3.95,2.5,MINT,"왜 좋은가","코드를 고쳐도 'pytest' 한 줄로 안 깨졌는지 즉시 확인. 분리(②)의 보상.");
  s.addText("이제 로컬에서 만들기·자동화가 끝났다 → 클라우드로(⑤).",{x:M,y:4.8,w:11.9,h:0.5,fontFace:KR,fontSize:14,italic:true,color:MUTED});
  foot(s);
}

// ═══ 19. SECTION ⑤ ═══
section("⑤","PHASE 5 · 클라우드 배포","코드 올리고, VM에서 매일 돌리기","업로드 → 환경 구성 → 1주일 빌드 → cron 자동");

// ═══ 20. 코드 올리기 ═══
{ const s=p.addSlide(); light(s); head(s,"⑤-a","코드 올리기 — git 또는 scp");
  s.addText("방법 A · git (권장)",{x:M,y:1.85,w:6,h:0.4,fontFace:KR,fontSize:15,bold:true,color:TEAL});
  code(s,M,2.25,6.0,2.4,[
    [{t:"git init && git add . ",c:MINT}],
    [{t:'git commit -m "tdf crawler"',c:MINT}],
    [{t:"git push  ",c:MINT},{t:"# GitHub 비공개 repo"}],
    [],
    [{t:"# VM에서: git clone … / git pull",c:CMT}],
  ],11.5);
  s.addText("방법 B · scp/pscp (간단)",{x:7.1,y:1.85,w:6,h:0.4,fontFace:KR,fontSize:15,bold:true,color:TEAL});
  code(s,7.1,2.25,5.5,2.4,[
    [{t:"pscp -i key.ppk -r ",c:MINT},{t:"project"}],
    [{t:"   user@vm:~/tdf-crawler",c:CODETX}],
    [],
    [{t:"# 변환 없이 .ppk 그대로",c:CMT}],
    [{t:"# (PuTTY 도구)",c:CMT}],
  ],11.5);
  callout(s,M,4.95,11.9,0.95,AMBER,"보안","개인키·data/tdf.db 는 절대 git/이미지에 올리지 말 것(.gitignore 확인).");
  foot(s);
}

// ═══ 21. VM 준비 ═══
{ const s=p.addSlide(); light(s); head(s,"⑤-b","VM 준비 — 독립 환경(venv)");
  code(s,M,1.95,11.9,2.7,[
    [{t:"ssh user@<vm-ip>",c:MINT},{t:"                          # 접속"}],
    [{t:"sudo apt install -y python3-venv python3-pip ",c:MINT},{t:"# (없을 때만)"}],
    [{t:"cd ~/tdf-crawler && python3 -m venv .venv",c:MINT}],
    [{t:".venv/bin/pip install -e .",c:MINT},{t:"               # requests 등 설치"}],
  ],12.5);
  callout(s,M,4.95,11.9,1.0,MINT,"두려워 말 것","VM의 venv는 네 로컬 윈도우 환경을 전혀 안 쓴다. 서버에 깨끗한 독립 환경이 새로 생긴다.");
  foot(s);
}

// ═══ 22. 클라우드 DB 구축 ═══
{ const s=p.addSlide(); light(s); head(s,"⑤-c","클라우드에서 1주일치 DB 구축");
  code(s,M,1.95,11.9,1.9,[
    [{t:"bash cloud_quickstart/run_week.sh",c:MINT},{t:"    # 최근 1주일 적재 + 검증(자동감지)"}],
    [{t:"bash cloud_quickstart/verify.sh",c:MINT},{t:"      # 행수·날짜·시계열 샘플"}],
    [],
    [{t:"# 휴장일 스킵·resume 내장 → 중단해도 다시 실행하면 이어서",c:CMT}],
  ],12.5);
  callout(s,M,4.2,11.9,1.6,MINT,"실제 결과","GCP VM(Ubuntu)에서 5영업일 · nav 9,757행 적재 확인. data/tdf.db 가 서버 안에 생성됨. 크롤링↔DB 연결이 클라우드에서 그대로 일어난다.");
  foot(s);
}

// ═══ 23. cron 자동 ═══
{ const s=p.addSlide(); light(s); head(s,"⑤-d","cron 으로 매일 자동 + 검증");
  code(s,M,1.95,11.9,2.5,[
    [{t:"sudo timedatectl set-timezone Asia/Seoul",c:MINT}],
    [{t:'echo "0 8 * * * cd ~/tdf-crawler && ',c:MINT},{t:".venv/bin/python -m tdf_crawler.run \\"}],
    [{t:'      >> ~/tdf-crawler/logs/crawl.log 2>&1" | crontab -',c:MINT}],
    [{t:"crontab -l",c:MINT},{t:"     # 등록 확인 · systemctl is-active cron",c:CMT}],
  ],12);
  callout(s,M,4.75,5.85,1.0,MINT,"즉","매일 08:00 KST 무인 실행 → 안 켜도 매일 한 장씩.");
  callout(s,6.75,4.75,5.85,1.0,AMBER,"함정",'crontab -l 비면? echo "…"|crontab - 로 직접 설치(set -e+grep 주의).');
  foot(s);
}

// ═══ 24. 재현 체크리스트 ═══
{ const s=p.addSlide(); light(s); head(s,"RECAP","전체 재현 체크리스트");
  const steps=[
    "① 데이터 소스: KOFIA 실제 POST 파악 (proframeWeb 대문자!)",
    "② 크롤러: fetch(POST) → parse(selectMeta/tmpV) → TDF 필터",
    "③ DB: 스키마 + 멱등 upsert → python -m tdf_crawler.run",
    "④ 자동화: backfill로 과거 누적 + pytest 통과",
    "⑤ 클라우드: 업로드 → venv → run_week.sh → crontab 등록",
  ];
  steps.forEach((t,i)=>{const y=1.95+i*0.92;
    s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:M,y:y,w:0.55,h:0.55,fill:{color:DARK},rectRadius:0.1});
    s.addText(String(i+1),{x:M,y:y,w:0.55,h:0.55,fontFace:MONO,fontSize:18,bold:true,color:MINT,align:"center",valign:"middle",margin:0});
    s.addText(t,{x:M+0.85,y:y,w:11.0,h:0.55,fontFace:KR,fontSize:15,color:INK,valign:"middle",margin:0});
  });
  foot(s);
}

// ═══ 25. 결과 & 다음 ═══
{ const s=p.addSlide(); light(s); head(s,"NEXT","이제 가진 것 & 더 배우기");
  const items=[["가진 것","로컬에서 만들어 클라우드에서 매일 도는 TDF 데이터 DB"],
               ["손으로 더","team_learning/ 레슨 00–11 (직접 따라 만들기)"],
               ["빠른 실습","cloud_quickstart/ (1주일 클라우드 빌드)"],
               ["깊이 보기","docs/ (설계·개발·운영·분석) · docs/schema (ER·컬럼)"]];
  items.forEach((it,i)=>{const y=1.95+i*1.12;
    s.addShape(p.shapes.ROUNDED_RECTANGLE,{x:M,y:y,w:2.1,h:0.72,fill:{color:DARK},rectRadius:0.08});
    s.addText(it[0],{x:M,y:y,w:2.1,h:0.72,fontFace:KR,fontSize:14,bold:true,color:MINT,align:"center",valign:"middle",margin:0});
    s.addText(it[1],{x:M+2.4,y:y,w:9.7,h:0.72,fontFace:KR,fontSize:14.5,color:INK,valign:"middle",margin:0});
  });
  foot(s);
}

// ═══ 26. CLOSING ═══
{ const s=p.addSlide(); dark(s);
  s.addText("따라 만들면, 당신도",{x:M,y:1.9,w:12,h:0.6,fontFace:KR,fontSize:18,color:MINT});
  s.addText("데이터를 매일\n자동으로 쌓는다.",{x:M,y:2.5,w:12,h:2.0,fontFace:KR,fontSize:42,bold:true,color:WHITE,lineSpacingMultiple:1.05});
  s.addText("소스 찾기 → 크롤러 → DB 적재 → 자동화 → 클라우드 cron",{x:M,y:4.7,w:12,h:0.5,fontFace:KR,fontSize:15,color:ICE});
  s.addShape(p.shapes.LINE,{x:M,y:5.45,w:4,h:0,line:{color:TEAL,width:2}});
  s.addText("tdf_crawler · cloud_quickstart · docs/ · team_learning",{x:M,y:5.7,w:12,h:0.4,fontFace:MONO,fontSize:13,color:CMT});
}

p.writeFile({fileName:"project_guide.pptx"}).then(f=>console.log("WROTE",f));
