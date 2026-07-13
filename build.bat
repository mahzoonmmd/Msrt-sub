@echo off
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "MSRT" --icon "icon.ico" --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." --add-binary "icon.ico;." --add-binary "icon_256.png;." --hidden-import "groq" --hidden-import "PyQt6" app.py
echo Done! MSRT.exe is in dist folder.
pause
