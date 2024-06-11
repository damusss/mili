# MILI

Minimal immediate-mode python user interface library.

On the same repository an image viewer using mili.

# Run

Run from source the image viewer:
```
pip install -r requirements.txt
python ImageViewer.py
``` 
Build the image viewer:
```
pip install pyinstaller
pip install -r requirements.txt
pyinstaller --onefile ImageViewer.py
start dist/ImageViewer.exe
```
