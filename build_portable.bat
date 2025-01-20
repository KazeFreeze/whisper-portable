@echo off
REM Create and activate virtual environment
python -m venv whisper-env
call whisper-env\Scripts\activate

REM Install required packages
pip install -r requirements.txt

REM Create launcher script
echo @echo off > run_whisper_gui.bat
echo call whisper-env\Scripts\activate >> run_whisper_gui.bat
echo python whisper_gui\main.py >> run_whisper_gui.bat
echo pause >> run_whisper_gui.bat

REM Create directory structure
mkdir whisper_gui
move whisper_gui.py whisper_gui\main.py
echo from whisper_gui.main import * > whisper_gui\__init__.py

REM Download FFmpeg
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"
powershell -Command "Expand-Archive ffmpeg.zip -DestinationPath ."
move ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe whisper-env\Scripts\
del ffmpeg.zip
rmdir /s /q ffmpeg-master-latest-win64-gpl

echo Build complete! Run "run_whisper_gui.bat" to start the application.