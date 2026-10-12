@echo off
cd /d D:\blog\lcy631zz.github.io-master\lcy631zz.github.io-master
"C:\hugo\hugo.exe" server -p 1313 --bind 0.0.0.0 --navigateToChanged=false --disableFastRender > "D:\blog\lcy631zz.github.io-master\lcy631zz.github.io-master\hugo.log" 2>&1
