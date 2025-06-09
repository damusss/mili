import pygame
import typing
from mili import _core
from mili import typing as _typing
from mili import _richtext
from mili import error as _error
from mili._utils._window import (
    GenericApp,
    UIApp,
    AdaptiveUIScaler,
    CustomWindowBorders,
    CustomWindowBehavior,
)
from mili._utils._interaction import (
    InteractionCursor,
    InteractionSound,
)
from mili._utils._prefabs import (
    Dragger,
    Selectable,
    Scroll,
    Scrollbar,
    Slider,
    DropMenu,
)
from mili._utils._entries import EntryLine, TextBox
from mili._utils._context_menu import ContextMenu

__all__ = (
    "Selectable",
    "Dragger",
    "Scroll",
    "Scrollbar",
    "Slider",
    "DropMenu",
    "EntryLine",
    "TextBox",
    "ContextMenu",
    "GenericApp",
    "UIApp",
    "AdaptiveUIScaler",
    "InteractionSound",
    "InteractionCursor",
    "CustomWindowBorders",
    "CustomWindowBehavior",
    "GIF",
    "percentage",
    "fit_image",
    "round_image_borders",
    "round_image",
)

_richtext.ScrollClass = Scroll
_richtext.ScrollbarClass = Scrollbar


class GIF:
    def __init__(
        self,
        frames: pygame.typing.SequenceLike[tuple[pygame.Surface, float]] | None,
        file: pygame.typing.FileLike | None = None,
    ):
        if file is not None:
            frames = pygame.image.load_animation(file)
        if frames is None:
            raise _error.MILIValueError(
                "You need to provide either the frames or the file, both cannot be None"
            )
        self.set_frames(frames)

    @property
    def frames(self):
        return self._frames

    @property
    def duration(self) -> float:
        return self._period

    @property
    def playback(self):
        return self._cur_time

    @playback.setter
    def playback(self, value):
        self._cur_time = value
        if self._cur_time >= self._period:
            self._cur_time = 0
        self._start = pygame.time.get_ticks() - self._cur_time
        self._last_time = self._start
        for i, delay in enumerate(self._delays):
            if delay > self._cur_time:
                self._frame = i
                self._next_delay = delay
                break
        else:
            self._frame = -1
            self._next_delay = float("inf")

    def set_frames(
        self, frames: pygame.typing.SequenceLike[tuple[pygame.Surface, float]]
    ):
        self.playing = True
        self._frames = frames
        if len(self._frames) <= 0:
            raise _error.MILIValueError("At least one frame is required for a GIF")
        self._start = pygame.time.get_ticks()
        self._frame = 0
        self._period = 0
        self._delays = []
        self._next_delay = self._frames[self._frame][1]
        self._last_time = self._start
        self._cur_time = self._start
        for frame in self._frames:
            self._period += frame[1]
            self._delays.append(self._period)

    def get_frame(self):
        if not self.playing:
            self._start = pygame.time.get_ticks() - self._cur_time
            return self._frames[self._frame][0]
        now = pygame.time.get_ticks()
        tot_elapsed = now - self._start
        if tot_elapsed > self._period:
            self._start += self._period
        time_in_range = tot_elapsed % self._period
        elapsed = now - self._last_time
        if elapsed >= (self._period - self._cur_time):
            for i, delay in enumerate(self._delays):
                if delay > time_in_range:
                    self._frame = i
                    self._next_delay = delay
                    break
            else:
                self._frame = -1
                self._next_delay = float("inf")
            self._last_time = now
            self._cur_time = time_in_range
            return self._frames[self._frame][0]
        if time_in_range >= self._next_delay:
            for i in range(self._frame, len(self._frames) - 1):
                delay = self._delays[i]
                if delay > time_in_range:
                    self._frame = i
                    self._next_delay = delay
                    break
            else:
                self._frame = -1
                self._next_delay = float("inf")
        self._last_time = now
        self._cur_time = time_in_range
        return self._frames[self._frame][0]

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    def sync(self, gif: "GIF"):
        self._start = gif._start
        self._last_time = gif._last_time
        self._cur_time = min(gif._cur_time, self._period)
        for i, delay in enumerate(self._delays):
            if delay > self._cur_time:
                self._frame = i
                self._next_delay = delay
                break
        else:
            self._frame = -1
            self._next_delay = float("inf")


def percentage(percentage: float, value: float) -> float:
    return (percentage * value) / 100


def fit_image(
    rect: pygame.typing.RectLike,
    surface: pygame.Surface,
    padx: int = 0,
    pady: int = 0,
    do_fill: bool = False,
    do_stretchx: bool = False,
    do_stretchy: bool = False,
    fill_color: pygame.typing.ColorLike | None = None,
    border_radius: float | pygame.typing.SequenceLike[float] = 0,
    alpha: int = 255,
    smoothscale: bool = False,
    ninepatch: int = 0,
    transforms: pygame.typing.SequenceLike[typing.Callable | pygame.typing.SequenceLike]
    | None = None,
    filters: pygame.typing.SequenceLike[typing.Callable | pygame.typing.SequenceLike]
    | None = None,
) -> pygame.Surface:
    return _core._coreutils._get_image(
        pygame.Rect(rect),
        surface,
        int(padx),
        int(pady),
        do_fill,
        do_stretchx,
        do_stretchy,
        fill_color,
        border_radius,
        int(alpha),
        smoothscale,
        int(ninepatch),
        transforms,
        filters,
    )


def round_image_borders(
    surface: pygame.Surface,
    border_radius: float | str | pygame.typing.SequenceLike[float | str],
):
    mindim = min(surface.size)
    mask_surf = pygame.Surface(surface.size, pygame.SRCALPHA)
    newdata = pygame.Surface(surface.size, pygame.SRCALPHA)
    newdata.blit(surface)
    if not isinstance(border_radius, float | int | str):
        pygame.draw.rect(
            mask_surf,
            (255, 255, 255, 255),
            (0, 0, surface.width, surface.height),
            0,
            0,
            *[int(_core._coreutils._abs_perc(br, mindim)) for br in border_radius],
        )
    else:
        pygame.draw.rect(
            mask_surf,
            (255, 255, 255, 255),
            (0, 0, surface.width, surface.height),
            0,
            int(_core._coreutils._abs_perc(border_radius, mindim)),
        )
    newdata.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return newdata


def round_image(
    surface: pygame.Surface,
    antialias: bool = True,
    allow_ellipse: bool = False,
):
    mindim = min(surface.size)
    mask_surf = pygame.Surface(surface.size, pygame.SRCALPHA)
    newdata = pygame.Surface(surface.size, pygame.SRCALPHA)
    newdata.blit(surface)
    if surface.width == surface.height or not allow_ellipse:
        (pygame.draw.aacircle if antialias else pygame.draw.circle)(
            mask_surf,
            (255,) * 4,
            (surface.width // 2, surface.height // 2),
            mindim // 2,
        )
    else:
        pygame.draw.ellipse(mask_surf, (255,) * 4, ((0, 0), surface.size))
    newdata.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return newdata


class _DictPushContextManager:
    def __init__(self, original: dict, override: dict):
        self._original = original
        self._copy = original.copy()
        self._original.update(override)
        self._reverted = False

    def __enter__(self):
        return self

    def revert(self):
        if self._reverted:
            return
        self._original.clear()
        self._original.update(self._copy)
        self._reverted = True

    def __exit__(self, *args, **kwargs):
        if self._reverted:
            return
        self.revert()


def dict_push(
    dictionary: dict | typing.Any,
    override_data: dict | None = None,
    **override_data_kwargs,
):
    if override_data is None:
        override_data = {}
    return _DictPushContextManager(dictionary, override_data | override_data_kwargs)
