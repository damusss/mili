import pygame
import typing
import threading
import webbrowser
import copy

from mili import _core
from mili import _richtext
from mili import error as _error
from mili import data as _data
from mili import typing as _typing


__all__ = (
    "MILI",
    "MarkDown",
    "register_custom_component",
    "pack_component",
    "get_font_cache",
    "clear_font_cache",
)


def register_custom_component(name: str, component_type: _typing.ComponentProtocol):
    _core._globalctx._component_types[name] = component_type


def pack_component(name: str, data: typing.Any, style: _typing.AnyStyleLike):
    return {"type": name, "data": data, "style": style}


def get_font_cache():
    return _core._globalctx._font_cache.copy()


def clear_font_cache():
    _core._globalctx._font_cache = {}


def register_update_id(
    update_id: str | None, function: typing.Callable[[_data.Interaction], None]
):
    _core._globalctx._register_update_id(update_id, function)


class MarkDown:
    def __init__(
        self, source: str, style: _typing.MarkDownStyleLike | dict | None = None
    ):
        self._source = source
        self._any_hover = False
        self._parse_result: None | list = None
        self._images = {}
        self._heights = {}
        if style is None:
            style = {}
        copy = style.get("code_copy_style", {})
        sbar = style.get("code_scrollbar_style", {})
        self.style: _typing.MarkDownStyleLike = {
            "quote_width": style.get("quote_width", 3),
            "quote_border_radius": style.get("quote_border_radius", 3),
            "indent_width": style.get("indent_width", 30),
            "separator_height": style.get("separator_height", 5),
            "line_break_size": style.get("line_break_size", 1),
            "bullet_diameter": style.get("bullet_diameter", 5),
            "table_outline_size": style.get("table_outline_size", 1),
            "table_border_radius": style.get("table_border_radius", 7),
            "table_alignx": style.get("table_alignx", "left"),
            "table_aligny": style.get("table_aligny", "center"),
            "line_break_color": style.get("line_break_color", (80, 80, 80)),
            "bullet_color": style.get("bullet_color", "white"),
            "table_bg_color": style.get("table_bg_color", (30, 30, 30)),
            "quote_color": style.get("quote_color", (150, 150, 150)),
            "code_bg_color": style.get("code_bg_color", (40, 40, 40)),
            "code_outline_color": style.get("code_outline_color", (50, 50, 50)),
            "code_border_radius": style.get("code_border_radius", 3),
            "code_copy_style": {
                "size": copy.get("size", 26),
                "icon_color": copy.get(
                    "icon_color",
                    {"default": (120,) * 3, "hover": (180,) * 3, "press": (100,) * 3},
                ),
                "icon_pad": "10",
            },
            "code_scrollbar_style": {
                "height": sbar.get("height", 7),
                "padx": sbar.get("padx", 1),
                "pady": sbar.get("pady", 1),
                "border_radius": sbar.get("border_radius", 3),
                "bar_color": sbar.get("bar_color", (30,) * 3),
                "handle_color": sbar.get(
                    "handle_color",
                    {
                        "default": (50,) * 3,
                        "hover": (60,) * 3,
                        "press": (50,) * 3,
                    },
                ),
            },
            "title1_size": style.get("title1_size", 26),
            "title2_size": style.get("title2_size", 22),
            "title3_size": style.get("title3_size", 19),
            "title4_size": style.get("title4_size", 16),
            "title5_size": style.get("title5_size", 14),
            "title6_size": style.get("title6_size", 12),
            "allow_image_link": style.get("allow_image_link", True),
            "change_cursor": style.get("change_cursor", True),
            "load_images_async": style.get("load_images_async", True),
            "open_links_in_browser": style.get("open_links_in_browser", True),
            "parse_async": style.get("parse_async", True),
        }
        self.rebuild()

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        changed = False
        if self._source != value:
            changed = True
        self._source = value
        if changed:
            self.rebuild()

    def rebuild(self):
        if self.style["parse_async"]:
            thread = threading.Thread(
                target=_richtext._markdown_parse, args=(self._source, self)
            )
            thread.daemon = True
            thread.start()
        else:
            _richtext._markdown_parse(self._source, self)

    def _link_hover(self, dt):
        self._any_hover = True

    def _link_click(self, dt):
        if self.style["open_links_in_browser"]:
            webbrowser.open(str(dt))


class MILI:
    def __init__(
        self, canva: pygame.Surface | None = None, use_global_mouse: bool = False
    ):
        self._ctx = _core._ctx(self)
        if canva is not None:
            self.canva = canva
        self.use_global_mouse = use_global_mouse
        self.last_interaction: _data.Interaction | None = None
        self.current_parent_interaction: _data.Interaction | None = None

    @property
    def id(self):
        return self._ctx._id

    @id.setter
    def id(self, value):
        self.id_checkpoint(value)

    @property
    def stack_id(self) -> int:
        return self._ctx._stack["id"]

    @property
    def current_parent_id(self) -> int:
        return self._ctx._parent["id"] if self._ctx._parent else -1

    @property
    def all_elements_ids(self) -> list[int]:
        return list(self._ctx._memory.keys())

    @property
    def canva(self) -> pygame.Surface | None:
        return self._ctx._canva

    @canva.setter
    def canva(self, v: pygame.Surface):
        self._ctx._canva = v
        self._ctx._canva_rect = v.get_rect()

    @property
    def canva_offset(self) -> pygame.Vector2:
        return self._ctx._offset

    @canva_offset.setter
    def canva_offset(self, v: typing.Sequence[float]):
        self._ctx._offset = pygame.Vector2(v)

    @property
    def use_global_mouse(self) -> bool:
        return self._ctx._global_mouse

    @use_global_mouse.setter
    def use_global_mouse(self, v: bool):
        self._ctx._global_mouse = v
        if v:
            self._ctx._get_just_pressed_func = self._ctx._get_just_pressed
            self._ctx._get_just_released_func = self._ctx._get_just_released
        else:
            self._ctx._get_just_pressed_func = pygame.mouse.get_just_pressed
            self._ctx._get_just_released_func = pygame.mouse.get_just_released

    def default_style(self, type: str, style: _typing.AnyStyleLike):
        if type != "element" and type not in _core._globalctx._component_types:
            raise _error.MILIValueError("Invalid style type")
        else:
            if type not in self._ctx._default_styles:
                self._ctx._default_styles[type] = {}
        self._ctx._default_styles[type].update(style)

    def default_styles(self, **types_styles: _typing.AnyStyleLike):
        for name, value in types_styles.items():
            self.default_style(name, value)

    def reset_default_styles(self, *types: str):
        for tp in types:
            if tp != "element" and tp not in _core._globalctx._component_types:
                raise _error.MILIValueError("Invalid style type")
            self._ctx._default_styles[tp] = {}

    def push_styles(self, **types_styles: _typing.AnyStyleLike):
        self._ctx._styles_stack.append(copy.deepcopy(self._ctx._styles))
        for type_, style in types_styles.items():
            if type_ not in self._ctx._styles:
                self._ctx._styles[type_] = style
            else:
                self._ctx._styles[type_].update(style)
        return _core._PushStylesCtx(self)

    def pop_styles(self):
        try:
            last = self._ctx._styles_stack.pop()
            self._ctx._styles = last
        except IndexError:
            raise _error.MILIStatusError("MILI.pop_styles called too many times")

    def reset_styles(self):
        self._ctx._styles = {}
        self._ctx._styles_stack = []

    def start(
        self,
        style: _typing.ElementStyleLike | None = None,
        is_global=True,
        window_position: pygame.typing.Point | None = None,
    ) -> typing.Literal[True]:
        if self._ctx._canva is None:
            raise _error.MILIStatusError("Canva was not set")
        _core._globalctx._mili_stack.append(self)
        _core._globalctx._mili = self
        if style is None:
            style = {"blocking": False}
        else:
            style = style.copy()
            style["blocking"] = False
        self._ctx._start(style, window_position)
        if is_global:
            _data.ImageCache._preallocated_index = -1
            _data.TextCache._preallocated_index = -1
        return True

    def update_draw(self):
        self._ctx._organize_element(self._ctx._stack)
        self._ctx._started = False
        self._ctx._draw_update_element(self._ctx._stack, (0, 0))
        for layer_cache in self._ctx._image_layer_caches:
            _core._coreutils._render_layer_cache(layer_cache, self._ctx._canva)
        abs_hovered = sorted(self._ctx._abs_hovered, key=lambda e: e["z"], reverse=True)
        if len(abs_hovered) > 0:
            abs_hovered[0]["top"] = True
        if len(_core._globalctx._mili_stack) > 0:
            _core._globalctx._mili_stack.pop()
        if len(_core._globalctx._mili_stack) > 0:
            _core._globalctx._mili = _core._globalctx._mili_stack[-1]
        else:
            _core._globalctx._mili = None
        if self._ctx._cleared > 0:
            self._ctx._cleared -= 1

    def markdown(self, markdown: MarkDown) -> bool:
        changed = False
        if markdown.style["change_cursor"]:
            if markdown._any_hover:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                changed = True
            markdown._any_hover = False
        _richtext._markdown_ui(self, markdown)
        return changed

    def element(
        self,
        rect: pygame.typing.RectLike | None,
        style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        self._ctx._start_check()
        el, interaction = self._ctx._get_element(rect, style)
        interaction._did_begin = False
        interaction.parent = self.current_parent_interaction
        self.last_interaction = interaction
        if uid := self._ctx._style_val(el["style"], "element", "update_id", None):
            uids = [uid]
            if not isinstance(uid, str):
                uids = uid
            for ui in uids:
                methods = _core._globalctx._update_ids.get(ui, [])
                for meth in methods:
                    meth(interaction)
        return interaction

    def begin(
        self,
        rect: pygame.typing.RectLike | None,
        style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        self._ctx._start_check()
        el, interaction = self._ctx._get_element(rect, style, True)
        interaction._did_begin = True
        interaction.parent = self.current_parent_interaction
        self.last_interaction = self.current_parent_interaction = interaction
        self._ctx._parent = el
        self._ctx._parents_stack.append(el)
        if uid := self._ctx._style_val(el["style"], "element", "update_id", None):
            uids = [uid]
            if not isinstance(uid, str):
                uids = uid
            for ui in uids:
                methods = _core._globalctx._update_ids.get(ui, [])
                for meth in methods:
                    meth(interaction)
        return interaction

    def add_element_style(
        self, style: _typing.ElementStyleLike | None, element_id: int | None = None
    ):
        self._ctx._start_check()
        if style is None:
            return
        if element_id is None:
            if not self._ctx._element:
                raise _error.MILIStatusError(
                    "Cannot add style to previous element if no element was created"
                )
            element = self._ctx._element
        else:
            element = self._ctx._memory.get(element_id, None)
            if element is None:
                raise _error.MILIValueError(
                    f"Cannot add style to inexistent element with ID {element_id}"
                )
        element["style"].update(style)
        if "z" in style:
            element["z"] = style["z"]

    def end(self):
        self._ctx._start_check()
        parent = self._ctx._parent
        if parent and parent["id"] != 0:
            self._ctx._organize_element(parent)
            if parent["id"] == self._ctx._inside_cache:
                self._ctx._inside_cache = -1
                self._ctx._static_cache = False
        else:
            raise _error.MILIStatusError("end() called too many times")
        if len(self._ctx._parents_stack) > 1:
            self._ctx._parents_stack.pop()
            self._ctx._parent = self._ctx._parents_stack[-1]
        else:
            self._ctx._parent = self._ctx._parents_stack[0]
        self._ctx._element = self._ctx._parent
        if self.current_parent_interaction is not None:
            self.current_parent_interaction = self.current_parent_interaction.parent

    def cache_should_create_children(self):
        return self._ctx._inside_cache == -1 or not self._ctx._static_cache

    def rect(self, style: _typing.RectStyleLike | None = None) -> typing.Self:
        self._ctx._add_component("rect", None, style)
        return self

    def rect_element(
        self,
        rect_style: _typing.RectStyleLike | None = None,
        element_rect: pygame.typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        data = self.element(element_rect, element_style)
        self.rect(rect_style)
        return data

    def transparet_rect(
        self, style: _typing.TransparentRectStyleLike | None = None
    ) -> typing.Self:
        if style is None:
            style = {}
        self.image(
            _core._globalctx._sample_surf,
            {
                "fill": True,
                "cache": "auto",
                "pad": style.get("pad", 0),
                "padx": style.get("padx", 0),
                "pady": style.get("pady", 0),
                "fill_color": style.get("color", None),
                "alpha": style.get("alpha", 255),
                "border_radius": style.get("border_radius", 0),
            },
        )
        return self

    def transparent_rect_element(
        self,
        transparent_rect_style: _typing.TransparentRectStyleLike | None = None,
        element_rect: pygame.typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        data = self.element(element_rect, element_style)
        self.transparet_rect(transparent_rect_style)
        return data

    def circle(self, style: _typing.CircleStyleLike | None = None) -> typing.Self:
        self._ctx._add_component("circle", None, style)
        return self

    def circle_element(
        self,
        circle_style: _typing.CircleStyleLike | None = None,
        element_rect: pygame.typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        data = self.element(element_rect, element_style)
        self.circle(circle_style)
        return data

    def polygon(
        self, points: _typing.PointsLike, style: _typing.PolygonStyleLike | None = None
    ) -> typing.Self:
        self._ctx._add_component("polygon", points, style)
        return self

    def polygon_element(
        self,
        points: _typing.PointsLike,
        polygon_style: _typing.PolygonStyleLike | None = None,
        element_rect: pygame.typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        data = self.element(element_rect, element_style)
        self.polygon(points, polygon_style)
        return data

    def line(
        self,
        start_end: _typing.PointsLike,
        style: _typing.LineStyleLike | None = None,
    ) -> typing.Self:
        self._ctx._add_component("line", start_end, style)
        return self

    def hline(self, style: _typing.LineStyleLike | None = None) -> typing.Self:
        return self.line([("-50", 0), ("50", 0)], style)

    def vline(self, style: _typing.LineStyleLike | None = None) -> typing.Self:
        return self.line([(0, "-50"), (0, "50")], style)

    def line_element(
        self,
        start_end: _typing.PointsLike,
        line_style: _typing.LineStyleLike | None = None,
        element_rect: pygame.typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        data = self.element(element_rect, element_style)
        self.line(start_end, line_style)
        return data

    def vline_element(
        self,
        line_style: _typing.LineStyleLike | None = None,
        element_rect: pygame.typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        data = self.element(element_rect, element_style)
        self.vline(line_style)
        return data

    def hline_element(
        self,
        line_style: _typing.LineStyleLike | None = None,
        element_rect: pygame.typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        data = self.element(element_rect, element_style)
        self.hline(line_style)
        return data

    def text(
        self, text: str, style: _typing.TextStyleLike | None = None
    ) -> typing.Self:
        self._ctx._add_component("text", str(text), style)
        return self

    def text_element(
        self,
        text: str,
        text_style: _typing.TextStyleLike | None = None,
        element_rect: pygame.typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        data = self.element(element_rect, element_style)
        self.text(text, text_style)
        return data

    def text_size(
        self,
        text: str,
        style: _typing.TextStyleLike | None = None,
        padded: bool = False,
    ) -> pygame.Vector2:
        if style is None:
            style = {}
        size = pygame.Vector2(self._ctx._text_size(text, style))
        if not padded:
            return size

        pad: float = self._ctx._style_val(style, "text", "pad", None)  # type: ignore
        if pad is not None:
            padx = pady = pad
        else:
            padx: float = self._ctx._style_val(style, "text", "padx", 5)  # type: ignore
            pady: float = self._ctx._style_val(style, "text", "pady", 3)  # type: ignore
        size.x += padx * 2
        size.y += pady * 2
        return size

    def text_font(self, style: _typing.TextStyleLike | None = None) -> pygame.Font:
        if style is None:
            style = {}
        return self._ctx._get_font(style)

    def image(
        self, surface: pygame.Surface, style: _typing.ImageStyleLike | None = None
    ) -> typing.Self:
        self._ctx._add_component("image", surface, style)
        return self

    def image_element(
        self,
        surface: pygame.Surface,
        image_style: _typing.ImageStyleLike | None = None,
        element_rect: pygame.typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
    ) -> _data.Interaction:
        data = self.element(element_rect, element_style)
        self.image(surface, image_style)
        return data

    def custom_component(
        self, component: str, data: typing.Any, style: dict[str, typing.Any] | None
    ):
        if (
            component not in self._ctx._default_styles
            and component in _core._globalctx._component_types
        ):
            self._ctx._default_styles[component] = {}
        elif component not in _core._globalctx._component_types:
            raise _error.MILIStatusError(
                f"No custom component '{component}' registered"
            )
        self._ctx._add_component(component, data, style)
        return self

    def packed_component(
        self,
        *packed_components: dict[typing.Literal["type", "style", "data"], typing.Any],
    ):
        for comp in packed_components:
            if comp["type"] not in _core._globalctx._component_types:
                _error.MILIStatusError(f"No component '{comp['type']}' exists")
            self._ctx._add_component(comp["type"], comp["data"], comp["style"])
        return self

    def register_prefab(
        self, name: str, prefab_function: typing.Callable[["MILI"], typing.Any]
    ):
        self._ctx._prefabs[name] = prefab_function

    def prefab(self, name: str, *args, **kwargs) -> typing.Any:
        if name not in self._ctx._prefabs:
            raise _error.MILIValueError(
                f"No prefab was registered with name '{name}'. Existing prefabs: {list(self._ctx._prefabs.keys())}"
            )
        return self._ctx._prefabs[name](self, *args, **kwargs)

    def image_layer_renderer(self, layer: _data.ImageLayerCache) -> typing.Self:
        self._ctx._add_component("image_layer", layer, {"draw_above": True})
        return self

    def data_from_id(self, element_id: int) -> _data.ElementData | None:
        self._ctx._start_check()
        if element_id in self._ctx._memory:
            return _core._coreutils._element_data(
                self._ctx, self._ctx._memory[element_id]
            )
        elif element_id == 0:
            return _core._coreutils._element_data(self._ctx, self._ctx._stack)

    def clear_memory(self, keep_ids: list[int] | None = None):
        ctx = self._ctx
        ctx._cleared = 3
        memory_keep = {}
        old_data_keep = {}
        if keep_ids:
            for _id in keep_ids:
                if _id in ctx._memory:
                    memory_keep[_id] = ctx._memory[_id]
                if _id in ctx._old_data:
                    old_data_keep[_id] = ctx._old_data[_id]
        ctx._memory.clear()
        ctx._old_data.clear()
        ctx._interaction_cache.clear()
        if keep_ids:
            ctx._memory.update(memory_keep)
            ctx._old_data.update(old_data_keep)

    def id_checkpoint(self, id_: int):
        if id_ < 1:
            id_ = 1
        if self._ctx._id <= id_:
            self._ctx._id = id_
            self._ctx._last_checkpoint = id_
        else:
            raise _error.MILIStatusError(
                f"The current ID ({self._ctx._id}) already surpassed the checkpoint ({id_}) so it cannot be applied"
            )

    def id_jump(self, amount: int):
        new_id = self._ctx._last_checkpoint + amount
        if new_id >= self._ctx._id:
            self._ctx._id = new_id
            self._ctx._last_checkpoint = new_id
        else:
            raise _error.MILIStatusError(
                f"Jumping from {self._ctx._last_checkpoint} by {amount} IDs does not surpass the current ID ({self._ctx._id}) so it cannot be done"
            )
