import typing
import pygame
from mili import data as _data

if typing.TYPE_CHECKING:
    from mili import _core
    from mili import utility

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
    "ScrollbarStyleLike",
    "SliderStyleLike",
    "DropMenuStyleLike",
    "EntryLineStyleLike",
    "MarkDownStyleLike",
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


class _ConditionalColorStyleLike(typing.TypedDict):
    default: pygame.typing.ColorLike | None
    hover: pygame.typing.ColorLike | None
    pressed: pygame.typing.ColorLike | None


class _MarkDownCodeCopyStyleLike(typing.TypedDict):
    size: float
    icon_color: _ConditionalColorStyleLike
    icon_pad: NumberOrPercentage


class _MarkDownCodeScrollbarStyleLike(typing.TypedDict):
    border_radius: float
    height: float
    padx: float
    pady: float
    bar_color: pygame.typing.ColorLike | None
    handle_color: _ConditionalColorStyleLike


class MarkDownStyleLike(typing.TypedDict):
    element_style: "ElementStyleLike"
    rect_style: "RectStyleLike"
    circle_style: "CircleStyleLike"
    line_style: "LineStyleLike"
    image_style: "ImageStyleLike"
    text_style: "TextStyleLike"
    quote_width: float
    quote_border_radius: float
    indent_width: float
    separator_height: float
    line_break_size: float
    bullet_diameter: float
    table_outline_size: float
    table_border_radius: float
    table_alignx: typing.Literal["left", "center", "right"]
    table_aligny: typing.Literal["top", "center", "bottom"]
    line_break_color: pygame.typing.ColorLike
    bullet_color: pygame.typing.ColorLike
    table_bg_color: pygame.typing.ColorLike|None
    quote_color: pygame.typing.ColorLike
    code_bg_color: pygame.typing.ColorLike
    code_outline_color: pygame.typing.ColorLike
    code_border_radius: NumberOrPercentage
    code_copy_style: _MarkDownCodeCopyStyleLike
    code_scrollbar_style: _MarkDownCodeScrollbarStyleLike
    title1_size: int
    title2_size: int
    title3_size: int
    title4_size: int
    title5_size: int
    title6_size: int
    allow_image_link: bool
    change_cursor: bool
    load_images_async: bool
    open_links_in_browser: bool
    parse_async: bool


class ScrollbarStyleLike(typing.TypedDict):
    axis: typing.Literal["x", "y"]
    short_size: float
    border_dist: float
    padding: float
    size_reduce: float
    bar_update_id: str | None
    handle_update_id: str | None


class SliderStyleLike(typing.TypedDict):
    lock_x: bool
    lock_y: bool
    handle_size: typing.Sequence[float]
    strict_borders: bool
    area_update_id: str | None
    handle_update_id: str | None


class DropMenuStyleLike(typing.TypedDict):
    direction: typing.Literal["up", "down"]
    anchor: typing.Literal["first", "center", "last"]
    padding: float
    selected_update_id: str | None
    option_update_id: str | None
    menu_update_id: str | None


class EntryLineStyleLike(typing.TypedDict):
    placeholder: str
    placeholder_color: pygame.typing.ColorLike
    text_filly: str
    text_style: "TextStyleLike"
    bg_rect_style: "RectStyleLike|None"
    outline_rect_style: "RectStyleLike|None"
    selection_style: "RectStyleLike|None"
    selection_color: pygame.typing.ColorLike | None
    error_color: pygame.typing.ColorLike
    cursor_color: pygame.typing.ColorLike
    cursor_width: int
    blink_interval: int
    double_click_interval: int
    input_validator: typing.Callable[[str], str | None] | None
    text_validator: typing.Callable[[str], tuple[str, bool]] | None
    validator_lowercase: bool
    validator_uppercase: bool
    validator_windows_path: bool
    target_number: bool
    number_min: float | None
    number_max: float | None
    number_integer: bool
    enable_history: bool
    history_limit: int | None
    keymod: int
    copy_key: int | None
    paste_key: int | None
    cut_key: int | None
    select_all_key: int | None
    delete_all_key: int | None
    undo_key: int | None
    redo_key: int | None
    scroll: "utility.Scroll|None"


class _ElementStyleLike(typing.TypedDict):
    resizex: bool
    resizey: bool
    fillx: bool | NumberOrPercentage
    filly: bool | NumberOrPercentage
    size_clamp: (
        dict[typing.Literal["min", "max"], tuple[float | None, float | None]] | None
    )
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
    parent_flag: int
    cache_rect_size: bool

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
    ready_rect: pygame.typing.RectLike | None


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


class _TextRichMarkdownStyleLike(typing.TypedDict):
    spoiler_color: pygame.typing.ColorLike
    spoiler_text_color: pygame.typing.ColorLike
    code_bg_color: pygame.typing.ColorLike
    code_text_color: pygame.typing.ColorLike
    highlight_color: pygame.typing.ColorLike


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
    rich: bool
    rich_aligny: typing.Literal["top", "center", "bottom"]
    rich_linespace: int
    rich_actions: dict[str, typing.Callable[[typing.Any], None]]
    rich_link_color: pygame.typing.ColorLike
    rich_markdown: bool
    rich_markdown_style: _TextRichMarkdownStyleLike


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
    ready_border_radius: NumberOrPercentage
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
