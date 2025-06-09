import pygame
import typing
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from mili import MILI as _MILI

__all__ = (
    "ImageCache",
    "TextCache",
    "ParentCache",
    "ImageLayerCache",
    "Interaction",
    "ElementData",
)


class ParentCache:
    def __init__(self, static):
        self._cache = None
        self._rebuild = True
        self._size = None
        self._grid = None
        self._static = static
        self._style = None

    def refresh(self):
        self._rebuild = True
        self._cache = {
            "children": [],
            "children_grid": [],
            "children_fillx": [],
            "children_filly": [],
        }
        self._grid = None


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
    def get_next_cache(cls):
        cls._preallocated_index += 1
        if cls._preallocated_index > len(cls._preallocated_caches) - 1:
            cls._preallocated_caches.append(ImageCache())
        return cls._preallocated_caches[cls._preallocated_index]


class ImageLayerCache:
    def __init__(
        self,
        mili: "_MILI",
        size: typing.Sequence[float],
        offset: typing.Sequence[float] = (0, 0),
        blit_flags: int = 0,
    ):
        self._offset = pygame.Vector2(0, 0)
        self._surface = pygame.Surface((0, 0))
        self.size = size
        self.active = True
        self.blit_flags: int = blit_flags
        self._offset = pygame.Vector2(offset)
        self._erase_rects: tuple[pygame.Rect, ...] | None = None
        self._mili = mili
        self._caches = []
        self._caches_set = set()
        self._caches_activity = {}
        self._rendered = False
        self._mili._ctx._image_layer_caches.append(self)

    @property
    def erase_rects(self) -> tuple[pygame.Rect, ...] | None:
        return self._erase_rects

    @erase_rects.setter
    def erase_rects(self, v):
        if v is None:
            if v != self._erase_rects:
                self._dirty = True
            self._erase_rects = v
            return
        v = tuple(v)
        if self._erase_rects is None:
            self._erase_rects = v
            self._dirty = True
            return
        if len(v) != len(self._erase_rects):
            self._erase_rects = v
            self._dirty = True
            return
        for i in range(len(v) - 1):
            a, b = v[i], self._erase_rects[i]
            if a != b:
                self._dirty = True
                break
        self._erase_rects = v

    @property
    def offset(self) -> pygame.Vector2:
        return self._offset

    @offset.setter
    def offset(self, v: typing.Sequence[float]):
        if v == self._offset:
            return
        self._offset = pygame.Vector2(v)
        self._dirty = True

    @property
    def size(self) -> pygame.Vector2:
        return pygame.Vector2(self._surface.size)

    @size.setter
    def size(self, v: typing.Sequence[float]):
        if v == self._surface.size:
            return
        self._surface = pygame.Surface(v, pygame.SRCALPHA)
        self._dirty = True

    def destroy(self):
        self._mili._ctx._image_layer_caches.remove(self)


class TextCache:
    _preallocated_caches = []
    _preallocated_index = -1

    def __init__(self):
        self._cache: dict[str, typing.Any] | None = None
        self._rich: dict | None = None

    def get_output(self) -> pygame.Surface | None:
        if self._cache is None:
            return None
        return self._cache["output"]

    @classmethod
    def get_next_cache(cls):
        cls._preallocated_index += 1
        if cls._preallocated_index > len(cls._preallocated_caches) - 1:
            cls._preallocated_caches.append(TextCache())
        return cls._preallocated_caches[cls._preallocated_index]


@dataclass(slots=True)
class ElementGridData:
    overflowx: float
    overflowy: float
    padx: float
    pady: float
    spacing: float
    spacex: float
    spacey: float


@dataclass
class ElementData:
    rect: pygame.Rect
    absolute_rect: pygame.Rect
    z: int
    id: int
    style: dict[str, typing.Any]
    components: dict[typing.Literal["type", "style", "data"], typing.Any]
    parent_id: int
    _grid: dict | None | ElementGridData
    _children: list[dict]
    _children_ids: list[int] | None = None

    @property
    def grid(self) -> ElementGridData:
        if isinstance(self._grid, ElementGridData):
            return self._grid
        if self._grid is None:
            self._grid = ElementGridData(0, 0, 0, 0, 0, 0, 0)
            return self._grid
        self._grid = ElementGridData(**self._grid)
        return self._grid

    @property
    def children_ids(self) -> list[int]:
        if self._children_ids is None:
            self._children_ids = [el["id"] for el in self._children]
        return self._children_ids


@dataclass
class Interaction:
    _mili: "_MILI"
    hovered: bool
    press_button: int
    just_pressed_button: int
    just_released_button: int
    absolute_hover: bool
    unhover_pressed: bool
    _just_hover: int
    _raw_data: dict[str, typing.Any]
    _data: ElementData | None = None
    _did_begin: bool = False
    parent: "Interaction|None" = None

    @property
    def just_hovered(self) -> bool:
        return self._just_hover == 1

    @property
    def just_unhovered(self) -> bool:
        return self._just_hover == -1

    @property
    def left_pressed(self) -> bool:
        return self.press_button == pygame.BUTTON_LEFT

    @property
    def left_just_pressed(self) -> bool:
        return self.just_pressed_button == pygame.BUTTON_LEFT

    @property
    def left_just_released(self) -> bool:
        return self.just_released_button == pygame.BUTTON_LEFT

    left_clicked = left_just_released

    @property
    def right_pressed(self) -> bool:
        return self.press_button == pygame.BUTTON_RIGHT

    @property
    def right_just_pressed(self) -> bool:
        return self.just_pressed_button == pygame.BUTTON_RIGHT

    @property
    def right_just_released(self) -> bool:
        return self.just_released_button == pygame.BUTTON_RIGHT

    right_clicked = right_just_released

    @property
    def middle_pressed(self) -> bool:
        return self.press_button == pygame.BUTTON_MIDDLE

    @property
    def middle_just_pressed(self) -> bool:
        return self.just_pressed_button == pygame.BUTTON_MIDDLE

    @property
    def middle_just_released(self) -> bool:
        return self.just_released_button == pygame.BUTTON_MIDDLE

    middle_clicked = middle_just_released

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
        if self._did_begin:
            self._mili.end()
