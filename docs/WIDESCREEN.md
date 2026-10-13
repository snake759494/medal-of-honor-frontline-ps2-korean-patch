# PCSX2 16:9 와이드 패치 사용법

`SLPM-67525_E560ED68.pnach`는 이 판(SLPM-67525)용 16:9 와이드 패치입니다. PCSX2 내장 패치 모음과 웹에는
북미판(SLUS-20368, 작성자 nemesis2000)용만 있어서, 그 패치의 원리를 이 판의 실행 파일에 맞게 옮겨 만들었습니다.

**원본·한글판 공용:** 한글 패치는 실행 파일(SLPM_675.25, MOH2RDVD.ELF)을 고치지 않으므로 PCSX2가 계산하는
게임 CRC가 원본과 한글판 모두 **E560ED68**입니다. 같은 파일 하나로 두 ISO에 모두 적용됩니다.

## 패치 내용

- 시야각 설정 함수(MOH2RDVD.ELF 0x14cf90)를 4바이트 앞(0x14cf8c)에서 시작하도록 다시 작성해, 가로 시야각을
  0.8125로 나눠 넓힙니다(북미판과 같은 계수). 이 함수를 부르는 3곳(0x146d88/0x146da8/0x146dc8)을 새 시작점으로 연결.
- 세로 시야 비율 상수(0x326390)를 0.75 → 0.609375로 바꿔 세로 시야는 원래대로 유지(3D 화면이 늘어나지 않음).
- `gsaspectratio=16:9`로 PCSX2 화면 비율을 함께 16:9로 맞춥니다.

## PCSX2 2.x (Qt) — 권장

1. `SLPM-67525_E560ED68.pnach`를 PCSX2 사용자 폴더의 `patches` 폴더에 넣습니다.
   - 설치판: `문서\PCSX2\patches\`
   - 포터블판: `PCSX2 폴더\patches\`
2. PCSX2 게임 목록에서 **Medal of Honor - Frontline**(한글 ISO)을 오른쪽 클릭 → **속성(Properties)**.
3. **패치(Patches)** 탭에서 **Widescreen 16:9**에 체크합니다. 목록에 없으면 1단계의 폴더와 파일 이름을 확인하세요.
4. **그래픽(Graphics) → 디스플레이(Display)**에서 **FMV 화면 비율 전환(FMV Aspect Ratio Override)**을 **4:3**으로 두면
   인트로·브리핑 동영상이 원래 비율로 나옵니다(화면 비율은 패치가 자동으로 16:9로 바꿉니다).
5. 게임을 시작하면 왼쪽 위에 “1개의 게임 패치가 활성화되었습니다”가 표시됩니다.

설정 파일로 켜려면 `문서\PCSX2\gamesettings\SLPM-67525_E560ED68.ini`에 다음 내용을 저장합니다.

```ini
[Patches]
Enable = Widescreen 16:9

[EmuCore/GS]
FMVAspectRatioSwitch = 4:3
```

## PCSX2 1.6 (wxWidgets)

1. 파일 이름을 `E560ED68.pnach`로 바꿔 `cheats_ws` 폴더에 넣습니다.
2. **시스템(System) → 와이드스크린 패치 사용(Enable Widescreen Patches)**을 켭니다.
3. **설정(Config) → 비디오(Video) → 창 설정(Window Settings)**에서 화면 비율을 16:9로 바꿉니다.

## 참고

- 메뉴·로딩 화면 같은 2D 화면은 원래 4:3이라 좌우로 늘어나 보입니다(게임 3D 화면은 정상 비율).
- 세로 비율 상수는 메뉴 쪽 코드에서도 참조하므로 일부 메뉴 연출이 달라 보일 수 있습니다(북미판 패치와 같은 방식).
- 끄려면 패치 탭의 체크를 해제하거나 `.ini`의 `Enable` 줄을 지웁니다.
- PCSX2 2.2에서 확인: 로그 `Enabled patch: Widescreen 16:9`, D-Day 레벨 3D 화면이 16:9로 넓어지고 총·HUD·나침반 정상.
  다른 레벨 전체와 실기(PS2 + 와이드 TV)는 미검증입니다.
