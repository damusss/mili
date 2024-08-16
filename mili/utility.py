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
    "percentage",
    "indent",
)


class Selectable:
    def __init__(self, selected: bool = False):
        self.selected: bool = selected

    def update[IT: _data.Interaction | _data.ElementData](
        self,
        element: IT,
        selectable_group: typing.Sequence["Selectable"] | None = None,
        can_deselect_group: bool = True,
    ) -> IT:
        if selectable_group is None:
            selectable_group = []
        interaction = element
        if isinstance(element, _data.ElementData):
            interaction = element.interaction
        if interaction.left_just_released:
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
    ):
        if position is None:
            position = (0, 0)
        self.position = pygame.Vector2(position)
        self.rel = pygame.Vector2()
        self.lock_x = lock_x
        self.lock_y = lock_y
        self.changed: bool = False
        self.clamp_x: tuple[int, int] | None = None
        self.clamp_y: tuple[int, int] | None = None
        self.style: _typing.ElementStyleLike = {"ignore_grid": True}
        self._before_update_pos = pygame.Vector2()

    def update[IT: _data.Interaction | _data.ElementData](
        self,
        element: IT,
    ) -> IT:
        self.changed = False
        self._before_update_pos = self.position.copy()
        if element.left_pressed:
            rel = _core._globalctx._mouse_rel.copy()
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
        clamp_x: tuple[int, int] | None = None,
        clamp_y: tuple[int, int] | None = None,
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
    def __init__(self, window: pygame.Window):
        if not pygame.get_init():
            raise _error.MILIStatusError(
                "pygame.init() must be called before creating a generic app"
            )
        self.window = window
        self.clock = pygame.Clock()
        self.target_framerate: int = 60
        self.mili = _MILI(self.window.get_surface())
        self.clear_color: _typing.ColorLike = 0
        self.start_style: _typing.ElementStyleLike | None = None
        self.delta_time: float = 0

    def update(self): ...

    def ui(self): ...

    def event(self, event: pygame.Event): ...

    def quit(self):
        self.on_quit()
        pygame.quit()
        raise SystemExit

    def on_quit(self): ...

    def run(self):
        while True:
            self.mili.start(self.start_style)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.event(event)

            self.window.get_surface().fill(self.clear_color)
            self.update()
            self.ui()
            self.mili.update_draw()
            self.window.flip()
            self.delta_time = self.clock.tick(self.target_framerate) / 1000


class Scroll:
    def __init__(self):
        self.scroll_offset: pygame.Vector2 = pygame.Vector2()
        self._element_data: _data.ElementData = None

    def update(self, element_data: _data.ElementData) -> _data.ElementData:
        if isinstance(element_data, _data.Interaction):
            raise _error.MILIError(
                "Scroll.update does not allow Interaction objects. Set get_data=True to get the correct ElementData object"
            )
        self._element_data = element_data
        self.clamp()
        return element_data

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
    ):
        self._scroll = scroll
        self.axis = axis
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

    def update(self, element_data: _data.ElementData) -> _data.ElementData:
        if isinstance(element_data, _data.Interaction):
            raise _error.MILIError(
                "Scrollbar.update does not allow Interaction objects. Set get_data=True to get the correct ElementData object"
            )
        rectsize = element_data.rect.h if self.axis == "x" else element_data.rect.w
        self.size = (
            (element_data.rect.w if self.axis == "x" else element_data.rect.h)
            - self.padding * 2
            - self.size_reduce
        )
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
        self.handle_size = self._scroll.get_handle_size(self.size, self.axis)
        return element_data

    def update_handle[IT: _data.ElementData | _data.Interaction](
        self, element: IT
    ) -> IT:
        self.handle_dragger.update(
            element,
        )
        self.handle_dragger.clamp(
            clamp_x=(0, self.size - self.handle_size) if self.axis == "x" else None,
            clamp_y=(0, self.size - self.handle_size) if self.axis == "y" else None,
            previous_clamps=False,
        )
        if self.handle_dragger.changed:
            self._scroll.set_scroll_from_rel_handle_pos(
                self.size,
                (
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
    ):
        self.lock_x = lock_x
        self.lock_y = lock_y
        self.handle_size = handle_size
        self.strict_borders = strict_borders
        self._area_data: _data.ElementData | None = None
        self.handle_dragger: Dragger = Dragger()
        self.moved: bool = False

        self.area_style: _typing.ElementStyleLike = {"clip_draw": False}
        self.handle_style: _typing.ElementStyleLike = {"ignore_grid": True}
        self.handle_rect: pygame.Rect = pygame.Rect()

    @classmethod
    def from_axis(
        cls,
        axis: typing.Literal["x", "y"],
        handle_size: typing.Sequence[float],
        strict_borders: bool = False,
    ):
        return cls(axis == "y", axis == "x", handle_size, strict_borders)

    def update_area(self, element_data: _data.ElementData) -> _data.ElementData:
        if isinstance(element_data, _data.Interaction):
            raise _error.MILIError(
                "Slider.update_area does not allow Interaction objects. Set get_data=True to get the correct ElementData object"
            )
        previous = self.value
        self._area_data = element_data
        if self.value != previous:
            self.value = previous
        return element_data

    def update_handle[IT: _data.ElementData | _data.Interaction](
        self, element: IT
    ) -> IT:
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
            self.handle_size[0] / 2 if self.strict_borders else 0,
            self.handle_size[1] / 2 if self.strict_borders else 0,
        )
        self.handle_dragger.update(
            element,
        )
        self.handle_dragger.clamp(
            (0 + clamp_padx, self._area_data.rect.w - clamp_padx),
            (0 + clamp_pady, self._area_data.rect.h - clamp_pady),
            False,
        )
        if self._area_data.rect.w < self.handle_size[0]:
            self.handle_dragger.position.x = (
                self.handle_size[0] / 2 if self.strict_borders else 0
            )
        if self._area_data.rect.h < self.handle_size[1]:
            self.handle_dragger.position.y = (
                self.handle_size[1] / 2 if self.strict_borders else 0
            )
        self.handle_rect = pygame.Rect(
            (
                self.handle_dragger.position.x - self.handle_size[0] / 2,
                self.handle_dragger.position.y - self.handle_size[1] / 2,
            ),
            self.handle_size,
        )
        self.moved = self.handle_dragger.changed
        return element

    @property
    def value(self) -> pygame.Vector2:
        if self._area_data is None:
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
    def value(self, v: typing.Sequence[float]):
        if self._area_data is None:
            return
        if not self.strict_borders:
            if not self.lock_x:
                self.handle_dragger.position.x = v[0] * self._area_data.rect.w
            if not self.lock_y:
                self.handle_dragger.position.y = v[1] * self._area_data.rect.h
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
        self.valuey = pygame.Vector2(self.value.x, v)


class InteractionSound:
    def __init__(
        self,
        hover: pygame.mixer.Sound | None = None,
        unhover: pygame.mixer.Sound | None = None,
        press: pygame.mixer.Sound | None = None,
        release: pygame.mixer.Sound | None = None,
        button: int = pygame.BUTTON_LEFT,
    ):
        self.hover_sound = hover
        self.unhover_sound = unhover
        self.press_sound = press
        self.release_sound = release
        self.button = button

    def play[IT: _data.Interaction | _data.ElementData](
        self,
        interaction: IT,
        channel: pygame.Channel | None = None,
        maxtime: int = 0,
        fade_ms: int = 0,
    ) -> IT:
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


def percentage(percentage: float, value: float) -> float:
    return (percentage * value) / 100


def indent(*args, **kwargs): ...
