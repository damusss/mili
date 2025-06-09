import pygame
import typing
from mili import _core
from mili import typing as _typing
from mili import error as _error
from mili import icon as _icon

if typing.TYPE_CHECKING:
    from mili.mili import MILI


class _MenuContextManager:
    def __init__(self, parent: "ContextMenu|None", element):
        self._parent = parent
        self._element = element

    def __enter__(
        self,
    ):
        if self._element is None:
            return self
        self._element.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        if self._parent is None:
            return
        self._parent._id_stack.pop()
        if len(self._parent._id_stack) > 0:
            self._parent._id = self._parent._id_stack[-1]
        else:
            self._parent._id = None
        self._parent._menu_rect_stack.pop()
        if len(self._parent._menu_rect_stack) > 0:
            self._parent._menu_rect = self._parent._menu_rect_stack[-1]
        else:
            self._parent._menu_rect = None
        last = self._parent._mid_stack.pop()
        self._parent._mili._ctx._id = last
        self._element.__exit__()


class _RowContextManager:
    def __init__(self, parent: "ContextMenu|None", element):
        self._parent = parent
        self._element = element
        if self._parent is not None:
            self._parent._row = True

    def __enter__(
        self,
    ):
        if self._element is None:
            return self
        self._element.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        if self._parent is None:
            return
        self._parent._row = False
        self._element.__exit__()


class ContextMenu:
    def __init__(
        self, mili: "MILI", style: _typing.ContextMenuStyleLike | dict | None = None
    ):
        self._mili = mili
        if style is None:
            style = {}
        default = style.get("default_icons", {})
        self.style: _typing.ContextMenuStyleLike = {
            "bg_color": style.get("bg_color", (24, 24, 24)),
            "clamp_size": style.get("clamp_size", None),
            "hover_color": style.get("hover_color", (40, 40, 40)),
            "icon_style": style.get("icon_style", {}),
            "outline_color": style.get("outline_color", (40, 40, 40)),
            "text_style": style.get("text_style", {}),
            "label_height": style.get("label_height", None),
            "icon_height": style.get("icon_height", 20),
            "menu_style": style.get(
                "menu_style",
                {
                    "padx": 3,
                    "pady": 3,
                    "spacing": 1,
                    "resizex": True,
                    "default_align": "center",
                    "anchor": "center",
                },
            ),
            "row_style": style.get(
                "row_style",
                {
                    "pad": 1,
                    "spacing": 1,
                    "anchor": "center",
                    "default_align": "center",
                },
            ),
            "items_update_id": style.get("items_update_id", "cursor"),
            "separator_style": style.get(
                "separator_style",
                {
                    "size": 2,
                    "padx": 0,
                    "color": style.get("outline_color", (40, 40, 40)),
                },
            ),
            "menu_border_radius": style.get("menu_border_radius", 7),
            "hover_border_radius": style.get("hover_border_radius", 7),
            "menu_width": style.get("menu_width", 0),
            "shadow_color": style.get("shadow_color", (0, 0, 0, 85)),
            "menu_dist": style.get("menu_dist", 3),
            "default_icons": {
                "arrow_left": default.get("arrow_left", "chevron_left"),
                "arrow_right": default.get("arrow_right", "chevron_right"),
                "checkbox_empty": default.get(
                    "checkbox_empty", "check_box_outline_blank"
                ),
                "checkbox_full": default.get("checkbox_full", "check_box"),
            },
            "submenu_on_hover": style.get("submenu_on_hover", True),
            "google_icon_color": style.get("google_icon_color", "default"),
            "item_bg_color": style.get("item_bg_color", None),
        }
        self.close()

    def close(self):
        self._id_stack = []
        self._id = None
        self._next_id = None
        self._parent_id = None
        self._clamp_pos = {}
        self._ticks = {}
        self._last_i: dict[typing.Any, typing.Any] = {None: -1}
        self._item_i: dict[typing.Any, typing.Any] = {None: 0}
        self._open = {}
        self._menu_rect_stack = []
        self._menu_rect = None
        self._global_i = 0
        self._children = {}
        self._label_rects = {}
        self._next_submenu = False
        self._menu_rects = {}
        self._row = False
        self._mid_stack = []
        self._menu_directions = {}
        self._level_stack = []
        self._label_hover = False
        self._label_hover_change = False
        self._pad = 1
        self._arrow_size = 0
        self.opened = False

    def open(self):
        self.close()
        self.opened = True

    def toggle(self):
        prev = self.opened
        self.close()
        self.opened = not prev

    def collidepoint(self, point):
        for _id, rect in self._menu_rects.items():
            _open = self._open.get(_id, False) or _id == "__contextmenu__"
            if _open:
                if rect.collidepoint(point):
                    return True
        return False

    def begin(
        self,
        pos: pygame.typing.SequenceLike[float] = (0, 0),
        parent_id: int | None = None,
        default_bg: bool = True,
    ):
        if not self.opened:
            return _MenuContextManager(None, None)
        self._mid_stack.append(self._mili._ctx._id)
        self._mili._ctx._id = 10**6 + 1000 * len(self._id_stack)
        self._id = "__contextmenu__"
        if self._id not in self._level_stack:
            self._level_stack.append(self._id)
        if self._id not in self._ticks:
            self._ticks[self._id] = 0
        if self._id not in self._children:
            self._children[self._id] = []
        self._id_stack: list[typing.Any] = [self._id]
        self._label_height_stack = []
        self._label_height = 0
        self._last_i[self._id] = self._item_i.get(self._id, 0) - 1
        self._item_i[self._id] = 0
        new_pos = None
        if self._id in self._clamp_pos:
            new_pos = self._clamp_pos[self._id]
        extra_style = {}
        if parent_id:
            extra_style["parent_id"] = parent_id
        if self.style["menu_width"] == 0:
            extra_style["resizex"] = True
        cont = self._mili.begin(
            (pos if new_pos is None else new_pos, (self.style["menu_width"], 0)),
            {
                "z": 9999 + self._global_i,
                "ignore_grid": True,
                "resizey": True,
                "size_clamp": {"min": (self.style["menu_width"], None)},
            }
            | extra_style
            | self.style["menu_style"],
        )
        self._pad = cont.data.grid.padx
        if default_bg:
            self._menu_bg()
        rect = cont.data.rect
        clamped = rect

        if (
            self.style["clamp_size"] is not None
            and self._ticks[self._id] > 0
            and rect.size > (0, 0)
        ):
            clamped = rect.clamp(((0, 0), self.style["clamp_size"]))
            if clamped.x < 0:
                clamped.x = 0
            if clamped.y < 0:
                clamped.y = 0
            self._clamp_pos[self._id] = clamped.topleft
        self._menu_rect = clamped
        self._menu_rect_stack = [self._menu_rect]
        self._menu_rects[self._id] = self._menu_rect
        self._ticks[self._id] += 1
        self._item_i[self._id] = 0
        self._parent_id = cont.data.parent_id
        return _MenuContextManager(self, cont)

    def begin_submenu(self, default_bg: bool = True):
        if self._next_id not in self._label_rects or self._menu_rect is None:
            raise _error.MILIStatusError(
                "You must call begin and label_submenu before this method"
            )
        if self._row:
            raise _error.MILIStatusError("You cannot add submenus inside rows")
        self._mid_stack.append(self._mili._ctx._id)
        self._mili._ctx._id = 10**6 + 1000 * len(self._id_stack)
        parent = self._id
        self._id = self._next_id
        if len(self._level_stack) > 0:
            if self._id not in self._level_stack:
                self._level_stack.append(self._id)
        if self._id not in self._children[parent]:
            self._children[parent].append(self._id)
        if self._id not in self._menu_directions:
            self._menu_directions[self._id] = "right"
        if self._id not in self._children:
            self._children[self._id] = []
        if self._id not in self._ticks:
            self._ticks[self._id] = 0
        self._id_stack.append(self._id)
        self._last_i[self._id] = self._item_i.get(self._id, 1) - 1
        new_pos = None
        if self._id in self._clamp_pos:
            new_pos = self._clamp_pos[self._id]
        extra_style = {}
        if self.style["menu_width"] == 0:
            extra_style["resizex"] = True
        pos = (
            self._label_rects[self._id].topright
            + pygame.Vector2(self._menu_rect.topleft)
            + pygame.Vector2(self.style["menu_dist"] + self._pad, 0)
        )
        cont = self._mili.begin(
            (new_pos if new_pos is not None else pos, (self.style["menu_width"], 0)),
            {
                "z": self._global_i + 9999,
                "ignore_grid": True,
                "resizey": True,
                "size_clamp": {"min": (self.style["menu_width"], None)},
                "parent_id": self._parent_id,
            }
            | extra_style
            | self.style["menu_style"],
        )
        if default_bg:
            self._menu_bg()
        rect = cont.data.rect
        clamped = rect
        if (
            self.style["clamp_size"] is not None
            and self._ticks[self._id] > 0
            and rect.size > (0, 0)
            and self._id not in self._clamp_pos
        ):
            clamped = rect.clamp(((0, 0), self.style["clamp_size"]))
            if clamped.x != rect.x:
                clamped.x = self._menu_rect.x - rect.w - self.style["menu_dist"]
                self._menu_directions[self._id] = "left"
            if clamped.x < 0:
                clamped.x = 0
            if clamped.y < 0:
                clamped.y = 0
            self._clamp_pos[self._id] = clamped.topleft
        self._item_i[self._id] = 0
        self._menu_rect = clamped
        self._menu_rect_stack.append(clamped)
        self._menu_rects[self._id] = clamped
        self._ticks[self._id] += 1
        self._global_i += 1000
        self._pad = cont.data.grid.padx
        return _MenuContextManager(self, cont)

    def checkbox(
        self,
        text: str,
        value: bool,
        icon_side: typing.Literal["left", "right"] = "left",
    ):
        if not self.opened:
            return False, False
        if self._menu_rect is None:
            raise _error.MILIStatusError("You must call begin before this method")
        if self._row:
            raise _error.MILIStatusError("You cannot add checkboxes inside rows")
        self._global_i += 1
        extra_style = {}
        h = None
        if self.style["label_height"] is None:
            extra_style["growy"] = True
            h = self.style["label_height"]
        tstyle = self.style["text_style"] | extra_style
        tsize = self._mili.text_size(text, tstyle, True)
        if not h:
            h = tsize.y
        with self._mili.begin(
            None,
            {
                "fillx": True,
                "resizey": True,
                "axis": "x",
                "pady": 0,
                "padx": 1,
                "size_clamp": {"min": (tsize.x + h * 2 + 2, None)},
                "update_id": self.style["items_update_id"],
            },
        ) as row:
            rh = row.data.rect.h
            if row.hovered:
                fbr = self._get_border_radius()
                self._mili.rect(
                    {"color": self.style["hover_color"], "border_radius": fbr}
                )
            elif self.style["item_bg_color"] is not None:
                fbr = self._get_border_radius()
                self._mili.rect(
                    {"color": self.style["item_bg_color"], "border_radius": fbr}
                )
            if icon_side == "left":
                self._icon(
                    rh,
                    self._get_icon("checkbox_full" if value else "checkbox_empty"),
                )
            else:
                self._mili.element((0, 0, rh, 0), {"filly": True, "blocking": False})
            with self._mili.element(
                (
                    0,
                    0,
                    0,
                    self.style["label_height"]
                    if self.style["label_height"] is not None
                    else 0,
                ),
                {"fillx": True, "blocking": False},
            ):
                self._mili.text(text, tstyle)
            if icon_side == "right":
                self._icon(
                    rh,
                    self._get_icon("checkbox_full" if value else "checkbox_empty"),
                )
            else:
                self._mili.element((0, 0, rh, 0), {"filly": True, "blocking": False})
            self._item_i[self._id] += 1
            retval = value
            change = False
            if row.left_clicked:
                self._close_children(self._id)
                retval = not value
                change = True
            return change, retval

    def label(self, text: str, clickable=True):
        if not self.opened:
            return False
        if self._menu_rect is None:
            raise _error.MILIStatusError("You must call begin before this method")
        self._global_i += 1
        extra_style = {}
        if self.style["label_height"] is None:
            extra_style["growy"] = True
        tstyle = self.style["text_style"] | extra_style
        tsize = self._mili.text_size(text, tstyle, True)
        with self._mili.element(
            (
                0,
                0,
                0,
                self.style["label_height"]
                if self.style["label_height"] is not None
                else 0,
            ),
            {
                "fillx": True,
                "size_clamp": {"min": (tsize.x, None)},
                "update_id": self.style["items_update_id"] if clickable else None,
            },
        ) as element:
            if element.hovered and clickable:
                fbr = self._get_border_radius()
                self._mili.rect(
                    {"color": self.style["hover_color"], "border_radius": fbr}
                )
            elif self.style["item_bg_color"] is not None:
                fbr = self._get_border_radius()
                self._mili.rect(
                    {"color": self.style["item_bg_color"], "border_radius": fbr}
                )
            self._mili.text(text, tstyle)
            self._item_i[self._id] += 1
            retval = element.left_clicked and clickable
            self._label_hover = element.hovered and clickable
            self._label_hover_change = (
                element.just_hovered and self.style["submenu_on_hover"]
            )
            if retval or self._label_hover_change:
                self._close_children(self._id)
            return retval

    def icon_label(
        self,
        text: str,
        icon: pygame.Surface | str,
        side: typing.Literal["left", "right"] = "left",
        clickable=True,
    ):
        if not self.opened:
            return False
        if self._menu_rect is None:
            raise _error.MILIStatusError("You must call begin before this method")
        if isinstance(icon, str):
            icon = _icon.get_google(icon, self.style["google_icon_color"])
        self._global_i += 1
        extra_style = {}
        h = None
        if self.style["label_height"] is None:
            extra_style["growy"] = True
            h = self.style["label_height"]
        tstyle = self.style["text_style"] | extra_style
        tsize = self._mili.text_size(text, tstyle, True)
        if not h:
            h = tsize.y
        with self._mili.begin(
            None,
            {
                "fillx": True,
                "resizey": True,
                "axis": "x",
                "pady": 0,
                "padx": 1,
                "size_clamp": {"min": (tsize.x + h * 2 + 2, None)},
                "update_id": self.style["items_update_id"] if clickable else None,
            },
        ) as row:
            rh = row.data.rect.h
            if row.hovered and clickable:
                fbr = self._get_border_radius()
                self._mili.rect(
                    {"color": self.style["hover_color"], "border_radius": fbr}
                )
            elif self.style["item_bg_color"] is not None:
                fbr = self._get_border_radius()
                self._mili.rect(
                    {"color": self.style["item_bg_color"], "border_radius": fbr}
                )
            if side == "left":
                self._icon(rh, icon)
            else:
                self._mili.element((0, 0, rh, 0), {"filly": True, "blocking": False})
            with self._mili.element(
                (
                    0,
                    0,
                    0,
                    self.style["label_height"]
                    if self.style["label_height"] is not None
                    else 0,
                ),
                {"fillx": True, "blocking": False},
            ) as element:
                if element.hovered and clickable:
                    fbr = self._get_border_radius()
                    self._mili.rect(
                        {"color": self.style["hover_color"], "border_radius": fbr}
                    )
                self._mili.text(text, tstyle)
            if side == "right":
                self._icon(rh, icon)
            else:
                self._mili.element((0, 0, rh, 0), {"filly": True, "blocking": False})
            self._item_i[self._id] += 1
            retval = row.left_clicked and clickable

            self._label_hover = row.hovered and clickable
            self._label_hover_change = (
                row.just_hovered and self.style["submenu_on_hover"]
            )
            if retval or self._label_hover_change:
                self._close_children(self._id)
            return retval

    def label_submenu(
        self,
        text: str,
        icon: pygame.Surface | None = None,
        icon_side: typing.Literal["left", "right"] = "left",
        arrows: bool = True,
    ):
        if not self.opened:
            return False
        if self._row:
            raise _error.MILIStatusError("You cannot add label submenus inside rows")
        self._next_id = str(self._id) + text
        self._label_hover = False
        tsize = self._mili.text_size(text, self.style["text_style"], True)
        with self._mili.begin(
            None,
            {
                "axis": "x",
                "anchor": "center",
                "default_align": "center",
                "pad": 0,
                "spacing": 0,
                "resizey": True,
                "fillx": True,
                "size_clamp": {"min": (tsize.x + self._arrow_size * 2, None)},
            },
        ) as row:
            fbr = self._get_border_radius()
            h = row.data.rect.h
            w = h * 0.75
            hover = False
            retvalue = False
            if arrows:
                retvalue = self._arrow("left", w, h)
                if self._mili.last_interaction and self._mili.last_interaction.hovered:
                    hover = True
            self._next_submenu = self._next_id
            retvalue = (
                self.label(text)
                if icon is None
                else self.icon_label(text, icon, icon_side)
            ) or retvalue
            if self._label_hover:
                hover = True
            if self._label_hover_change and self.style["submenu_on_hover"]:
                retvalue = True
            if self._next_id not in self._label_rects and self._ticks[self._id] > 1:
                self._label_rects[self._next_id] = row.data.rect
            self._next_submenu = None
            if arrows:
                retvalue = self._arrow("right", w, h) or retvalue
                if self._mili.last_interaction and self._mili.last_interaction.hovered:
                    hover = True
            if hover:
                self._mili.rect(
                    {
                        "color": self.style["hover_color"],
                        "border_radius": fbr,
                        "element_id": row.data.id,
                    }
                )
        if retvalue:
            if self._next_id in self._open:
                self._set_submenu_status(self._next_id, not self._open[self._next_id])
            else:
                self._set_submenu_status(self._next_id, True)

        return self._open.get(self._next_id, False)

    def icon(self, image: pygame.Surface | str, clickable=True):
        if not self.opened:
            return False
        if self._menu_rect is None:
            raise _error.MILIStatusError("You must call begin before this method")
        if isinstance(image, str):
            image = _icon.get_google(image, self.style["google_icon_color"])
        self._global_i += 1
        with self._mili.element(
            (0, 0, 0, self.style["icon_height"]),
            {
                "fillx": True,
                "update_id": self.style["items_update_id"] if clickable else None,
                "align": "center",
            },
        ) as element:
            if element.hovered and clickable:
                fbr = self._get_border_radius()
                self._mili.rect(
                    {"color": self.style["hover_color"], "border_radius": fbr}
                )
            elif self.style["item_bg_color"] is not None:
                fbr = self._get_border_radius()
                self._mili.rect(
                    {"color": self.style["item_bg_color"], "border_radius": fbr}
                )
            self._mili.image(image, self.style["icon_style"])
            self._item_i[self._id] += 1
            retval = element.left_clicked and clickable
            if retval:
                self._close_children(self._id)
            return retval

    def row(self):
        if not self.opened:
            return _RowContextManager(None, None)
        if self._menu_rect is None:
            raise _error.MILIStatusError("You must call begin before this method")
        if self._row:
            raise _error.MILIStatusError("You cannot add rows inside rows")
        self._global_i += 1
        return _RowContextManager(
            self,
            self._mili.begin(
                None,
                {
                    "fillx": True,
                    "axis": "x",
                    "resizey": True,
                }
                | self.style["row_style"],
            ),
        )

    def separator(self):
        if not self.opened:
            return
        if self._menu_rect is None:
            raise _error.MILIStatusError("You must call begin before this method")
        if self._row:
            raise _error.MILIStatusError("You cannot add separators inside rows")
        self._global_i += 1
        self._item_i[self._id] += 1
        return self._mili.hline_element(
            self.style["separator_style"],
            (0, 0, 0, float(self.style["separator_style"].get("size", 1))),
            {"fillx": True},
        )

    def _get_icon(self, name):
        value = self.style["default_icons"][name]
        return _icon._get_icon(value)

    def _icon(self, h, surf):
        with self._mili.element((0, 0, h, 0), {"filly": True, "blocking": False}):
            self._mili.image(
                surf,
                self.style["icon_style"],
            )

    def _arrow(self, _dir, w, h):
        with self._mili.element(
            (0, 0, w, h), {"update_id": self.style["items_update_id"]}
        ) as element:
            icon = self._get_icon(f"arrow_{_dir}")
            if isinstance(icon, pygame.Surface):
                self._mili.image(icon)
            if self._arrow_size == 0:
                self._arrow_size = element.data.rect.w
            return element.left_clicked

    def _set_submenu_status(self, _id, _open=False):
        self._open[_id] = _open
        if _id in self._ticks:
            del self._ticks[_id]
        if not _open:
            self._level_stack = []
            self._close_children(_id)

    def _close_children(self, _id):
        if _id in self._children:
            for children in self._children[_id]:
                if self._next_submenu == children:
                    continue
                self._open[children] = False
                self._level_stack = []
                if children in self._ticks:
                    del self._ticks[children]
                self._close_children(children)

    def _menu_bg(self):
        br = self.style["menu_border_radius"]
        _dir = self._menu_directions.get(self._id, None)
        if _dir is not None:
            if _dir == "right":
                br = (0, br, br, br)
            else:
                br = (br, 0, br, br)
        self._mili.rect(
            {
                "color": self.style["bg_color"],
                "border_radius": br,
            }
        )
        if self.style["shadow_color"] is not None:
            try:
                idx = self._level_stack.index(self._id)
                if idx < len(self._level_stack) - 2:
                    self._mili.image(
                        _core._globalctx._sample_surf,
                        {
                            "fill": True,
                            "fill_color": self.style["shadow_color"],
                            "cache": "auto",
                            "border_radius": br,
                            "draw_above": True,
                        },
                    )
            except ValueError:
                ...
        self._mili.rect(
            {
                "color": self.style["outline_color"],
                "outline": 1,
                "border_radius": br,
                "draw_above": True,
            }
        )

    def _get_border_radius(self):
        br = self.style["menu_border_radius"]
        hbr = self.style["hover_border_radius"]
        fbr = hbr
        _dir = self._menu_directions.get(self._id, None)
        if not self._row and self._next_submenu is None:
            if self._item_i[self._id] == 0:
                fbr = (
                    0 if _dir == "right" else br,
                    0 if _dir == "left" else br,
                    hbr,
                    hbr,
                )
            elif self._item_i[self._id] == self._last_i.get(self._id, -1):
                fbr = (hbr, hbr, br, br)
        return fbr
