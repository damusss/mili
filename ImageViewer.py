import pygame
import mili
import os
import sys
import math
import json
import threading
import imagesize
from tkinter import filedialog
import send2trash
# import ez_profile

pygame.init()
W, H = pygame.display.get_desktop_sizes()[0]
S = 5

REMOVE_PATH_MSG = "Are you sure you want to remove this path? Note that the actual directory will not be deleted but you'll need to add it again if you change your mind."
FILEPICKER_MSG = "Could not open the file dialog (exception message: '{e}'). To achieve the same result, close the program, open 'data.json' and add an entry to the 'paths' key."
TRASH_BYTES = b"\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x011114\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd1114\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x011114\xfd\xfd\xfd\xfd\xe7\xe7\xe7\xe8\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xc6\xe7\xe7\xe7\xe8\xfd\xfd\xfd\xfd1114\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x011114\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd1114\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x011114\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd1114\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f<<<?\xfd\xfd\xfd\xfd\x9d\x9d\x9d\x9f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\x9d\x9d\x9d\x9f\xfd\xfd\xfd\xfd<<<?\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\r\r\r\x0f\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\xe8\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x16\x16\x16\x17LLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLNLLLN\x16\x16\x16\x17\x00\x00\x00\x01\x00\x00\x00\x01AAA8\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdAAA8\x00\x00\x00\x01\x00\x00\x00\x01&&&\x1d\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdVVVG,,,\x1a\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xa0\xa0\xa0\xa2\x15\x15\x15\x16\xa0\xa0\xa0\xa2\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd,,,\x1aVVVG\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd&&&\x1d\x00\x00\x00\x01\x00\x00\x00\x01\x0b\x0b\x0b\x05\xfd\xfd\xfd\xfb\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdHHH=\x00\x00\x00\x01\xfd\xfd\xfd\xf4\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xf3\x00\x00\x00\x01III=\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfb\x0b\x0b\x0b\x05\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xef\xef\xef\xe4\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdYYYO\x00\x00\x00\x01\xeb\xeb\xeb\xe1\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xeb\xeb\xeb\xe1\x00\x00\x00\x01YYYO\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xef\xef\xef\xe3\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xd4\xd4\xd4\xc9\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdiiia\x00\x00\x00\x01\xdb\xdb\xdb\xcf\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xdb\xdb\xdb\xcf\x00\x00\x00\x01iiia\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xd4\xd4\xd4\xc9\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xb9\xb9\xb9\xae\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd~~~s\x00\x00\x00\x01\xca\xca\xca\xbd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xca\xca\xca\xbd\x00\x00\x00\x01~~~t\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xb9\xb9\xb9\xae\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x9e\x9e\x9e\x93\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x92\x92\x92\x86\x00\x00\x00\x01\xb3\xb3\xb3\xab\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xb3\xb3\xb3\xab\x00\x00\x00\x01\x92\x92\x92\x86\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x9e\x9e\x9e\x93\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x83\x83\x83y\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xa1\xa1\xa1\x98\x00\x00\x00\x01\xa2\xa2\xa2\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xa2\xa2\xa2\x98\x00\x00\x00\x01\xa1\xa1\xa1\x98\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x83\x83\x83x\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01hhh^\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xb2\xb2\xb2\xaa\x00\x00\x00\x01\x93\x93\x93\x86\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x93\x93\x93\x86\x00\x00\x00\x01\xb2\xb2\xb2\xaa\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdggg^\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01MMMC\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xca\xca\xca\xbc\x00\x00\x00\x01~~~t\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd~~~t\x00\x00\x00\x01\xca\xca\xca\xbc\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdMMMC\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01111(\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xda\xda\xda\xce\x00\x00\x00\x01iiib\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdiiib\x00\x00\x00\x01\xda\xda\xda\xcf\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd111(\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x16\x16\x16\r\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xea\xea\xea\xe1\x00\x00\x00\x01ZZZP\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdZZZP\x00\x00\x00\x01\xea\xea\xea\xe1\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x15\x15\x15\r\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xf9\xf9\xf9\xee\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xf3\x00\x00\x00\x01JJJ>\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdJJJ>\x00\x00\x00\x01\xfd\xfd\xfd\xf3\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xf9\xf9\xf9\xee\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xdf\xdf\xdf\xd4\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x14\x14\x14\t222+\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd222+\x14\x14\x14\t\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xde\xde\xde\xd3\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xc3\xc3\xc3\xb9\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd$$$\x1b!!!\x19\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd!!!\x19$$$\x1c\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xc3\xc3\xc3\xb9\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xa9\xa9\xa9\x9e\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd444.\x12\x12\x12\x08\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x11\x11\x11\x07444.\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xa8\xa8\xa8\x9e\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x8d\x8d\x8d\x83\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdKKK@\x00\x00\x00\x01\xfd\xfd\xfd\xf1\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xf1\x00\x00\x00\x01KKK@\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x8d\x8d\x8d\x83\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01sssi\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd]]]R\x00\x00\x00\x01\xe8\xe8\xe8\xdf\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xe7\xe7\xe7\xdf\x00\x00\x00\x01]]]R\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdrrrh\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01WWWN\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdllld\x00\x00\x00\x01\xd7\xd7\xd7\xcd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xd7\xd7\xd7\xcc\x00\x00\x00\x01llld\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdWWWM\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01===3\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd~~~v\x00\x00\x00\x01\xc8\xc8\xc8\xba\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xc8\xc8\xc8\xba\x00\x00\x00\x01~~~v\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd<<<3\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01!!!\x18\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x95\x95\x95\x88\x00\x00\x00\x01\xb1\xb1\xb1\xa8\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xb1\xb1\xb1\xa8\x00\x00\x00\x01\x95\x95\x95\x89\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd!!!\x18\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x07\x07\x07\x03\xfd\xfd\xfd\xf8\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xa5\xa5\xa5\x9b\x00\x00\x00\x01\x9f\x9f\x9f\x96\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x9e\x9e\x9e\x96\x00\x00\x00\x01\xa5\xa5\xa5\x9b\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xf7\x06\x06\x06\x03\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xea\xea\xea\xdf\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xb5\xb5\xb5\xad\x00\x00\x00\x01\x8f\x8f\x8f\x84\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x8f\x8f\x8f\x84\x00\x00\x00\x01\xb5\xb5\xb5\xad\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xea\xea\xea\xde\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xcf\xcf\xcf\xc4\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xca\xca\xca\xbf\x00\x00\x00\x01~~~r\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd~~~q\x00\x00\x00\x01\xca\xca\xca\xbf\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xcf\xcf\xcf\xc3\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\xb4\xb4\xb4\xa9\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xdd\xdd\xdd\xd1\x06\x06\x06\x02pppe\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x97\x97\x97\x99\x00\x00\x00\x01\x97\x97\x97\x99\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdpppe\x06\x06\x06\x02\xdd\xdd\xdd\xd1\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xb4\xb4\xb4\xa9\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x98\x98\x98\x8e\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfb\xf8\xf8\xf8\xf3\xfd\xfd\xfd\xfb\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfa\xfa\xfa\xfa\xf5\xf5\xf5\xf5\xfa\xfa\xfa\xfa\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfb\xf8\xf8\xf8\xf3\xfd\xfd\xfd\xfb\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\x98\x98\x98\x8e\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01}}}s\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd}}}s\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01bbbY\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfdaaaX\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01"
DELETE_IMAGE_MSG = "Are you sure you want to recycle this image? If you confirm, it will be sent to your trash and not deleted forever. If this operation fails, the image will not be deleted."
RECYCLE_ERROR_MSG = "Could not recycle this image (exception message: '{e}'). The image did not get deleted."
DELETE_FOLDER_MSG = "Are you sure you want to recycle the folder contents? If you confirm, all valid images will be sent to the trash. If the folder is empty it will be permanently deleted. If the recycling operation fails, no data will be lost."
FOLDER_RECYCLE_MSG = "Could not recycle the folder contents (exception message: '{e}'). The contents did not get deleted."
FOLDER_ERROR_MSG = "The contents have been recycled but the empty folder could not be deleted (exception meesage: '{e}')"
WRONG_PATH_ABS = "The path '{path}' was removed as it is not an absolute path. Only absolute paths are allowed."
WRONG_PATH_EXIST = "The path '{path}' was removed as it does not exist anymore."


def load_image_async(dirpath, file, storage):
    try:
        img = pygame.image.load(os.path.join(dirpath, file)).convert_alpha()
    except Exception:
        img = None
    storage[file] = img


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))

        self.clock = pygame.Clock()

        self.mili = mili.MILI(self.screen)

        self.mode = 0

        desktop_path = (
            os.getenv("APPDATA") + "\\Microsoft\\Windows\\Themes\\TranscodedWallpaper"
        )
        if os.path.exists(desktop_path):
            self.desktop_bg = pygame.image.load(desktop_path, "png")
        else:
            self.desktop_bg = pygame.Surface((W, H))
            self.desktop_bg.fill(0)
        mask = pygame.Surface(self.desktop_bg.size, pygame.SRCALPHA)
        mask.fill((40, 40, 40, 180))
        self.desktop_bg.blit(mask, (0, 0))
        self.desktop_cache = mili.ImageCache()

        s = 300
        self.hover_surf = pygame.Surface((s, s), pygame.SRCALPHA)
        for x in range(self.hover_surf.width):
            for y in range(self.hover_surf.height):
                dist = math.sqrt((x - s // 2) ** 2 + (y - s // 2) ** 2)
                self.hover_surf.set_at(
                    (x, y),
                    pygame.Color(
                        255,
                        255,
                        255,
                        max(0, min(255, int((1 - ((dist / (s // 2)) ** 0.6)) * 45))),
                    ),
                )
        self.hover_cache = mili.ImageCache()
        self.drag_pos = pygame.Vector2(0, 0)
        self.drag_offset = pygame.Vector2(0, 0)

        self.square = pygame.Surface((10, 10))
        self.square.fill("white")

        self.cards_cache = [mili.ImageCache() for _ in range(1000)]

        self.mili.default_styles(
            text={
                "name": "Segoe UI",
                "sysfont": True,
                "growx": True,
                "growy": True,
                "padx": 10,
            },
            rect={"border_radius": 0},
            line={"color": "white"},
        )

        if not os.path.exists("data.json"):
            with open("data.json", "w") as file:
                json.dump(
                    {
                        "paths": [],
                        "favorites": [],
                        "size": "m",
                        "smoothscale": True,
                        "last_open": None,
                    },
                    file,
                )

        with open("data.json", "r") as file:
            data = json.load(file)
            self.search_paths = [p.replace("\\", "/") for p in data.get("paths", [])]
            self.favorites_paths = data.get("favorites", [])
            self.size = data.get("size", "m")
            self.smoothscale = data.get("smoothscale", True)
            self.last_open = data.get("last_open", None)

        self.loaded_images = {}
        self.images_cache = {}
        self.images_sizes = {}

        self.content_scroll = mili.ScrollHelper()
        self.back_topleft = (S, S)

        self.cur_path = None
        self.cur_file = None

        self.folder_nums = {
            "xxxs": 30,
            "xxs": 25,
            "xs": 20,
            "s": 17,
            "m": 13,
            "l": 9,
            "xl": 6,
            "xxl": 4,
            "xxxl": 3,
        }
        self.image_nums = {
            "xxxs": 40,
            "xxs": 30,
            "xs": 20,
            "s": 12,
            "m": 8,
            "l": 6,
            "xl": 4,
            "xxl": 3,
            "xxxl": 2,
        }
        self.preview_nums = {
            "xxxs": 60,
            "xxs": 45,
            "xs": 32,
            "s": 25,
            "m": 18,
            "l": 14,
            "xl": 10,
            "xxl": 8,
            "xxxl": 6,
        }
        self.size_menu_open = False
        self.size_menu_pos = (0, 0)
        self.compute_sizes()
        self.reset_view()
        self.schedule_for_open = None
        self.image_back_time = -99999

        self.trash_img = pygame.image.frombytes(
            TRASH_BYTES,
            (27, 38),
            "RGBA",
        )
        self.last_cache_time = pygame.time.get_ticks()
        self.cache_folder_contents()

    def wrong_path_info(self, path, exists):
        message = WRONG_PATH_ABS if exists else WRONG_PATH_EXIST
        pygame.display.message_box(
            "Path Removed",
            message.replace("{path}", path),
            "info",
            buttons=("Understood",),
        )

    def cache_folder_contents(self):
        self.folder_contents_iter = {}
        self.folder_contents_abs = {}
        refresh = False

        for rootpath in list(self.search_paths):
            if not os.path.exists(rootpath):
                self.wrong_path_info(rootpath, False)
                self.search_paths.remove(rootpath)
                refresh = True
                continue

            if not os.path.isabs(rootpath):
                self.wrong_path_info(rootpath, True)
                self.search_paths.remove(rootpath)
                refresh = True
                continue

            self.folder_contents_iter[rootpath] = {}
            for dirpath, subfolders, filenames in os.walk(rootpath):
                any_image_in_dirpath = False
                dirpath = dirpath.replace("\\", "/")
                valid_files = []
                for file in filenames:
                    if any(
                        [
                            f"{ext}" in file
                            for ext in [
                                ".png",
                                ".jpg",
                                ".jpeg",
                                ".svg",
                                ".gif",
                                ".bmp",
                                ".tiff",
                            ]
                        ]
                    ):
                        valid_files.append(file)
                        any_image_in_dirpath = True
                if any_image_in_dirpath:
                    self.folder_contents_iter[rootpath][dirpath] = valid_files
                    self.folder_contents_abs[dirpath] = valid_files

        if refresh:
            self.save_data()

    def exit(self):
        pygame.quit()
        sys.exit()

    def reset_view(self):
        self.cur_img: pygame.Surface = None
        self.img_output = None
        self.reset_view_data()

    def reset_view_data(self):
        self.view_offset = pygame.Vector2()
        self.view_zoom = 1

    def save_data(self):
        with open("data.json", "w") as file:
            data = {
                "paths": self.search_paths,
                "favorites": self.favorites_paths,
                "size": self.size,
                "smoothscale": self.smoothscale,
                "last_open": self.last_open,
            }
            json.dump(data, file)

    def get_size(self, num):
        available = W - 20 - 3 * (num - 1)
        return available // num

    def compute_sizes(self):
        self.folder_sizes = {
            name: self.get_size(num) for name, num in self.folder_nums.items()
        }
        self.image_sizes = {
            name: self.get_size(num) for name, num in self.image_nums.items()
        }
        self.preview_sizes = {
            name: self.get_size(num) for name, num in self.preview_nums.items()
        }

    def base_btn_img(self, data):
        self.mili.image(
            self.square,
            {
                "fill_color": ((70, 70, 70) if data.left_pressed else (90, 90, 90)),
                "alpha": 140,
                "fill": True,
            },
        )

    def base_btn_hover(self, data):
        if data.hovered and not data.left_pressed:
            self.mili.rect({"color": (150, 150, 150), "outline_size": 1})
            self.glow(data.id, data.absolute_rect)

    def ui_1_back_arrow(self):
        with self.mili.begin(
            pygame.Rect(S, 0, 60, 40), {"z": 9999}, get_data=True
        ) as a_data:
            self.back_topleft = a_data.absolute_rect.topleft
            self.base_btn_img(a_data)
            self.mili.line((("-25", 0), ("35", 0)), {"size": 1})
            self.mili.line((("-25", 0), ("-2", "-32")), {"size": 1})
            self.mili.line((("-25", 0), ("-2", "32")), {"size": 1})
            self.base_btn_hover(a_data)
            if a_data.interaction.left_just_released:
                if pygame.time.get_ticks() - self.image_back_time > 10:
                    self.back_to_content()

    def ui_1_star(self):
        with self.mili.begin(
            pygame.Rect(0, 0, 40, 40), {"z": 9999}, get_data=True
        ) as f_data:
            self.base_btn_img(f_data)
            self.mili.polygon(
                [
                    (0, "10"),
                    ("-25", "25"),
                    ("-15", 0),
                    ("-30", "-15"),
                    ("-10", "-15"),
                    (0, "-35"),
                    ("10", "-15"),
                    ("30", "-15"),
                    ("15", 0),
                    ("25", "25"),
                ],
                {
                    "color": (255, 230, 0),
                    "outline_size": (0 if self.cur_path in self.favorites_paths else 1),
                },
            )
            self.base_btn_hover(f_data)
            if f_data.interaction.left_just_released:
                self.toggle_favorite()

    def toggle_favorite(self):
        if self.cur_path in self.favorites_paths:
            self.favorites_paths.remove(self.cur_path)
        else:
            self.favorites_paths.append(self.cur_path)
        self.save_data()

    def ui_1(self):
        self.card_idx = 0

        with self.mili.begin(None, {"fillx": True, "resizey": True, "axis": "x"}):
            self.ui_1_back_arrow()
            self.ui_1_star()

            self.mili.text_element(
                f"{self.cur_path}", {"size": 30, "align": "left"}, None, {"fillx": True}
            )

        if self.cur_path is None:
            return

        self.ui_delete(self.delete_folder)

        self.mili.line_element(
            (("-50", 0), ("50", 0)),
            {"color": (80, 80, 80)},
            (0, 0, 0, 20),
            {"fillx": "100"},
        )

        with self.mili.begin(
            (0, 0, W - S * 2, 0),
            {
                "resizex": (False if self.size == "list" else {"max": W - S * 2}),
                "filly": True,
                "grid": (False if self.size == "list" else True),
                "axis": ("y" if self.size == "list" else "x"),
            },
            get_data=True,
        ) as content_data:
            self.content_scroll.update(content_data)
            if self.cur_path not in self.folder_contents_abs:
                self.back_to_content()
                return
            files = self.folder_contents_abs[self.cur_path]
            if len(files) <= 0:
                self.back_to_content()
                return
            any_valid = False
            for file in files:
                if self.size != "list":
                    self.load_if_necessary(self.cur_path, file)
                else:
                    self.load_size_if_necessary(self.cur_path, file)
                if self.image_card(file):
                    any_valid = True
            if not any_valid:
                self.back_to_content()
                return

    def image_card(self, file):
        if self.cur_path is None:
            return False
        img = self.loaded_images[self.cur_path].get(file, None)
        imgsize = self.images_sizes[self.cur_path].get(file, None)
        if self.size == "list" and imgsize is None:
            return False
        if img is None and self.size != "list":
            return False
        size = (
            (self.image_sizes[self.size], self.image_sizes[self.size])
            if self.size != "list"
            else (0, 0)
        )
        with self.mili.begin(
            ((0, 0), size),
            {
                "offset": self.content_scroll.get_offset(),
                "fillx": (True if self.size == "list" else 0),
            },
            get_data=True,
        ) as i_data:
            self.mili.image(
                self.square,
                mili.conditional_style(
                    i_data,
                    {
                        "fill_color": (80, 80, 80),
                        "alpha": 140,
                        "cache": self.cards_cache[self.card_idx],
                        "fill": (True if self.size == "list" else False),
                    },
                    {},
                    {"fill_color": (65, 65, 65)},
                ),
            )
            if self.size == "list":
                self.mili.text(
                    self.image_str(file, self.cur_path),
                    {
                        "growx": False,
                        "growy": (True if self.size == "list" else False),
                        "wraplen": (0 if self.size == "list" else "100"),
                        "align": ("midleft" if self.size == "list" else "center"),
                        "font_align": (
                            pygame.FONT_LEFT
                            if self.size == "list"
                            else pygame.FONT_CENTER
                        ),
                    },
                )
            else:
                if img == "loading":
                    self.mili.text("Loading...", {"size": 20, "wraplength": "100"})
                else:
                    self.mili.image(
                        img,
                        {
                            "cache": self.images_cache[self.cur_path][file],
                            "smoothscale": self.smoothscale,
                        },
                    )
            if i_data.interaction.hovered and not i_data.interaction.left_pressed:
                self.mili.rect({"color": (150, 150, 150), "outline_size": 1})
                self.glow(i_data.id, i_data.absolute_rect)
                if i_data.press_button != pygame.BUTTON_MIDDLE:
                    if self.size != "list":
                        self.simple_info(file)
                else:
                    self.any_press = True
            if i_data.interaction.left_just_released and img != "loading":
                self.any_press = True
                if img is None:
                    self.load_if_necessary(self.cur_path, file)
                    self.schedule_for_open = file
                else:
                    self.schedule_for_open = None
                    self.open_image(file)
            self.card_idx += 1
        return True

    def simple_info(self, file):
        self.mili.basic_element(
            (pygame.mouse.get_pos(), (0, 0)),
            {
                "blocking": False,
                "ignore_grid": True,
                "parent_id": self.main_data.id,
                "z": 9999,
            },
            self.image_str(file, self.cur_path),
            {"size": 20},
            {"color": (85, 85, 90)},
            {"color": (150, 150, 150)},
        )

    def draw_view(self, canva, rect, clip):
        if self.img_output is None:
            return
        canva.blit(self.img_output, self.img_output.get_rect(center=(W / 2, H / 2)))

    def ui_2(self):
        if self.cur_path is None or self.cur_file is None:
            self.back_to_folder()
        self.ui_2_back_arrow()
        self.ui_delete(self.delete_image)

        with self.mili.begin(None, {"fillx": True, "resizey": True, "pady": 0}):
            self.mili.text_element(
                f"{self.image_str(self.cur_file, self.cur_path)}",
                {"size": 19},
                None,
                {"align": "center"},
            )

    def ui_delete(self, function):
        with self.mili.begin(
            pygame.Rect(0, 0, 40, 40).move_to(bottomright=(W - S, H - S)),
            {"z": 9999, "ignore_grid": True},
            get_data=True,
        ) as d_data:
            self.base_btn_img(d_data)
            self.mili.image(self.trash_img, {"pady": "10"})
            self.base_btn_hover(d_data)
            if d_data.left_just_released:
                function()

    def delete_image(self):
        msg = pygame.display.message_box(
            "Confirm Image Recycle",
            DELETE_IMAGE_MSG,
            "warn",
            buttons=("Recycle Image", "Cancel"),
        )
        if msg == 1:
            return
        try:
            send2trash.send2trash(
                [(self.cur_path + "/" + self.cur_file).replace("/", "\\")]
            )
        except Exception as e:
            pygame.display.message_box(
                "Image Recycle Error",
                RECYCLE_ERROR_MSG.replace("{e}", str(e)),
                "error",
                buttons=("Understood",),
            )
            return
        if self.cur_file in self.loaded_images[self.cur_path]:
            self.loaded_images[self.cur_path].pop(self.cur_file)
        self.cache_folder_contents()
        self.back_to_folder()

    def delete_folder(self):
        msg = pygame.display.message_box(
            "Confirm Folder Content Recycle",
            DELETE_FOLDER_MSG,
            "warn",
            buttons=("Recycle Folder Content", "Cancel"),
        )
        if msg == 1:
            return
        img_files = [
            file
            for file in os.listdir(self.cur_path)
            if file in self.loaded_images[self.cur_path]
        ]
        try:
            send2trash.send2trash(
                [(f"{self.cur_path}/{file}").replace("/", "\\") for file in img_files]
            )
        except Exception as e:
            pygame.display.message_box(
                "Folder Content Recycle Error",
                FOLDER_RECYCLE_MSG.replace("{e}", str(e)),
                "error",
                buttons=("Understood",),
            )
            return
        if len(os.listdir(self.cur_path)) <= 0:
            try:
                os.rmdir(self.cur_path)
            except Exception as e:
                pygame.display.message_box(
                    "Folder Deletion Error",
                    FOLDER_ERROR_MSG.replace("{e}", str(e)),
                    "error",
                    buttons=("Understood",),
                )
        for file in img_files:
            if file in self.loaded_images[self.cur_path]:
                self.loaded_images[self.cur_path].pop(file)
        self.cache_folder_contents()
        self.back_to_content()

    def ui_2_back_arrow(self):
        with self.mili.begin(
            pygame.Rect(self.back_topleft, (60, 40)),
            {"z": 9999, "ignore_grid": True},
            get_data=True,
        ) as a_data:
            self.base_btn_img(a_data)
            self.mili.line((("-25", 0), ("35", 0)), {"size": 1})
            self.mili.line((("-25", 0), ("-2", "-32")), {"size": 1})
            self.mili.line((("-25", 0), ("-2", "32")), {"size": 1})
            self.base_btn_hover(a_data)
            if a_data.interaction.left_just_released:
                self.image_back_time = pygame.time.get_ticks()
                self.back_to_folder()

    def back_to_content(self):
        self.cur_path = None
        self.mode = 0
        self.schedule_for_open = None

    def ui_0(self):
        self.card_idx = 0

        self.mili.text_element(
            "Images", {"size": 40, "align": "center"}, None, {"fillx": True}
        )

        self.ui_0_add_path()

        self.mili.line_element(
            (("-50", 0), ("50", 0)),
            {"color": (80, 80, 80)},
            (0, 0, 0, 20),
            {"fillx": "100"},
        )

        self.ui_0_content()

    def ui_0_add_path(self):
        with self.mili.begin(
            (S + S / 2, S + S / 2, 0, 0),
            {"ignore_grid": True, "z": 9999},
            get_data=True,
        ) as add_path_d:
            self.base_btn_img(add_path_d)
            self.mili.text("Add Path", {"size": 24})
            self.base_btn_hover(add_path_d)
            if add_path_d.left_just_released:
                self.try_add_path()

    def try_add_path(self):
        try:
            if self.last_open is not None:
                directory = filedialog.askdirectory(initialdir=self.last_open)
            else:
                directory = filedialog.askdirectory()
        except Exception as e:
            msg = pygame.display.message_box(
                "File Dialog Error",
                FILEPICKER_MSG.replace("{e}", str(e)),
                "error",
                buttons=("Close App", "Understood"),
            )
            if msg == 0:
                self.exit()
            directory = None
        if directory:
            self.search_paths.append(directory)
            self.last_open = directory
            self.cache_folder_contents()
            self.save_data()

    def ui_0_path_title(self, path):
        with self.mili.begin(
            None,
            {
                "fillx": True,
                "resizey": True,
                "padx": 0,
                "pady": 0,
                "axis": "x",
                "offset": self.content_scroll.get_offset(),
            },
        ):
            self.mili.text_element(f"{path}", {"size": 28})
            with self.mili.begin(
                (0, 0, 32, 32),
                {"align": "center"},
                get_data=True,
            ) as trash_d:
                self.base_btn_img(trash_d)
                self.mili.image(self.trash_img, {"pady": "10"})
                self.base_btn_hover(trash_d)
                if trash_d.left_just_released:
                    self.remove_path(path)

    def remove_path(self, path):
        if path in self.search_paths:
            msg = pygame.display.message_box(
                "Confirm Path Removal",
                REMOVE_PATH_MSG,
                "info",
                buttons=("Remove Path", "Cancel"),
            )
            if msg == 1:
                return

            if path in self.folder_contents_iter:
                for subfolder in self.folder_contents_iter[path].keys():
                    if subfolder in self.loaded_images:
                        self.loaded_images.pop(subfolder)
                    if subfolder in self.images_sizes:
                        self.images_sizes.pop(subfolder)

            self.search_paths.remove(path)
            self.cache_folder_contents()
            self.save_data()

    def ui_0_favorites(self):
        self.mili.text_element(
            "Favorites",
            {"size": 30},
            None,
            {"offset": self.content_scroll.get_offset()},
        )
        with self.mili.begin(
            (0, 0, W - S * 2, 1),
            {
                "resizex": (False if self.size == "list" else {"max": W - S * 2}),
                "resizey": True,
                "axis": ("y" if self.size == "list" else "x"),
                "grid": (False if self.size == "list" else True),
                "offset": self.content_scroll.get_offset(),
            },
        ):
            for favpath in list(self.favorites_paths):
                if not os.path.exists(favpath):
                    self.favorites_paths.remove(favpath)
                    continue
                if not os.path.isabs(favpath):
                    self.favorites_paths.remove(favpath)
                    continue
                if favpath not in self.folder_contents_abs:
                    self.favorites_paths.remove(favpath)
                    continue
                self.folder_card(favpath, favpath)

    def ui_0_content(self):
        with self.mili.begin(
            None,
            {"axis": "y", "fillx": "100", "filly": "100", "padx": 0, "pady": 0},
            get_data=True,
        ) as content_data:
            self.content_scroll.update(content_data)
            if len(self.favorites_paths) > 0:
                self.ui_0_favorites()

            for rootpath, subpaths in self.folder_contents_iter.items():
                self.ui_0_path_title(rootpath)

                if len(subpaths) > 0:
                    self.ui_0_content_folder(subpaths, rootpath)
                else:
                    self.mili.text_element(
                        "No images found",
                        {"size": 23},
                        None,
                        {"offset": self.content_scroll.get_offset()},
                    )

    def ui_0_content_folder(self, subpaths, rootpath):
        with self.mili.begin(
            (0, 0, W - S * 2, 0),
            {
                "resizex": (False if self.size == "list" else {"max": W - S * 2}),
                "resizey": True,
                "axis": ("y" if self.size == "list" else "x"),
                "grid": (False if self.size == "list" else True),
                "offset": self.content_scroll.get_offset(),
            },
            get_data=True,
        ):
            for dirpath, files in subpaths.items():
                dirpath = dirpath.replace("\\", "/")
                any_image = False
                for file in files:
                    if any([f"{ext}" in file for ext in [".png", ".jpg", ".jpeg"]]):
                        any_image = True
                if any_image:
                    dirname = dirpath.replace(rootpath + "/", "")
                    self.folder_card(dirname, dirpath)

    def folder_card(self, dirname, dirpath):
        size = (
            (self.folder_sizes[self.size], self.folder_sizes[self.size])
            if self.size != "list"
            else (0, 0)
        )
        with self.mili.begin(
            ((0, 0), size),
            {"fillx": ("100" if self.size == "list" else 0)},
            get_data=True,
        ) as f_data:
            self.mili.image(
                self.square,
                mili.conditional_style(
                    f_data,
                    {
                        "fill_color": (80, 80, 80),
                        "alpha": 140,
                        "cache": self.cards_cache[self.card_idx],
                        "fill": (True if self.size == "list" else False),
                    },
                    {},
                    {"fill_color": (65, 65, 65)},
                ),
            )
            self.mili.text(
                f"{dirname}",
                {
                    "size": 20,
                    "growx": False,
                    "growy": (True if self.size == "list" else False),
                    "wraplen": (0 if self.size == "list" else "100"),
                    "align": ("midleft" if self.size == "list" else "center"),
                    "font_align": (
                        pygame.FONT_LEFT if self.size == "list" else pygame.FONT_CENTER
                    ),
                },
            )
            if f_data.interaction.hovered and not f_data.interaction.left_pressed:
                self.mili.rect({"color": (150, 150, 150), "outline_size": 1})
                self.glow(f_data.id, f_data.absolute_rect)
                self.content_info(dirpath)
            if f_data.interaction.left_just_released:
                self.open_folder(dirpath)
                self.any_press = True
            self.card_idx += 1

    def open_folder(self, dirpath):
        self.cur_path = dirpath
        self.mode = 1

    def update_view(self):
        self.clamp_offset()
        scale_func = (
            pygame.transform.smoothscale_by
            if self.smoothscale
            else pygame.transform.scale_by
        )
        scale = self.img_scale * self.view_zoom
        if self.view_zoom <= 1:
            self.img_output = scale_func(self.cur_img, scale)
            self.view_offset = pygame.Vector2()
        else:
            subw, subh = (
                self.cur_img.width / self.view_zoom + 2,
                self.cur_img.height / self.view_zoom + 2,
            )
            if subw * scale < W:
                subw = W / scale
            if subh * scale < H:
                subh = H / scale
            subw = min(subw, self.cur_img.width - 1)
            subh = min(subh, self.cur_img.height - 1)
            subs = self.cur_img.subsurface(
                pygame.FRect(0, 0, subw, subh)
                .move_to(
                    center=(
                        self.cur_img.width / 2 + self.view_offset.x / scale,
                        self.cur_img.height / 2 + self.view_offset.y / scale,
                    )
                )
                .clamp(self.cur_img.get_frect())
            )
            sw, sh = subs.size
            if sw * scale > W * 2:
                scale = (W * 2) / sw
            if sh * scale > H * 2:
                scale = (H * 2) / sh
            self.img_output = scale_func(subs, scale)

    def clamp_offset(self):
        w, h = (
            self.cur_img.width / 2 * self.view_zoom * self.img_scale,
            self.cur_img.height / 2 * self.view_zoom * self.img_scale,
        )
        self.view_offset.x = pygame.math.clamp(self.view_offset.x, -w, h)
        self.view_offset.y = pygame.math.clamp(self.view_offset.y, -h, h)

    def open_image(self, file):
        self.reset_view()
        self.cur_file = file
        self.mode = 2
        try:
            self.cur_img = self.loaded_images[self.cur_path][self.cur_file]
        except Exception:
            self.back_to_content()
            return
        if self.cur_img.width >= self.cur_img.height:
            self.img_scale = W / self.cur_img.width
            self.img_wm = 1
            self.img_hm = self.cur_img.height / self.cur_img.height
            if self.cur_img.height * self.img_scale > H:
                self.img_scale = H / self.cur_img.height
                self.img_hm = 1
                self.img_wm = self.cur_img.width / self.cur_img.height
        else:
            self.img_scale = H / self.cur_img.height
            self.img_hm = 1
            self.img_wm = self.cur_img.width / self.cur_img.height
            if self.cur_img.width * self.img_scale > W:
                self.img_scale = W / self.cur_img.width
                self.img_wm = 1
                self.img_hm = self.cur_img.height / self.cur_img.height
        self.update_view()

    def back_to_folder(self):
        self.cur_file = None
        self.mode = 1
        self.schedule_for_open = None
        self.reset_view()

    def content_info(self, dirpath):
        preview = pygame.mouse.get_pressed()[1]
        extra = {}
        if preview:
            self.any_press = True
            extra = {
                "grid": True,
                "resizex": {"max": min(W / 2, W - S - pygame.mouse.get_pos()[0])},
                "axis": "x",
            }
        with self.mili.begin(
            (pygame.mouse.get_pos(), (0, 0)),
            {
                "blocking": False,
                "ignore_grid": True,
                "parent_id": self.main_data.id,
                "resizex": True,
                "resizey": True,
                "z": 99999,
                **extra,
            },
        ):
            size = self.size if self.size != "list" else "xxs"
            self.mili.rect({"color": (85, 85, 90)})
            self.mili.rect({"color": (150, 150, 150), "outline_size": 1})
            any_valid = False
            for file in self.folder_contents_abs[dirpath]:
                loading = False
                if preview:
                    self.load_if_necessary(dirpath, file)
                    img = self.loaded_images[dirpath].get(file, None)
                    if img == "loading":
                        loading = True
                    if img is None:
                        continue
                else:
                    self.load_size_if_necessary(dirpath, file)
                    s = self.images_sizes[dirpath].get(file, None)
                    if s is None:
                        continue
                any_valid = True
                if self.mili.element(
                    (0, 0, self.preview_sizes[size], self.preview_sizes[size])
                    if preview
                    else None,
                    {},
                ):
                    if preview:
                        if loading:
                            self.mili.text("Loading...", {"size": 17})
                        else:
                            self.mili.image(
                                img,
                                {
                                    "cache": self.images_cache[dirpath][file],
                                    "smoothscale": self.smoothscale,
                                },
                            )
                    else:
                        self.mili.text(self.image_str(file, dirpath), {"size": 17})
            if not any_valid:
                self.mili.text_element("Error: No valid images found", {"size": 17})

    def load_if_necessary(self, dirpath, file):
        if dirpath not in self.loaded_images:
            self.loaded_images[dirpath] = {}
            self.images_cache[dirpath] = {}
            self.images_sizes[dirpath] = {}
        if file not in self.loaded_images[dirpath]:
            self.loaded_images[dirpath][file] = "loading"
            self.images_cache[dirpath][file] = mili.ImageCache()
            try:
                imgsize = imagesize.get(os.path.join(dirpath, file))
                if imgsize[0] == -1 or imgsize[1] == -1:
                    self.loaded_images[dirpath][file] = None
                    self.images_sizes[dirpath][file] = None
                    return
                self.images_sizes[dirpath][file] = imgsize
                if imgsize[0] > 20000 or imgsize[1] > 20000:
                    self.loaded_images[dirpath][file] = None
                threading.Thread(
                    target=load_image_async,
                    args=(dirpath, file, self.loaded_images[dirpath]),
                ).start()
            except Exception:
                self.loaded_images[dirpath][file] = None
                self.images_sizes[dirpath][file] = None

    def load_size_if_necessary(self, dirpath, file):
        if dirpath not in self.loaded_images:
            self.loaded_images[dirpath] = {}
            self.images_cache[dirpath] = {}
            self.images_sizes[dirpath] = {}
        if file not in self.images_sizes[dirpath]:
            try:
                imgsize = imagesize.get(os.path.join(dirpath, file))
                if imgsize[0] == -1 or imgsize[1] == -1:
                    self.loaded_images[dirpath][file] = None
                    self.images_sizes[dirpath][file] = None
                    return
                self.images_sizes[dirpath][file] = imgsize
                if imgsize[0] > 20000 or imgsize[1] > 20000:
                    self.loaded_images[dirpath][file] = None
            except Exception:
                self.loaded_images[dirpath][file] = None
                self.images_sizes[dirpath][file] = None

    def ui_x(self):
        with self.mili.begin(
            pygame.Rect(0, 0, 40, 40).move_to(topright=(W - S, S)),
            {"ignore_grid": True, "z": 9999},
            get_data=True,
        ) as x_data:
            self.base_btn_img(x_data)
            self.mili.line((("-30", "-30"), ("30", "30")), {"size": 1})
            self.mili.line((("-30", "30"), ("30", "-30")), {"size": 1})
            self.base_btn_hover(x_data)
            if x_data.interaction.left_just_released:
                self.exit()

    def ui(self):
        self.any_press = False
        with self.mili.begin(
            self.screen.get_rect(),
            {
                "axis": "y",
                "ignore_grid": True,
                "mid_draw_func": (self.draw_view if self.mode == 2 else None),
            },
            get_data=True,
        ) as self.main_data:
            self.mili.image(
                self.desktop_bg, {"fill": True, "cache": self.desktop_cache}
            )

            getattr(self, f"ui_{self.mode}")()

        self.ui_x()

        if self.size_menu_open:
            self.ui_size_menu()
        else:
            if not self.any_press:
                if pygame.mouse.get_just_released()[2]:
                    self.size_menu_open = True
                    self.size_menu_pos = pygame.mouse.get_pos()

    def ui_size_menu(self):
        if pygame.mouse.get_just_released()[2]:
            self.size_menu_pos = pygame.mouse.get_pos()
        with self.mili.begin(
            (self.size_menu_pos, (0, 0)),
            {
                "resizex": True,
                "resizey": True,
                "z": 9999,
                "parent_id": self.main_data.id,
            },
            get_data=True,
        ) as menu_data:
            if self.any_press:
                self.size_menu_open = False
            else:
                if (
                    pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[1]
                ) and not menu_data.absolute_rect.collidepoint(pygame.mouse.get_pos()):
                    self.size_menu_open = False

            self.mili.rect({"color": (75, 75, 80)})
            self.mili.rect({"color": (150, 150, 150), "outline_size": 1})

            if self.mode == 2:
                self.size_menu_reset_view()

            self.mili.text_element("Smoothscale", {"size": 22})
            with self.mili.begin(None, {"fillx": True, "resizey": True, "axis": "x"}):
                self.size_menu_smoothscale_option(True, self.smoothscale)
                self.size_menu_smoothscale_option(False, not self.smoothscale)

            self.mili.text_element("Size", {"size": 22})
            for size_name in ["list"] + list(self.folder_sizes.keys()):
                self.size_menu_size(size_name)

    def size_menu_reset_view(self):
        if rv_int := self.mili.element(None, {"fillx": True}):
            self.mili.rect(
                mili.conditional_style(
                    rv_int,
                    {"color": (85, 85, 90)},
                    {"color": (105, 105, 110)},
                    {"color": (75, 75, 80)},
                )
            )
            self.mili.text("Reset View", {"size": 19})
            self.mili.rect({"color": (145, 145, 150), "outline_size": 1})
            if rv_int.left_just_released:
                self.reset_view_data()
                self.update_view()

    def size_menu_size(self, size_name):
        if s_int := self.mili.element((0, 0, mili.percentage(8, W), 0)):
            self.mili.rect(
                mili.conditional_style(
                    s_int,
                    {"color": (85, 85, 90)},
                    {"color": (105, 105, 110)},
                    {"color": (75, 75, 80)},
                    size_name == self.size,
                )
            )
            self.mili.text(f"{size_name.upper()}", {"size": 19, "growx": False})
            self.mili.rect({"color": (145, 145, 150), "outline_size": 1})
            if s_int.left_just_released:
                self.size = size_name
                self.save_data()

    def size_menu_smoothscale_option(self, option, selected):
        if opt_int := self.mili.element(None, {"fillx": True}):
            self.mili.rect(
                mili.conditional_style(
                    opt_int,
                    {"color": (85, 85, 90)},
                    {"color": (105, 105, 110)},
                    {"color": (75, 75, 80)},
                    selected,
                )
            )
            self.mili.text("ON" if option else "OFF", {"size": 19})
            self.mili.rect({"color": (145, 145, 150), "outline_size": 1})
            if opt_int.left_just_released:
                self.smoothscale = option
                self.save_data()
                if self.mode == 2:
                    self.update_view()

    def glow(self, parent_id, abs_rect):
        self.mili.image_element(
            self.hover_surf,
            {"cache": self.hover_cache},
            pygame.Rect(0, 0, 300, 300).move_to(
                center=pygame.Vector2(pygame.mouse.get_pos()) - abs_rect.topleft
            ),
            {"blocking": False, "ignore_grid": True, "parent_id": parent_id},
        )

    def image_str(self, file, dirpath):
        self.load_size_if_necessary(dirpath, file)
        size = self.images_sizes[dirpath].get(file, None)
        img: pygame.Surface = self.loaded_images[dirpath].get(file, None)
        if size is None:
            return "Couldn't load image (you shouldn't be able to see this error, report it please)"
        if img == "loading":
            return f"{file} | {size[0]} x {size[1]} (loading...)"
        return f"{file} | {size[0]} x {size[1]}"

    def run(self):
        global W, H
        while True:
            self.mili.start()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.exit()
                if e.type == pygame.MOUSEBUTTONDOWN and (
                    e.button == pygame.BUTTON_MIDDLE or e.button == pygame.BUTTON_LEFT
                ):
                    self.drag_pos = pygame.Vector2(pygame.mouse.get_pos())
                    self.drag_offset = self.view_offset.copy()
                if e.type == pygame.MOUSEMOTION and self.mode == 2:
                    if (
                        pygame.mouse.get_pressed()[1] or pygame.mouse.get_pressed()[0]
                    ) and not (
                        pygame.mouse.get_just_pressed()[1]
                        or pygame.mouse.get_just_pressed()[0]
                    ):
                        old_offset = self.view_offset.copy()
                        self.view_offset = self.drag_offset - (
                            pygame.mouse.get_pos() - self.drag_pos
                        )
                        self.clamp_offset()
                        if self.view_offset != old_offset:
                            self.update_view()
                if e.type == pygame.MOUSEWHEEL:
                    if self.mode == 2:
                        self.view_zoom += (e.y * 0.05) * self.view_zoom
                        self.view_zoom = pygame.math.clamp(self.view_zoom, 0.01, 1000)
                        self.update_view()
                    else:
                        self.content_scroll.scroll(e.x, -e.y * 50)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        if self.mode == 1:
                            self.back_to_content()
                if e.type == pygame.VIDEORESIZE:
                    W, H = e.w, e.h
                    self.compute_sizes()
                    if self.mode == 2:
                        self.open_image(self.cur_file)

            self.screen.fill(0)

            if self.schedule_for_open is not None and self.cur_path is not None:
                img = self.loaded_images[self.cur_path][self.schedule_for_open]
                if img is not None and img != "loading":
                    self.open_image(self.schedule_for_open)
                    self.schedule_for_open = None

            if pygame.time.get_ticks() - self.last_cache_time > 6000:
                self.cache_folder_contents()
                self.last_cache_time = pygame.time.get_ticks()

            self.ui()

            self.mili.update_draw()

            pygame.display.flip()
            self.clock.tick(0)
            pygame.display.set_caption(str(int(self.clock.get_fps())))


if __name__ == "__main__":
    App().run()
