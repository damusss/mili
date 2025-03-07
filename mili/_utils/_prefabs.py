import pygame
import typing
from mili import _core
from mili import data as _data
from mili import typing as _typing
from mili import error as _error


class Selectable:
    def __init__(self, selected: bool = False, update_id: str | None = None):
        self.selected: bool = selected
        _core._globalctx._register_update_id(update_id, self.update)

    def update(
        self,
        element: _data.Interaction,
        selectable_group: typing.Sequence["Selectable"] | None = None,
        can_deselect_group: bool = True,
    ) -> _data.Interaction:
        if selectable_group is None:
            selectable_group = []
        if element.left_just_released:
            self.selected = not self.selected
            if len(selectable_group) > 0:
                if self.selected:
                    for sel in selectable_group:
                        if sel is not self:
                            sel.selected = False
                elif not can_deselect_group:
                    one = False
                    for sel in selectable_group:
                        if sel is not self and sel.selected:
                            one = True
                            break
                    if not one:
                        self.selected = True
        elif len(selectable_group) > 0:
            for sel in selectable_group:
                if sel is not self and sel.selected:
                    self.selected = False
                    break
        return element


class Dragger:
    def __init__(
        self,
        position: typing.Sequence[float] | None = None,
        lock_x: bool = False,
        lock_y: bool = False,
        update_id: str | None = None,
    ):
        if position is None:
            position = (0, 0)
        self.position = pygame.Vector2(position)
        self.rel = pygame.Vector2()
        self.lock_x = lock_x
        self.lock_y = lock_y
        self.changed: bool = False
        self.clamp_x: tuple[float, float] | None = None
        self.clamp_y: tuple[float, float] | None = None
        self.style: _typing.ElementStyleLike = {"ignore_grid": True}
        self._before_update_pos = pygame.Vector2()
        _core._globalctx._register_update_id(update_id, self.update)

    def update(
        self,
        element: _data.Interaction,
    ) -> _data.Interaction:
        if _core._globalctx._mili is None:
            raise _error.MILIStatusError("MILI.start() not called")
        self.changed = False
        self._before_update_pos = self.position.copy()
        if element.left_pressed:
            rel = _core._globalctx._mili._ctx._mouse_rel.copy()
            if self.lock_x:
                rel.x = 0
            if self.lock_y:
                rel.y = 0
            prev = self.position.copy()
            self.position += rel
            if self.position != prev:
                self.changed = True
            self.rel = rel.copy()
        return element

    def clamp(
        self,
        clamp_x: tuple[float, float] | None = None,
        clamp_y: tuple[float, float] | None = None,
        previous_clamps: bool = True,
    ) -> bool:
        if previous_clamps:
            clamp_x = self.clamp_x
            clamp_y = self.clamp_y
        prev = self.position.copy()
        if clamp_x is not None:
            self.position.x = pygame.math.clamp(self.position.x, *clamp_x)
        if clamp_y is not None:
            self.position.y = pygame.math.clamp(self.position.y, *clamp_y)
        if self.position != prev:
            self.changed = True
        if self.changed and self.position == self._before_update_pos:
            self.changed = False
        self.clamp_x = clamp_x
        self.clamp_y = clamp_y
        return self.changed


class Scroll:
    def __init__(self, update_id: str | None = None):
        self.scroll_offset: pygame.Vector2 = pygame.Vector2()
        self._element_data: _data.ElementData | None = None
        self._scrollbars: list["Scrollbar"] = []
        _core._globalctx._register_update_id(update_id, self.update)

    def update[IT: _data.Interaction | _data.ElementData](self, container: IT) -> IT:
        if isinstance(container, _data.ElementData):
            self._element_data = container
        else:
            self._element_data = container.data
        self.clamp()
        return container

    def wheel_event(
        self,
        event: pygame.Event,
        multiplier: float = 35,
        axis_invert_kmod: int | None = None,
    ):
        if event.type == pygame.MOUSEWHEEL:
            x, y = -event.x * multiplier, -event.y * multiplier
            if (
                axis_invert_kmod is not None
                and pygame.key.get_mods() & axis_invert_kmod
            ):
                x, y = y, x
            self.scroll(x, y)

    def scroll(self, x: float, y: float):
        self.scroll_offset.x += x
        self.scroll_offset.y += y
        self.clamp()
        for sbar in self._scrollbars:
            sbar.scroll_moved()

    def set_scroll(self, x: float, y: float):
        self.scroll_offset.x = x
        self.scroll_offset.y = y
        self.clamp()
        for sbar in self._scrollbars:
            sbar.scroll_moved()

    def clamp(self):
        maxx, maxy = float("inf"), float("inf")
        if self._element_data is not None and self._element_data.grid is not None:
            maxx = self._element_data.grid.overflowx
            maxy = self._element_data.grid.overflowy
        self.scroll_offset.x = pygame.math.clamp(self.scroll_offset.x, 0, maxx)
        self.scroll_offset.y = pygame.math.clamp(self.scroll_offset.y, 0, maxy)

    def get_offset(self) -> tuple[float, float]:
        return (-self.scroll_offset.x, -self.scroll_offset.y)

    def get_handle_size(
        self, scrollbar_size: int | float, axis: typing.Literal["x", "y"] = "y"
    ):
        if self._element_data is not None and self._element_data.grid is not None:
            if axis == "x":
                rectsize = self._element_data.rect.w
                overflow = self._element_data.grid.overflowx
            else:
                rectsize = self._element_data.rect.h
                overflow = self._element_data.grid.overflowy
            den = rectsize + overflow
            if den == 0:
                return scrollbar_size
            return min(
                scrollbar_size,
                (rectsize / den) * scrollbar_size,
            )
        return 0

    def get_rel_handle_pos_from_scroll(
        self,
        scrollbar_size: int | float,
        handle_size: int | float,
        axis: typing.Literal["x", "y"] = "y",
    ):
        if self._element_data is None or self._element_data.grid is None:
            return 0
        if axis == "x":
            offset = self.scroll_offset.x
            overflow = self._element_data.grid.overflowx
        else:
            offset = self.scroll_offset.y
            overflow = self._element_data.grid.overflowy
        if overflow == 0:
            return 0
        return (offset / overflow) * (scrollbar_size - handle_size)

    def set_scroll_from_rel_handle_pos(
        self,
        scrollbar_size: int | float,
        rel_handle_pos: int | float,
        handle_size: int,
        axis: typing.Literal["x", "y"] = "y",
    ):
        if self._element_data is None or self._element_data.grid is None:
            return
        if scrollbar_size - handle_size == 0:
            return
        if axis == "x":
            self.scroll_offset.x = self._element_data.grid.overflowx * (
                rel_handle_pos / (scrollbar_size - handle_size)
            )
        else:
            self.scroll_offset.y = self._element_data.grid.overflowy * (
                rel_handle_pos / (scrollbar_size - handle_size)
            )
        self.clamp()


class Scrollbar:
    def __init__(
        self,
        scroll: Scroll,
        style: _typing.ScrollbarStyleLike | dict | None = None,
    ):
        if style is None:
            style = {}
        self._scroll = scroll
        self._scroll._scrollbars.append(self)
        self.style: _typing.ScrollbarStyleLike = {
            "axis": style.get("axis", "y"),
            "short_size": style.get("short_size", 10),
            "border_dist": style.get("border_dist", 3),
            "padding": style.get("padding", 3),
            "size_reduce": style.get("size_reduce", 0),
            "bar_update_id": style.get("bar_update_id", None),
            "handle_update_id": style.get("handle_update_id", None),
        }
        self.size: int | float = 0
        self.handle_size: int = 0
        self.handle_dragger: Dragger = Dragger(
            lock_x=self.axis == "y", lock_y=self.axis == "x"
        )
        self.bar_rect: pygame.Rect = pygame.Rect()
        self.handle_rect: pygame.Rect = pygame.Rect()

        self.bar_style: _typing.ElementStyleLike = {"ignore_grid": True, "z": 999}
        self.handle_style: _typing.ElementStyleLike = {"ignore_grid": True, "z": 9999}

        _core._globalctx._register_update_id(self.style["bar_update_id"], self.update)
        _core._globalctx._register_update_id(
            self.style["handle_update_id"], self.update_handle
        )

    @property
    def axis(self) -> typing.Literal["x", "y"]:
        return self.style["axis"]

    @axis.setter
    def axis(self, value):
        self.axis = value
        self.handle_dragger.lock_x = self.axis == "x"
        self.handle_dragger.lock_y = self.axis == "y"

    @property
    def needed(self):
        if (
            self._scroll._element_data is None
            or self._scroll._element_data.grid is None
        ):
            return False
        return (
            self._scroll._element_data.grid.overflowy
            if self.axis == "y"
            else self._scroll._element_data.grid.overflowx
        ) > 0

    def update[IT: _data.Interaction | _data.ElementData](self, container: IT) -> IT:
        if isinstance(container, _data.ElementData):
            element_data = container
        else:
            element_data = container.data
        rectsize = element_data.rect.h if self.axis == "x" else element_data.rect.w
        previous = self.size
        self.size = (
            (element_data.rect.w if self.axis == "x" else element_data.rect.h)
            - self.style["padding"] * 2
            - self.style["size_reduce"]
        )
        if previous != self.size and previous != 0:
            inc = self.size / previous
            if self.axis == "x":
                self.handle_dragger.position.x *= inc
            else:
                self.handle_dragger.position.y *= inc
            self.handle_dragger.changed = True
        if self.axis == "x":
            self.bar_rect = pygame.Rect(
                self.style["padding"],
                rectsize - self.style["border_dist"] - self.style["short_size"],
                self.size,
                self.style["short_size"],
            )
        else:
            self.bar_rect = pygame.Rect(
                rectsize - self.style["border_dist"] - self.style["short_size"],
                self.style["padding"],
                self.style["short_size"],
                self.size,
            )
        self.handle_size = int(self._scroll.get_handle_size(self.size, self.axis))
        return container

    def update_handle(self, handle_element: _data.Interaction) -> _data.Interaction:
        changed = self.handle_dragger.changed
        self.handle_dragger.update(
            handle_element,
        )
        self.handle_dragger.clamp(
            clamp_x=(0, self.size - self.handle_size) if self.axis == "x" else None,
            clamp_y=(0, self.size - self.handle_size) if self.axis == "y" else None,
            previous_clamps=False,
        )
        if self.handle_dragger.changed or changed:
            self._scroll.set_scroll_from_rel_handle_pos(
                self.size,
                int(
                    self.handle_dragger.position.x
                    if self.axis == "x"
                    else self.handle_dragger.position.y
                ),
                self.handle_size,
                self.axis,
            )
        if self.axis == "x":
            self.handle_rect = pygame.Rect(
                self.handle_dragger.position.x,
                0,
                self.handle_size,
                self.style["short_size"],
            )
        else:
            self.handle_rect = pygame.Rect(
                0,
                self.handle_dragger.position.y,
                self.style["short_size"],
                self.handle_size,
            )
        return handle_element

    def scroll_moved(self):
        pos = self._scroll.get_rel_handle_pos_from_scroll(
            self.size, self.handle_size, self.axis
        )
        if self.axis == "x":
            self.handle_dragger.position.x = pos
        else:
            self.handle_dragger.position.y = pos
        self.handle_dragger.clamp()


class Slider:
    def __init__(
        self,
        style: _typing.SliderStyleLike | dict | None = None,
    ):
        if style is None:
            style = {}
        self.style: _typing.SliderStyleLike = {
            "lock_x": style.get("lock_x", False),
            "lock_y": style.get("lock_y", False),
            "handle_size": style.get("handle_size", (10, 10)),
            "strict_borders": style.get("strict_borders", False),
            "area_update_id": style.get("area_update_id", None),
            "handle_update_id": style.get("handle_update_id", None),
        }
        self._area_data: _data.ElementData | None = None
        self._start_value: pygame.Vector2 | None = None
        self.handle_dragger: Dragger = Dragger()
        self.moved: bool = False

        self.area_style: _typing.ElementStyleLike = {"clip_draw": False}
        self.handle_style: _typing.ElementStyleLike = {"ignore_grid": True}
        self.handle_rect: pygame.Rect = pygame.Rect()

        _core._globalctx._register_update_id(
            self.style["area_update_id"], self.update_area
        )
        _core._globalctx._register_update_id(
            self.style["handle_update_id"], self.update_handle
        )

    @classmethod
    def from_axis(
        cls,
        axis: typing.Literal["x", "y"],
        style: _typing.SliderStyleLike | dict | None,
    ):
        if style is None:
            style = {}
        return cls({**style, "lock_x": axis == "x", "lock_y": axis == "y"})

    def update_area[IT: _data.Interaction | _data.ElementData](
        self, area_element: IT
    ) -> IT:
        previous = self.value
        if isinstance(area_element, _data.ElementData):
            self._area_data = area_element
        else:
            self._area_data = area_element.data
        if (
            self._area_data is not None
            and self._start_value is not None
            and (self._area_data.rect.w != 0 or self._area_data.rect.h != 0)
        ):
            self.value = self._start_value
            self._start_value = None
        else:
            if self.value != previous:
                self.value = previous
        return area_element

    def update_handle(self, handle_element: _data.Interaction) -> _data.Interaction:
        if self._area_data is None:
            raise _error.MILIStatusError(
                "Slider.update_area must be called before Slider.update_handle"
            )
        self.handle_dragger.lock_x = self.style["lock_x"]
        self.handle_dragger.lock_y = self.style["lock_y"]
        if self.style["lock_x"]:
            self.handle_dragger.position.x = self._area_data.rect.w / 2
        if self.style["lock_y"]:
            self.handle_dragger.position.y = self._area_data.rect.h / 2
        clamp_padx, clamp_pady = (
            self.style["handle_size"][0] / 2
            if self.style["strict_borders"]
            and self._area_data.rect.w >= self.style["handle_size"][0]
            else 0,
            self.style["handle_size"][1] / 2
            if self.style["strict_borders"]
            and self._area_data.rect.h >= self.style["handle_size"][1]
            else 0,
        )
        self.handle_dragger.update(
            handle_element,
        )
        self.handle_dragger.clamp(
            (0 + clamp_padx, self._area_data.rect.w - clamp_padx),
            (0 + clamp_pady, self._area_data.rect.h - clamp_pady),
            False,
        )
        self.handle_rect = pygame.Rect(
            (
                self.handle_dragger.position.x - self.style["handle_size"][0] / 2,
                self.handle_dragger.position.y - self.style["handle_size"][1] / 2,
            ),
            self.style["handle_size"],
        )
        self.moved = self.handle_dragger.changed
        return handle_element

    @property
    def value(self) -> pygame.Vector2:
        if self._area_data is None:
            if self._start_value is not None:
                return self._start_value
            return pygame.Vector2(-1, -1)
        if not self.style["strict_borders"]:
            return pygame.Vector2(
                0
                if self.style["lock_x"] or self._area_data.rect.w == 0
                else self.handle_dragger.position.x / self._area_data.rect.w,
                0
                if self.style["lock_y"] or self._area_data.rect.h == 0
                else self.handle_dragger.position.y / self._area_data.rect.h,
            )
        hx, hy = self.style["handle_size"][0] / 2, self.style["handle_size"][1] / 2
        return pygame.Vector2(
            0
            if self.style["lock_x"] or self._area_data.rect.w == 0
            else (self.handle_dragger.position.x - hx)
            / (self._area_data.rect.w - hx * 2),
            0
            if self.style["lock_y"] or self._area_data.rect.h == 0
            else (self.handle_dragger.position.y - hy)
            / (self._area_data.rect.h - hy * 2),
        )

    @value.setter
    def value(self, v: typing.Sequence[float] | pygame.Vector2):
        v = (pygame.math.clamp(v[0], 0, 1), pygame.math.clamp(v[1], 0, 1))
        if self._area_data is None:
            self._start_value = pygame.Vector2(v)
            return
        if not self.style["strict_borders"]:
            if not self.style["lock_x"]:
                self.handle_dragger.position.x = v[0] * self._area_data.rect.w
            if not self.style["lock_y"]:
                self.handle_dragger.position.y = v[1] * self._area_data.rect.h
            self.handle_rect = pygame.Rect(
                (
                    self.handle_dragger.position.x - self.style["handle_size"][0] / 2,
                    self.handle_dragger.position.y - self.style["handle_size"][1] / 2,
                ),
                self.style["handle_size"],
            )
            return
        hx, hy = self.style["handle_size"][0] / 2, self.style["handle_size"][1] / 2
        if not self.style["lock_x"]:
            self.handle_dragger.position.x = (
                v[0] * (self._area_data.rect.w - hx * 2) + hx
            )
        if not self.style["lock_y"]:
            self.handle_dragger.position.y = (
                v[1] * (self._area_data.rect.h - hy * 2) + hy
            )
        self.handle_rect = pygame.Rect(
            (
                self.handle_dragger.position.x - self.style["handle_size"][0] / 2,
                self.handle_dragger.position.y - self.style["handle_size"][1] / 2,
            ),
            self.style["handle_size"],
        )

    @property
    def valuex(self) -> float:
        return self.value.x

    @property
    def valuey(self) -> float:
        return self.value.y

    @valuex.setter
    def valuex(self, v: float):
        self.value = pygame.Vector2(v, self.value.y)

    @valuey.setter
    def valuey(self, v: float):
        self.value = pygame.Vector2(self.value.x, v)


class DropMenu:
    def __init__(
        self,
        options: typing.Sequence[typing.Any],
        selected: typing.Any,
        style: _typing.DropMenuStyleLike | dict | None = None,
    ):
        if style is None:
            style = {}
        self.options = list(options)
        self.selected = selected
        self.just_selected: bool = False
        self.shown: bool = False
        self.style: _typing.DropMenuStyleLike = {
            "direction": style.get("direction", "down"),
            "anchor": style.get("anchor", "first"),
            "padding": style.get("padding", 3),
            "selected_update_id": style.get("selected_update_id", None),
            "option_update_id": style.get("option_update_id", None),
            "menu_update_id": style.get("menu_update_id", None),
        }
        self.topleft = pygame.Vector2(0, 0)
        self.menu_style: _typing.ElementStyleLike = {"ignore_grid": True}
        self._menu_rect: pygame.Rect | None = None
        self._menu_parent_abspos = pygame.Vector2()
        self._option_i = 0
        self.__just_open = False
        _core._globalctx._register_update_id(
            style["selected_update_id"], self.update_selected
        )
        _core._globalctx._register_update_id(
            style["option_update_id"], self.update_option
        )
        _core._globalctx._register_update_id(style["menu_update_id"], self.update_menu)

    def show(self):
        self.shown = True

    def hide(self):
        self.shown = False

    def toggle(self):
        self.shown = not self.shown

    def update_selected(self, selected_element: _data.Interaction) -> _data.Interaction:
        if selected_element.left_just_released:
            self.toggle()
            self.__just_open = True
        else:
            self.__just_open = False
        if self._menu_rect is None:
            return selected_element
        menur = self._menu_rect
        selr = selected_element.data.absolute_rect
        match self.style["anchor"]:
            case "center":
                self.topleft = pygame.Vector2(
                    selr.x - (menur.w - selr.w) / 2 - self._menu_parent_abspos.x, 0
                )
            case "first":
                self.topleft = pygame.Vector2(selr.x - self._menu_parent_abspos.x, 0)
            case "last":
                self.topleft = pygame.Vector2(
                    selr.x - (menur.w - selr.w) - self._menu_parent_abspos.x, 0
                )
        if self.style["direction"] == "down":
            self.topleft.y = (
                selr.bottom + self.style["padding"] - self._menu_parent_abspos.y
            )
        else:
            self.topleft.y = (
                selr.top - menur.h - self.style["padding"] - self._menu_parent_abspos.y
            )
        return selected_element

    def update_menu(self, menu_element: _data.Interaction) -> _data.Interaction:
        self._option_i = 0
        self._menu_rect = menu_element.data.rect
        if _core._globalctx._mili is None:
            self._menu_parent_abspos = pygame.Vector2(0, 0)
            return menu_element
        parent = _core._globalctx._mili.data_from_id(menu_element.data.parent_id)
        if parent is None:
            self._menu_parent_abspos = pygame.Vector2(0, 0)
            return menu_element
        self._menu_parent_abspos = pygame.Vector2(parent.absolute_rect.topleft)
        return menu_element

    def update_option(self, option_element: _data.Interaction) -> _data.Interaction:
        self.just_selected = False
        if option_element.left_just_released and not self.__just_open:
            self.selected = self.options[self._option_i]
            self.just_selected = True
            self.hide()
        self._option_i += 1
        return option_element


class EntryLine:
    def __init__(
        self, text: str, style: _typing.EntryLineStyleLike | dict | None = None
    ):
        if style is None:
            style = {}
        self.style: _typing.EntryLineStyleLike = {
            "blink_interval": style.get("blink_interval", 350),
            "cursor_color": style.get("cursor_color", "white"),
            "cursor_width": style.get("cursor_width", 2),
            "error_color": style.get("error_color", "red"),
            "input_validator": style.get("input_validator", None),
            "number_integer": style.get("number_integer", False),
            "number_max": style.get("number_max", None),
            "number_min": style.get("number_min", None),
            "placeholder": style.get("placeholder", "Enter text..."),
            "placeholder_color": style.get("placeholder_color", (180,) * 3),
            "selection_color": style.get("selection_color", (20, 80, 225)),
            "target_number": style.get("target_number", False),
            "text_style": style.get("text_style", {}),
            "text_validator": style.get("text_validator", None),
            "validator_lowercase": style.get("validator_lowercase", False),
            "validator_uppercase": style.get("validator_uppercase", False),
            "validator_windows_path": style.get("validator_windows_path", False),
            "copy_key": style.get("copy_key", pygame.K_c),
            "keymod": style.get("keymod", pygame.KMOD_CTRL),
            "paste_key": style.get("paste_key", pygame.K_v),
            "select_all_key": style.get("select_all_key", pygame.K_a),
            "delete_all_key": style.get("delete_all_key", pygame.K_BACKSPACE),
            "scroll": style.get("scroll", None),
            "bg_rect_style": style.get("bg_rect_style", None),
            "outline_rect_style": style.get("outline_rect_style", None),
            "text_filly": style.get("text_filly", "100"),
            "selection_style": style.get("selection_style", None),
            "double_click_interval": style.get("double_click_interval", 250),
            "cut_key": style.get("cut_key", pygame.K_x),
            "enable_history": style.get("enable_history", True),
            "redo_key": style.get("redo_key", pygame.K_y),
            "undo_key": style.get("undo_key", pygame.K_z),
            "history_limit": style.get("history_limit", 1000),
        }
        self._text = str(text)
        self.cursor = len(self._text)
        self.focused = False
        self._error = False
        self._cursor_on = True
        self._cursor_time = pygame.time.get_ticks()
        self._selection_start = None
        self._offset = 0
        self._size = 0
        self._cont_w = 0
        self._pad = 0
        self._just_checked = False
        self._rect = pygame.Rect()
        self._press = False
        self._focus_press = False
        self._press_cursor = 0
        self._press_time = pygame.time.get_ticks()
        self._release_time = pygame.time.get_ticks()
        self._press_count = 0
        self._font = None
        self._cont_rect = pygame.Rect()
        self._history = []
        self._history_index = -1

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, v):
        self._text = str(v)
        self.cursor = len(self._text)

    @property
    def text_strip(self):
        return self._text.strip()

    @property
    def text_as_number(self) -> float:
        try:
            text = self.text
            if text.startswith("0x") or text.startswith("0o"):
                number = eval(text)
            else:
                number = float(text)
            prev = number
            number = pygame.math.clamp(
                number,
                self.style["number_min"] if self.style["number_min"] else float("-inf"),
                self.style["number_max"] if self.style["number_max"] else float("inf"),
            )
            if prev != number:
                self._error = True
            if self.style["number_integer"]:
                number = int(number)
        except (ValueError, SyntaxError):
            number = (
                self.style["number_min"] if self.style["number_min"] else float("nan")
            )
            if number != float("nan") and self.style["number_integer"]:
                number = int(number)
            self._error = True
        return number

    def ui(self, container_element: _data.Interaction):
        mpos = pygame.mouse.get_pos()
        mposx = mpos[0]
        if pygame.time.get_ticks() - self._cursor_time >= self.style["blink_interval"]:
            self._cursor_on = not self._cursor_on
            self._cursor_time = pygame.time.get_ticks()
        if not self.focused:
            self._cursor_on = False
        if self._press and (pygame.time.get_ticks() - self._press_time >= 40):
            self._set_cursor_on()
            new_cursor, tocheck = self._cursor_from_pos(mposx, 1)
            if (
                new_cursor != self._press_cursor
                and new_cursor - 1 != self._press_cursor
                and self._selection_start is None
            ):
                self._selection_start = self.cursor
                if new_cursor < self._press_cursor:
                    self._selection_start += 1
            if tocheck:
                self._check()
            self.cursor = new_cursor
        mili = _core._globalctx._mili
        if mili is None:
            return None
        if mili._ctx._parent["id"] != container_element.data.id:
            raise _error.MILIStatusError(
                "Entryline's container element must be created as a parent"
            )
        if self.style["bg_rect_style"] is not None:
            mili.rect(self.style["bg_rect_style"])
        if self.style["outline_rect_style"] is not None:
            mili.rect(self.style["outline_rect_style"])
        color = self.style["text_style"].get("color", "white")
        text = self._text
        if len(self._text) <= 0 and not self.focused:
            text = self.style["placeholder"]
            color = self.style["placeholder_color"]
        if self._error:
            color = self.style["error_color"]

        style = (
            {"growy": False}
            | self.style["text_style"]
            | {
                "growx": True,
                "color": color,
                "padx": 0,
                "pady": 0,
            }
        )
        pad = container_element.data.grid.padx
        self._cont_rect = container_element.data.absolute_rect
        self._font = mili.text_font(style)
        fonth = self._font.get_height()
        text_to_cursor = self._text[: self.cursor]
        size = mili.text_size(text_to_cursor, style)
        self._size = size.x
        self._pad = pad
        self._cont_w = container_element.data.rect.w
        if self._just_checked:
            self._check()
            self._just_checked = False
        scrolloffset = pygame.Vector2()
        if self.style["scroll"] is not None:
            scrolloffset = self.style["scroll"].get_offset()
        te = mili.element(
            None,
            {
                "blocking": False,
                "filly": self.style["text_filly"],
                "offset": pygame.Vector2(-self._offset, 0) + scrolloffset,
            },
        )
        self._rect = te.data.absolute_rect
        if self._selection_start is not None and self.cursor != self._selection_start:
            start, end = (
                min(self.cursor, self._selection_start),
                max(self.cursor, self._selection_start),
            )
            text_to_start = self.text[:start]
            text_to_end = self.text[:end]
            size_start = mili.text_size(text_to_start, style).x
            size_end = mili.text_size(text_to_end, style).x
            extra_style = {}
            if self.style["selection_style"] is not None:
                extra_style = self.style["selection_style"]
            sel_rect = pygame.Rect(
                size_start - scrolloffset[0] + te.data.absolute_rect.x,
                te.data.rect.h
                - te.data.rect.h / 2
                - fonth / 2
                - scrolloffset[1]
                + te.data.absolute_rect.y,
                size_end - size_start,
                fonth,
            )
            mili.rect(
                extra_style
                | {"ready_rect": sel_rect, "color": self.style["selection_color"]}
            )
        mili.text(text, style)
        mili.element(
            (
                pad + (self._size - self._offset),
                te.data.rect.bottom - te.data.rect.h / 2 - fonth / 2,
                self.style["cursor_width"],
                fonth,
            ),
            {"ignore_grid": True, "offset": scrolloffset, "blocking": False},
        )
        if self._cursor_on:
            mili.rect(
                {"color": self.style["cursor_color"], "border_radius": 0, "outline": 0},
            )
        if container_element.left_just_pressed and self._rect.collidepoint(mpos):
            self.focused = True
            self._press_time = pygame.time.get_ticks()
            if (
                pygame.time.get_ticks() - self._release_time
                <= self.style["double_click_interval"]
            ):
                self._press_count += 1
                if self._press_count == 1:
                    checkspace = True
                    try:
                        if self._text[self.cursor] == " ":
                            checkspace = False
                    except IndexError:
                        ...
                    left, right = self._text[: self.cursor], self._text[self.cursor :]
                    li = len(left) - 1
                    while li >= 0:
                        char = left[li]
                        if (char == " " and checkspace) or (
                            char != " " and not checkspace
                        ):
                            break
                        li -= 1
                    li += 1
                    ri = 0
                    while ri < len(right):
                        char = right[ri]
                        if (char == " " and checkspace) or (
                            char != " " and not checkspace
                        ):
                            break
                        ri += 1
                    self._selection_start = self.cursor - (len(left) - li)
                    self.cursor = self.cursor + ri
                    self._check()
                elif self._press_count == 2:
                    self.cursor = len(self._text)
                    self._selection_start = 0
                    self._press_count = 0
                    self._check()
                else:
                    self.cursor, tocheck = self._cursor_from_pos(mposx)
                    if tocheck:
                        self._check()
            else:
                self._press_count = 0
                self._press = True
                self.cancel_selection()
                self.cursor, tocheck = self._cursor_from_pos(mposx)
                if tocheck:
                    self._check()
                self._press_cursor = self.cursor
            self._set_cursor_on()
        if container_element.left_just_pressed:
            self._focus_press = True
        if container_element.left_just_released:
            self.focused = True
            self._press = False
            self._set_cursor_on()
            if self._rect.collidepoint(mpos):
                self._release_time = pygame.time.get_ticks()
            else:
                self.cursor = len(self._text)
                self._set_cursor_on()
                self.cancel_selection()

    def event(self, event: pygame.Event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
            self._press = False
            self._press_cursor = 0
            if not self._focus_press:
                self.unfocus()
            self._focus_press = False
        if not self.focused:
            return
        if event.type == pygame.TEXTINPUT:
            text = event.text
            self.insert(text)
        if event.type == pygame.KEYDOWN:
            if event.mod & self.style["keymod"]:
                if event.key == self.style["select_all_key"]:
                    self.cursor = len(self._text)
                    self._selection_start = 0
                    self._set_cursor_on()
                if event.key == self.style["delete_all_key"]:
                    self._history_save()
                    self.text = ""
                    self.cursor = 0
                if event.key == self.style["copy_key"]:
                    text = self.get_selection()
                    pygame.scrap.put_text(text)
                if event.key == self.style["paste_key"]:
                    text = pygame.scrap.get_text()
                    if self._selection_start is not None:
                        self.delete_selection()
                    self.insert(text)
                if event.key == self.style["cut_key"]:
                    self._history_save()
                    text = self.get_selection()
                    pygame.scrap.put_text(text)
                    self.delete_selection()
                if event.key == self.style["undo_key"]:
                    self.undo()
                if event.key == self.style["redo_key"]:
                    self.redo()
                if event.key == pygame.K_LEFT:
                    self.cursor = 0
                    self._set_cursor_on()
                if event.key == pygame.K_RIGHT:
                    self.cursor = len(self._text)
                    self._set_cursor_on()
                return
            moved = False
            if event.mod & pygame.KMOD_SHIFT:
                if event.key == pygame.K_LEFT:
                    if self._selection_start is None:
                        self._selection_start = self.cursor
                    self.move_cursor(-1)
                    self._set_cursor_on()
                    moved = True
                if event.key == pygame.K_RIGHT:
                    if self._selection_start is None:
                        self._selection_start = self.cursor
                    self.move_cursor(1)
                    self._set_cursor_on()
                    moved = True
            if event.key == pygame.K_LEFT and not moved:
                if self._selection_start is not None:
                    if self.cursor == self._selection_start:
                        self.move_cursor(-1)
                    self.cancel_selection()
                else:
                    self.move_cursor(-1)
                self._set_cursor_on()
            if event.key == pygame.K_RIGHT and not moved:
                if self._selection_start is not None:
                    if self.cursor == self._selection_start:
                        self.move_cursor(1)
                    self.cancel_selection()
                else:
                    self.move_cursor(1)
                self._set_cursor_on()
            if event.key == pygame.K_BACKSPACE:
                if self._selection_start is not None:
                    self.delete_selection()
                else:
                    self.delete(-1)
            if event.key == pygame.K_DELETE:
                if self._selection_start is not None:
                    self.delete_selection()
                else:
                    self.delete(1)
            if event.key in [pygame.K_RETURN]:
                if self.style["target_number"]:
                    self._history_save()
                    self.text = f"{self.text_as_number}"
                    self._error = False

    def clear_history(self):
        self._history = []
        self._history_index = -1

    def undo(self):
        if not self.style["enable_history"]:
            return
        if self._history_index <= 0:
            return
        self._history_index -= 1
        self._history_apply()

    def redo(self):
        if not self.style["enable_history"]:
            return
        if self._history_index >= len(self._history) - 1:
            return
        self._history_index += 1
        self._history_apply()

    def insert(self, string: str):
        self._history_save()
        string = self._validate(string)
        if self._selection_start is not None:
            self.delete_selection()
        left, right = self._text[: self.cursor], self._text[self.cursor :]
        self._text = left + string + right
        self.cursor += len(string)
        self._check(True)

    def move_cursor(self, amount: int):
        self.cursor += amount
        self._check()

    def select(self, start: int, end: int):
        self.cursor = max(start, end)
        self._selection_start = min(start, end)

    def cancel_selection(self):
        self._selection_start = None

    def delete(self, amount: int):
        if amount == 0:
            return
        self._history_save()
        left, right = self._text[: self.cursor], self._text[self.cursor :]
        if amount > 0:
            amount = abs(amount)
            if amount > len(right):
                amount = len(right)
            newright = right[amount:]
            self._text = left + newright
        else:
            amount = abs(amount)
            if amount > len(left):
                amount = len(left)
            newleft = left[: len(left) - amount]
            self._text = newleft + right
            self.cursor -= amount
        self._check(True)

    def delete_selection(self):
        if self._selection_start is None:
            raise _error.MILIStatusError(
                "Cannot delete entryline selection with no active selection"
            )
        self._history_save()
        start, end = (
            min(self.cursor, self._selection_start),
            max(self.cursor, self._selection_start),
        )
        self._text = self.text[:start] + self.text[end:]
        self.cursor = start
        self.cancel_selection()

    def get_selection(self):
        if self._selection_start is None:
            raise _error.MILIStatusError(
                "Cannot get entryline selection with no active selection"
            )
        start, end = (
            min(self.cursor, self._selection_start),
            max(self.cursor, self._selection_start),
        )
        return self.text[start:end]

    def focus(self):
        self.focused = True
        self._set_cursor_on()

    def unfocus(self):
        self.focused = False
        self.cancel_selection()

    def _set_cursor_on(self):
        self._cursor_on = True
        self._cursor_time = pygame.time.get_ticks()

    def _cursor_from_pos(self, posx, add=0):
        tocheck = False
        if posx < self._cont_rect.left or posx > self._cont_rect.right:
            tocheck = True
        if posx <= self._rect.left:
            return 0, tocheck
        if posx >= self._rect.right:
            return len(self._text), tocheck
        if self._font is None:
            return 0, tocheck
        dx = posx - self._rect.x
        for i in range(len(self._text) + 1):
            tw = self._font.size(self._text[:i])[0]
            if tw >= dx:
                return i - 1 + add, tocheck
        return len(self._text), tocheck

    def _check(self, edit=False):
        self._just_checked = True
        if self.cursor < 0:
            self.cursor = 0
        if self.cursor > len(self._text):
            self.cursor = len(self._text)
        cursorpos = self._size - self._offset
        if cursorpos > self._cont_w - self._pad * 2:
            self._offset = self._size - (self._cont_w - self._pad * 2)
        if cursorpos < 0:
            self._offset = self._size
        if self.style["scroll"] is not None:
            self.style["scroll"].scroll_offset.x = 0
        if edit:
            self._set_cursor_on()
            self._error = False
            if self.style["text_validator"]:
                result = self.style["text_validator"](self.text)
                self._text, self._error = result[0], not result[1]
            if self.style["target_number"]:
                self.text_as_number

    def _validate(self, text):
        text = text.replace("\n", "")
        if self.style["validator_lowercase"]:
            text = text.lower()
        if self.style["validator_uppercase"]:
            text = text.upper()
        if (
            self.style["validator_windows_path"]
            or self.style["input_validator"]
            or self.style["target_number"]
        ):
            string = ""
            for letter in text:
                if self.style["target_number"]:
                    if letter not in "-0123456789.exoabcdefABCDEF":
                        continue
                    if self.style["number_integer"] and letter == ".":
                        continue
                if self.style["validator_windows_path"] and letter in '<>:"/\\|?*':
                    continue
                if self.style["input_validator"]:
                    res = self.style["input_validator"](letter)
                    if res is None:
                        continue
                    string += res
                else:
                    string += letter
            text = string
        return text

    def _history_save(self):
        if not self.style["enable_history"]:
            return
        state = {
            "text": self._text,
            "cursor": self.cursor,
            "selection": self._selection_start,
            "error": self._error,
            "offset": self._offset,
        }
        if len(self._history) <= 0:
            self._history.append(state)
            self._history_index = 0
        else:
            if self._history_index < len(self._history) - 1:
                # print("before", self._history)
                self._history = self._history[: self._history_index]
                # print("after")
            self._history.append(state)
            self._history_index += 1
        if self.style["history_limit"] is None:
            return
        if len(self._history) > abs(self.style["history_limit"]):
            self._history = self._history[
                len(self._history) - abs(self.style["history_limit"]) :
            ]

    def _history_apply(self):
        state = self._history[self._history_index]
        self._text = state["text"]
        self.cursor = state["cursor"]
        self._selection_start = state["selection"]
        self._error = state["error"]
        self._offset = state["offset"]
