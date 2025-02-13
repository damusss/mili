import pygame
from mili import _core
from mili import data as _data


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
