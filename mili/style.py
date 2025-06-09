import typing
import pygame
import functools

from mili import _core
from mili import error as _error
from mili import data as _data
from mili import typing as _typing

if typing.TYPE_CHECKING:
    from mili import MILI as _MILI

__all__ = (
    "Style",
    "StyleStatus",
    "conditional",
    "cond_value",
    "filter",
    "same",
    "RESIZE",
    "X",
    "CENTER",
    "PADLESS",
    "FLOATING",
    "SPACELESS",
)


class Style:
    def __init__(
        self,
        element: _typing.ElementStyleLike | None = None,
        rect: _typing.RectStyleLike | None = None,
        circle: _typing.CircleStyleLike | None = None,
        polygon: _typing.PolygonStyleLike | None = None,
        line: _typing.LineStyleLike | None = None,
        text: _typing.TextStyleLike | None = None,
        image: _typing.ImageStyleLike | None = None,
    ):
        self.styles = {
            "element": element if element else {},
            "rect": rect if rect else {},
            "circle": circle if circle else {},
            "polygon": polygon if polygon else {},
            "line": line if line else {},
            "text": text if text else {},
            "image": image if image else {},
        }

    def set(self, type: str, style: _typing.AnyStyleLike):
        if type not in self.styles:
            raise _error.MILIValueError("Invalid style type")
        self.styles[type] = style

    def sets(self, **types_styles: _typing.AnyStyleLike):
        for type, style in types_styles.items():
            self.set(type, style)

    def get(self, type: str) -> _typing.AnyStyleLike:
        if type not in self.styles:
            raise _error.MILIValueError("Invalid style type")
        return self.styles[type]

    get_element = functools.partialmethod(get, "element")
    get_rect = functools.partialmethod(get, "rect")
    get_circle = functools.partialmethod(get, "circle")
    get_polygon = functools.partialmethod(get, "polygon")
    get_line = functools.partialmethod(get, "line")
    get_text = functools.partialmethod(get, "text")
    get_image = functools.partialmethod(get, "image")

    def set_default(self, mili: "_MILI"):
        for name, style in self.styles.items():
            mili.default_style(name, style)


class StyleStatus:
    def __init__(
        self,
        base: Style | None = None,
        hover: Style | None = None,
        press: Style | None = None,
    ):
        self.base = base if base else Style()
        self.hover = hover if hover else Style()
        self.press = press if press else Style()

    def set(self, status: str, style: Style):
        if status not in ["base", "press", "hover"]:
            raise _error.MILIValueError("Invalid status type")
        setattr(self, status, style)

    def get(
        self, type: str, interaction: _data.Interaction, selected: bool = False
    ) -> _typing.AnyStyleLike:
        if type not in _core._globalctx._component_types.keys():
            raise _error.MILIValueError("Invalid style type")
        return conditional(
            interaction,
            self.base.get(type),  # type: ignore
            self.hover.get(type),  # type: ignore
            self.press.get(type),  # type: ignore
            selected,
        )

    get_element = functools.partialmethod(get, "element")
    get_rect = functools.partialmethod(get, "rect")
    get_circle = functools.partialmethod(get, "circle")
    get_polygon = functools.partialmethod(get, "polygon")
    get_line = functools.partialmethod(get, "line")
    get_text = functools.partialmethod(get, "text")
    get_image = functools.partialmethod(get, "image")


def conditional[TK, TV](
    interaction: _data.Interaction,
    base: dict[TK, TV] | None = None,
    hover: dict[TK, TV] | None = None,
    press: dict[TK, TV] | None = None,
    selected=False,
    press_button: int = pygame.BUTTON_LEFT,
    absolute_hover: bool = False,
    force_hover: bool = False,
) -> dict[TK, TV]:
    if hover is None:
        hover = {}
    if press is None:
        press = {}
    if base is None:
        base = {}
    new_base = {}
    new_base.update(base)
    if (
        interaction.hovered
        or (absolute_hover and interaction.absolute_hover)
        or force_hover
    ):
        if selected or interaction.press_button == press_button:
            new_base.update(press)
        else:
            new_base.update(hover)
    else:
        if selected or interaction.press_button == press_button:
            new_base.update(press)
    return new_base


def cond_value[TV](
    interaction: _data.Interaction,
    base: TV,
    hover: TV,
    press: TV,
    selected=False,
    press_button: int = pygame.BUTTON_LEFT,
    absolute_hover: bool = False,
    repeat: int = 1,
    force_hover: bool = False,
):
    if selected or interaction.press_button == press_button:
        return press if repeat <= 1 else (press,) * repeat
    if (
        interaction.hovered
        or (absolute_hover and interaction.absolute_hover)
        or force_hover
    ):
        return hover if repeat <= 1 else (hover,) * repeat
    return base if repeat <= 1 else (base,) * repeat


def filter[TK, TV](
    style: dict[TK, TV],
    whitelist: list[TK] | set[TK] | None = None,
    blacklist: list[TK] | set[TK] | None = None,
) -> dict[TK, TV]:
    if style is None:
        style = {}
    style = style.copy()
    if whitelist is not None:
        whitelist = set(whitelist)
        for name in list(style.keys()):
            if name not in whitelist:
                style.pop(name)
    if blacklist is not None:
        blacklist = set(blacklist)
        for bname in blacklist:
            if bname in style:
                style.pop(bname)
    return style


def same[TV](value: TV, *names: str) -> dict[str, TV]:
    return {name: value for name in names}


def color(color):
    return {"color": color}


def outline(color, size=1):
    return {"color": color, "outline": size, "draw_above": True}


RESIZE = {"resizex": True, "resizey": True}
FILL = {"fillx": True, "filly": True}
PADLESS = {"padx": 0, "pady": 0}
SPACELESS = {"spacing": 0, "grid_spacex": 0, "grid_spacy": 0}
X = {"axis": "x"}
CENTER = {
    "grid_align": "center",
    "anchor": "center",
    "align": "center",
    "default_align": "center",
    "font_align": pygame.FONT_CENTER,
}
FLOATING = {"ignore_grid": True, "parent_id": 0}
