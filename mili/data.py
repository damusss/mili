import pygame
import typing
from mili import error as _error
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from mili import MILI as _MILI

__all__ = ("ImageCache", "Interaction", "ElementData")


class ImageCache:
    _preallocated_caches = []
    _preallocated_index = -1

    def __init__(self):
        self._cache: dict[str, typing.Any] | None = None

    def get_output(self) -> pygame.Surface | None:
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


@dataclass
class ElementGridData:
    overflowx: float
    overflowy: float
    padx: float
    pady: float
    spacing: float


@dataclass
class ElementData:
    rect: pygame.Rect
    absolute_rect: pygame.Rect
    z: int
    id: int
    style: dict[str, typing.Any]
    children_ids: list[int]
    components: dict[typing.Literal["type", "style", "data"], typing.Any]
    parent_id: int
    grid: ElementGridData


@dataclass
class Interaction:
    _mili: "_MILI"
    hovered: bool
    press_button: int
    just_pressed_button: int
    just_released_button: int
    absolute_hover: bool
    unhover_pressed: bool
    just_hovered: bool
    just_unhovered: bool
    _raw_data: dict[str, typing.Any]
    _data: ElementData | None = None

    @property
    def left_pressed(self) -> bool:
        return self.press_button == pygame.BUTTON_LEFT

    @property
    def left_just_pressed(self) -> bool:
        return self.just_pressed_button == pygame.BUTTON_LEFT

    @property
    def left_just_released(self) -> bool:
        return self.just_released_button == pygame.BUTTON_LEFT

    @property
    def data(self) -> ElementData:
        if self._data is None:
            self._data = self._mili._ctx._coreutils._element_data(
                self._mili._ctx, self._raw_data
            )
        return self._data

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self._mili.end()
