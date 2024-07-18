import pygame
import typing
from mili import error as _error

if typing.TYPE_CHECKING:
    from mili import MILI as _MILI

__all__ = ("ImageCache", "Interaction", "ElementData")


class ImageCache:
    _preallocated_caches = []
    _preallocated_index = -1

    def __init__(self):
        self._cache = None

    def get_output(self) -> pygame.Surface:
        if self._cache is None:
            return None
        return self._cache.get("output", None)

    @classmethod
    def preallocate_caches(cls, amount: int):
        cls._preallocated_caches = [ImageCache() for _ in range(amount)]

    @classmethod
    def get_next_cache(cls):
        cls._preallocated_index += 1
        if cls._preallocated_index > len(cls._preallocated_caches) - 1:
            raise _error.MILIStatusError(
                "Too few image caches preallocated, failed to retrieve the next one"
            )
        return cls._preallocated_caches[cls._preallocated_index]


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
    overflowx: float
    overflowy: float
    padx: float
    pady: float
    spacing: float

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
