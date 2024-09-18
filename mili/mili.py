import pygame
import typing

from mili import _core
from mili import error as _error
from mili import data as _data
from mili import typing as _typing


__all__ = ("MILI", "register_custom_component", "pack_component")


def register_custom_component(name: str, component_type: _typing.ComponentProtocol):
    _core._globalctx._component_types[name] = component_type


def pack_component(name: str, data: typing.Any, style: _typing.AnyStyleLike):
    return {"type": name, "data": data, "style": style}


class MILI:
    def __init__(self, canva: pygame.Surface | None = None):
        self._ctx = _core._ctx(self)
        self.always_get_data: bool = False
        if canva is not None:
            self.set_canva(canva)

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
        self.set_canva(v)

    def default_style(self, type: str, style: _typing.AnyStyleLike):
        if type not in _core._globalctx._component_types:
            raise _error.MILIValueError("Invalid style type")
        else:
            if type not in self._ctx._default_styles:
                self._ctx._default_styles[type] = {}
        self._ctx._default_styles[type].update(style)

    def default_styles(self, **types_styles: _typing.AnyStyleLike):
        for name, value in types_styles.items():
            self.default_style(name, value)

    def reset_style(self, *types: str):
        for tp in types:
            if tp not in _core._globalctx._component_types:
                raise _error.MILIValueError("Invalid style type")
            self._ctx._default_styles[tp] = {}

    def start(
        self, style: _typing.ElementStyleLike | None = None, is_global=True
    ) -> typing.Literal[True]:
        if self._ctx._canva is None:
            raise _error.MILIStatusError("Canva was not set")
        _core._globalctx._mili_stack.append(self)
        _core._globalctx._mili = self
        if style is None:
            style = {}
        style = style.copy()
        style.update(blocking=False)
        self._ctx._start(style)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        self._ctx._mouse_rel = mouse_pos - self._ctx._mouse_pos
        self._ctx._mouse_pos = mouse_pos
        if is_global:
            _data.ImageCache._preallocated_index = -1
        return True

    def set_canva(self, surface: pygame.Surface):
        self._ctx._canva = surface
        self._ctx._canva_rect = surface.get_rect()

    def update_draw(self):
        self._ctx._organize_element(self._ctx._stack)
        self._ctx._started = False
        self._ctx._draw_update_element(self._ctx._stack, (0, 0))
        abs_hovered = sorted(self._ctx._abs_hovered, key=lambda e: e["z"], reverse=True)
        if len(abs_hovered) > 0:
            abs_hovered[0]["top"] = True
        if len(_core._globalctx._mili_stack) > 0:
            _core._globalctx._mili_stack.pop()
        if len(_core._globalctx._mili_stack) > 0:
            _core._globalctx._mili = _core._globalctx._mili_stack[-1]
        else:
            _core._globalctx._mili = None

    def element(
        self,
        rect: _typing.RectLike | None,
        style: _typing.ElementStyleLike | None = None,
        get_data: bool = False,
    ) -> _data.Interaction | _data.ElementData:
        self._ctx._start_check()
        el, interaction = self._ctx._get_element(rect, style)
        if get_data or self.always_get_data:
            return _core._globalctx._element_data(self, el, interaction)
        return interaction

    def begin(
        self,
        rect: _typing.RectLike | None,
        style: _typing.ElementStyleLike | None = None,
        header: str = "",
        get_data: bool = False,
    ) -> _data.Interaction | _data.ElementData:
        self._ctx._start_check()
        el, interaction = self._ctx._get_element(rect, style)
        self._ctx._parent = el
        self._ctx._parents_stack.append(el)
        if get_data or self.always_get_data:
            return _core._globalctx._element_data(self, el, interaction)
        return interaction

    def end(self, header: str = ""):
        self._ctx._start_check()
        if self._ctx._parent and self._ctx._parent["id"] != 0:
            self._ctx._organize_element(self._ctx._parent)
        else:
            raise _error.MILIStatusError("end() called too many times")
        if len(self._ctx._parents_stack) > 1:
            self._ctx._parents_stack.pop()
            self._ctx._parent = self._ctx._parents_stack[-1]
        else:
            self._ctx._parent = self._ctx._parents_stack[0]

    def rect(self, style: _typing.RectStyleLike | None = None):
        self._ctx._add_component("rect", None, style)

    def rect_element(
        self,
        rect_style: _typing.RectStyleLike | None = None,
        element_rect: _typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
        get_data: bool = False,
    ) -> _data.Interaction | _data.ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.rect(rect_style)
        return data

    def circle(self, style: _typing.CircleStyleLike | None = None):
        self._ctx._add_component("circle", None, style)

    def circle_element(
        self,
        circle_style: _typing.CircleStyleLike | None = None,
        element_rect: _typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
        get_data: bool = False,
    ) -> _data.Interaction | _data.ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.circle(circle_style)
        return data

    def polygon(
        self, points: _typing.PointsLike, style: _typing.PolygonStyleLike | None = None
    ):
        self._ctx._add_component("polygon", points, style)

    def polygon_element(
        self,
        points: _typing.PointsLike,
        polygon_style: _typing.PolygonStyleLike | None = None,
        element_rect: _typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
        get_data: bool = False,
    ) -> _data.Interaction | _data.ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.polygon(points, polygon_style)
        return data

    def line(
        self,
        start_end: _typing.PointsLike,
        style: _typing.LineStyleLike | None = None,
    ):
        self._ctx._add_component("line", start_end, style)

    def line_element(
        self,
        start_end: _typing.PointsLike,
        line_style: _typing.LineStyleLike | None = None,
        element_rect: _typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
        get_data: bool = False,
    ) -> _data.Interaction | _data.ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.line(start_end, line_style)
        return data

    def text(self, text: str, style: _typing.TextStyleLike | None = None):
        self._ctx._add_component("text", str(text), style)

    def text_element(
        self,
        text: str,
        text_style: _typing.TextStyleLike | None = None,
        element_rect: _typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
        get_data: bool = False,
    ) -> _data.Interaction | _data.ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.text(text, text_style)
        return data

    def text_size(
        self, text: str, style: _typing.TextStyleLike | None = None
    ) -> pygame.Vector2:
        if style is None:
            style = {}
        return pygame.Vector2(self._ctx._text_size(text, style))

    def text_font(self, style: _typing.TextStyleLike | None = None) -> pygame.Font:
        if style is None:
            style = {}
        return self._ctx._get_font(style)

    def image(
        self, surface: pygame.Surface, style: _typing.ImageStyleLike | None = None
    ):
        self._ctx._add_component("image", surface, style)

    def image_element(
        self,
        surface: pygame.Surface,
        image_style: _typing.ImageStyleLike | None = None,
        element_rect: _typing.RectLike | None = None,
        element_style: _typing.ElementStyleLike | None = None,
        get_data: bool = False,
    ) -> _data.Interaction | _data.ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.image(surface, image_style)
        return data

    def basic_element(
        self,
        rect: _typing.RectLike | None = None,
        style: _typing.ElementStyleLike | None = None,
        comp_data=None,
        comp_style: _typing.AnyStyleLike | None = None,
        bg_style: _typing.RectStyleLike | None = None,
        outline_style: _typing.RectStyleLike | None = None,
        component="text",
        get_data: bool = False,
    ) -> _data.Interaction | _data.ElementData:
        if component not in _core._globalctx._component_types.keys():
            raise _error.MILIValueError("Invalid component name")
        if not outline_style:
            outline_style = {}
        if "outline" not in outline_style:
            outline_style["outline"] = 1
        data = self.element(rect, style, get_data)
        self.rect(bg_style)
        comp = getattr(self, component)
        try:
            comp(comp_data, comp_style)
        except TypeError:
            comp(comp_style)
        self.rect(outline_style)
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

    def packed_component(
        self,
        *packed_components: dict[typing.Literal["type", "style", "data"], typing.Any],
    ):
        for comp in packed_components:
            if comp["type"] not in _core._globalctx._component_types:
                _error.MILIStatusError(f"No component '{comp['type']}' exists")
            self._ctx._add_component(comp["type"], comp["data"], comp["style"])

    def data_from_id(self, element_id: int) -> _data.ElementData | None:
        self._ctx._start_check()
        if element_id in self._ctx._memory:
            el = self._ctx._memory[element_id]
            return _core._globalctx._element_data(
                self, el, self._ctx._get_interaction(el)
            )

    def clear_memory(self):
        self._ctx._memory = {}

    def id_checkpoint(self, id_: int):
        if id_ < 1:
            id_ = 1
        if self._ctx._id < id_:
            self._ctx._id = id_
