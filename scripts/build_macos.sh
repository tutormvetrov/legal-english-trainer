#!/bin/bash
set -e
echo "=== Legal English Trainer - macOS build ==="
cd "$(dirname "$0")/.."

pip install pyinstaller PyQt6 --quiet

if [ -f "assets/legal.icns" ]; then
    pyinstaller --windowed --icon=assets/legal.icns --name "LegalEnglishTrainer" \
        --add-data "packs:packs" \
        --add-data "src/database/schema.sql:src/database" \
        run.py
else
    pyinstaller --windowed --name "LegalEnglishTrainer" \
        --add-data "packs:packs" \
        --add-data "src/database/schema.sql:src/database" \
        run.py
fi

echo ""
echo "Build complete. Application: dist/LegalEnglishTrainer.app"
echo "On first launch, right-click → Open to bypass Gatekeeper."
