import pygame
import typing
from mili import data as _data
from mili import _core

__all__ = ("Selectable", "Dragger", "Scroll", "percentage", "gray", "indent")


class Selectable:
    def __init__(self, selected: bool = False):
        self.selected: bool = selected

    def update(
        self,
        element: _data.Interaction | _data.ElementData,
        selectable_group: typing.Sequence["Selectable"] = None,
        can_deselect_group: bool = True,
    ) -> _data.Interaction | _data.ElementData:
        if selectable_group is None:
            selectable_group = []
        interaction = element
        if isinstance(element, _data.ElementData):
            interaction = element.interaction
        if interaction.left_just_released:
            self.selected = not self.selected
            if len(selectable_group) > 0:
                if self.selected:
                    for sel in selectable_group:
                        if sel is not self:
                            sel.selected = False
                elif not can_deselect_group:
                    one = False
                    for sel in selectable_group:
                        if sel is not self and sel.selected:
                            one = True
                            break
                    if not one:
                        self.selected = True
        elif len(selectable_group) > 0:
            for sel in selectable_group:
                if sel is not self and sel.selected:
                    self.selected = False
                    break
        return element


class Dragger:
    def __init__(self, position: typing.Sequence = None):
        if position is None:
            position = (0, 0)
        self.position = pygame.Vector2(position)
        self.rel = pygame.Vector2()

    def update(
        self, element: _data.Interaction | _data.ElementData
    ) -> _data.Interaction | _data.ElementData:
        if element.left_pressed:
            self.position += _core._globalctx._mouse_rel
            self.rel = _core._globalctx._mouse_rel.copy()
        return element


class Scroll:
    def __init__(self):
        self.scroll_offset: pygame.Vector2 = pygame.Vector2()
        self._element_data: _data.ElementData = None

    def update(self, element_data: _data.ElementData) -> _data.ElementData:
        if not isinstance(element_data, _data.ElementData):
            raise TypeError("element_data argument must be of type _data.ElementData")
        self._element_data = element_data
        self.clamp()
        return element_data

    def scroll(self, x: float, y: float):
        self.scroll_offset.x += x
        self.scroll_offset.y += y
        self.clamp()

    def set_scroll(self, x: float, y: float):
        self.scroll_offset.x = x
        self.scroll_offset.y = y
        self.clamp()

    def clamp(self):
        maxx, maxy = float("inf"), float("inf")
        if self._element_data is not None and self._element_data.grid is not None:
            maxx = self._element_data.grid.overflow_x
            maxy = self._element_data.grid.overflow_y
        self.scroll_offset.x = pygame.math.clamp(self.scroll_offset.x, 0, maxx)
        self.scroll_offset.y = pygame.math.clamp(self.scroll_offset.y, 0, maxy)

    def get_offset(self) -> tuple[float, float]:
        return (-self.scroll_offset.x, -self.scroll_offset.y)


def percentage(percentage: float, value: float) -> float:
    return (percentage * value) / 100


def gray(value=100):
    return (value, value, value)


def indent(*args, **kwargs): ...
