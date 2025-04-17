from .mili import (
    MILI,
    MarkDown,
    register_custom_component,
    pack_component,
    get_font_cache,
    clear_font_cache,
)
from .data import ElementData, Interaction, ImageCache, TextCache, ImageLayerCache, ParentCache
from .style import RESIZE, X, CENTER, PADLESS, FLOATING, FILL, SPACELESS
from .utility import (
    Selectable,
    Dragger,
    Scroll,
    Scrollbar,
    Slider,
    DropMenu,
    EntryLine,
    GenericApp,
    UIApp,
    AdaptiveUIScaler,
    InteractionSound,
    InteractionCursor,
    CustomWindowBorders,
    CustomWindowBehavior,
    percentage,
    fit_image,
)
from . import error
from . import style
from . import typing
from . import data
from . import animation
from . import icon

from collections import namedtuple
# explain UIApp in guide
VERSION = namedtuple("VersionInfo", "major minor micro")(1, 0, 6)
VERSION_STR = f"{VERSION.major}.{VERSION.minor}.{VERSION.micro}"
del namedtuple

__all__ = (
    "MILI",
    "MarkDown",
    "ElementData",
    "Interaction",
    "ImageCache",
    "TextCache",
    "ImageLayerCache",
    "ParentCache",
    "Selectable",
    "Dragger",
    "Scroll",
    "Scrollbar",
    "Slider",
    "DropMenu",
    "EntryLine",
    "GenericApp",
    "UIApp",
    "AdaptiveUIScaler",
    "InteractionSound",
    "InteractionCursor",
    "CustomWindowBorders",
    "CustomWindowBehavior",
    "percentage",
    "fit_image",
    "register_custom_component",
    "pack_component",
    "get_font_cache",
    "clear_font_cache",
    "RESIZE",
    "X",
    "CENTER",
    "PADLESS",
    "FLOATING",
    "SPACELESS",
    "FILL",
    "error",
    "style",
    "typing",
    "data",
    "animation",
    "icon",
    "VERSION",
    "VERSION_STR",
)
