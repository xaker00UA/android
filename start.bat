




call D:\Mem\.venv\Scripts\activate
REM Сохраняем текущую ветку
setlocal
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i

REM Переключаемся на ветку main
git checkout main

REM Запускаем Python-скрипт
python main.py

REM Возвращаемся на исходную ветку
git checkout %BRANCH%
endlocal
pause