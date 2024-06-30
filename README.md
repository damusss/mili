# MILI

Minimal immediate-mode python user interface library.

On the same repository an image viewer using mili.

# Guide

### [Styles Guide](mili/style.md)

# Run

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
