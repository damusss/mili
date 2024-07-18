# MILI

Minimal immediate-mode python user interface library.

# Guide

### [General Guide](mili/guide.md)
### [Styles Guide](mili/style.md)

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
