import typing
import pygame
import math
from mili import typing as _typing
from mili import error as _error
from mili import data as _data
import mili._core as _core

_animators: list["Animator"] = []

__all__ = (
    "EaseLinear",
    "EaseIn",
    "EaseOut",
    "EaseInCirc",
    "EaseOutCirc",
    "EaseInSin",
    "EaseOutSin",
    "EaseInOutSin",
    "EaseOvershoot",
    "EaseBounce",
    "Animator",
    "ABAnimation",
    "StepsAnimation",
    "StatusAnimation",
    "update_all",
)


class _BaseEase:
    def __call__(self, t: float) -> float:
        return NotImplemented

    def get(self, t: float) -> float:
        return self.__call__(t)


class _BasePowerEase(_BaseEase):
    def __init__(self, n: int = 2):
        if n < 1:
            raise _error.MILIValueError("n argument must be >= 1")
        self.n = n


class EaseLinear(_BaseEase):
    def __call__(self, t):
        return t


class EaseIn(_BasePowerEase):
    def __call__(self, t):
        return t**self.n


class EaseOut(_BasePowerEase):
    def __call__(self, t):
        return 1 - (1 - t) ** self.n


class EaseInCirc(_BasePowerEase):
    def __call__(self, t):
        return 1 - math.sqrt(1 - t**self.n)


class EaseOutCirc(_BasePowerEase):
    def __call__(self, t):
        return math.sqrt(1 - (1 - t) ** self.n)


class EaseInSin(_BasePowerEase):
    def __call__(self, t):
        return 1 - math.cos(t * 0.5 * math.pi) ** (1 / self.n)


class EaseOutSin(_BasePowerEase):
    def __call__(self, t):
        return math.sin(t * 0.5 * math.pi) ** (1 / self.n)


class EaseInOutSin(_BaseEase):
    def __call__(self, t):
        return -math.cos(t * math.pi) / 2 + 0.5


class EaseOvershoot(_BaseEase):
    def __call__(self, t):
        return 1 - math.cos(4 * math.pi * t) * (1 - t)


class EaseBounce(_BaseEase):
    def __call__(self, t):
        if 2 * t - 2 == 0:
            return (1 - t) * abs(math.sin(0))
        return (1 - t) * abs(math.sin(math.pi / (2 * t - 2)))


def update_all():
    for anim in _animators:
        anim.update()


class Animator:
    EPSILON: typing.ClassVar[float] = 0.01

    def __init__(
        self,
        start_value: _typing.AnimValueLike,
        end_value: _typing.AnimValueLike,
        value_type: typing.Literal["number", "color", "sequence"],
        duration_ms: int,
        easing: _typing.EasingLike | None = None,
        finish_callback: typing.Callable[[], float] | None = None,
    ):
        if easing is None:
            easing = EaseLinear()
        self.start_value = start_value
        self.end_value = end_value
        self.value: _typing.AnimValueLike = self.start_value
        self.duration_ms = duration_ms
        self.easing = easing
        self.value_type = value_type
        self.finish_callback = finish_callback
        self.active = False
        self._start_time = 0
        if self not in _animators:
            _animators.append(self)
        if self.duration_ms == 0:
            raise _error.MILIValueError("Duration must be different from 0")
        if self.value_type not in ["number", "color", "sequence"]:
            raise _error.MILIValueError("Unsupported value type")

    def change_values(
        self, start_value: _typing.AnimValueLike, end_value: _typing.AnimValueLike
    ):
        self.start_value, self.end_value = start_value, end_value

    def start(self) -> typing.Self:
        self._start_time = pygame.time.get_ticks()
        self.active = True
        self.value = self.start_value
        return self

    def stop(self) -> typing.Self:
        self.active = False
        return self

    def flip_direction(self) -> typing.Self:
        self.start_value, self.end_value = self.end_value, self.start_value
        return self

    def update(self) -> typing.Self:
        if not self.active:
            return self
        t = self.easing((pygame.time.get_ticks() - self._start_time) / self.duration_ms)
        if self.value_type == "number":
            self.value = pygame.math.lerp(self.start_value, self.end_value, t)  # type: ignore
            if abs(self.value - self.end_value) <= self.EPSILON:  # type: ignore
                self.value = self.end_value
                self.stop()
                if self.finish_callback:
                    self.finish_callback()
        elif self.value_type == "color":
            self.value = self.start_value.lerp(  # type: ignore
                self.end_value,  # type: ignore
                pygame.math.clamp(t, 0, 1),
            )
            if (
                abs(self.value.r - self.end_value.r) <= 1  # type: ignore
                and abs(self.value.g - self.end_value.g) <= 1  # type: ignore
                and abs(self.value.b - self.end_value.b) <= 1  # type: ignore
                and abs(self.value.a - self.end_value.a) <= 1  # type: ignore
            ):
                self.value = self.end_value
                self.stop()
                if self.finish_callback:
                    self.finish_callback()
        elif self.value_type == "sequence":
            cur_sequence = []
            finished = 0
            for sval, eval in zip(self.start_value, self.end_value):  # type: ignore
                cval = pygame.math.lerp(sval, eval, t)
                if abs(cval - eval) <= self.EPSILON:
                    cval = eval
                    finished += 1
                cur_sequence.append(cval)
            self.value = cur_sequence
            if finished >= len(self.start_value):  # type: ignore
                self.value = self.end_value
                self.stop()
                if self.finish_callback:
                    self.finish_callback()
        else:
            raise _error.MILIValueError(f"Unsupported value type '{self.value_type}'")
        return self


class _AnimatorWrapper:
    animator: Animator

    def stop(self) -> typing.Self:
        self.animator.stop()
        return self

    def update(self) -> typing.Self:
        self.animator.update()
        return self

    @property
    def value(self) -> _typing.AnimValueLike:
        return self.animator.value

    @value.setter
    def value(self, value):
        self.animator.value = value

    @property
    def active(self) -> bool:
        return self.animator.active


class ABAnimation(_AnimatorWrapper):
    def __init__(
        self,
        a: _typing.AnimValueLike,
        b: _typing.AnimValueLike,
        value_type: typing.Literal["number", "color", "sequence"],
        ab_duration_ms: int,
        ba_duration_ms: int,
        easing: _typing.EasingLike | None = None,
        reach_a_callback: typing.Callable[[], typing.Any] | None = None,
        reach_b_callback: typing.Callable[[], typing.Any] | None = None,
    ):
        self.a, self.b = a, b
        self.direction: str = "ab"
        self.ab_duration_ms, self.ba_duration_ms = ab_duration_ms, ba_duration_ms
        self.reach_a_callback, self.reach_b_callback = (
            reach_a_callback,
            reach_b_callback,
        )
        self.animator = Animator(
            self.a,
            self.b,
            value_type,
            self.ab_duration_ms,
            easing,
            self.reach_b_callback,
        )

    def goto_a(self) -> typing.Self:
        self.animator.change_values(self.animator.value, self.a)
        self.animator.finish_callback = self.reach_a_callback
        self.direction = "ba"
        self.animator.start()
        return self

    def goto_b(self) -> typing.Self:
        self.animator.change_values(self.animator.value, self.b)
        self.animator.finish_callback = self.reach_b_callback
        self.direction = "ab"
        self.animator.start()
        return self

    def flip_direction(self) -> typing.Self:
        if self.direction == "ba":
            self.goto_b()
        else:
            self.goto_a()
        return self

    def change_ab(
        self, a: _typing.AnimValueLike, b: _typing.AnimValueLike
    ) -> typing.Self:
        self.a, self.b = a, b
        if self.direction == "ab":
            self.animator.end_value = self.b
        else:
            self.animator.end_value = self.a
        return self


class StepsAnimation(_AnimatorWrapper):
    def __init__(
        self,
        steps: typing.Sequence[_typing.AnimValueLike],
        value_type: typing.Literal["number", "color", "sequence"],
        duration_ms: int,
        easing: _typing.EasingLike | None = None,
        reach_callback: typing.Callable[[], typing.Any] | None = None,
    ):
        if len(steps) <= 2:
            raise _error.MILIValueError("At least 2 animation steps are required")
        self.steps = steps
        self.step = -1
        self.animator = Animator(
            self.steps[0],
            self.steps[1],
            value_type,
            duration_ms,
            easing,
            reach_callback,
        )

    def goto(self, step: int) -> typing.Self:
        if step < 0 or step >= len(self.steps):
            raise _error.MILIValueError("Step out of bounds")
        self.step = step
        self.animator.change_values(self.animator.value, self.steps[step])
        self.animator.start()
        return self


class StatusAnimation(_AnimatorWrapper):
    def __init__(
        self,
        base_value: _typing.AnimValueLike,
        hover_value: _typing.AnimValueLike | None,
        press_value: _typing.AnimValueLike | None,
        value_type: typing.Literal["number", "color"],
        duration_ms: int,
        easing: _typing.EasingLike | None = None,
        reach_callback: typing.Callable[[], typing.Any] | None = None,
        style_name: str = "",
        press_button: int = pygame.BUTTON_LEFT,
        update_id: str | None = None,
    ):
        self.base_value = base_value
        self.hover_value = hover_value
        self.press_value = press_value
        self.press_button = press_button
        self.style_name = style_name
        self._last_value = self.base_value
        self.animator = Animator(
            base_value,
            base_value,
            value_type,
            duration_ms,
            easing,
            reach_callback,
        )
        _core._globalctx._register_update_id(update_id, self.status_update)

    def status_update(
        self, element: _data.Interaction, selected: bool = False
    ) -> _data.Interaction:
        if element.hovered:
            if self.press_value is not None and (
                element.press_button == self.press_button or selected
            ):
                if self._last_value != self.press_value:
                    self.animator.start_value = self._last_value
                    self._last_value = self.press_value
                    self.animator.end_value = self.press_value
                    self.animator.start()
            elif self.hover_value is not None:
                if self._last_value != self.hover_value:
                    self.animator.start_value = self._last_value
                    self._last_value = self.hover_value
                    self.animator.end_value = self.hover_value
                    self.animator.start()
            elif self._last_value != self.base_value:
                self.animator.start_value = self._last_value
                self._last_value = self.base_value
                self.animator.end_value = self.base_value
                self.animator.start()
        else:
            if (
                selected or element.press_button == self.press_button
            ) and self.press_value is not None:
                if self._last_value != self.press_value:
                    self.animator.start_value = self._last_value
                    self._last_value = self.press_value
                    self.animator.end_value = self.press_value
                    self.animator.start()
            elif self._last_value != self.base_value:
                self.animator.start_value = self._last_value
                self._last_value = self.base_value
                self.animator.end_value = self.base_value
                self.animator.start()
        return element

    @property
    def style(self):
        return {self.style_name: self.value}
