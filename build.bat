@echo off
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "MSRT" --icon "icon.ico" --add-binary "icon.ico;." --add-binary "icon_256.png;." --add-binary "C:\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe;." --add-binary "C:\ffmpeg-8.1.2-essentials_build\bin\ffprobe.exe;." --hidden-import "groq" --hidden-import "PyQt6" app.py
echo Done! MSRT.exe is in dist folder.
pause
