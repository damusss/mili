import math
import pygame
import typing
from mili import _core
from mili import data as _data
from mili import typing as _typing
from mili import error as _error
from mili._utils import _prefabs

if typing.TYPE_CHECKING:
    from mili.mili import MILI


class _TBLine:
    def __init__(self, parent: "TextBox", mili: "MILI", text):
        self._parent = parent
        self._mili = mili
        self._text = text
        self._cache = _data.TextCache()
        self._size: pygame.Vector2 = pygame.Vector2(0, self._parent._font.get_height())
        self._absrect = pygame.Rect()
        self._rects = None

    def _update_absrect(self, rect: pygame.Rect):
        self._absrect = rect
        self._topleft = pygame.Vector2(self._absrect.topleft)

    def _processed(self):
        rich = self._cache._rich
        if rich is None:
            return
        self._size = pygame.Vector2(rich["size"])

    def _get_cursor_rect(self, cursorx):
        rich = self._cache._rich
        if rich is None or "blocks" not in rich:
            return
        if self._text == "":
            return pygame.Rect(
                self._topleft.x,
                self._topleft.y,
                self._parent.style["cursor_width"],
                self._parent._font.get_height(),
            )
        charidx = 0
        for block in rich["blocks"]:
            amount = len(block["text"])
            if charidx + amount >= cursorx:
                text_to_cursor = block["text"][: (cursorx - charidx)]
                sizex = self._parent._font.size(text_to_cursor)[0]
                return pygame.Rect(
                    block["rect"].x + sizex + self._topleft.x,
                    block["rect"].y + self._topleft.y,
                    self._parent.style["cursor_width"],
                    block["rect"].h,
                )
            else:
                charidx += amount

    def _get_any_hovered(self):
        rich = self._cache._rich
        if rich is None or "blocks" not in rich:
            return False
        for block in rich["blocks"]:
            br = block["rect"].copy()
            br.topleft += self._topleft
            if br.collidepoint(self._parent._mpos):
                return True
        return False

    def _get_cursor(self):
        rich = self._cache._rich
        if rich is None or "blocks" not in rich:
            return 0
        cursor = 0
        for block in rich["blocks"]:
            br = block["rect"].copy()
            br.topleft += self._topleft
            if br.collidepoint(self._parent._mpos):
                rel_x = self._parent._mpos[0] - br.x
                pospercentage = rel_x / br.w
                cur_index = max(0, int(pospercentage * len(block["text"])) - 3)
                prev_size = 0
                for i in range(len(block["text"]) - cur_index + 1):
                    cur_index += 1
                    if cur_index >= len(block["text"]):
                        return cursor + len(block["text"]) - 1
                    text_until_index = block["text"][:cur_index]
                    this_size = self._parent._font.size(text_until_index)[0]
                    if this_size >= rel_x:
                        extra = 0
                        average = (this_size - prev_size) / 2 + prev_size
                        if rel_x <= average:
                            extra = 1
                        return cursor + cur_index - extra
                    prev_size = this_size
            else:
                cursor += len(block["text"])
        return cursor

    def _get_closest_cursor(self, point, linei):
        rich = self._cache._rich
        if rich is None or "blocks" not in rich:
            return
        previous_cx = 0
        for block in rich["blocks"]:
            br = block["rect"].copy()
            br.topleft += self._topleft
            if (
                br.y - self._parent._cont_space <= point[1]
                and br.bottom + self._parent._cont_space >= point[1]
            ):
                rel_x = point[0] - br.x
                pospercentage = rel_x / br.w
                cur_index = min(
                    len(block["text"]) - 2,
                    max(0, int(pospercentage * len(block["text"])) - 3),
                )
                prev_size = 0
                for i in range(len(block["text"]) - cur_index + 1):
                    cur_index += 1
                    if cur_index >= len(block["text"]):
                        return previous_cx + len(block["text"]), linei
                    text_until_index = block["text"][:cur_index]
                    this_size = self._parent._font.size(text_until_index)[0]
                    if this_size >= rel_x:
                        extra = 0
                        average = (this_size - prev_size) / 2 + prev_size
                        if rel_x <= average:
                            extra = 1
                        return previous_cx + cur_index - extra, linei
                    prev_size = this_size
            else:
                previous_cx += len(block["text"])

    def _get_selection_rects_sameline(self):
        rich = self._cache._rich
        if rich is None or "blocks" not in rich:
            return
        rects = []
        for block in rich["blocks"]:
            rect = block["rect"].copy()
            rect.topleft += self._topleft
            rects.append(rect)
        self._rects = rects
        return rects

    def _get_selection_rects_fullline(
        self,
    ):
        rich = self._cache._rich
        if rich is None or "blocks" not in rich:
            return
        rects = []
        for block in rich["blocks"]:
            rect = block["rect"].copy()
            rect.topleft += self._topleft
            rects.append(rect)
        self._rects = rects
        return rects

    def _get_selection_rects_startline(self):
        rich = self._cache._rich
        if rich is None or "blocks" not in rich:
            return
        rects = []
        for block in rich["blocks"]:
            rect = block["rect"].copy()
            rect.topleft += self._topleft
            rects.append(rect)
        self._rects = rects
        return rects

    def _get_selection_rects_endline(self):
        rich = self._cache._rich
        if rich is None or "blocks" not in rich:
            return
        rects = []
        for block in rich["blocks"]:
            rect = block["rect"].copy()
            rect.topleft += self._topleft
            rects.append(rect)
        self._rects = rects
        return rects


class TextBox:
    def __init__(self, mili: "MILI", style):
        if style is None:
            style = {}
        sbar_style = style.get("scrollbar_style", {})
        self.style = {
            "blink_interval": style.get("blink_interval", 350),  #
            "cursor_color": style.get("cursor_color", "white"),  #
            "cursor_width": style.get("cursor_width", 2),  #
            "placeholder": style.get("placeholder", "Enter text..."),  #
            "placeholder_color": style.get("placeholder_color", (180,) * 3),  #
            "selection_color": style.get("selection_color", (20, 80, 225)),  #
            "copy_key": style.get("copy_key", pygame.K_c),  #
            "keymod": style.get("keymod", pygame.KMOD_CTRL),  #
            "paste_key": style.get("paste_key", pygame.K_v),  #
            "select_all_key": style.get("select_all_key", pygame.K_a),  #
            "delete_all_key": style.get("delete_all_key", pygame.K_BACKSPACE),  #
            "bg_rect_style": style.get("bg_rect_style", None),  #
            "outline_rect_style": style.get("outline_rect_style", None),  #
            "text_style": style.get("text_style", {}),  #
            "text_wrap": style.get("text_wrap", False),  #
            "selection_style": style.get("selection_style", None),  #
            "double_click_interval": style.get("double_click_interval", 250),  #
            "cut_key": style.get("cut_key", pygame.K_x),  #
            "enable_history": style.get("enable_history", True),  #
            "redo_key": style.get("redo_key", pygame.K_y),  #
            "undo_key": style.get("undo_key", pygame.K_z),  #
            "history_limit": style.get("history_limit", 1000),  #
            # "text_anchor": style.get("text_anchor", "left"),
            "characters_limit": style.get("characters_limit", None),  #
            "scroll_wheel_mult": style.get("scroll_wheel_mult", 35),
            "scroll_drag_mult": style.get("scroll_drag_mult", 5),
            "scrollbar_style": {
                "short_size": sbar_style.get("short_size", 10),
                "border_dist": sbar_style.get("border_dist", 1),
                "padding": sbar_style.get("padding", 1),
                "border_radois": sbar_style.get("border_radius", 3),
                "bar_color": sbar_style.get("bar_color", (30, 30, 30)),
                "handle_color": sbar_style.get("handle_color", (40, 40, 40)),
                "handle_hover_color": sbar_style.get("handle_bg_color", (60, 60, 60)),
            },
        }
        self._mili = mili
        self._font = self._mili.text_font(self.style["text_style"])
        self._lines: list[_TBLine] = [_TBLine(self, self._mili, "")]
        TEXT = (
            """TEST1 sdhajkdhas dhsajk hdksajd asd asdsa dsa d
asd
as
d asdsa dsa das dasdsadhgshdgshdgshdgshgdashdjasgdjhas gdgsajhd gajhdgsjhagdjashgdjhsad asd
sad sad asdasd sadsad as  das ds ahgdjgsadjgsajhdas
dsa daDSAHgddg767(S d ADsa dsa d )aa sd asd as
das  dsa ds
dsa
das dasdasdasgdjhsgahj dsad
"""
            * 2
        )
        self._lines = [_TBLine(self, self._mili, txt) for txt in TEXT.splitlines()]
        self._cursorx = 20
        self._cursory = 4
        self.focused = False
        self._cursor_on = True
        self._cursor_time = pygame.time.get_ticks()
        self._selection_start = None
        self._scroll_y_need = False
        self._scroll_x_need = False
        self._scroll = _prefabs.Scroll()
        self._sbar_x = _prefabs.Scrollbar(self._scroll, {"axis": "x"})
        self._sbar_y = _prefabs.Scrollbar(self._scroll, {"axis": "y"})
        self._cont_arect = pygame.Rect()
        self._press = False
        self._focus_press = False
        self._press_cursor = None
        self._press_time = pygame.time.get_ticks()
        self._press_mouse = (0, 0)
        self._release_time = pygame.time.get_ticks()
        self._press_count = 0
        self._offset_change = 0

    @property
    def cursor(self):
        return (self._cursorx, self._cursory)

    @cursor.setter
    def cursor(self, value):
        self._cursorx, self._cursory = value
        self._clamp_cursor()

    def ui(self, container: _data.Interaction) -> _data.Interaction:
        self._update_start()
        self._ui_prep(container)
        prev = self._scroll.scroll_offset.copy()
        self._scroll.update(container)
        self._offset_change = self._scroll.scroll_offset.y-prev.y
        self._ui_scrollbars(container)
        if self._cont_resizey:
            self._ui_lines_resizey()
        elif self.style["text_wrap"]:
            self._ui_lines_wrap()
        else:
            self._ui_lines()
        self._update_end(container)
        return container

    def _update_end(self, container: _data.Interaction):
        now = pygame.time.get_ticks()
        if self._press and (now - self._press_time >= 80):
            self._set_cursor_on()
            before_mouse = pygame.Vector2(self._mpos)
            clamped_mouse = pygame.Vector2(
                pygame.math.clamp(
                    self._mpos[0], self._cont_arect.x, self._cont_arect.right
                ),
                pygame.math.clamp(
                    self._mpos[1], self._cont_arect.y, self._cont_arect.bottom
                ),
            )
            closest = self._get_closest_cursor(clamped_mouse)
            if closest is not None:
                self.cursor = closest
            if before_mouse.x != clamped_mouse.x:
                amount = math.copysign(
                        self.style["scroll_drag_mult"], before_mouse.x - clamped_mouse.x
                    )
                self._scroll.scroll(
                    amount,
                    0,
                )
                self._offset_change = amount
            if before_mouse.y != clamped_mouse.y:
                amount = math.copysign(
                        self.style["scroll_drag_mult"], before_mouse.y - clamped_mouse.y
                    )
                self._scroll.scroll(
                    0,
                    amount,
                )
                self._offset_change = amount
            if (
                closest is not None
                and self._selection_start is None
                and self.cursor != self._press_cursor
            ):
                self._selection_start = self.cursor
        if container.left_just_pressed:
            self._focus_press = True
            self.focused = True
            self._press_time = now
            if (
                now - self._release_time <= self.style["double_click_interval"]
                and self._hovered_line is not None
                and self._mpos == self._press_mouse
            ):
                self._press_count += 1
                if self._press_count == 1:  # word select
                    ...
                elif self._press_count == 2:  # line select
                    ...
                elif self._press_count == 3:  # whole select
                    self._press_count = 0
                else:  # single cursor
                    self.cursor = self._get_cursor_at_hover()
                    self._press_mouse = self._mpos
            else:
                self._press_count = 0
                self._press = True
                self.cancel_selection()
                self.cursor = self._get_cursor_at_hover()
                self._press_cursor = (self._cursorx, self._cursory)
                self._press_mouse = None

        if container.left_just_released:
            self.focused = True
            self._press = False
            self._set_cursor_on()
            self._release_time = now
        self._offset_change = 0

    def _get_cursor_at_hover(self):
        if self._hovered_line is not None:
            return (
                self._hovered_line[0]._get_cursor(),
                self._hovered_line[1],
            )
        ret = self._get_closest_cursor()
        if ret:
            return ret
        return (0, 0)

    def _get_closest_cursor(self, point=None):
        if point is None:
            point = self._mpos
        for line, linei in self._visible_lines:
            cursor = line._get_closest_cursor(point, linei)
            if cursor is None:
                continue
            return cursor
        return None

    def _update_start(self):
        self._mpos = pygame.mouse.get_pos()
        if pygame.time.get_ticks() - self._cursor_time >= self.style["blink_interval"]:
            self._cursor_on = not self._cursor_on
            self._cursor_time = pygame.time.get_ticks()
        self._hovered_line = None
        if not self.focused:
            self._cursor_on = False
        self._visible_lines = []
        self._selection_ys = None
        if self._selection_start is not None:
            self._selection_ys = (
                min(self._cursory, self._selection_start[1]),
                max(self._cursory, self._selection_start[1]),
            )

    def _ui_prep(self, container: _data.Interaction):
        cont_style = container.data.style
        cont_grid = container.data.grid
        self._cont_padx = cont_grid.padx
        self._cont_pady = cont_grid.pady
        self._cont_space = cont_grid.spacing
        self._cont_fsize = container.data.rect.size
        self._cont_arect = container.data.absolute_rect
        self._cont_resizey = cont_style.get("resizey", False)
        if cont_style.get("axis", "y") != "y":
            raise _error.MILIIncompatibleStylesError(
                "Textbox container must organize children on the y axis"
            )
        if cont_style.get("layout", "stack") != "stack":
            raise _error.MILIIncompatibleStylesError(
                "Textbox container must organize children with a stack layout"
            )
        if cont_style.get("resizex", False) and self.style["text_wrap"]:
            raise _error.MILIIncompatibleStylesError(
                "Textbox container cannot resize on the x axis if text is supposed to wrap"
            )
        self._cont_size = pygame.Vector2(
            self._cont_fsize[0] - self._cont_padx * 2,
            self._cont_fsize[1] - self._cont_pady * 2,
        )
        if self._cont_resizey:
            self._scroll_x_need = self._scroll_y_need = False
        if self.style["text_wrap"]:
            self._scroll_x_need = False
        sbar_style = self.style["scrollbar_style"]
        if self._scroll_y_need:
            self._cont_size.x -= sbar_style["short_size"] + sbar_style["border_dist"]
        if self._scroll_x_need:
            self._cont_size.y -= sbar_style["short_size"] + sbar_style["border_dist"]
        self._font = self._mili.text_font(self.style["text_style"])
        if self.style["bg_rect_style"] is not None:
            self._mili.rect(self.style["bg_rect_style"])
        if self.style["outline_rect_style"] is not None:
            self._mili.rect(self.style["outline_rect_style"])

    def _ui_scrollbars(self, container: _data.Interaction):
        self._sbar_x.update(container)
        self._sbar_y.update(container)
        if not self._cont_resizey:
            self._scroll_x_need = self._sbar_x.needed
            self._scroll_y_need = self._sbar_y.needed
        else:
            self._scroll_x_need = self._scroll_y_need = False
        if self.style["text_wrap"]:
            self._scroll_x_need = False
        sbar_style = self.style["scrollbar_style"]
        reduce = sbar_style["short_size"] + sbar_style["border_dist"]
        self._sbar_x.style["short_size"] = self._sbar_y.style["short_size"] = (
            sbar_style["short_size"]
        )
        self._sbar_x.style["border_dist"] = self._sbar_y.style["border_dist"] = (
            sbar_style["border_dist"]
        )
        self._sbar_x.style["padding"] = self._sbar_y.style["padding"] = sbar_style[
            "padding"
        ]
        self._sbar_x.style["size_reduce"] = reduce * self._scroll_y_need
        prev = self._scroll.scroll_offset.copy()
        for sbar, need in [
            (self._sbar_y, self._scroll_y_need),
            (self._sbar_x, self._scroll_x_need),
        ]:
            if need:
                with self._mili.begin(
                    sbar.bar_rect,
                    sbar.bar_style | {"z": len(self._lines) * 2},
                ):
                    if sbar_style["bar_color"] is not None:
                        self._mili.rect({"color": sbar_style["bar_color"]})
                    with self._mili.element(
                        sbar.handle_rect, sbar.handle_style | {"update_id": "cursor"}
                    ) as handle:
                        self._mili.rect(
                            {
                                "color": sbar_style[
                                    "handle_hover_color"
                                    if handle.hovered or handle.unhover_pressed
                                    else "handle_color"
                                ]
                            }
                        )
                        sbar.update_handle(handle)
        self._offset_change = self._scroll.scroll_offset.y-prev.y

    def _ui_lines_resizey(self):
        sbar_style = self.style["scrollbar_style"]
        reduce = sbar_style["short_size"] + sbar_style["border_dist"]
        for cur_line, line_obj in enumerate(self._lines):
            self._ui_line(cur_line, line_obj, reduce)
        if self._scroll_x_need:
            self._mili.element((0, 0, 0, reduce))

    def _ui_lines_wrap(self):
        sbar_style = self.style["scrollbar_style"]
        reduce = sbar_style["short_size"] + sbar_style["border_dist"]
        cur_bottom = 0
        cur_line = 0
        for cur_line, line_obj in enumerate(self._lines):
            bottom = cur_bottom + line_obj._size.y + self._cont_space
            if bottom > self._scroll.scroll_offset.y:
                break
            cur_bottom = bottom
        if cur_bottom > 0:
            self._mili.element((0, 0, 0, cur_bottom))
        cur_bottom -= self._scroll.scroll_offset.y
        prev = None
        while True:
            if cur_line >= len(self._lines):
                break
            line_obj = self._lines[cur_line]
            self._ui_line(cur_line, line_obj, reduce)
            line_obj._processed()
            if prev is not None:
                cur_bottom += prev._size.y + self._cont_space
            prev = line_obj
            cur_line += 1
            if cur_bottom > self._cont_size[1]:
                break
        extra_size = 0
        for i in range(cur_line, len(self._lines) - 1):
            extra_size += self._lines[i]._size.y + self._cont_space
        self._mili.element((0, 0, 0, extra_size + reduce * self._scroll_x_need))

    def _ui_lines(self):
        sbar_style = self.style["scrollbar_style"]
        reduce = sbar_style["short_size"] + sbar_style["border_dist"]
        line_height = self._font.get_height() + self._cont_space
        cur_line = max(0, int(abs(self._scroll.scroll_offset.y) / (line_height)) - 1)
        cur_bottom = 0
        if cur_line > 0:
            previous_space = cur_line * line_height - self._cont_space
            cur_bottom = previous_space + self._cont_space
            self._mili.element((0, 0, 0, previous_space))
        cur_bottom -= self._scroll.scroll_offset.y
        prev = None
        while True:
            if cur_line >= len(self._lines):
                break
            line_obj = self._lines[cur_line]
            self._ui_line(cur_line, line_obj, reduce)
            line_obj._processed()
            if prev is not None:
                cur_bottom += prev._size.y + self._cont_space
            prev = line_obj
            cur_line += 1
            if cur_bottom > self._cont_size[1]:
                break
        extra = 0
        if len(self._lines) > cur_line + 1:
            extra = len(self._lines) - (cur_line + 1)
        self._mili.element(
            (0, 0, 0, extra * line_height + reduce * self._scroll_x_need)
        )

    def _ui_line(self, cur_line, line_obj: _TBLine, reduce):
        self._visible_lines.append((line_obj, cur_line))
        if self._scroll_y_need:
            self._mili.begin(
                None,
                {
                    "axis": "x",
                    "resizex": True,
                    "resizey": True,
                    "pad": 0,
                    "spacing": 0,
                    "align": "first",
                    "blocking": False,
                    "offset": self._scroll.get_offset(),
                    "z": cur_line,
                    #"clip_draw": False,
                },
            )
        with self._mili.element(
            None,
            {
                "align": "first",
                "blocking": False,
                "offset": self._scroll.get_offset()
                if not self._scroll_y_need
                else (0, 0),
                "z": cur_line,
                "clip_draw": False,
            },
        ) as element:
            line_obj._update_absrect(element.data.absolute_rect)
            hovering_block = line_obj._get_any_hovered()
            if hovering_block:
                self._hovered_line = (line_obj, cur_line)
            if self._selection_start is not None and self._selection_ys is not None:
                rects = None
                if self._offset_change != 0:
                    ...
                else:
                    if self._selection_ys[0] == self._selection_ys[1] == cur_line:
                        rects = line_obj._get_selection_rects_sameline()
                    elif (
                        self._selection_ys[0] < cur_line
                        and self._selection_ys[1] > cur_line
                    ):
                        rects = line_obj._get_selection_rects_fullline()
                    elif (
                        self._selection_ys[0] < cur_line
                        and self._selection_ys[1] == cur_line
                    ):
                        rects = line_obj._get_selection_rects_endline()
                    elif (
                        self._selection_ys[0] == cur_line
                        and self._selection_ys[1] > cur_line
                    ):
                        rects = line_obj._get_selection_rects_startline()
                if rects is not None:
                    for rect in rects:
                        self._mili.rect(
                            {
                                "color": self.style["selection_color"],
                                "ready_rect": rect,
                            }
                        )
            self._mili.text(
                line_obj._text,
                self.style["text_style"]
                | {
                    "align": "left",
                    "font_align": pygame.FONT_LEFT,
                    "rich": True,
                    "_textbox": True,
                    "wraplen": self._cont_size[0] if self.style["text_wrap"] else 0,
                    "cache": line_obj._cache,
                    "growy": True,
                    "growx": True,
                    "padx": 0,
                    "pady": 0,
                    "rich_linespace": self._cont_space,
                },
            )
            if cur_line == self._cursory and self._cursor_on:
                rect = line_obj._get_cursor_rect(self._cursorx)
                if rect is not None:
                    self._mili.rect(
                        {
                            "color": self.style["cursor_color"],
                            "ready_rect": rect,
                            "draw_above": True,
                        }
                    )
        if self._scroll_y_need:
            self._mili.element((0, 0, reduce, 0))
            self._mili.end()

    def _clamp_cursor(self):
        if self._cursory < 0:
            self._cursory = 0
        if self._cursory > len(self._lines) - 1:
            self._cursory = len(self._lines) - 1
        line = self._lines[self._cursory]
        if self._cursorx < 0:
            self._cursorx = 0
        if self._cursorx > len(line._text):
            self._cursorx = len(line._text)
        if self._selection_start is not None:
            self._selection_start = (
                min(len(line._text), max(0, self._selection_start[0])),
                min(len(self._lines) - 1, max(0, self._selection_start[1])),
            )

    def _set_cursor_on(self):
        self._cursor_on = True
        self._cursor_time = pygame.time.get_ticks()

    def event(self, event: pygame.Event):
        prev = self._scroll.scroll_offset.copy()
        self._scroll.wheel_event(
            event, self.style["scroll_wheel_mult"], self._cont_arect, pygame.KMOD_CTRL
        )
        self._offset_change = self._scroll.scroll_offset.y-prev.y
        if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
            self._press = False
            self._press_cursor = 0
            if not self._focus_press:
                self.unfocus()
            self._focus_press = False
        if not self.focused:
            return

    def focus(self):
        self.focused = True
        self._set_cursor_on()

    def unfocus(self):
        self.focused = False
        self.cancel_selection()

    def cancel_selection(self):
        self._selection_start = None

    def move_cursor(self, x=0, y=0):
        self._cursorx += x
        self._cursory += y
        self._clamp_cursor()

    def get_line(self, cursor_y: int | None = None):
        if cursor_y is None:
            cursor_y = self._cursory
        return self._lines[min(len(self._lines) - 1, max(0, cursor_y))]._text

    def get_lines(self):
        return [line._text for line in self._lines]

    def get_text(self):
        return "\n".join(self.get_lines())

    def set_line(self, text: str, cursor_y: int | None = None):
        if cursor_y is None:
            cursor_y = self._cursory
        line = self._lines[min(len(self._lines) - 1, max(0, cursor_y))]
        line._text = str(text)
        self._clamp_cursor()

    def pop_line(self, cursor_y: int | None = None):
        if cursor_y is None:
            cursor_y = self._cursory
        ret = self._lines.pop(min(len(self._lines) - 1, max(0, cursor_y)))._text
        self._clamp_cursor()
        return ret

    def select(self, start_cursor, end_cursor):
        self._selection_start = start_cursor
        self.cursor = end_cursor


class EntryLine:
    def __init__(
        self, text: str, style: _typing.EntryLineStyleLike | dict | None = None
    ):
        if style is None:
            style = {}
        self.style: _typing.EntryLineStyleLike = {
            "blink_interval": style.get("blink_interval", 350),
            "cursor_color": style.get("cursor_color", "white"),
            "cursor_width": style.get("cursor_width", 2),
            "error_color": style.get("error_color", "red"),
            "input_validator": style.get("input_validator", None),
            "number_integer": style.get("number_integer", False),
            "number_max": style.get("number_max", None),
            "number_min": style.get("number_min", None),
            "placeholder": style.get("placeholder", "Enter text..."),
            "placeholder_color": style.get("placeholder_color", (180,) * 3),
            "selection_color": style.get("selection_color", (20, 80, 225)),
            "target_number": style.get("target_number", False),
            "text_style": style.get("text_style", {}),
            "text_validator": style.get("text_validator", None),
            "validator_lowercase": style.get("validator_lowercase", False),
            "validator_uppercase": style.get("validator_uppercase", False),
            "validator_windows_path": style.get("validator_windows_path", False),
            "copy_key": style.get("copy_key", pygame.K_c),
            "keymod": style.get("keymod", pygame.KMOD_CTRL),
            "paste_key": style.get("paste_key", pygame.K_v),
            "select_all_key": style.get("select_all_key", pygame.K_a),
            "delete_all_key": style.get("delete_all_key", pygame.K_BACKSPACE),
            "scroll": style.get("scroll", None),
            "bg_rect_style": style.get("bg_rect_style", None),
            "outline_rect_style": style.get("outline_rect_style", None),
            "text_filly": style.get("text_filly", "100"),
            "selection_style": style.get("selection_style", None),
            "double_click_interval": style.get("double_click_interval", 250),
            "cut_key": style.get("cut_key", pygame.K_x),
            "enable_history": style.get("enable_history", True),
            "redo_key": style.get("redo_key", pygame.K_y),
            "undo_key": style.get("undo_key", pygame.K_z),
            "history_limit": style.get("history_limit", 1000),
            "text_anchor": style.get("text_anchor", "left"),
            "characters_limit": style.get("characters_limit", None),
        }
        self._text = str(text)
        self.cursor = len(self._text)
        self.focused = False
        self._error = False
        self._cursor_on = True
        self._cursor_time = pygame.time.get_ticks()
        self._selection_start = None
        self._offset = 0
        self._size = 0
        self._cont_w = 0
        self._pad = 0
        self._just_checked = False
        self._rect = pygame.Rect()
        self._press = False
        self._focus_press = False
        self._press_cursor = 0
        self._press_time = pygame.time.get_ticks()
        self._release_time = pygame.time.get_ticks()
        self._press_count = 0
        self._font = None
        self._cont_rect = pygame.Rect()
        self._history = []
        self._history_index = -1

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, v):
        self._text = str(v)
        self.cursor = len(self._text)

    @property
    def text_strip(self):
        return self._text.strip()

    @property
    def text_as_number(self) -> float:
        try:
            text = self.text
            if text.startswith("0x") or text.startswith("0o"):
                number = eval(text)
            else:
                number = float(text)
            prev = number
            number = pygame.math.clamp(
                number,
                self.style["number_min"] if self.style["number_min"] else float("-inf"),
                self.style["number_max"] if self.style["number_max"] else float("inf"),
            )
            if prev != number:
                self._error = True
            if self.style["number_integer"]:
                number = int(number)
        except (ValueError, SyntaxError):
            number = (
                self.style["number_min"] if self.style["number_min"] else float("nan")
            )
            if number != float("nan") and self.style["number_integer"]:
                number = int(number)
            self._error = True
        return number

    def ui(self, container_element: _data.Interaction):
        mpos = pygame.mouse.get_pos()
        mposx = mpos[0]
        if pygame.time.get_ticks() - self._cursor_time >= self.style["blink_interval"]:
            self._cursor_on = not self._cursor_on
            self._cursor_time = pygame.time.get_ticks()
        if not self.focused:
            self._cursor_on = False
        if self._press and (pygame.time.get_ticks() - self._press_time >= 80):
            self._set_cursor_on()
            new_cursor, tocheck = self._cursor_from_pos(mposx)
            if (
                new_cursor != self._press_cursor
                # and new_cursor - 1 != self._press_cursor
                and self._selection_start is None
            ):
                self._selection_start = self.cursor
                # if new_cursor < self._press_cursor:    self._selection_start += 1
            if tocheck:
                self._check()
            self.cursor = new_cursor
        mili = _core._globalctx._mili
        if mili is None:
            return None
        if mili._ctx._parent["id"] != container_element.data.id:
            raise _error.MILIStatusError(
                "Entryline's container element must be created as a parent"
            )
        if self.style["bg_rect_style"] is not None:
            mili.rect(self.style["bg_rect_style"])
        if self.style["outline_rect_style"] is not None:
            mili.rect(self.style["outline_rect_style"])
        color = self.style["text_style"].get("color", "white")
        text = self._text
        if len(self._text) <= 0 and not self.focused:
            text = self.style["placeholder"]
            color = self.style["placeholder_color"]
        if self._error:
            color = self.style["error_color"]

        style = (
            {"growy": False}
            | self.style["text_style"]
            | {
                "growx": True,
                "color": color,
                "padx": 0,
                "pady": 0,
            }
        )
        pad = container_element.data.grid.padx
        self._cont_rect = container_element.data.absolute_rect
        self._font = mili.text_font(style)
        fonth = self._font.get_height()
        if self.style["text_anchor"] != "right":
            text_to_cursor = self._text[: self.cursor]
            size = mili.text_size(text_to_cursor, style)
        else:
            text_from_cursor = self._text[self.cursor :]
            size = mili.text_size(text_from_cursor, style)
        self._size = size.x
        self._pad = pad
        self._cont_w = container_element.data.rect.w
        if self._just_checked:
            self._check()
            self._just_checked = False
        scrolloffset = pygame.Vector2()
        if self.style["scroll"] is not None:
            scrolloffset = self.style["scroll"].get_offset()
        need_middle = self._rect.w < (self._cont_w - pad * 2)
        if (
            self.style["text_anchor"] == "center"
            and container_element.data.style.get("axis", "y") != "y"
        ):
            raise _error.MILIIncompatibleStylesError(
                "The entry line container must organize children on the y axis (not x) for the text to be aligned in the center"
            )
        te = mili.element(
            None,
            {
                "blocking": False,
                "filly": self.style["text_filly"],
                "offset": pygame.Vector2(-self._offset, 0) + scrolloffset,
                "align": "first"
                if (
                    self.style["text_anchor"] == "left"
                    or (self.style["text_anchor"] == "center" and not need_middle)
                )
                else ("last" if self.style["text_anchor"] == "right" else "center"),
            },
        )
        self._rect = te.data.absolute_rect
        if self._selection_start is not None and self.cursor != self._selection_start:
            start, end = (
                min(self.cursor, self._selection_start),
                max(self.cursor, self._selection_start),
            )
            text_to_start = self.text[:start]
            text_to_end = self.text[:end]
            size_start = mili.text_size(text_to_start, style).x
            size_end = mili.text_size(text_to_end, style).x
            extra_style = {}
            if self.style["selection_style"] is not None:
                extra_style = self.style["selection_style"]
            sel_rect = pygame.Rect(
                size_start - scrolloffset[0] + te.data.absolute_rect.x,
                te.data.rect.h
                - te.data.rect.h / 2
                - fonth / 2
                - scrolloffset[1]
                + te.data.absolute_rect.y,
                size_end - size_start,
                fonth,
            )
            mili.rect(
                extra_style
                | {"ready_rect": sel_rect, "color": self.style["selection_color"]}
            )
        mili.text(text, style)
        cursor_pos = pad + (self._size - self._offset)
        if self.style["text_anchor"] == "right":
            cursor_pos = self._cont_w - pad - self._size - self._offset
        elif self.style["text_anchor"] == "center" and need_middle:
            cursor_pos = self._cont_w / 2 + self._size - self._offset - self._rect.w / 2
        mili.element(
            (
                cursor_pos,
                te.data.rect.bottom - te.data.rect.h / 2 - fonth / 2,
                self.style["cursor_width"],
                fonth,
            ),
            {"ignore_grid": True, "offset": scrolloffset, "blocking": False},
        )
        if self._cursor_on:
            mili.rect(
                {"color": self.style["cursor_color"], "border_radius": 0, "outline": 0},
            )
        if container_element.left_just_pressed:
            self._focus_press = True
            self.focused = True
            self._press_time = pygame.time.get_ticks()
            if (
                pygame.time.get_ticks() - self._release_time
                <= self.style["double_click_interval"]
            ):
                self._press_count += 1
                if self._press_count == 1:
                    checkspace = True
                    try:
                        if self._text[self.cursor] == " ":
                            checkspace = False
                    except IndexError:
                        ...
                    left, right = self._text[: self.cursor], self._text[self.cursor :]
                    li = len(left) - 1
                    while li >= 0:
                        char = left[li]
                        if (char == " " and checkspace) or (
                            char != " " and not checkspace
                        ):
                            break
                        li -= 1
                    li += 1
                    ri = 0
                    while ri < len(right):
                        char = right[ri]
                        if (char == " " and checkspace) or (
                            char != " " and not checkspace
                        ):
                            break
                        ri += 1
                    self._selection_start = self.cursor - (len(left) - li)
                    self.cursor = self.cursor + ri
                    self._check()
                elif self._press_count == 2:
                    self.cursor = len(self._text)
                    self._selection_start = 0
                    self._press_count = 0
                    self._check()
                else:
                    self.cursor, tocheck = self._cursor_from_pos(mposx)
                    if tocheck:
                        self._check()
            else:
                self._press_count = 0
                self._press = True
                self.cancel_selection()
                self.cursor, tocheck = self._cursor_from_pos(mposx)
                if tocheck:
                    self._check()
                self._press_cursor = self.cursor
            self._set_cursor_on()
        if container_element.left_just_released:
            self.focused = True
            self._press = False
            self._set_cursor_on()
            self._release_time = pygame.time.get_ticks()

    def event(self, event: pygame.Event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
            self._press = False
            self._press_cursor = 0
            if not self._focus_press:
                self.unfocus()
            self._focus_press = False
        if not self.focused:
            return
        if event.type == pygame.TEXTINPUT:
            if (cl := self.style["characters_limit"]) is not None:
                if len(self._text) >= cl:
                    return
            text = event.text
            self.insert(text)
        if event.type == pygame.KEYDOWN:
            if event.mod & self.style["keymod"]:
                if event.key == self.style["select_all_key"]:
                    self.cursor = len(self._text)
                    self._selection_start = 0
                    self._set_cursor_on()
                if event.key == self.style["delete_all_key"]:
                    self._history_save()
                    self.text = ""
                    self.cursor = 0
                if event.key == self.style["copy_key"]:
                    text = self.get_selection()
                    pygame.scrap.put_text(text)
                if event.key == self.style["paste_key"]:
                    text = pygame.scrap.get_text()
                    if self._selection_start is not None:
                        self.delete_selection()
                    if (cl := self.style["characters_limit"]) is not None:
                        text = text[: cl - len(self._text)]
                    self.insert(text)
                if event.key == self.style["cut_key"]:
                    self._history_save()
                    text = self.get_selection()
                    pygame.scrap.put_text(text)
                    self.delete_selection()
                if event.key == self.style["undo_key"]:
                    self.undo()
                if event.key == self.style["redo_key"]:
                    self.redo()
            moved = False
            control = event.mod & pygame.KMOD_CTRL
            if event.mod & pygame.KMOD_SHIFT:
                if event.key == pygame.K_LEFT:
                    if self._selection_start is None:
                        self._selection_start = self.cursor
                    self.move_cursor(self._get_move_amount(control, -1))
                    self._set_cursor_on()
                    moved = True
                if event.key == pygame.K_RIGHT:
                    if self._selection_start is None:
                        self._selection_start = self.cursor
                    self.move_cursor(self._get_move_amount(control, 1))
                    self._set_cursor_on()
                    moved = True
            if event.key == pygame.K_LEFT and not moved:
                if self._selection_start is not None:
                    if self.cursor == self._selection_start:
                        self.move_cursor(self._get_move_amount(control, -1))
                    self.cancel_selection()
                else:
                    self.move_cursor(self._get_move_amount(control, -1))
                self._set_cursor_on()
            if event.key == pygame.K_RIGHT and not moved:
                if self._selection_start is not None:
                    if self.cursor == self._selection_start:
                        self.move_cursor(self._get_move_amount(control, 1))
                    self.cancel_selection()
                else:
                    self.move_cursor(self._get_move_amount(control, 1))
                self._set_cursor_on()
            if event.key == pygame.K_BACKSPACE:
                if self._selection_start is not None:
                    self.delete_selection()
                else:
                    self.delete(-1)
            if event.key == pygame.K_DELETE:
                if self._selection_start is not None:
                    self.delete_selection()
                else:
                    self.delete(1)
            if event.key in [pygame.K_RETURN]:
                if self.style["target_number"]:
                    self._history_save()
                    self.text = f"{self.text_as_number}"
                    self._error = False

    def clear_history(self):
        self._history = []
        self._history_index = -1

    def undo(self):
        if not self.style["enable_history"]:
            return
        if self._history_index <= 0:
            return
        self._history_index -= 1
        self._history_apply()

    def redo(self):
        if not self.style["enable_history"]:
            return
        if self._history_index >= len(self._history) - 1:
            return
        self._history_index += 1
        self._history_apply()

    def insert(self, string: str):
        self._history_save()
        string = self._validate(string)
        if self._selection_start is not None:
            self.delete_selection()
        left, right = self._text[: self.cursor], self._text[self.cursor :]
        self._text = left + string + right
        self.cursor += len(string)
        self._check(True)

    def move_cursor(self, amount: int):
        self.cursor += amount
        self._check()

    def select(self, start: int, end: int):
        self.cursor = max(start, end)
        self._selection_start = min(start, end)

    def cancel_selection(self):
        self._selection_start = None

    def delete(self, amount: int):
        if amount == 0:
            return
        self._history_save()
        left, right = self._text[: self.cursor], self._text[self.cursor :]
        if amount > 0:
            amount = abs(amount)
            if amount > len(right):
                amount = len(right)
            newright = right[amount:]
            self._text = left + newright
        else:
            amount = abs(amount)
            if amount > len(left):
                amount = len(left)
            newleft = left[: len(left) - amount]
            self._text = newleft + right
            self.cursor -= amount
        self._check(True)

    def delete_selection(self):
        if self._selection_start is None:
            raise _error.MILIStatusError(
                "Cannot delete entryline selection with no active selection"
            )
        self._history_save()
        start, end = (
            min(self.cursor, self._selection_start),
            max(self.cursor, self._selection_start),
        )
        self._text = self.text[:start] + self.text[end:]
        self.cursor = start
        self.cancel_selection()

    def get_selection(self):
        if self._selection_start is None:
            raise _error.MILIStatusError(
                "Cannot get entryline selection with no active selection"
            )
        start, end = (
            min(self.cursor, self._selection_start),
            max(self.cursor, self._selection_start),
        )
        return self.text[start:end]

    def focus(self):
        self.focused = True
        self._set_cursor_on()

    def unfocus(self):
        self.focused = False
        self.cancel_selection()

    def _get_move_amount(self, control, direction):
        if not control:
            return direction
        amount = 0
        if direction == 1:
            if self.cursor >= len(self._text) - 1:
                return direction
            nextchar = self._text[self.cursor]
            startchar = nextchar
            while nextchar == " " if startchar == " " else nextchar != " ":
                amount += 1
                if self.cursor + amount >= len(self._text):
                    return amount
                nextchar = self._text[self.cursor + amount]
            return amount
        else:
            if self.cursor == 0:
                return direction
            curchar = self._text[self.cursor - 1]
            startchar = curchar
            while curchar == " " if startchar == " " else curchar != " ":
                amount -= 1
                if self.cursor + amount <= 0:
                    return amount
                curchar = self._text[self.cursor + amount]
            return amount + 1

    def _set_cursor_on(self):
        self._cursor_on = True
        self._cursor_time = pygame.time.get_ticks()

    def _cursor_from_pos(self, posx, add=0):
        tocheck = False
        if posx < self._cont_rect.left or posx > self._cont_rect.right:
            tocheck = True
        if posx <= self._rect.left:
            return 0, tocheck
        if posx >= self._rect.right:
            return len(self._text), tocheck
        if self._font is None:
            return 0, tocheck
        dx = posx - self._rect.x
        for i in range(len(self._text) + 1):
            tw = self._font.size(self._text[:i])[0]
            if tw >= dx:
                return i - 1 + add, tocheck
        return len(self._text), tocheck

    def _check(self, edit=False):
        self._just_checked = True
        if self.cursor < 0:
            self.cursor = 0
        if self.cursor > len(self._text):
            self.cursor = len(self._text)
        if self.style["text_anchor"] != "right":
            cursorpos = self._size - self._offset
            if cursorpos > self._cont_w - self._pad * 2:
                self._offset = self._size - (self._cont_w - self._pad * 2)
            if cursorpos < 0:
                self._offset = self._size
            if self.style["text_anchor"] == "center" and self._rect.w < (
                self._cont_w - self._pad * 2
            ):
                self._offset = 0
        else:
            cursorpos = self._cont_w - self._pad * 2 - self._size - self._offset
            if cursorpos > self._cont_w - self._pad * 2:
                self._offset = -self._size
            if cursorpos < 0:
                self._offset = -(self._size - (self._cont_w - self._pad * 2))
        if self.style["scroll"] is not None:
            self.style["scroll"].scroll_offset.x = 0
        if edit:
            self._set_cursor_on()
            self._error = False
            if self.style["text_validator"]:
                result = self.style["text_validator"](self.text)
                self._text, self._error = result[0], not result[1]
            if self.style["target_number"]:
                self.text_as_number

    def _validate(self, text):
        text = text.replace("\n", "")
        if self.style["validator_lowercase"]:
            text = text.lower()
        if self.style["validator_uppercase"]:
            text = text.upper()
        if (
            self.style["validator_windows_path"]
            or self.style["input_validator"]
            or self.style["target_number"]
        ):
            string = ""
            for letter in text:
                if self.style["target_number"]:
                    if letter not in "-0123456789.exoabcdefABCDEF":
                        continue
                    if self.style["number_integer"] and letter == ".":
                        continue
                if self.style["validator_windows_path"] and letter in '<>:"/\\|?*':
                    continue
                if self.style["input_validator"]:
                    res = self.style["input_validator"](letter)
                    if res is None:
                        continue
                    string += res
                else:
                    string += letter
            text = string
        return text

    def _history_save(self):
        if not self.style["enable_history"]:
            return
        state = {
            "text": self._text,
            "cursor": self.cursor,
            "selection": self._selection_start,
            "error": self._error,
            "offset": self._offset,
        }
        if len(self._history) <= 0:
            self._history.append(state)
            self._history_index = 0
        else:
            if self._history_index < len(self._history) - 1:
                self._history = self._history[: self._history_index]
            self._history.append(state)
            self._history_index += 1
        if self.style["history_limit"] is None:
            return
        if len(self._history) > abs(self.style["history_limit"]):
            self._history = self._history[
                len(self._history) - abs(self.style["history_limit"]) :
            ]

    def _history_apply(self):
        state = self._history[self._history_index]
        self._text = state["text"]
        self.cursor = state["cursor"]
        self._selection_start = state["selection"]
        self._error = state["error"]
        self._offset = state["offset"]
