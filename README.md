# MILI

Minimal immediate-mode python user interface library.

# [MILI Guide](guide/guide.md)

# Image Viewer

Run from source the image viewer:
```shell
pip install -r requirements.txt
python ImageViewer.py
``` 
Build the image viewer:
```shell
pip install pyinstaller
pip install -r requirements.txt
pyinstaller --onefile ImageViewer.py
start dist/ImageViewer.exe
```
