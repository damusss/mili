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
        _core._globalctx._register_update_id(update_id, self.update)

    def update[IT: _data.Interaction | _data.ElementData](self, container: IT) -> IT:
        if isinstance(container, _data.ElementData):
            self._element_data = container
        else:
            self._element_data = container.data
        self.clamp()
        return container

    def scroll(self, x: float, y: float):
        self.scroll_offset.x += x
        self.scroll_offset.y += y
        self.clamp()

    def set_scroll(self, x: float, y: float):
        self.scroll_offset.x = x
        self.scroll_offset.y = y
        self.clamp()

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
