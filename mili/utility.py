import pygame
import typing
from mili import _core
from mili import data as _data
from mili import typing as _typing
from mili import error as _error
from mili.mili import MILI as _MILI

__all__ = (
    "Selectable",
    "Dragger",
    "Scroll",
    "Scrollbar",
    "Slider",
    "GenericApp",
    "InteractionSound",
    "InteractionCursor",
    "CustomWindowBorders",
    "percentage",
    "indent",
    "fit_image",
)


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


class GenericApp:
    def __init__(
        self,
        window: pygame.Window,
        target_framerate: int = 60,
        clear_color: pygame.typing.ColorLike = 0,
        start_style: _typing.ElementStyleLike | None = None,
        use_global_mouse: bool = False,
    ):
        if not pygame.get_init():
            raise _error.MILIStatusError(
                "pygame.init() must be called before creating a generic app"
            )
        self.window = window
        self.clock = pygame.Clock()
        self.target_framerate: int = target_framerate
        self.mili = _MILI(self.window.get_surface(), use_global_mouse)
        self.clear_color: pygame.typing.ColorLike = clear_color
        self.start_style: _typing.ElementStyleLike | None = start_style
        self.delta_time: float = 0

    def update(self): ...

    def ui(self): ...

    def event(self, event: pygame.Event): ...

    def quit(self):
        self.on_quit()
        pygame.quit()
        raise SystemExit

    def on_quit(self): ...

    def post_draw(self): ...

    def run(self):
        while True:
            self.mili.start(self.start_style, window_position=self.window.position)
            for event in pygame.event.get():
                if event.type == pygame.WINDOWCLOSE and event.window == self.window:
                    self.quit()
                else:
                    self.event(event)

            self.window.get_surface().fill(self.clear_color)
            self.update()
            self.ui()
            self.mili.update_draw()
            self.post_draw()
            self.window.flip()
            self.delta_time = self.clock.tick(self.target_framerate) / 1000


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
        self, scrollbar_size: int, axis: typing.Literal["x", "y"] = "y"
    ):
        if self._element_data is not None and self._element_data.grid is not None:
            if axis == "x":
                rectsize = self._element_data.rect.w
                overflow = self._element_data.grid.overflowx
            else:
                rectsize = self._element_data.rect.h
                overflow = self._element_data.grid.overflowy
            return min(
                scrollbar_size, (rectsize / (rectsize + overflow)) * scrollbar_size
            )
        return 0

    def get_rel_handle_pos_from_scroll(
        self,
        scrollbar_size: int,
        handle_size: int,
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
        scrollbar_size: int,
        rel_handle_pos: int,
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
        short_size: int,
        border_dist: int = 3,
        padding: int = 3,
        size_reduce: int = 0,
        axis: typing.Literal["x", "y"] = "y",
        update_id: str | None = None,
        handle_update_id: str | None = None,
    ):
        self._scroll = scroll
        self.axis: typing.Literal["x", "y"] = axis
        self.short_size = short_size
        self.border_dist = border_dist
        self.padding = padding
        self.size_reduce = size_reduce
        self.size: int = 0
        self.handle_size: int = 0
        self.handle_dragger: Dragger = Dragger(
            lock_x=self.axis == "y", lock_y=self.axis == "x"
        )
        self.bar_rect: pygame.Rect = pygame.Rect()
        self.handle_rect: pygame.Rect = pygame.Rect()

        self.bar_style: _typing.ElementStyleLike = {"ignore_grid": True, "z": 999}
        self.handle_style: _typing.ElementStyleLike = {"ignore_grid": True, "z": 9999}

        _core._globalctx._register_update_id(update_id, self.update)
        _core._globalctx._register_update_id(handle_update_id, self.update_handle)

    def change_axis(self, axis: typing.Literal["x", "y"]):
        self.axis = axis
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
            - self.padding * 2
            - self.size_reduce
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
                self.padding,
                rectsize - self.border_dist - self.short_size,
                self.size,
                self.short_size,
            )
        else:
            self.bar_rect = pygame.Rect(
                rectsize - self.border_dist - self.short_size,
                self.padding,
                self.short_size,
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
                self.handle_dragger.position.x, 0, self.handle_size, self.short_size
            )
        else:
            self.handle_rect = pygame.Rect(
                0, self.handle_dragger.position.y, self.short_size, self.handle_size
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
        lock_x: bool,
        lock_y: bool,
        handle_size: typing.Sequence[float],
        strict_borders: bool = False,
        area_update_id: str | None = None,
        handle_update_id: str | None = None,
    ):
        self.lock_x = lock_x
        self.lock_y = lock_y
        self.handle_size = handle_size
        self.strict_borders = strict_borders
        self._area_data: _data.ElementData | None = None
        self._start_value: pygame.Vector2 | None = None
        self.handle_dragger: Dragger = Dragger()
        self.moved: bool = False

        self.area_style: _typing.ElementStyleLike = {"clip_draw": False}
        self.handle_style: _typing.ElementStyleLike = {"ignore_grid": True}
        self.handle_rect: pygame.Rect = pygame.Rect()

        _core._globalctx._register_update_id(area_update_id, self.update_area)
        _core._globalctx._register_update_id(handle_update_id, self.update_handle)

    @classmethod
    def from_axis(
        cls,
        axis: typing.Literal["x", "y"],
        handle_size: typing.Sequence[float],
        strict_borders: bool = False,
    ):
        return cls(axis == "y", axis == "x", handle_size, strict_borders)

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
        self.handle_dragger.lock_x = self.lock_x
        self.handle_dragger.lock_y = self.lock_y
        if self.lock_x:
            self.handle_dragger.position.x = self._area_data.rect.w / 2
        if self.lock_y:
            self.handle_dragger.position.y = self._area_data.rect.h / 2
        clamp_padx, clamp_pady = (
            self.handle_size[0] / 2
            if self.strict_borders and self._area_data.rect.w >= self.handle_size[0]
            else 0,
            self.handle_size[1] / 2
            if self.strict_borders and self._area_data.rect.h >= self.handle_size[1]
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
                self.handle_dragger.position.x - self.handle_size[0] / 2,
                self.handle_dragger.position.y - self.handle_size[1] / 2,
            ),
            self.handle_size,
        )
        self.moved = self.handle_dragger.changed
        return handle_element

    @property
    def value(self) -> pygame.Vector2:
        if self._area_data is None:
            if self._start_value is not None:
                return self._start_value
            return pygame.Vector2(-1, -1)
        if not self.strict_borders:
            return pygame.Vector2(
                0
                if self.lock_x or self._area_data.rect.w == 0
                else self.handle_dragger.position.x / self._area_data.rect.w,
                0
                if self.lock_y or self._area_data.rect.h == 0
                else self.handle_dragger.position.y / self._area_data.rect.h,
            )
        hx, hy = self.handle_size[0] / 2, self.handle_size[1] / 2
        return pygame.Vector2(
            0
            if self.lock_x or self._area_data.rect.w == 0
            else (self.handle_dragger.position.x - hx)
            / (self._area_data.rect.w - hx * 2),
            0
            if self.lock_y or self._area_data.rect.h == 0
            else (self.handle_dragger.position.y - hy)
            / (self._area_data.rect.h - hy * 2),
        )

    @value.setter
    def value(self, v: typing.Sequence[float] | pygame.Vector2):
        v = (pygame.math.clamp(v[0], 0, 1), pygame.math.clamp(v[1], 0, 1))
        if self._area_data is None:
            self._start_value = pygame.Vector2(v)
            return
        if not self.strict_borders:
            if not self.lock_x:
                self.handle_dragger.position.x = v[0] * self._area_data.rect.w
            if not self.lock_y:
                self.handle_dragger.position.y = v[1] * self._area_data.rect.h
            self.handle_rect = pygame.Rect(
                (
                    self.handle_dragger.position.x - self.handle_size[0] / 2,
                    self.handle_dragger.position.y - self.handle_size[1] / 2,
                ),
                self.handle_size,
            )
            return
        hx, hy = self.handle_size[0] / 2, self.handle_size[1] / 2
        if not self.lock_x:
            self.handle_dragger.position.x = (
                v[0] * (self._area_data.rect.w - hx * 2) + hx
            )
        if not self.lock_y:
            self.handle_dragger.position.y = (
                v[1] * (self._area_data.rect.h - hy * 2) + hy
            )
        self.handle_rect = pygame.Rect(
            (
                self.handle_dragger.position.x - self.handle_size[0] / 2,
                self.handle_dragger.position.y - self.handle_size[1] / 2,
            ),
            self.handle_size,
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


class InteractionSound:
    def __init__(
        self,
        hover: pygame.mixer.Sound | None = None,
        unhover: pygame.mixer.Sound | None = None,
        press: pygame.mixer.Sound | None = None,
        release: pygame.mixer.Sound | None = None,
        button: int = pygame.BUTTON_LEFT,
        update_id: str | None = None,
    ):
        self.hover_sound = hover
        self.unhover_sound = unhover
        self.press_sound = press
        self.release_sound = release
        self.button = button
        _core._globalctx._register_update_id(update_id, self.play)

    def play(
        self,
        interaction: _data.Interaction,
        channel: pygame.Channel | None = None,
        maxtime: int = 0,
        fade_ms: int = 0,
    ) -> _data.Interaction:
        if interaction.just_hovered and self.hover_sound is not None:
            if channel is not None:
                channel.play(self.hover_sound, 0, maxtime, fade_ms)
            else:
                self.hover_sound.play(0, maxtime, fade_ms)
        if interaction.just_unhovered and self.unhover_sound is not None:
            if channel is not None:
                channel.play(self.unhover_sound, 0, maxtime, fade_ms)
            else:
                self.unhover_sound.play(0, maxtime, fade_ms)
        if (
            interaction.just_pressed_button == self.button
            and self.press_sound is not None
        ):
            if channel is not None:
                channel.play(self.press_sound, 0, maxtime, fade_ms)
            else:
                self.press_sound.play(0, maxtime, fade_ms)
        if (
            interaction.just_released_button == self.button
            and self.release_sound is not None
        ):
            if channel is not None:
                channel.play(self.release_sound, 0, maxtime, fade_ms)
            else:
                self.release_sound.play(0, maxtime, fade_ms)
        return interaction


class InteractionCursor:
    _cursor_stolen: int | pygame.Cursor | None = None
    idle_cursor: int | pygame.Cursor | None = pygame.SYSTEM_CURSOR_ARROW
    hover_cursor: int | pygame.Cursor | None = pygame.SYSTEM_CURSOR_HAND
    press_cursor: int | pygame.Cursor | None | dict[int, int | pygame.Cursor | None] = (
        pygame.SYSTEM_CURSOR_HAND
    )
    disabled_cursor: int | pygame.Cursor | None = pygame.SYSTEM_CURSOR_NO

    @classmethod
    def setup(
        cls,
        idle_cursor: int | pygame.Cursor | None = pygame.SYSTEM_CURSOR_ARROW,
        hover_cursor: int | pygame.Cursor | None = pygame.SYSTEM_CURSOR_HAND,
        press_cursor: int
        | pygame.Cursor
        | None
        | dict[int, int | pygame.Cursor | None] = pygame.SYSTEM_CURSOR_HAND,
        disabled_cursor: int | pygame.Cursor | None = pygame.SYSTEM_CURSOR_NO,
        update_id: str | None = None,
    ):
        cls._cursor_stolen = None
        cls.idle_cursor = idle_cursor
        cls.hover_cursor = hover_cursor
        cls.press_cursor = press_cursor
        cls.disabled_cursor = disabled_cursor
        _core._globalctx._register_update_id(update_id, cls.update)

    @classmethod
    def apply(
        cls,
    ) -> int | pygame.Cursor | None:
        if cls._cursor_stolen is None and cls.idle_cursor is not None:
            pygame.mouse.set_cursor(cls.idle_cursor)
            cls._cursor_stolen = None
            return cls.idle_cursor
        elif cls._cursor_stolen is not None:
            pygame.mouse.set_cursor(cls._cursor_stolen)
            cursor_ret = cls._cursor_stolen
            cls._cursor_stolen = None
            return cursor_ret
        cls._cursor_stolen = None
        return None

    @classmethod
    def update(
        cls,
        interaction: _data.Interaction,
        disabled: bool = False,
        **cursor_overrides: int
        | pygame.Cursor
        | None
        | dict[int, int | pygame.Cursor | None],
    ) -> _data.Interaction:
        hovered = interaction.hovered
        pressed = interaction.press_button != -1
        if disabled and (hovered or pressed):
            cursor = cursor_overrides.get("disabled_cursor", cls.disabled_cursor)
            if not isinstance(cursor, dict):
                cls._cursor_stolen = cursor
            else:
                cls._cursor_stolen = cls.disabled_cursor
            if cls._cursor_stolen is not None:
                return interaction
        if pressed:
            press_cursor = cursor_overrides.get("press_cursor", cls.press_cursor)
            if isinstance(press_cursor, dict):
                cls._cursor_stolen = press_cursor.get(interaction.press_button, None)
                if cls._cursor_stolen is not None:
                    return interaction
            elif interaction.press_button == pygame.BUTTON_LEFT:
                cls._cursor_stolen = press_cursor
                if cls._cursor_stolen is not None:
                    return interaction
        if hovered:
            cursor = cursor_overrides.get("hover_cursor", cls.hover_cursor)
            if not isinstance(cursor, dict):
                cls._cursor_stolen = cursor
            else:
                cls._cursor_stolen = cls.hover_cursor
            return interaction
        return interaction


class CustomWindowBorders:
    def __init__(
        self,
        window: pygame.Window,
        border_size: int = 3,
        corner_size: int = 6,
        titlebar_height: int = 30,
        change_cursor: bool = True,
        minimum_ratio: float | None = None,
        ratio_axis: typing.Literal["x", "y"] = "y",
        uniform_resize_key: int | None = pygame.K_LSHIFT,
        allowed_directions: list[
            typing.Literal[
                "top",
                "left",
                "bottom",
                "right",
                "topleft",
                "topright",
                "bottomleft",
                "bottomright",
            ]
        ]
        | typing.Literal["all"] = "all",
        on_move: typing.Callable[[], None] | None = None,
        on_resize: typing.Callable[[], None] | None = None,
        on_start_move: typing.Callable[[], None] | None = None,
        on_start_resize: typing.Callable[[], None] | None = None,
        on_end_move: typing.Callable[[], None] | None = None,
        on_end_resize: typing.Callable[[], None] | None = None,
    ):
        self.window = window
        self.border_size = border_size
        self.corner_size = corner_size
        self.titlebar_height = titlebar_height
        self.change_cursor = change_cursor
        self.minimum_ratio = minimum_ratio
        self.ratio_axis = ratio_axis
        self.uniform_resize_key = uniform_resize_key
        self.allowed_directions = allowed_directions
        self._callbacks: dict[
            typing.Literal["move", "resize"],
            dict[
                typing.Literal["start", "end", "during"],
                typing.Callable[[], None] | None,
            ],
        ] = {
            "move": {"start": on_start_move, "end": on_end_move, "during": on_move},
            "resize": {
                "start": on_start_resize,
                "end": on_end_resize,
                "during": on_resize,
            },
        }
        self.dragging: bool = False
        self.resizing: bool = False
        self.relative: pygame.Vector2 = pygame.Vector2()
        self.cumulative_relative: pygame.Vector2 = pygame.Vector2()

        self._left_pressed = False
        self._press_rel = pygame.Vector2()
        self._press_global = pygame.Vector2()
        self._start_val = pygame.Vector2()
        self._resize_winsize = None
        self._resize_winpos = None
        self._resize_handle: CustomWindowBorders._ResizeHandle | None = None
        self._resize_handles = [
            CustomWindowBorders._ResizeHandle(
                self, "topleft", True, None, "xy", pygame.SYSTEM_CURSOR_SIZENWSE
            ),
            CustomWindowBorders._ResizeHandle(
                self, "topright", True, None, "y", pygame.SYSTEM_CURSOR_SIZENESW
            ),
            CustomWindowBorders._ResizeHandle(
                self, "bottomleft", True, None, "x", pygame.SYSTEM_CURSOR_SIZENESW
            ),
            CustomWindowBorders._ResizeHandle(
                self, "bottomright", True, None, None, pygame.SYSTEM_CURSOR_SIZENWSE
            ),
            CustomWindowBorders._ResizeHandle(
                self, "top", False, "x", "y", pygame.SYSTEM_CURSOR_SIZENS
            ),
            CustomWindowBorders._ResizeHandle(
                self, "left", False, "y", "x", pygame.SYSTEM_CURSOR_SIZEWE
            ),
            CustomWindowBorders._ResizeHandle(
                self, "bottom", False, "x", None, pygame.SYSTEM_CURSOR_SIZENS
            ),
            CustomWindowBorders._ResizeHandle(
                self, "right", False, "y", None, pygame.SYSTEM_CURSOR_SIZEWE
            ),
        ]

    def update(self) -> bool:
        if not self.window.focused:
            return False

        mpos = pygame.Vector2(pygame.mouse.get_pos())
        gmpos = pygame.Vector2(pygame.mouse.get_pos(True))
        pressed = pygame.mouse.get_pressed(5, True)[0]
        just = pressed and not self._left_pressed
        self._left_pressed = pressed
        modified_cursor = False

        tbar_rect = pygame.Rect(0, 0, self.window.size[0], self.titlebar_height)
        for handle in self._resize_handles:
            if (
                self.allowed_directions == "all"
                or handle._name in self.allowed_directions
            ):
                handle._make_rect()

        if self.change_cursor:
            if not self.resizing:
                if tbar_rect.h > 0 and (tbar_rect.collidepoint(mpos) or self.dragging):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    modified_cursor = True
            for handle in self._resize_handles:
                if (
                    self.allowed_directions == "all"
                    or handle._name in self.allowed_directions
                ) and (
                    handle._rect.collidepoint(mpos)
                    or (self.resizing and self._resize_handle is handle)
                ):
                    pygame.mouse.set_cursor(handle._cursor)
                    modified_cursor = True
                    break

        if just:
            for handle in self._resize_handles:
                if (
                    self.allowed_directions == "all"
                    or handle._name in self.allowed_directions
                ) and handle._rect.collidepoint(mpos):
                    self.resizing = True
                    self._resize_handle = handle
                    self._press_global = gmpos
                    self._press_rel = mpos
                    self._resize_winpos = self.window.position
                    self._resize_winsize = self.window.size
                    self._start_val = pygame.Vector2(self.window.size)
                    callback = self._callbacks["resize"]["start"]
                    if callback is not None:
                        callback()
                    break

        if pressed:
            if self.resizing and self._resize_handle:
                self._resize_handle._update(gmpos)
        else:
            if self.resizing:
                self.cumulative_relative = self.window.size - self._start_val
                callback = self._callbacks["resize"]["end"]
                if callback is not None:
                    callback()
            self.resizing = False
            self._resize_handle = None
            self.relative = pygame.Vector2()

        if self.resizing or tbar_rect.h <= 0:
            return modified_cursor

        if just and tbar_rect.collidepoint(mpos):
            self._press_rel = mpos
            self._press_global = gmpos
            self._start_val = pygame.Vector2(self.window.position)
            self.dragging = True
            callback = self._callbacks["move"]["start"]
            if callback is not None:
                callback()

        if pressed:
            if not just and self.dragging:
                previous = pygame.Vector2(self.window.position)
                self.window.position = self._start_val + (gmpos - self._press_global)
                self.relative = self.window.position - previous
                self.cumulative_relative = self.window.position - self._start_val
                callback = self._callbacks["move"]["during"]
                if callback is not None:
                    callback()
        else:
            if self.dragging:
                self.cumulative_relative = self.window.position - self._start_val
                callback = self._callbacks["move"]["end"]
                if callback is not None:
                    callback()
            self.dragging = False
            self.relative = pygame.Vector2()
        return modified_cursor

    class _ResizeHandle:
        def __init__(
            self,
            parent: "CustomWindowBorders",
            name,
            iscorner,
            axis,
            movewindow,
            cursor,
        ):
            self._parent = parent
            self._name = name
            self._iscorner = iscorner
            self._axis = axis
            self._movewindow = movewindow
            self._cursor = cursor
            self._axis_lock = (
                "x" if self._axis == "y" else "y" if self._axis == "x" else None
            )
            self._rect: pygame.Rect = pygame.Rect()

        def _make_rect(self):
            if self._iscorner:
                rect = pygame.Rect(
                    0, 0, self._parent.corner_size, self._parent.corner_size
                )
            else:
                rect = pygame.Rect(
                    0,
                    0,
                    self._parent.window.size[0]
                    if self._axis == "x"
                    else self._parent.border_size,
                    self._parent.window.size[1]
                    if self._axis == "y"
                    else self._parent.border_size,
                )
            if self._name == "topright":
                rect = rect.move_to(topright=(self._parent.window.size[0], 0))
            elif self._name == "bottomleft" or self._name == "bottom":
                rect = rect.move_to(bottomleft=(0, self._parent.window.size[1]))
            elif self._name == "bottomright" or self._name == "right":
                rect = rect.move_to(bottomright=self._parent.window.size)
            self._rect = rect

        def _update(self, gmpos):
            if self._parent._resize_winsize is None:
                return
            previous = pygame.Vector2(self._parent.window.size)
            rel: pygame.Vector2 = gmpos - self._parent._press_global
            posrel = pygame.Vector2()
            if self._axis_lock == "y":
                rel.x = 0
            elif self._axis_lock == "x":
                rel.y = 0
            if self._movewindow == "x":
                rel.x *= -1
            elif self._movewindow == "y":
                rel.y *= -1
            elif self._movewindow == "xy":
                rel.x *= -1
                rel.y *= -1
            if (
                self._parent.uniform_resize_key is not None
                and pygame.key.get_pressed()[self._parent.uniform_resize_key]
            ):
                if rel.x != rel.y:
                    if abs(rel.x) > abs(rel.y):
                        rel.y = rel.x
                    else:
                        rel.x = rel.y
            if self._movewindow == "x":
                posrel.x = rel.x
            elif self._movewindow == "y":
                posrel.y = rel.y
            elif self._movewindow == "xy":
                posrel = rel
            newsize = self._parent._resize_winsize + rel
            if newsize.x <= 0 or newsize.y <= 0:
                return
            if self._parent.minimum_ratio is not None:
                if self._parent.ratio_axis:
                    ratio = newsize[0] / newsize[1]
                else:
                    ratio = newsize[1] / newsize[0]
                if ratio < self._parent.minimum_ratio:
                    if self._parent.ratio_axis == "y":
                        newsize = pygame.Vector2(
                            newsize[1] * self._parent.minimum_ratio, newsize[1]
                        )
                    else:
                        newsize = pygame.Vector2(
                            newsize[0], newsize[0] * self._parent.minimum_ratio
                        )
            self._parent.window.size = newsize
            diff = self._parent.window.size - newsize
            if self._movewindow == "x" and diff.x != 0:
                posrel.x += diff.x
            elif self._movewindow == "y" and diff.y != 0:
                posrel.y += diff.y
            elif self._movewindow == "xy" and diff.length() != 0:
                posrel += diff
            self._parent.relative = self._parent.window.size - previous
            self._parent.cumulative_relative = (
                self._parent.window.size - self._parent._start_val
            )
            if posrel.length() != 0 and self._parent._resize_winpos is not None:
                self._parent.window.position = self._parent._resize_winpos - posrel
            callback = self._parent._callbacks["resize"]["during"]
            if callback is not None:
                callback()


def percentage(percentage: float, value: float) -> float:
    return (percentage * value) / 100


def indent(*args, **kwargs): ...


def fit_image(
    rect: pygame.typing.RectLike,
    surface: pygame.Surface,
    padx: int = 0,
    pady: int = 0,
    do_fill: bool = False,
    do_stretchx: bool = False,
    do_stretchy: bool = False,
    fill_color: pygame.typing.ColorLike | None = None,
    border_radius: int = 0,
    alpha: int = 255,
    smoothscale: bool = False,
    ninepatch: int = 0,
) -> pygame.Surface:
    return _core._coreutils._get_image(
        pygame.Rect(rect),  # type: ignore
        surface,
        int(padx),
        int(pady),
        do_fill,
        do_stretchx,
        do_stretchy,
        fill_color,
        int(border_radius),
        int(alpha),
        smoothscale,
        int(ninepatch),
    )
