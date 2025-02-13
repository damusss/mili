import pygame
import typing
from mili import typing as _typing
from mili.mili import MILI as _MILI


class GenericApp:
    def __init__(
        self,
        window: pygame.Window,
        target_framerate: int = 60,
        clear_color: pygame.typing.ColorLike = 0,
        start_style: _typing.ElementStyleLike | None = None,
        use_global_mouse: bool = False,
    ):
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
