import typing
import pygame
from mili import data as _data

if typing.TYPE_CHECKING:
    from mili import _core

__all__ = (
    "NumberOrPercentage",
    "ColorLike",
    "RectLike",
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
type ColorLike = int | str | typing.Sequence[int] | pygame.Color
type RectLike = typing.Sequence[float | typing.Sequence[float]] | pygame.Rect
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


class _RectStyleLike(typing.TypedDict):
    pad: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    outline: NumberOrPercentage
    border_radius: NumberOrPercentage | typing.Iterable[NumberOrPercentage]
    color: ColorLike
    aspect_ratio: float | None
    align: BoundingAlignLike
    draw_above: bool


type RectStyleLike = _RectStyleLike | dict[str, typing.Any]


class _CircleStyleLike(typing.TypedDict):
    pad: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    outline: NumberOrPercentage
    color: ColorLike
    antialias: bool
    aspect_ratio: float | None
    align: BoundingAlignLike
    corners: typing.Iterable[bool]
    dash_size: float | typing.Iterable[float]
    dash_anchor: float | typing.Iterable[float]
    draw_above: bool


type CircleStyleLike = _CircleStyleLike | dict[str, typing.Any]


class _LineStyleLike(typing.TypedDict):
    size: NumberOrPercentage
    color: ColorLike
    antialias: bool
    dash_size: NumberOrPercentage | typing.Iterable[NumberOrPercentage]
    dash_offset: NumberOrPercentage
    draw_above: bool


type LineStyleLike = _LineStyleLike | dict[str, typing.Any]


class _PolygonStyleLike(typing.TypedDict):
    outline: NumberOrPercentage
    color: ColorLike
    draw_above: bool


type PolygonStyleLike = _PolygonStyleLike | dict[str, typing.Any]


class _TextStyleLike(typing.TypedDict):
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
    color: ColorLike
    bg_color: ColorLike
    growx: bool
    growy: bool
    pad: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    wraplen: NumberOrPercentage
    draw_above: bool
    slow_grow: bool


type TextStyleLike = _TextStyleLike | dict[str, typing.Any]


class _ImageStyleLike(typing.TypedDict):
    cache: _data.ImageCache | None
    pad: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    fill: bool
    stretchx: bool
    stretchy: bool
    fill_color: ColorLike
    smoothscale: bool
    border_radius: NumberOrPercentage
    alpha: int
    ninepatch_size: NumberOrPercentage
    draw_above: bool


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
