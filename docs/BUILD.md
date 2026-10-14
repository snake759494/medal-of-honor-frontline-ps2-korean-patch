# 재빌드

Python 3.13에서 검증했습니다. 저장소 루트에 해시가 일치하는 원본을 `Medal of Honor - Frontline (Korea).iso`라는
이름으로 두고, 글꼴 `NanumSquareNeo-bRg.ttf`, `NanumSquareNeo-cBd.ttf`, `NanumSquareNeo-dEb.ttf`,
`NanumSquareNeo-eHv.ttf`, `SeoulHangangB.ttf`, `SeoulHangangEB.ttf`를 루트에 별도로 준비합니다(Git 제외).

```powershell
python -m pip install -r requirements.txt
python -X utf8 tools/build.py      # 원본 ISO → Medal of Honor - Frontline (Korean).iso (동영상 자막 인코딩 포함, 약 1시간)
python -X utf8 tools/build.py --nomovie   # 동영상을 바꾸지 않는 판
```

번역표(`translation/*.tsv`)는 `번호<TAB>한국어`만 담고 있습니다. 번호에 해당하는 영어 원문은 빌드할 때
`tools/make_src.py`가 원본 ISO에서 같은 순서로 추출합니다(ui: chars.bum·SCR·PauseScr 고유 문자열, subs: ABK의 SMUL 자막 블록).
완성 ISO SHA-256은 README와 일치해야 합니다.

## 동영상 자막

- `translation/movies/<이름>.tsv`: `시작초<TAB>끝초<TAB>한국어`(줄바꿈 `\n`). 빌드가 `tools/movie_sub.py`로 자막이 걸린 GOP만 다시 인코딩해 `movie/enc/`에 만든다.
- MPC 동영상은 MPCh 청크 하나가 픽처 하나다. 재인코딩한 GOP를 픽처 단위로 나눠 같은 청크 자리에 넣어야 게임이 재생한다(청크 크기는 달라도 됨).
  처음 두 GOP는 바꾸지 않으며, GOP 헤더의 타임코드는 원본 값을 유지한다.
- `tools/movie_asr.py`: 영어 음성 받아쓰기(faster-whisper large-v3, 번역 작업용 참고 자료, 빌드에는 불필요).

## 구성

- `tools/build.py`: 전체 빌드(텍스트·자막·폰트·이미지 → VIV/ABK/BMP/SSH → ISO)
- `tools/make_src.py`: 원본에서 번역 대상 원문을 결정적 순서로 추출
- `tools/bum.py`, `tools/scr.py`, `tools/smul.py`: chars.bum/binum.bum, 셸 화면 스크립트(SCR) 문자열표, ABK 자막 블록
- `tools/sfn.py`, `tools/kfont.py`, `tools/fontcfg.py`: SFN(FNTS) 폰트, 한글 글리프 추가(2바이트 코드 0x81~0x9F/0x80~0xBF)
- `tools/ssh.py`, `tools/imgko.py`, `tools/images.py`, `tools/cfgdetect.py`: SHPS 이미지, 글자 지우기·한글 합성, 이미지별 사양
- `tools/mpc.py`, `tools/movie_sub.py`, `tools/movie_asr.py`: EA MPC 동영상 청크, 자막 합성·재인코딩, 음성 받아쓰기
- `tools/viv.py`: BIGF/C0FB 아카이브 재구성(16MB 초과 C0FB는 BIGF로 다시 씀)
- `tools/ext.py`, `tools/isofs.py`, `tools/isobuild.py`, `tools/udf.py`, `tools/levels.py`: ISO9660/UDF 읽기·쓰기
- `tools/mdis.py`, `tools/xref.py`: ELF 분석(디스어셈블·참조 검색)
- `tools/emu.ps1`, `tools/nav.sh`, `tools/e.sh`: PCSX2 자동 조작·캡처

## 패치 생성/복원

```powershell
xdelta3 -e -0 -S none -A -s "Medal of Honor - Frontline (Korea).iso" "Medal of Honor - Frontline (Korean).iso" Medal_of_Honor_Frontline_PS2_KO_v1.1.xdelta
xdelta3 -d -s "Medal of Honor - Frontline (Korea).iso" Medal_of_Honor_Frontline_PS2_KO_v1.1.xdelta roundtrip.iso
```

xdelta 버전/옵션에 따라 패치 바이트는 달라질 수 있지만 복원 ISO는 같아야 합니다. 게임 자료나 폰트를 커밋하지 마세요.
