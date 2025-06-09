import pygame
import typing
from mili import typing as _typing
from mili.mili import MILI as _MILI
from mili._utils._interaction import InteractionCursor
from mili import icon as _icon
from mili import error as _error
from mili import animation as _anim
from mili import _coreutils


class GenericApp:
    def __init__(
        self,
        window: pygame.Window,
        target_framerate: int = 60,
        clear_color: pygame.typing.ColorLike | None = 0,
        start_style: _typing.ElementStyleLike | None = None,
        use_global_mouse: bool = False,
    ):
        self.window = window
        self.clock = pygame.Clock()
        self.target_framerate: int = target_framerate
        self.mili = _MILI(self.window.get_surface(), use_global_mouse)
        self.clear_color: pygame.typing.ColorLike | None = clear_color
        self.start_style: _typing.ElementStyleLike | None = start_style
        self.delta_time: float = 0
        self.running = True

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
        while self.running:
            self.mili.start(self.start_style, window_position=self.window.position)
            for event in pygame.event.get():
                if event.type == pygame.WINDOWCLOSE and event.window == self.window:
                    self.quit()
                    return
                else:
                    self.event(event)

            if self.clear_color is not None:
                self.window.get_surface().fill(self.clear_color)
            self.update()
            self.ui()
            self.mili.update_draw()
            self.post_draw()
            self.window.flip()
            self.delta_time = self.clock.tick(self.target_framerate) / 1000


def _titlebar_button_style(
    style, icon, bg_hover=(60, 60, 60)
) -> _typing._UIAppButtonStyleLike:
    if style is None:
        style = {}
    bg = style.get("bg_color", {})
    alpha = style.get("alpha", {})
    return {
        "bg_color": {
            "default": bg.get("default", (40, 40, 40)),
            "hover": bg.get("hover", bg_hover),
            "press": bg.get("press", (32, 32, 32)),
        },
        "icon": style.get("icon", icon),
        "alpha": {
            "default": alpha.get("default", 180),
            "hover": alpha.get("hover", 255),
            "press": alpha.get("press", 150),
        },
    }


class UIApp:
    def __init__(
        self,
        window: pygame.Window,
        style: _typing.UIAppStyleLike | dict | None = None,
        use_global_mouse: bool = False,
    ):
        pygame.init()
        self.window = window
        if style is None:
            style = {}
        self.style: _typing.UIAppStyleLike = {
            "start_style": style.get("start_style", {}),
            "target_framerate": style.get("target_framerate", 60),
            "clear_color": style.get("clear_color", (22, 22, 22)),
            "window_outline": style.get("window_outline", 1),
            "window_icon": style.get("window_icon", None),
            "outline_color": style.get("outline_color", (40, 40, 40)),
            "fullscreen_key": style.get("fullscreen_key", pygame.K_F11),
            "titlebar_show_title": style.get("titlebar_show_title", True),
            "title_style": style.get(
                "title_style", {"size": 18, "color": (180, 180, 180)}
            ),
            "titlebar_color": style.get("titlebar_color", (40, 40, 40)),
            "use_appdata_folder": style.get("use_appdata_folder", True),
            "minimize_button": _titlebar_button_style(
                style.get("minimize_button", {}),
                _icon.lazy_colored("iconify", "minimize", "material-symbols", "white"),
            ),
            "maximize_button": _titlebar_button_style(
                style.get("maximize_button", {}),
                _icon.lazy_colored(
                    "iconify", "square-rounded", "material-symbols", "white"
                ),
            ),
            "close_button": _titlebar_button_style(
                style.get("close_button", {}),
                _icon.lazy_colored("iconify", "close", "material-symbols", "white"),
                "red",
            ),
        }
        self.clock = pygame.Clock()
        self.delta_time: float = 0
        self.mili = _MILI(self.window.get_surface(), use_global_mouse)
        self.win_borders = CustomWindowBorders(self.window)
        self.win_behavior = CustomWindowBehavior(
            self.window, self.win_borders, pygame.display.get_desktop_sizes()[0]
        )
        self.adaptive_scaler = AdaptiveUIScaler(self.window, self.window.size)
        self.scale = self.adaptive_scaler.scale
        self.running = True
        InteractionCursor.setup(update_id="cursor")
        _coreutils._number_mods["s"] = self.adaptive_scaler.scale
        if self.style["use_appdata_folder"]:
            import os

            if not os.path.exists("appdata"):
                os.mkdir("appdata")
            _icon.setup("appdata", "white")

    def update(self): ...

    def ui(self): ...

    def ui_tbar_pretitle(self): ...
    def ui_tbar_posttitle(self): ...
    def ui_tbar_prebuttons(self): ...

    def event(self, event: pygame.Event): ...

    def quit(self):
        self.on_quit()
        pygame.quit()
        raise SystemExit

    def on_quit(self): ...

    def post_draw(self): ...

    def run(self):
        while self.running:
            style = self.style["start_style"]
            if self.window.borderless:
                style = {"pad": 0, "spacing": 0}
            else:
                self.win_borders.active = False
            self.mili.start(style, window_position=self.window.position)
            for event in pygame.event.get():
                if event.type == pygame.WINDOWCLOSE and event.window == self.window:
                    self.quit()
                    return
                else:
                    self.event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == self.style["fullscreen_key"]:
                        self.win_behavior.toggle_fullscreen()
                    if event.key == pygame.K_ESCAPE and self.win_behavior.fullscreen:
                        self.win_behavior.fullscreen_off()

            ccolor = self.style["clear_color"]
            self.win_borders.update()
            self.adaptive_scaler.update()
            _anim.update_all()
            self.update()
            outline, outline_col = (
                self.style["window_outline"],
                self.style["outline_color"],
            )
            if self.window.borderless and not self.win_behavior.fullscreen:
                wsize = self.window.size
                h = self.win_borders.titlebar_height
                with self.mili.begin(
                    (0, 0, wsize[0], h),
                    {"axis": "x", "pad": 0, "spacing": 0, "z": 9999},
                ):
                    self.mili.rect(
                        {"color": self.style["titlebar_color"], "border_radius": 0}
                    )
                    self.ui_tbar_pretitle()
                    if (icon := self.style["window_icon"]) is not None:
                        self.mili.image_element(icon, {"pad": 1}, (0, 0, h, h))
                    if self.style["titlebar_show_title"]:
                        self.mili.text_element(
                            self.window.title,
                            self.style["title_style"] | {"growy": False, "growx": True},
                            (0, 0, 0, h),
                        )
                    self.ui_tbar_posttitle()
                    self.mili.element(None, {"fillx": True})
                    self.ui_tbar_prebuttons()
                    for name, button in [
                        ("minimize", self.style["minimize_button"]),
                        ("maximize", self.style["maximize_button"]),
                        ("close", self.style["close_button"]),
                    ]:
                        if button is None:
                            continue
                        surf = _icon._get_icon(button["icon"])
                        if surf is None:
                            continue
                        with self.mili.element((0, 0, h, h)) as btn:
                            bg = _coreutils._get_conditional_color(
                                btn, button["bg_color"]
                            )
                            alpha = _coreutils._get_conditional_color(
                                btn, button["alpha"]
                            )
                            self.mili.rect({"color": bg, "border_radius": 0})
                            self.mili.image(surf, {"alpha": alpha, "smoothscale": True})
                            if btn.left_clicked and self.win_borders.can_interact():
                                match name:
                                    case "close":
                                        self.quit()
                                    case "maximize":
                                        self.win_behavior.toggle_maximize()
                                    case "minimize":
                                        self.win_behavior.minimize()
                with self.mili.begin(
                    (0, 0, wsize[0], wsize[1] - h), self.style["start_style"]
                ):
                    if ccolor is not None:
                        self.mili.rect({"color": ccolor, "border_radius": 0})
                    if outline:
                        self.mili.rect(
                            {
                                "color": outline_col,
                                "outline": 1,
                                "draw_above": True,
                                "border_radius": 0,
                            }
                        )
                    try:
                        self.mili.id_checkpoint(10)
                    except _error.MILIStatusError:
                        ...
                    self.ui()
            else:
                if ccolor is not None:
                    self.mili.rect({"color": ccolor, "border_radius": 0})
                if outline:
                    self.mili.rect(
                        {
                            "color": outline_col,
                            "outline": 1,
                            "draw_above": True,
                            "border_radius": 0,
                        }
                    )
                try:
                    self.mili.id_checkpoint(10)
                except _error.MILIStatusError:
                    ...
                self.ui()
            InteractionCursor.apply()
            self.mili.update_draw()
            self.post_draw()
            self.window.flip()
            self.delta_time = self.clock.tick(self.style["target_framerate"]) / 1000


class _HasSizeAttr(typing.Protocol):
    size: typing.Sequence[float]


class AdaptiveUIScaler:
    def __init__(
        self,
        window: pygame.Window | _HasSizeAttr,
        relative_size: typing.Sequence[float],
        scale_clamp: tuple[float | None, float | None] | None = (0.2, 1.2),
        width_weight: float = 1,
        height_weight: float = 1,
        min_value: float | None = 1,
        int_func: typing.Callable[[float], int] = int,
    ):
        self.window = window
        self.relative_size = pygame.Vector2(relative_size)
        self.scale_clamp = scale_clamp
        self.width_weight = width_weight
        self.height_weight = height_weight
        self.min_value = min_value
        self.int_func = int_func
        self.extra_scale: float = 1
        self._mult = 1

    def update(self):
        size = self.window.size
        xmult = size[0] / self.relative_size.x
        ymult = size[1] / self.relative_size.y
        mult = (xmult * self.width_weight + ymult * self.height_weight) / (
            self.width_weight + self.height_weight
        )
        if self.scale_clamp is not None:
            clampmin, clampmax = self.scale_clamp
            if clampmin is not None and mult < clampmin:
                mult = clampmin
            if clampmax is not None and mult > clampmax:
                mult = clampmax
        self._mult = mult

    def scale(self, value: float, min_override: float | None = None) -> int:
        min_value = self.min_value
        if min_override is not None:
            min_value = min_override
        scaled = value * self._mult * self.extra_scale
        if min_value is not None and scaled < min_value:
            scaled = min_value
        return self.int_func(scaled)

    def scalef(self, value: float, min_override: float | None = None) -> float:
        min_value = self.min_value
        if min_override is not None:
            min_value = min_override
        scaled = value * self._mult * self.extra_scale
        if min_value is not None and scaled < min_value:
            scaled = min_value
        return scaled


class CustomWindowBorders:
    def __init__(
        self,
        window: pygame.Window,
        border_size: int = 3,
        corner_size: int = 6,
        titlebar_height: int = 25,
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
        constraint_rect: pygame.typing.RectLike | None = None,
        *,
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
        self.constraint_rect = (
            pygame.Rect(constraint_rect) if constraint_rect is not None else None
        )
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
        self.active = True
        self.active_drag = True
        self.active_resize = True

        self._double_click_cooldown = 100
        self._toggle_maximize_func: typing.Callable | None = None
        self._left_pressed = False
        self._press_count = 0
        self._press_time = 0
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

    def can_interact(self):
        return self.window.focused and self.cumulative_relative.length() == 0

    def mouse_changed(self):
        self._press_rel = pygame.mouse.get_pos()
        self._press_global = pygame.Vector2(pygame.mouse.get_pos(True))
        self._start_val = pygame.Vector2(
            self.window.position if self.dragging else self.window.size
        )

    def update(self) -> bool:
        if not self.window.focused or not self.active:
            InteractionCursor._active = True
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
            else:
                handle._rect = pygame.Rect()

        if self.change_cursor:
            next_cursor = None
            if not self.resizing and self.active_drag:
                if tbar_rect.h > 0 and (tbar_rect.collidepoint(mpos) or self.dragging):
                    next_cursor = pygame.SYSTEM_CURSOR_HAND
                    modified_cursor = True
            if not self.dragging and self.active_resize:
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
                        next_cursor = None
                        break
            if next_cursor is not None:
                pygame.mouse.set_cursor(next_cursor)

        if self.active_drag:
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
                self.cumulative_relative = pygame.Vector2()

        if self.resizing or tbar_rect.h <= 0:
            InteractionCursor._active = not modified_cursor
            return modified_cursor

        if self.active_drag:
            if just and tbar_rect.collidepoint(mpos):
                if self._press_count == 0:
                    self._press_count += 1
                    self._press_time = pygame.time.get_ticks()
                else:
                    if (
                        pygame.time.get_ticks() - self._press_time
                        <= self._double_click_cooldown
                        and self._toggle_maximize_func is not None
                    ):
                        self._toggle_maximize_func()
                    self._press_count = 0
                    self._press_time = 0
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
                    new_position = self._start_val + (gmpos - self._press_global)
                    self.window.position = self._constrain_position(new_position)
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
                self.cumulative_relative = pygame.Vector2()
        InteractionCursor._active = not modified_cursor
        return modified_cursor

    def _constrain_position(self, pos: pygame.Vector2):
        if self.constraint_rect is None:
            return pos
        sx, sy = self.window.size
        return pygame.Vector2(
            pygame.math.clamp(
                pos.x,
                self.constraint_rect.x,
                max(self.constraint_rect.right - sx, self.constraint_rect.x),
            ),
            pygame.math.clamp(
                pos.y,
                self.constraint_rect.y,
                max(self.constraint_rect.bottom - sy, self.constraint_rect.y),
            ),
        )

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
                if self._parent.ratio_axis == "y":
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
            if self._parent.constraint_rect is not None:
                newsize = pygame.Vector2(
                    pygame.math.clamp(newsize.x, 0, self._parent.constraint_rect.w),
                    pygame.math.clamp(newsize.y, 0, self._parent.constraint_rect.h),
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
                self._parent.window.position = self._parent._constrain_position(
                    self._parent._resize_winpos - posrel
                )
            callback = self._parent._callbacks["resize"]["during"]
            if callback is not None:
                callback()


_SNAP_POSITIONS = typing.Literal[
    "top",
    "topleft",
    "left",
    "bottomleft",
    "bottom",
    "bottomright",
    "right",
    "topright",
    "top",
    "height",
]


class CustomWindowBehavior:
    def __init__(
        self,
        window: pygame.Window,
        borders: CustomWindowBorders,
        display_size: typing.Sequence[float],
        taskbar_size: int = 30,
        taskbar_position: typing.Literal["bottom", "left", "right", "top"] = "bottom",
        double_click_cooldown: int | None = 300,
        snap_border_size=10,
        snap_corner_size=30,
        allow_snap: bool = True,
        before_maximize_data: tuple[tuple[int, int], tuple[int, int]] | None = None,
    ):
        self._taskbar_size = taskbar_size
        self._taskbar_position = taskbar_position
        self._display_size = display_size
        self.window = window
        self.borders = borders
        self.allow_snap = allow_snap
        self._maximized = False
        self._before_maximize_data = before_maximize_data
        self._minimized = False
        self._snapped = False
        self._snapped_name = None
        self._snapped_h = False
        self._snap_preview = False
        self._before_snap_data = None
        self._before_snap_preview_size = None
        self._maximize_snap_time = pygame.time.get_ticks()
        self._maximize_time = pygame.time.get_ticks()
        self._fullscreen = False
        self.borders._callbacks["move"]["during"] = self._during_move
        self.borders._callbacks["resize"]["during"] = self._during_resize
        self.borders._callbacks["move"]["end"] = self._end_move
        self.borders._callbacks["resize"]["end"] = self._end_resize
        self.double_click_cooldown = double_click_cooldown
        self.snap_border_size = snap_border_size
        self.snap_corner_size = snap_corner_size
        self._rebuild()

    @property
    def fullscreen(self):
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, value):
        if value:
            self.fullscreen_on()
        else:
            self.fullscreen_off()

    @property
    def snapped(self) -> None | str:
        if not self._snapped:
            if self._snapped_name in ["top", "bottom"]:
                return self._snapped_name
            return None
        if self._snapped_h:
            return "height"
        return self._snapped_name

    @snapped.setter
    def snapped(self, value: _SNAP_POSITIONS | None):
        if value is None:
            self.unsnap()
            return
        else:
            self.snap(value)

    @property
    def before_maximized_data(self):
        return self._before_maximize_data

    @property
    def maximized(self):
        return self._maximized

    @maximized.setter
    def maximized(self, v):
        if v:
            self.maximize()
        else:
            self.unmaximize()

    @property
    def minimized(self):
        return self._minimized

    @minimized.setter
    def minimized(self, v):
        if v:
            self.minimize()
        else:
            self.unminimize()

    @property
    def display_size(self):
        return self._display_size

    @display_size.setter
    def display_size(self, value):
        self._display_size = value
        self._rebuild()

    @property
    def taskbar_size(self):
        return self._taskbar_size

    @taskbar_size.setter
    def taskbar_size(self, value):
        self._taskbar_size = value
        self._rebuild()

    @property
    def taskbar_position(self):
        return self._taskbar_position

    @taskbar_position.setter
    def taskbar_position(self, value):
        self._taskbar_position = value
        self._rebuild()

    @property
    def double_click_cooldown(self):
        return (
            self.borders._double_click_cooldown
            if self.borders._toggle_maximize_func is not None
            else None
        )

    @double_click_cooldown.setter
    def double_click_cooldown(self, value):
        if value is None:
            self.borders._toggle_maximize_func = None
        else:
            self.borders._double_click_cooldown = value
            self.borders._toggle_maximize_func = self.toggle_maximize

    def _rebuild(self):
        r = None
        match self._taskbar_position:
            case "left":
                r = pygame.Rect(
                    self._taskbar_size,
                    0,
                    self._display_size[0] - self._taskbar_size,
                    self._display_size[1],
                )
            case "right":
                r = pygame.Rect(
                    0,
                    0,
                    self._display_size[0] - self._taskbar_size,
                    self._display_size[1],
                )
            case "top":
                r = pygame.Rect(
                    0,
                    self._taskbar_size,
                    self._display_size[0],
                    self._display_size[1] - self._taskbar_size,
                )
            case "bottom":
                r = pygame.Rect(
                    0,
                    0,
                    self._display_size[0],
                    self._display_size[1] - self._taskbar_size,
                )
        if r is None:
            r = pygame.Rect()
        self._display_rect = r
        cs = self.snap_corner_size
        bs = self.snap_border_size
        self._snap_areas = {
            "topleft": pygame.Rect(r.left, r.top, cs, cs),
            "left": pygame.Rect(r.left, r.top + cs, bs, r.h - cs * 2),
            "bottomleft": pygame.Rect(r.left, r.top + r.h - cs, cs, cs),
            "bottom": pygame.Rect(r.left + cs, r.top + r.h - cs, r.w - cs * 2, bs),
            "bottomright": pygame.Rect(r.left + r.w - cs, r.top + r.h - cs, cs, cs),
            "right": pygame.Rect(r.left + r.w - bs, r.top + cs, bs, r.h - cs * 2),
            "topright": pygame.Rect(r.left + r.w - cs, r.top, cs, cs),
            "top": pygame.Rect(r.left + cs, r.top, r.w - cs * 2, bs),
        }
        self._snap_rects = {
            "topleft": pygame.Rect(r.left, r.top, r.w / 2, r.h / 2),
            "left": pygame.Rect(r.left, r.top, r.w / 2, r.h),
            "bottomleft": pygame.Rect(r.left, r.top + r.h / 2, r.w / 2, r.h / 2),
            "bottom": pygame.Rect(r.left, r.top, r.w, r.h),
            "bottomright": pygame.Rect(
                r.left + r.w / 2, r.top + r.h / 2, r.w / 2, r.h / 2
            ),
            "right": pygame.Rect(r.left + r.w / 2, r.top, r.w / 2, r.h),
            "topright": pygame.Rect(r.left + r.w / 2, r.top, r.w / 2, r.h / 2),
            "top": pygame.Rect(r.left, r.top, r.w, r.h),
        }

    def center(self):
        w, h = self.window.size
        self.window.position = (
            self._display_rect.w / 2 - w / 2,
            self._display_rect.h / 2 - h / 2,
        )

    def snap(self, position: _SNAP_POSITIONS):
        if not self._snapped:
            self._before_snap_data = self.window.size, self.window.position
        if position == "height":
            self.window.position = (self.window.position[0], self._display_rect.top)
            self.window.size = (self.window.size[0], self._display_rect.h)
            self._snapped_h = True
            self._snapped = True
            return
        self._snapped_name = position
        if position in ["top", "bottom"]:
            self.maximize()
        else:
            rect = self._snap_rects[position]
            self.window.size, self.window.position = rect.size, rect.topleft
            self._snapped = True

    def fullscreen_on(self):
        if self._fullscreen:
            return
        self._maximized = self._snapped = self._snap_preview = self._snapped_h = False
        self._snapped_name = None
        self._before_maximize_data = self.window.size, self.window.position
        self.window.position = (0, 0)
        self.window.size = self._display_size
        self.borders.active = False
        self._fullscreen = True

    def fullscreen_off(self):
        if not self._fullscreen or self._before_maximize_data is None:
            return
        self._fullscreen = False
        self.borders.active = True
        self.window.size, self.window.position = self._before_maximize_data

    def toggle_fullscreen(self):
        if self._fullscreen:
            self.fullscreen_off()
        else:
            self.fullscreen_on()

    def minimize(self):
        if self._minimized:
            return
        self.window.minimize()
        self._minimized = True

    def unminimize(self):
        if not self._minimized:
            return
        self.window.restore()
        self.window.focus()
        self._minimized = True

    def toggle_minimize(self):
        if self._minimized:
            self.unminimize()
        else:
            self.minimize()

    def maximize(self):
        if self._maximized:
            return
        self._maximized = True
        self._before_maximize_data = self.window.size, self.window.position
        self.window.size, self.window.position = (
            self._display_rect.size,
            self._display_rect.topleft,
        )
        self.borders.resizing = self.borders.dragging = False
        self._snapped = self._snapped_h = False
        self._snapped_name = None
        self._maximize_snap_time = self._maximize_time = pygame.time.get_ticks()
        self.borders.active_resize = False

    def unmaximize(self):
        if not self._maximized or self._before_maximize_data is None:
            return
        self._maximized = self._snapped = self._snapped_h = False
        self._snapped_name = None
        self.window.size, self.window.position = self._before_maximize_data
        self.borders.resizing = self.borders.dragging = False
        self.borders.active_resize = True
        self._maximize_snap_time = self._maximize_time = pygame.time.get_ticks()

    def unsnap(self):
        if not self._snapped or self._before_snap_data is None:
            return
        self._snapped = False
        self._snapped_name = None
        if self._snapped_h:
            self.window.size = (self.window.size[0], self._before_snap_data[0][1])
            self.window.position = (
                self.window.position[0],
                self._before_snap_data[1][1],
            )
        else:
            self.window.size, self.window.position = self._before_snap_data
        self._snapped_h = False
        self._maximize_snap_time = pygame.time.get_ticks()

    def toggle_maximize(self):
        self._snapped = self._snapped_h = False
        self._snapped_name = None
        if self._maximized:
            self.unmaximize()
        else:
            self.maximize()

    def _during_resize(self):
        if self.borders.cumulative_relative.length() == 0:
            return
        if self._maximized and self.borders.relative.length() != 0:
            self.unmaximize()
            return
        if not self.allow_snap:
            return
        mouse = pygame.mouse.get_pos(True)
        collided = False
        for name in ["top", "bottom"]:
            area = self._snap_areas[name]
            if area.collidepoint(mouse):
                collided = True
                if not self._snap_preview:
                    self._before_snap_preview_size = self.window.size
                    self._snap_preview = True
                else:
                    self.window.size = (self.window.size[0], self._snap_rects[name].h)
                break
        if (
            not collided
            and self._snap_preview
            and self._before_snap_preview_size is not None
        ):
            self._snap_preview = False
            self.window.size = (self.window.size[0], self._before_snap_preview_size[1])

    def _end_resize(self):
        self._snap_preview = False
        if (
            not self.allow_snap
            or self._before_snap_preview_size is None
            or pygame.time.get_ticks() - self._maximize_time < 100
        ):
            return
        mouse = pygame.mouse.get_pos(True)
        for name in ["top", "bottom"]:
            if self._snap_areas[name].collidepoint(mouse):
                if not self._snapped:
                    self._before_snap_data = (
                        self._before_snap_preview_size,
                        self.window.position,
                    )
                    self._snapped = True
                    self._snapped_h = True
                self.window.size = (self.window.size[0], self._display_rect.h)
                self.window.position = (self.window.position[0], self._display_rect.top)
                self._maximize_snap_time = pygame.time.get_ticks()
                break

    def _during_move(self):
        if self.borders.cumulative_relative.length() == 0:
            return
        if self._maximized and self._before_maximize_data is not None:
            self._maximized = False
            self.window.size, self.window.position = self._before_maximize_data
            pygame.mouse.set_pos(
                (self.window.size[0] / 2, self.borders.titlebar_height / 2)
            )
            self.borders.mouse_changed()
            self._maximize_snap_time = self._maximize_time = pygame.time.get_ticks()
            self.borders.active_resize = True
            return
        if self._snapped:
            self.unsnap()
            pygame.mouse.set_pos(
                (self.window.size[0] / 2, self.borders.titlebar_height / 2)
            )
            self.borders.mouse_changed()
            self._maximize_snap_time = pygame.time.get_ticks()
            return
        if (
            self.allow_snap
            and pygame.time.get_ticks() - self._maximize_snap_time >= 100
        ):
            mouse = pygame.mouse.get_pos(True)
            collided = False
            for name, area in self._snap_areas.items():
                if area.collidepoint(mouse):
                    collided = True
                    if not self._snap_preview:
                        self._before_snap_preview_size = self.window.size
                        self._snap_preview = True
                    else:
                        self.window.size = self._snap_rects[name].size
                    break
            if (
                not collided
                and self._snap_preview
                and self._before_snap_preview_size is not None
            ):
                self._snap_preview = False
                self.window.size = self._before_snap_preview_size

    def _end_move(self):
        if self.borders.cumulative_relative.length() == 0:
            return
        self._snap_preview = False
        if (
            not self.allow_snap
            or self._before_snap_preview_size is None
            or pygame.time.get_ticks() - self._maximize_time < 100
        ):
            return
        mouse = pygame.mouse.get_pos(True)
        for name, area in self._snap_areas.items():
            if area.collidepoint(mouse):
                self._snapped_name = name
                if name in ["top", "bottom"]:
                    if not self._maximized:
                        self._maximized = True
                        self._before_maximize_data = (
                            self._before_snap_preview_size,
                            self.window.position,
                        )
                        self.window.size, self.window.position = (
                            self._display_rect.size,
                            self._display_rect.topleft,
                        )
                        self.borders.resizing = self.borders.dragging = False
                        self._snapped = self._snapped_h = False
                        self._maximize_snap_time = self._maximize_time = (
                            pygame.time.get_ticks()
                        )
                        self.borders.active_resize = False
                else:
                    if not self._snapped:
                        self._before_snap_data = (
                            self._before_snap_preview_size,
                            self.window.position,
                        )
                        self._snapped = True
                        self._snapped_h = False
                        self._maximize_snap_time = pygame.time.get_ticks()
                        rect = self._snap_rects[name]
                        self.window.size = rect.size
                        self.window.position = rect.topleft
                break
