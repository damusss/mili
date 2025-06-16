import pygame
import typing
from mili import _core
from mili import data as _data
from mili import typing as _typing
from mili import error as _error
from mili import icon as _icon


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
        self.style: _typing.ElementStyleLike = {
            "ignore_grid": True,
            "update_id": update_id,
        }
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
        self._update_id = update_id

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
        constrain_rect: pygame.typing.RectLike | None = None,
        axis_invert_kmod: int | None = None,
    ):
        if event.type == pygame.MOUSEWHEEL and (
            constrain_rect is None
            or pygame.Rect(constrain_rect).collidepoint(pygame.mouse.get_pos())
        ):
            x, y = event.x * multiplier, -event.y * multiplier
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
        self.handle_style: _typing.ElementStyleLike = {
            "ignore_grid": True,
            "z": 9999,
            "update_id": self.style["handle_update_id"],
        }

        _core._globalctx._register_update_id(self._scroll._update_id, self.update)
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
            "drag_area": style.get("drag_area", True),
        }
        self._area_data: _data.ElementData | None = None
        self._start_value: pygame.Vector2 | None = None
        self.dragging_area = False
        self.handle_dragger: Dragger = Dragger()
        self.moved: bool = False

        self.area_style: _typing.ElementStyleLike = {
            "clip_draw": False,
            "update_id": self.style["area_update_id"],
        }
        self.handle_style: _typing.ElementStyleLike = {
            "ignore_grid": True,
            "update_id": self.style["handle_update_id"],
        }
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
        return cls({**style, "lock_x": axis == "y", "lock_y": axis == "x"})

    def update_area(self, area_element: _data.Interaction) -> _data.Interaction:
        previous = self.value
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
        if self.style["drag_area"] and area_element.left_pressed:
            before = self.handle_dragger.position.copy()
            diff = (
                pygame.Vector2(pygame.mouse.get_pos())
                - self._area_data.absolute_rect.topleft
            )
            self.dragging_area = True
            clamp_padx, clamp_pady = self._pre_update()
            self.handle_dragger.position = diff
            self._post_update(clamp_padx, clamp_pady)
            self.moved = before != self.handle_dragger.position
        else:
            self.dragging_area = False
        return area_element

    def update_handle(self, handle_element: _data.Interaction) -> _data.Interaction:
        if self.dragging_area:
            return handle_element
        if self._area_data is None:
            raise _error.MILIStatusError(
                "Slider.update_area must be called before Slider.update_handle"
            )
        clamp_padx, clamp_pady = self._pre_update()
        self.handle_dragger.update(
            handle_element,
        )
        self._post_update(clamp_padx, clamp_pady)
        self.moved = self.handle_dragger.changed
        return handle_element

    def _post_update(self, clamp_padx, clamp_pady):
        if self._area_data is None:
            raise
        self.handle_dragger.clamp(
            (0 + clamp_padx, self._area_data.rect.w - clamp_padx),
            (0 + clamp_pady, self._area_data.rect.h - clamp_pady),
            False,
        )
        if self.style["lock_x"]:
            self.handle_dragger.position.x = self._area_data.rect.w / 2
        if self.style["lock_y"]:
            self.handle_dragger.position.y = self._area_data.rect.h / 2
        self.handle_rect = pygame.Rect(
            (
                self.handle_dragger.position.x - self.style["handle_size"][0] / 2,
                self.handle_dragger.position.y - self.style["handle_size"][1] / 2,
            ),
            self.style["handle_size"],
        )

    def _pre_update(self):
        if self._area_data is None:
            raise
        self.handle_dragger.lock_x = self.style["lock_x"]
        self.handle_dragger.lock_y = self.style["lock_y"]
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
        return clamp_padx, clamp_pady

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
        ui_style: _typing.DropMenuUIStyleLike | dict | None = None,
    ):
        if style is None:
            style = {}
        if ui_style is None:
            ui_style = {}
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
        opt_cols = ui_style.get("option_colors", {})
        selopt_cols = ui_style.get("selected_option_colors", {})
        self.ui_style: _typing.DropMenuUIStyleLike = {
            "bg_color": ui_style.get("bg_color", (24, 24, 24)),
            "border_radius": ui_style.get("border_radius", 7),
            "option_border_radius": ui_style.get("option_border_radius", 7),
            "option_color": {
                "default": opt_cols.get("default", None),
                "hover": opt_cols.get("hover", (40, 40, 40)),
                "press": opt_cols.get("press", (40, 40, 40)),
            },
            "selected_option_color": {
                "default": selopt_cols.get("default", (24, 24, 24)),
                "hover": selopt_cols.get("hover", (40, 40, 40)),
                "press": selopt_cols.get("press", (40, 40, 40)),
            },
            "outline_color": ui_style.get("outline_color", (40, 40, 40)),
            "menu_style": ui_style.get("menu_style", {"pad": 3, "spacing": 0}),
            "text_style": ui_style.get("text_style", {"align": "left"}),
            "icon_arrow_down": ui_style.get("icon_arrow_down", "arrow_drop_down"),
            "icon_arrow_up": ui_style.get("icon_arrow_up", "arrow_drop_up"),
            "option_text_style": ui_style.get("option_text_style", {"align": "left"}),
        }
        self.topleft = pygame.Vector2(0, 0)
        self.menu_style: _typing.ElementStyleLike = {
            "ignore_grid": True,
            "update_id": self.style["menu_update_id"],
        }
        self._menu_rect: pygame.Rect | None = None
        self._menu_parent_abspos = pygame.Vector2()
        self._option_i = 0
        self.__just_open = False
        _core._globalctx._register_update_id(
            self.style["selected_update_id"], self.update_selected
        )
        _core._globalctx._register_update_id(
            self.style["option_update_id"], self.update_option
        )
        _core._globalctx._register_update_id(
            self.style["menu_update_id"], self.update_menu
        )

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
        if self._menu_rect is None or self._menu_rect.h == 0:
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
        if not self.shown and _core._globalctx._mili is not None:
            parent = _core._globalctx._mili.data_from_id(
                selected_element.data.parent_id
            )
            if parent is not None:
                self._menu_parent_abspos = pygame.Vector2(parent.absolute_rect.topleft)
        return selected_element

    def update_menu(self, menu_element: _data.Interaction) -> _data.Interaction:
        self._option_i = 0
        if menu_element.data.rect.h != 0:
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

    def ui(
        self,
        selected_rect: pygame.typing.RectLike | None,
        selected_style: _typing.ElementStyleLike | None,
    ):
        upicon, downicon = (
            _icon._get_icon(self.ui_style["icon_arrow_up"]),
            _icon._get_icon(self.ui_style["icon_arrow_down"]),
        )
        _mili = _core._globalctx._mili
        if _mili is None:
            raise _error.MILIStatusError(
                "A MILI instance must be started to use this utility method"
            )
        with _mili.begin(
            selected_rect,
            {"pad": 0, "spacing": 0, "update_id": "cursor"}
            | (selected_style if selected_style else {})
            | {"axis": "x"},
        ) as selected:
            _mili.rect(
                {
                    "color": _core._coreutils._get_conditional_color(
                        selected, self.ui_style["selected_option_color"]
                    ),
                    "border_radius": self.ui_style["border_radius"],
                }
            )
            _mili.rect(
                {
                    "color": self.ui_style["outline_color"],
                    "border_radius": self.ui_style["border_radius"],
                    "outline": 1,
                    "draw_above": True,
                }
            )
            _mili.text_element(
                self.selected,
                {"growx": False} | self.ui_style["text_style"],
                None,
                {"fillx": True, "filly": True, "blocking": False},
            )
            surf = (
                (upicon if self.shown else downicon)
                if self.style["direction"] == "down"
                else (downicon if self.shown else upicon)
            )
            if surf:
                height = selected.data.rect.h
                ratio = surf.width / surf.height
                width = height * ratio
                _mili.image_element(
                    surf, None, (0, 0, width, height), {"blocking": False}
                )
            self.update_selected(selected)
            sel_width = selected.data.rect.w
        if self.shown:
            with _mili.begin(
                (self.topleft, (sel_width, 0)),
                {"z": 99999}
                | self.ui_style["menu_style"]
                | {"resizey": True, "ignore_grid": True},
            ) as menuel:
                _mili.rect(
                    {
                        "color": self.ui_style["bg_color"],
                        "border_radius": self.ui_style["border_radius"],
                    }
                )
                _mili.rect(
                    {
                        "color": self.ui_style["outline_color"],
                        "border_radius": self.ui_style["border_radius"],
                        "outline": 1,
                        "draw_above": True,
                    }
                )
                self.update_menu(menuel)
                for i, option in enumerate(self.options):
                    br = self.ui_style["option_border_radius"]
                    if i == 0:
                        br = (
                            self.ui_style["border_radius"],
                            self.ui_style["border_radius"],
                            br,
                            br,
                        )
                    elif i == len(self.options) - 1:
                        br = (
                            br,
                            br,
                            self.ui_style["border_radius"],
                            self.ui_style["border_radius"],
                        )
                    with _mili.element(
                        None, {"fillx": True, "update_id": "cursor"}
                    ) as optel:
                        _mili.rect(
                            {
                                "color": _core._coreutils._get_conditional_color(
                                    optel, self.ui_style["option_color"]
                                ),
                                "border_radius": br,
                            }
                        )
                        _mili.text(
                            option, {"growy": True} | self.ui_style["option_text_style"]
                        )
                        self.update_option(optel)
        else:
            with _mili.begin(
                (self.topleft, (sel_width, 0)),
                {"z": 99999}
                | self.ui_style["menu_style"]
                | {"resizey": True, "ignore_grid": True, "pad": 0, "spacing": 0},
            ) as menuel:
                self.update_menu(menuel)
                for opt in self.options:
                    _mili.element(None)
