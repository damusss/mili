import pygame
from mili import _core
from mili import _richtext
from mili._utils._window import GenericApp, UIApp, AdaptiveUIScaler, CustomWindowBorders, CustomWindowBehavior
from mili._utils._interaction import (
    InteractionCursor,
    InteractionSound,
)
from mili._utils._prefabs import (
    Dragger,
    Selectable,
    Scroll,
    Scrollbar,
    Slider,
    DropMenu,
    EntryLine,
)

__all__ = (
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
)

_richtext.ScrollClass = Scroll
_richtext.ScrollbarClass = Scrollbar


def percentage(percentage: float, value: float) -> float:
    return (percentage * value) / 100


def fit_image(
    rect: pygame.typing.RectLike,
    surface: pygame.Surface,
    padx: int = 0,
    pady: int = 0,
    do_fill: bool = False,
    do_stretchx: bool = False,
    do_stretchy: bool = False,
    fill_color: pygame.typing.ColorLike | None = None,
    border_radius: int = 0,
    alpha: int = 255,
    smoothscale: bool = False,
    ninepatch: int = 0,
    ready_border_radius: int = 0,
) -> pygame.Surface:
    return _core._coreutils._get_image(
        pygame.Rect(rect),
        surface,
        int(padx),
        int(pady),
        do_fill,
        do_stretchx,
        do_stretchy,
        fill_color,
        int(border_radius),
        int(alpha),
        smoothscale,
        int(ninepatch),
        int(ready_border_radius),
    )
