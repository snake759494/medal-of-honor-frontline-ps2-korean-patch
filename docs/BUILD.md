# 재빌드

Python 3.13에서 검증했습니다. 저장소 루트에 해시가 일치하는 원본을 `Medal of Honor - Frontline (Korea).iso`라는
이름으로 두고, 글꼴 `NanumSquareNeo-bRg.ttf`, `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-dEb.ttf`,
`NanumSquareNeo-eHv.ttf`, `SeoulHangangB.ttf`, `SeoulHangangEB.ttf`를 루트에 별도로 준비합니다(Git 제외).

```powershell
python -m pip install -r requirements.txt
python -X utf8 tools/build.py      # 원본 ISO → Medal of Honor - Frontline (Korean).iso
```

번역표(`translation/*.tsv`)는 `번호<TAB>한국어`만 담고 있습니다. 번호에 해당하는 영어 원문은 빌드할 때
`tools/make_src.py`가 원본 ISO에서 같은 순서로 추출합니다(ui: chars.bum·SCR·PauseScr 고유 문자열, subs: ABK의 SMUL 자막 블록).
완성 ISO SHA-256은 README와 일치해야 합니다.

## 구성

- `tools/build.py`: 전체 빌드(텍스트·자막·폰트·이미지 → VIV/ABK/BMP/SSH → ISO)
- `tools/make_src.py`: 원본에서 번역 대상 원문을 결정적 순서로 추출
- `tools/bum.py`, `tools/scr.py`, `tools/smul.py`: chars.bum/binum.bum, 셸 화면 스크립트(SCR) 문자열표, ABK 자막 블록
- `tools/sfn.py`, `tools/kfont.py`, `tools/fontcfg.py`: SFN(FNTS) 폰트, 한글 글리프 추가(2바이트 코드 0x81~0x9F/0x80~0xBF)
- `tools/ssh.py`, `tools/imgko.py`, `tools/images.py`, `tools/cfgdetect.py`: SHPS 이미지, 글자 지우기·한글 합성, 이미지별 사양
- `tools/viv.py`: BIGF/C0FB 아카이브 재구성(16MB 초과 C0FB는 BIGF로 다시 씀)
- `tools/ext.py`, `tools/isofs.py`, `tools/isobuild.py`, `tools/udf.py`, `tools/levels.py`: ISO9660/UDF 읽기·쓰기
- `tools/mdis.py`, `tools/xref.py`: ELF 분석(디스어셈블·참조 검색)
- `tools/emu.ps1`, `tools/nav.sh`, `tools/e.sh`: PCSX2 자동 조작·캡처

## 패치 생성/복원

```powershell
xdelta3 -e -9 -S none -A -s "Medal of Honor - Frontline (Korea).iso" "Medal of Honor - Frontline (Korean).iso" Medal_of_Honor_Frontline_PS2_KO_v1.0.xdelta
xdelta3 -d -s "Medal of Honor - Frontline (Korea).iso" Medal_of_Honor_Frontline_PS2_KO_v1.0.xdelta roundtrip.iso
```

xdelta 버전/옵션에 따라 패치 바이트는 달라질 수 있지만 복원 ISO는 같아야 합니다. 게임 자료나 폰트를 커밋하지 마세요.
