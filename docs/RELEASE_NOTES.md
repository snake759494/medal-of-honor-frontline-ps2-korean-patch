# 메달 오브 아너 프론트라인 PS2 한글 패치 v1.1

원본은 **한국판**(한국 정식 발매판, SLPM-67525)입니다. 한국판이지만 게임 안의 글자와 음성이 영어로만 들어 있어, 이 한국판 원본에 적용하는 정식 한글 패치입니다. 첨부 파일은 한글 패치 xdelta 두 종과 PCSX2 16:9 와이드 패치 pnach이며, 원본 ISO·게임 파일·폰트는 제공하지 않습니다.

## v1.1 변경 사항

- **동영상 자막 추가**: 음성은 나오지만 자막이 없던 동영상 16편에 한국어 자막 409줄을 넣었습니다.
  - 인트로(아이젠하워의 디데이 연설), 미션 브리핑 5편, 역사 영상 6편
  - 부가 영상: 죽기 좋은 날(군사 훈련), 개발팀 다큐, 짧은 대화(비트 챗), 여행 회고
  - 영어 음성을 받아 쓴 뒤 직접 번역했습니다(외부 기계 번역 미사용).
  - 블랙 한글패치와 같은 형식: 나눔스퀘어 네오 ExtraBold, 흰 글자 + 검은 테두리, 화면 아래 가운데.
  - 대사가 없는 제작 과정 영상(MAKING 1~6)과 부가 영상 1·3은 자막이 없습니다.
- 게임 텍스트·이미지·폰트는 v1.0과 같습니다.

## 첨부 파일

| 파일 | 내용 | 크기 |
|---|---|---|
| `Medal_of_Honor_Frontline_PS2_KO_v1.1.xdelta` | 한글 패치 + 동영상 자막(권장) | 약 1.0GB |
| `Medal_of_Honor_Frontline_PS2_KO_v1.1_nomovie.xdelta` | 동영상을 바꾸지 않는 판(동영상 자막 없음) | 약 278MB |
| `SLPM-67525_E560ED68.pnach` | PCSX2 16:9 와이드 패치(한국판 원본·한글판 공용) | 1KB |

동영상 자막판은 자막이 걸린 영상 구간을 다시 인코딩했기 때문에 패치가 큽니다(특히 17분짜리 개발팀 다큐). 용량이 부담되면 nomovie 판을 쓰세요.

## 한글 패치 적용

1. xdelta3(또는 xdeltaUI)를 준비합니다.
2. 한국판 원본 `Medal of Honor - Frontline (Korea).iso`의 SHA-256이 아래 값과 같은지 확인합니다.
3. 명령: `xdelta3 -d -s "Medal of Honor - Frontline (Korea).iso" Medal_of_Honor_Frontline_PS2_KO_v1.1.xdelta "Medal of Honor - Frontline (Korean).iso"`
   - nomovie 판은 xdelta 파일 이름만 바꿔서 같은 방법으로 적용합니다.
   - xdeltaUI: Patch에 xdelta, Source File에 한국판 원본 ISO, Output File에 만들 ISO 이름을 넣고 Patch를 누릅니다.

## 16:9 와이드 패치 사용법

이 판(SLPM-67525)용 와이드 패치는 웹과 PCSX2 내장 패치에 없어서, 북미판(SLUS-20368, 작성자 nemesis2000) 패치의 방식을 이 판의 실행 파일 주소에 맞게 옮겨 만들었습니다. 3D 시야각을 넓히는 방식이라 화면이 늘어나지 않습니다. 한글 패치는 실행 파일을 고치지 않아 원본과 한글판의 게임 CRC가 같으므로(**E560ED68**) 하나의 파일로 두 ISO 모두에 쓸 수 있습니다. v1.0에서 받은 파일과 내용이 같습니다.

**PCSX2 2.x(권장)**
1. 첨부한 `SLPM-67525_E560ED68.pnach`를 `문서\PCSX2\patches\`(포터블은 `PCSX2 폴더\patches\`)에 넣습니다.
2. 게임 목록에서 Medal of Honor - Frontline을 오른쪽 클릭 → 속성 → **패치** 탭 → **Widescreen 16:9** 체크.
3. 속성 → 그래픽 → 디스플레이에서 FMV 화면 비율 전환을 **4:3**으로 두면 동영상(자막 포함)이 원래 비율로 나옵니다(게임 화면 비율은 패치가 16:9로 바꿉니다).
4. 게임 시작 시 “1개의 게임 패치가 활성화되었습니다” 표시를 확인합니다.

설정 파일로 켜려면 `문서\PCSX2\gamesettings\SLPM-67525_E560ED68.ini`에 다음을 저장합니다.

```ini
[Patches]
Enable = Widescreen 16:9

[EmuCore/GS]
FMVAspectRatioSwitch = 4:3
```

**PCSX2 1.6** — 파일 이름을 `E560ED68.pnach`로 바꿔 `cheats_ws` 폴더에 넣고, 시스템 → 와이드스크린 패치 사용을 켠 뒤 비디오 → 창 설정에서 16:9를 고릅니다.

메뉴·로딩 화면 같은 2D 화면은 4:3 기준이라 좌우로 늘어나 보입니다. 끄려면 패치 탭 체크를 해제합니다. 자세한 내용은 저장소의 docs/WIDESCREEN.md를 보세요.

## 검증

- PCSX2 2.2에서 부팅 인트로를 자막과 함께 끝까지 재생, 미션 1 브리핑·부가 영상 2(인트로 자리에 넣어 시험)의 자막 재생 확인. 나머지 영상은 같은 방식으로 만들었고 게임 안에서 하나하나 재생해 보지는 않았습니다.
- 공개 소스 재빌드 결과와 xdelta 복원 ISO SHA-256 일치. 전체 레벨 완주와 실기는 미검증입니다.

한국판 원본 SHA-256: `3ca27eb122f99c7daf724fd126178484a5aaa96393456968f1ca6d7cb117af65`

완성 ISO SHA-256: `f1d1a9df23470536e70c27f4a185623b6d53d2e2ad8eb0d1e4da0135b11aaa58`

nomovie 완성 ISO SHA-256: `0093d3105f26eaab6a7cbfc96d6fbbca4e2982b673ed90c01ba8ce2943226cad`

xdelta SHA-256: `114ff660edc460d5e04c0830362a69b99c43d06046d920912835283af8955929`

nomovie xdelta SHA-256: `3ec4a919bee0283fb8b44d3a9b65b3201c833d0dda4cbf4b402b4f4de4799c10`

와이드 패치 SHA-256: `e76ef0329b71ba073733ee792c7702206a9a269bba86c069bc027f8b73228680`
