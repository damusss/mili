import typing
import pygame
from mili import data as _data

if typing.TYPE_CHECKING:
    from mili import _core
    from mili import utility

__all__ = (
    "SmartNumber",
    "SmartNumberOrPercentage",
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
    "IconLike",
    "UIAppStyleLike",
    "ContextMenuStyleLike",
    "TransparentRectStyleLike",
    "BoundingAlignLike",
)

type SmartNumber = int | float | str
type SmartNumberOrPercentage = int | float | str
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
type PointsLike = typing.Sequence[typing.Sequence[SmartNumberOrPercentage]]
type AnimValueLike = float | pygame.Color | typing.Sequence[float]
type EasingLike = typing.Callable[[float], float]
type IconLike = (
    pygame.Surface
    | typing.Callable[[], pygame.Surface]
    | typing.Callable[[typing.Optional[pygame.typing.ColorLike]], pygame.Surface]
    | str
)


class _ConditionalColorStyleLike(typing.TypedDict):
    default: pygame.typing.ColorLike | None
    hover: pygame.typing.ColorLike | None
    press: pygame.typing.ColorLike | None


class _MarkDownCodeCopyStyleLike(typing.TypedDict):
    size: float
    icon_color: _ConditionalColorStyleLike
    icon_pad: SmartNumberOrPercentage
    icon: IconLike


class _MarkDownCodeScrollbarStyleLike(typing.TypedDict):
    border_radius: float
    height: float
    padx: float
    pady: float
    bar_color: pygame.typing.ColorLike | None
    handle_color: _ConditionalColorStyleLike


class MarkDownStyleLike(typing.TypedDict):
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
    table_bg_color: pygame.typing.ColorLike | None
    quote_color: pygame.typing.ColorLike
    code_bg_color: pygame.typing.ColorLike
    code_outline_color: pygame.typing.ColorLike
    code_border_radius: SmartNumberOrPercentage
    code_copy_style: _MarkDownCodeCopyStyleLike
    code_scrollbar_style: _MarkDownCodeScrollbarStyleLike
    title1_size: SmartNumber
    title2_size: SmartNumber
    title3_size: SmartNumber
    title4_size: SmartNumber
    title5_size: SmartNumber
    title6_size: SmartNumber
    allow_image_link: bool
    change_cursor: bool
    load_images_async: bool
    link_handler: typing.Callable[[str]]|None
    parse_async: bool


class _UIAppButtonStyleLike(typing.TypedDict):
    bg_color: _ConditionalColorStyleLike
    icon: IconLike
    alpha: _ConditionalColorStyleLike


class UIAppStyleLike(typing.TypedDict):
    start_style: "ElementStyleLike"
    target_framerate: float
    clear_color: pygame.typing.ColorLike
    window_outline: float
    window_icon: pygame.Surface | None
    outline_color: pygame.typing.ColorLike
    fullscreen_key: int | None
    titlebar_show_title: bool
    title_style: "TextStyleLike"
    titlebar_color: pygame.typing.ColorLike
    minimize_button: _UIAppButtonStyleLike
    maximize_button: _UIAppButtonStyleLike
    close_button: _UIAppButtonStyleLike
    use_appdata_folder: bool


class ScrollbarStyleLike(typing.TypedDict):
    axis: typing.Literal["x", "y"]
    short_size: float
    border_dist: float
    padding: float
    size_reduce: float
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


class DropMenuUIStyleLike(typing.TypedDict):
    border_radius: SmartNumberOrPercentage
    option_border_radius: SmartNumberOrPercentage
    bg_color: pygame.typing.ColorLike
    outline_color: pygame.typing.ColorLike
    selected_option_color: _ConditionalColorStyleLike
    option_color: _ConditionalColorStyleLike
    menu_style: "ElementStyleLike"
    text_style: "TextStyleLike"
    option_text_style: "TextStyleLike"
    icon_arrow_down: IconLike
    icon_arrow_up: IconLike


class EntryLineStyleLike(typing.TypedDict):
    placeholder: str
    placeholder_color: pygame.typing.ColorLike
    text_filly: str
    text_style: "TextStyleLike"
    text_anchor: typing.Literal["left", "right", "center"]
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
    characters_limit: int | None


class _TextBoxScrollbarStyleLike(typing.TypedDict):
    short_size: float
    border_dist: float
    padding: float


class _ContextMenuDefaultIconsStyleLike(typing.TypedDict):
    arrow_left: IconLike
    arrow_right: IconLike
    checkbox_empty: IconLike
    checkbox_full: IconLike


class ContextMenuStyleLike(typing.TypedDict):
    bg_color: pygame.typing.ColorLike
    outline_color: pygame.typing.ColorLike
    hover_color: pygame.typing.ColorLike
    google_icon_color: pygame.typing.ColorLike | typing.Literal["default"] | None
    item_bg_color: pygame.typing.ColorLike | None
    shadow_color: pygame.typing.ColorLike | None
    text_style: "TextStyleLike"
    icon_style: "ImageStyleLike"
    menu_style: "ElementStyleLike"
    row_style: "ElementStyleLike"
    separator_style: "LineStyleLike"
    label_height: float | None
    icon_height: float
    items_update_id: str | None
    menu_border_radius: SmartNumberOrPercentage
    hover_border_radius: SmartNumberOrPercentage
    menu_width: float
    menu_dist: float
    default_icons: _ContextMenuDefaultIconsStyleLike
    submenu_on_hover: bool
    clamp_size: pygame.typing.Point | None


class _ElementStyleLike(typing.TypedDict):
    resizex: bool
    resizey: bool
    fillx: bool | SmartNumberOrPercentage
    filly: bool | SmartNumberOrPercentage
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
    update_id: str
    parent_flag: int
    cache_rect_size: bool
    cache: _data.ParentCache | None

    axis: typing.Literal["x", "y"]
    spacing: SmartNumberOrPercentage
    pad: SmartNumberOrPercentage
    padx: SmartNumberOrPercentage
    pady: SmartNumberOrPercentage
    anchor: typing.Literal["first", "center", "last", "max_spacing"]
    default_align: typing.Literal["first", "center", "last"]
    layout: typing.Literal["stack", "grid", "table"]
    grid_align: typing.Literal[
        "first", "center", "last", "max_spacing", "first_center", "last_center"
    ]
    grid_spacex: SmartNumberOrPercentage
    grid_spacey: SmartNumberOrPercentage


type ElementStyleLike = _ElementStyleLike | dict[str, typing.Any]


class _ComponentStyleLike(typing.TypedDict):
    draw_above: bool
    element_id: int
    pad: SmartNumberOrPercentage
    padx: SmartNumberOrPercentage
    pady: SmartNumberOrPercentage


class _RectStyleLike(_ComponentStyleLike):
    outline: SmartNumberOrPercentage
    border_radius: SmartNumberOrPercentage | typing.Iterable[SmartNumberOrPercentage]
    color: pygame.typing.ColorLike|None
    aspect_ratio: float | None
    align: BoundingAlignLike
    dash_size: SmartNumberOrPercentage | typing.Iterable[SmartNumberOrPercentage] | None
    dash_offset: SmartNumberOrPercentage
    ready_rect: pygame.typing.RectLike | None


type RectStyleLike = _RectStyleLike | dict[str, typing.Any]


class _TransparentRectStyleLike(_ComponentStyleLike):
    border_radius: SmartNumberOrPercentage|pygame.typing.SequenceLike[SmartNumberOrPercentage]
    color: pygame.typing.ColorLike
    alpha: int


type TransparentRectStyleLike = _TransparentRectStyleLike | dict[str, typing.Any]


class _CircleStyleLike(_ComponentStyleLike):
    outline: SmartNumberOrPercentage
    color: pygame.typing.ColorLike|None
    antialias: bool
    aspect_ratio: float | None
    align: BoundingAlignLike
    corners: typing.Iterable[bool]
    dash_size: float | typing.Iterable[float] | None
    dash_anchor: float | typing.Iterable[float]


type CircleStyleLike = _CircleStyleLike | dict[str, typing.Any]


class _LineStyleLike(_ComponentStyleLike):
    size: SmartNumberOrPercentage
    color: pygame.typing.ColorLike|None
    antialias: bool
    dash_size: SmartNumberOrPercentage | typing.Iterable[SmartNumberOrPercentage]
    dash_offset: SmartNumberOrPercentage


type LineStyleLike = _LineStyleLike | dict[str, typing.Any]


class _PolygonStyleLike(_ComponentStyleLike):
    outline: SmartNumberOrPercentage
    color: pygame.typing.ColorLike|None


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
    size: SmartNumber
    sysfont: bool
    align: BoundingAlignLike
    font_align: int
    font_direction: int
    bold: bool
    italic: bool
    underline: bool
    strikethrough: bool
    antialias: bool
    color: pygame.typing.ColorLike
    bg_color: pygame.typing.ColorLike
    outline_color: pygame.typing.ColorLike
    growx: bool
    growy: bool
    wraplen: SmartNumberOrPercentage
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
    fill: bool
    stretchx: bool
    stretchy: bool
    fill_color: pygame.typing.ColorLike
    smoothscale: bool
    ready_border_radius: SmartNumberOrPercentage
    border_radius: (
        SmartNumberOrPercentage | pygame.typing.SequenceLike[SmartNumberOrPercentage]
    )
    alpha: int
    ninepatch_size: SmartNumberOrPercentage
    ready: bool
    transforms: (
        pygame.typing.SequenceLike[typing.Callable | pygame.typing.SequenceLike] | None
    )
    filters: (
        pygame.typing.SequenceLike[typing.Callable | pygame.typing.SequenceLike] | None
    )


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


# deprecated. will be removed in 1.0.8
type NumberOrPercentage = SmartNumberOrPercentage
