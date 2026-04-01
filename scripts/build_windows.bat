@echo off
echo === Legal English Trainer - Windows build ===
cd /d "%~dp0.."

pip install pyinstaller PyQt6 --quiet

rem Use --icon if assets/legal.ico exists
if exist assets\legal.ico (
    pyinstaller --onefile --windowed --icon=assets\legal.ico --name "LegalEnglishTrainer" ^
        --add-data "packs;packs" ^
        --add-data "src\database\schema.sql;src\database" ^
        run.py
) else (
    pyinstaller --onefile --windowed --name "LegalEnglishTrainer" ^
        --add-data "packs;packs" ^
        --add-data "src\database\schema.sql;src\database" ^
        run.py
)

echo.
echo Build complete. Executable: dist\LegalEnglishTrainer.exe
pause
