# 메달 오브 아너 프론트라인 PS2 한글 패치 v1.0

원본은 **한국판**(한국 정식 발매판, SLPM-67525)입니다. 한국판이지만 게임 안의 글자와 음성이 영어로만 들어 있어, 이 한국판 원본에 적용하는 정식 한글 패치입니다. 첨부 파일은 한글 패치 xdelta와 PCSX2 16:9 와이드 패치 pnach이며, 원본 ISO·게임 파일·폰트는 제공하지 않습니다.

- 목표·안내·본부 힌트·메뉴·메모리 카드 문구와 대사 자막 496종 한글화(외부 기계 번역 미사용). 원본에서 비어 있던 미군 대사 자막도 새로 넣었습니다.
- 메인 메뉴 간판, 컨트롤러 설정 화면, 로딩 화면 미션 제목, 결과 화면, D-Day 인트로 문구 등 이미지 한글화.
- 실행 파일은 고치지 않고, 게임에 남아 있던 2바이트 디코더와 폰트의 16비트 글리프 표로 한글 724자(나눔스퀘어 네오·서울한강체)를 표시합니다.
- PCSX2에서 부팅·메뉴·미션 선택·로딩·D-Day 인트로·게임 중 자막과 HUD·일시정지·저장 화면·옵션·컨트롤러 화면·와이드 패치 확인, 공개 소스 재빌드 및 xdelta 복원 해시 일치. 전체 레벨 완주와 실기는 미검증입니다.

## 첨부 파일

- `Medal_of_Honor_Frontline_PS2_KO_v1.0.xdelta`: 한글 패치(한국판 원본 ISO용)
- `SLPM-67525_E560ED68.pnach`: PCSX2 16:9 와이드 패치(한국판 원본·한글판 공용)

## 한글 패치 적용

1. xdelta3(또는 xdeltaUI)를 준비합니다.
2. 한국판 원본 `Medal of Honor - Frontline (Korea).iso`의 SHA-256이 아래 값과 같은지 확인합니다.
3. 명령: `xdelta3 -d -s "Medal of Honor - Frontline (Korea).iso" Medal_of_Honor_Frontline_PS2_KO_v1.0.xdelta "Medal of Honor - Frontline (Korean).iso"`
   - xdeltaUI: Patch에 xdelta, Source File에 한국판 원본 ISO, Output File에 만들 ISO 이름을 넣고 Patch를 누릅니다.

## 16:9 와이드 패치 사용법

이 판(SLPM-67525)용 와이드 패치는 웹과 PCSX2 내장 패치에 없어서, 북미판(SLUS-20368, 작성자 nemesis2000) 패치의 방식을 이 판의 실행 파일 주소에 맞게 옮겨 만들었습니다. 3D 시야각을 넓히는 방식이라 화면이 늘어나지 않습니다. 한글 패치는 실행 파일을 고치지 않아 원본과 한글판의 게임 CRC가 같으므로(**E560ED68**) 하나의 파일로 두 ISO 모두에 쓸 수 있습니다.

**PCSX2 2.x(권장)**
1. 첨부한 `SLPM-67525_E560ED68.pnach`를 `문서\PCSX2\patches\`(포터블은 `PCSX2 폴더\patches\`)에 넣습니다.
2. 게임 목록에서 Medal of Honor - Frontline을 오른쪽 클릭 → 속성 → **패치** 탭 → **Widescreen 16:9** 체크.
3. 속성 → 그래픽 → 디스플레이에서 FMV 화면 비율 전환을 **4:3**으로 두면 동영상이 원래 비율로 나옵니다(게임 화면 비율은 패치가 16:9로 바꿉니다).
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

한국판 원본 SHA-256: `3ca27eb122f99c7daf724fd126178484a5aaa96393456968f1ca6d7cb117af65`

완성 ISO SHA-256: `0093d3105f26eaab6a7cbfc96d6fbbca4e2982b673ed90c01ba8ce2943226cad`

xdelta SHA-256: `73e29d09aa0d749295290bf4196f751c2c3bbafb2419702d911365f6ffdb6ce8`

와이드 패치 SHA-256: `e76ef0329b71ba073733ee792c7702206a9a269bba86c069bc027f8b73228680`
