import pygame
import typing

if typing.TYPE_CHECKING:
    from mili import MILI as _MILI

__all__ = ("ImageCache", "Interaction", "ElementData")


class ImageCache:
    def __init__(self):
        self._cache = None

    def get_output(self) -> pygame.Surface:
        if self._cache is None:
            return None
        return self._cache.get("output", None)


class Interaction:
    def __init__(
        self,
        mili: "_MILI",
        id: int,
        hovered: bool,
        press_button: bool,
        just_pressed_button: bool,
        just_released_button: bool,
        absolute_hover: bool,
    ):
        self._mili = mili
        self.id = id
        (
            self.hovered,
            self.press_button,
            self.just_pressed_button,
            self.just_released_button,
            self.absolute_hover,
        ) = (
            hovered,
            press_button,
            just_pressed_button,
            just_released_button,
            absolute_hover,
        )

    @property
    def left_pressed(self) -> bool:
        return self.press_button == pygame.BUTTON_LEFT

    @property
    def left_just_pressed(self) -> bool:
        return self.just_pressed_button == pygame.BUTTON_LEFT

    @property
    def left_just_released(self) -> bool:
        return self.just_released_button == pygame.BUTTON_LEFT

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self._mili.end()


class ElementGridData:
    overflow_x: float
    overflow_y: float

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)


class ElementData:
    interaction: Interaction
    rect: pygame.Rect
    absolute_rect: pygame.Rect
    z: int
    id: int
    style: dict[str]
    children_ids: list[int]
    parent_id: int
    grid: ElementGridData | None

    def __init__(self, mili: "_MILI", **kwargs):
        self._mili = mili
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self._mili.end()

    def __getattr__(self, name):
        if hasattr(self.interaction, name):
            return getattr(self.interaction, name)
        raise AttributeError
