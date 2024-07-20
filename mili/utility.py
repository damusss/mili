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
    "GenericApp",
    "percentage",
    "gray",
    "indent",
)


class Selectable:
    def __init__(self, selected: bool = False):
        self.selected: bool = selected

    def update(
        self,
        element: _data.Interaction | _data.ElementData,
        selectable_group: typing.Sequence["Selectable"] = None,
        can_deselect_group: bool = True,
    ) -> _data.Interaction | _data.ElementData:
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
        self.changed = False
        self._clamp_x = None
        self._clamp_y = None

    def update(
        self,
        element: _data.Interaction | _data.ElementData,
        clamp_x: tuple[int, int] | None = None,
        clamp_y: tuple[int, int] | None = None,
    ) -> _data.Interaction | _data.ElementData:
        if element.left_pressed:
            rel = _core._globalctx._mouse_rel.copy()
            if self.lock_x:
                rel.x = 0
            if self.lock_y:
                rel.y = 0
            prev = self.position.copy()
            self.position += rel
            if clamp_x is not None:
                self.position.x = pygame.math.clamp(self.position.x, *clamp_x)
            self._clamp_x = clamp_x
            if clamp_y is not None:
                self.position.y = pygame.math.clamp(self.position.y, *clamp_y)
            self._clamp_y = clamp_y
            if self.position != prev:
                self.changed = True
            self.rel = rel.copy()
        return element

    def clamp(
        self,
        clamp_x: tuple[int, int] | None = None,
        clamp_y: tuple[int, int] | None = None,
        previous_clamps: bool = True,
    ):
        if previous_clamps:
            clamp_x = self._clamp_x
            clamp_y = self._clamp_y
        if clamp_x is not None:
            self.position.x = pygame.math.clamp(self.position.x, *clamp_x)
        if clamp_y is not None:
            self.position.y = pygame.math.clamp(self.position.y, *clamp_y)


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
        if not isinstance(element_data, _data.ElementData):
            raise TypeError("element_data argument must be of type _data.ElementData")
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

    def update(self, element: _data.ElementData) -> _data.ElementData:
        if element is None:
            return element
        rectsize = element.rect.h if self.axis == "x" else element.rect.w
        self.size = (
            (element.rect.w if self.axis == "x" else element.rect.h)
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
        return element

    def update_handle(
        self, element: _data.ElementData | _data.Interaction
    ) -> _data.ElementData | _data.Interaction:
        if element is None:
            return element
        self.handle_dragger.update(
            element,
            clamp_x=(0, self.size - self.handle_size) if self.axis == "x" else None,
            clamp_y=(0, self.size - self.handle_size) if self.axis == "y" else None,
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


def percentage(percentage: float, value: float) -> float:
    return (percentage * value) / 100


def gray(
    value: int | typing.Any,
) -> tuple[int | typing.Any, int | typing.Any, int | typing.Any]:
    return (value, value, value)


def indent(*args, **kwargs): ...
