@echo off
rmdir /s /q build dist __pycache__
pyinstaller --onefile --noconsole --name="Wiki Scraper" --icon=icon.ico gui.py
pause
    