import typing
import pygame
from mili import data as _data

if typing.TYPE_CHECKING:
    from mili import _core

__all__ = (
    "NumberOrPercentage",
    "PointsLike",
    "AnimValueLike",
    "EasingLike",
    "ElementStyleLike",
    "RectStyleLike",
    "CircleStyleLike",
    "LineStyleLike",
    "PolygonStyleLike",
    "TextStyleLike",
    "ImageStyleLike",
    "AnyStyleLike",
    "ComponentProtocol",
)

type NumberOrPercentage = int | float | str
type BoundingAlignLike = typing.Literal[
    "center",
    "topleft",
    "bottomleft",
    "topright",
    "bottomright",
    "midleft",
    "left",
    "midright",
    "right",
    "midtop",
    "top",
    "midbottom",
    "bottom",
]
type PointsLike = typing.Sequence[typing.Sequence[NumberOrPercentage]]
type AnimValueLike = float | pygame.Color | typing.Sequence[float]
type EasingLike = typing.Callable[[float], float]


class _ElementStyleLike(typing.TypedDict):
    resizex: bool | dict[typing.Literal["min", "max"], NumberOrPercentage]
    resizey: bool | dict[typing.Literal["min", "max"], NumberOrPercentage]
    fillx: bool | NumberOrPercentage
    filly: bool | NumberOrPercentage
    blocking: bool
    ignore_grid: bool
    align: typing.Literal["first", "center", "last"]
    z: int
    parent_id: int
    offset: typing.Sequence[float]
    clip_draw: bool
    pre_draw_func: (
        typing.Callable[[pygame.Surface, _data.ElementData, pygame.Rect], None] | None
    )
    mid_draw_func: (
        typing.Callable[[pygame.Surface, _data.ElementData, pygame.Rect], None] | None
    )
    post_draw_func: (
        typing.Callable[[pygame.Surface, _data.ElementData, pygame.Rect], None] | None
    )
    update_id: str
    image_layer_cache: _data.ImageLayerCache | None

    axis: typing.Literal["x", "y"]
    spacing: NumberOrPercentage
    pad: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    anchor: typing.Literal["first", "center", "last", "max_spacing"]
    default_align: typing.Literal["first", "center", "last"]
    grid: bool
    grid_align: typing.Literal["first", "center", "last", "max_spacing"]
    grid_spacex: NumberOrPercentage
    grid_spacey: NumberOrPercentage


type ElementStyleLike = _ElementStyleLike | dict[str, typing.Any]


class _ComponentStyleLike(typing.TypedDict):
    draw_above: bool
    element_id: int


class _RectStyleLike(_ComponentStyleLike):
    pad: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    outline: NumberOrPercentage
    border_radius: NumberOrPercentage | typing.Iterable[NumberOrPercentage]
    color: pygame.typing.ColorLike
    aspect_ratio: float | None
    align: BoundingAlignLike
    dash_size: NumberOrPercentage | typing.Iterable[NumberOrPercentage] | None
    dash_offset: NumberOrPercentage


type RectStyleLike = _RectStyleLike | dict[str, typing.Any]


class _CircleStyleLike(_ComponentStyleLike):
    pad: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    outline: NumberOrPercentage
    color: pygame.typing.ColorLike
    antialias: bool
    aspect_ratio: float | None
    align: BoundingAlignLike
    corners: typing.Iterable[bool]
    dash_size: float | typing.Iterable[float] | None
    dash_anchor: float | typing.Iterable[float]


type CircleStyleLike = _CircleStyleLike | dict[str, typing.Any]


class _LineStyleLike(_ComponentStyleLike):
    size: NumberOrPercentage
    color: pygame.typing.ColorLike
    antialias: bool
    dash_size: NumberOrPercentage | typing.Iterable[NumberOrPercentage]
    dash_offset: NumberOrPercentage


type LineStyleLike = _LineStyleLike | dict[str, typing.Any]


class _PolygonStyleLike(_ComponentStyleLike):
    outline: NumberOrPercentage
    color: pygame.typing.ColorLike


type PolygonStyleLike = _PolygonStyleLike | dict[str, typing.Any]


class _TextStyleLike(_ComponentStyleLike):
    cache: _data.TextCache | None
    name: str | None
    size: int
    sysfont: bool
    align: BoundingAlignLike
    font_align: int
    bold: bool
    italic: bool
    underline: bool
    strikethrough: bool
    antialias: bool
    color: pygame.typing.ColorLike
    bg_color: pygame.typing.ColorLike
    growx: bool
    growy: bool
    pad: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    wraplen: NumberOrPercentage
    slow_grow: bool


type TextStyleLike = _TextStyleLike | dict[str, typing.Any]


class _ImageStyleLike(_ComponentStyleLike):
    cache: _data.ImageCache | None
    layer_cache: _data.ImageLayerCache | None
    pad: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    fill: bool
    stretchx: bool
    stretchy: bool
    fill_color: pygame.typing.ColorLike
    smoothscale: bool
    border_radius: NumberOrPercentage
    alpha: int
    ninepatch_size: NumberOrPercentage
    ready: bool


type ImageStyleLike = _ImageStyleLike | dict[str, typing.Any]


type AnyStyleLike = (
    ElementStyleLike
    | RectStyleLike
    | CircleStyleLike
    | LineStyleLike
    | PolygonStyleLike
    | TextStyleLike
    | ImageStyleLike
)


class ComponentProtocol(typing.Protocol):
    def draw(
        self,
        ctx: "_core._ctx",
        data: typing.Any,
        style: dict[str, typing.Any],
        element: dict[str, typing.Any],
        absolute_rect: pygame.Rect,
    ): ...

    def added(
        self,
        ctx: "_core._ctx",
        data: typing.Any,
        style: dict[str, typing.Any],
        element: dict[str, typing.Any],
    ): ...
