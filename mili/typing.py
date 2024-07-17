import typing
import pygame
from mili import data as _data

__all__ = (
    "NumberOrPercentage",
    "ColorLike",
    "RectLike",
    "PointsLike",
    "ElementStyleLike",
    "RectStyleLike",
    "CircleStyleLike",
    "LineStyleLike",
    "PolygonStyleLike",
    "TextStyleLike",
    "ImageStyleLike",
    "AnyStyleLike",
)

type NumberOrPercentage = int | float | str
type ColorLike = int | str | typing.Sequence[int] | pygame.Color
type RectLike = typing.Sequence[float | typing.Sequence[float]] | pygame.Rect
type PointsLike = typing.Sequence[typing.Sequence[NumberOrPercentage]]


class ElementStyleLike(typing.TypedDict):
    resizex: bool | dict[typing.Literal["min", "max"], NumberOrPercentage]
    resizey: bool | dict[typing.Literal["min", "max"], NumberOrPercentage]
    fillx: bool | NumberOrPercentage
    filly: bool | NumberOrPercentage
    blocking: bool
    ignore_grid: bool
    align: typing.Literal["first", "center", "last"]
    z: int
    parent_id: int

    axis: typing.Literal["x", "y"]
    spacing: NumberOrPercentage
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    anchor: typing.Literal["first", "center", "last", "max_spacing"]
    grid: bool
    grid_align: typing.Literal["first", "center", "last", "max_spacing"]
    grid_spacex: NumberOrPercentage
    grid_spacey: NumberOrPercentage


class RectStyleLike(typing.TypedDict):
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    outline: NumberOrPercentage
    border_radius: NumberOrPercentage
    color: ColorLike


class CircleStyleLike(typing.TypedDict):
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    outline: NumberOrPercentage
    color: ColorLike


class LineStyleLike(typing.TypedDict):
    size: NumberOrPercentage
    color: ColorLike


class PolygonStyleLike(typing.TypedDict):
    outline: NumberOrPercentage
    color: ColorLike


class TextStyleLike(typing.TypedDict):
    name: str | None
    size: int
    align: typing.Literal[
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
    padx: NumberOrPercentage
    pady: NumberOrPercentage
    wraplen: NumberOrPercentage


class ImageStyleLike(typing.TypedDict):
    cache: _data.ImageCache | None
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


type AnyStyleLike = (
    ElementStyleLike
    | RectStyleLike
    | CircleStyleLike
    | LineStyleLike
    | PolygonStyleLike
    | TextStyleLike
    | ImageStyleLike
)
