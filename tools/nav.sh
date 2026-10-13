#!/bin/bash
# 사용: nav.sh "0D:5 4B:3 s:name w:10 ..."  (포커스 없이 게시 입력 + PrintWindow 캡처)
E='D:/ps2/메달오브아너_프론트라인/tools/emu.ps1'
for t in $1; do
  k=${t%%:*}; v=${t#*:}
  case $k in
    s) powershell -ExecutionPolicy Bypass -File "$E" pshot "D:/ps2/메달오브아너_프론트라인/work/$v.png" >/dev/null;;
    w) sleep $v;;
    *) powershell -ExecutionPolicy Bypass -File "$E" hold "$k,150" >/dev/null; sleep ${v:-2};;
  esac
done
