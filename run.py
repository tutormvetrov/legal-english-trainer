"""
Точка входа для запуска приложения:
    python run.py
"""
import sys
import os

# Add project root to path so 'src' is importable as a package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    main()
