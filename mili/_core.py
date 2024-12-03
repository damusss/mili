import pygame
import typing
from mili import error
from mili import data as _data
from mili import typing as _typing
from mili import _coreutils

if typing.TYPE_CHECKING:
    from mili import MILI as _MILI

__all__ = ()


class _globalctx:
    _font_cache = {}
    _component_types: dict[str, str | _typing.ComponentProtocol] = dict.fromkeys(
        ["rect", "circle", "line", "polygon", "line", "text", "image"], "builtin"
    )
    _mili_stack = []
    _mili: "_MILI|None" = None
    _update_ids: dict[str, list[typing.Callable]] = {}

    @classmethod
    def _register_update_id(cls, uid, method):
        if uid is None:
            return
        if uid not in cls._update_ids:
            cls._update_ids[uid] = []
        cls._update_ids[uid].append(method)


class _ctx:
    def __init__(self, mili: "_MILI"):
        self._coreutils = _coreutils
        self._mili = mili
        self._parent: dict[str, typing.Any] = {
            "rect": pygame.Rect(0, 0, 1, 1),
            "abs_rect": pygame.Rect(0, 0, 1, 1),
            "style": {},
            "id": 0,
            "children": [],
            "children_grid": [],
            "components": [],
            "parent": None,
            "top": False,
            "z": 0,
            "hovered": False,
        }
        self._stack: dict[str, typing.Any] = self._parent
        self._parents_stack = [self._stack]
        self._id = 1
        self._memory: dict[int, dict[str, typing.Any]] = {}
        self._old_data: dict[int, dict[str, typing.Any]] = {}
        self._interaction_cache: dict[int, _data.Interaction] = {}
        self._element: dict[str, typing.Any] = self._parent
        self._canva: pygame.Surface | None = None
        self._canva_rect: pygame.Rect | None = None
        self._abs_hovered: list[dict[str, typing.Any]] = []
        self._started = False
        self._started_pressing_element = None
        self._started_pressing_button = -1
        self._z = 0
        self._offset = pygame.Vector2()
        self._mouse_pos = pygame.Vector2()
        self._mouse_rel = pygame.Vector2()
        self._global_mouse = False
        self._gmouse_pressed = [False] * 5
        self._gmouse_just_pressed = [False] * 5
        self._gmouse_just_released = [False] * 5
        self._get_just_pressed_func: typing.Callable = pygame.mouse.get_just_pressed
        self._get_just_released_func: typing.Callable = pygame.mouse.get_just_released
        self._image_layer_caches: list[_data.ImageLayerCache] = []
        self._dummy_interaction = _data.Interaction(
            mili, False, -1, -1, -1, False, False, False, False, {}
        )
        self._default_styles = {
            "element": {},
            "rect": {},
            "circle": {},
            "polygon": {},
            "line": {},
            "text": {},
            "image": {},
        }

    def _get_element(
        self, rect: pygame.typing.RectLike | None, arg_style
    ) -> tuple[dict[str, typing.Any], "_data.Interaction"]:
        if arg_style is None:
            arg_style = {}
        style = self._default_styles["element"].copy()
        style.update(arg_style)
        if rect is None:
            rect = (0, 0, 0, 0)
        rect = pygame.Rect(rect)
        parent = self._parent
        if "parent_id" in style:
            if style["parent_id"] in self._memory:
                parent = self._memory[style["parent_id"]]
            elif style["parent_id"] == 0:
                parent = self._stack
        element: dict[str, typing.Any] = {
            "rect": rect,
            "abs_rect": rect.copy(),
            "style": style,
            "id": self._id,
            "children": [],
            "components": [],
            "children_grid": [],
            "parent": parent,
            "top": False,
            "z": 1,
            "hovered": False,
        }
        interaction = self._get_interaction(element)
        self._memory[self._id] = element
        if parent:
            z = self._z
            if "z" in style:
                z = style["z"]
            if parent["z"] > z:
                z = parent["z"] + len(parent["children"]) + 1
            parent["children"].append(element)
            if not self._style_val(style, "element", "ignore_grid", False):
                parent["children_grid"].append(element)
            element["z"] = z + 1
        self._id += 1
        self._element = element
        self._z += 1
        return element, interaction

    def _style_val(self, style: dict, major, minor, default):
        return style.get(minor, self._default_styles[major].get(minor, default))

    def _organize_grid(
        self,
        element,
        a,
        oa,
        av,
        oav,
        rect,
        style,
        pada,
        padoa,
        space,
        anchor,
        resizeoa,
        resizea,
        minresizeoa,
        minresizea,
        maxresizea,
        maxresizeoa,
        padded_oa,
        padded_a,
        children,
    ):
        grid_align = self._style_val(style, "element", "grid_align", "first")
        _coreutils._check_align(grid_align)
        spacea = _coreutils._abs_perc(
            self._style_val(style, "element", f"grid_space{a}", space),
            getattr(rect, av),
        )
        spaceoa = _coreutils._abs_perc(
            self._style_val(style, "element", f"grid_space{oa}", space),
            getattr(rect, oav),
        )

        changed = []
        line_elements = []
        lines = []
        line_size_a = 0
        longest_line_size_a = 0
        current_pos_oa = padoa
        longest_line_size_oa = 0
        for child in children:
            ch_fill_a = self._style_val(child["style"], "element", f"fill{a}", False)
            ch_fill_oa = self._style_val(child["style"], "element", f"fill{oa}", False)

            if ch_fill_a is not False:
                if ch_fill_a is True:
                    ch_fill_a = "100"
                fill_a_v = _coreutils._abs_perc(ch_fill_a, getattr(rect, av))
                setattr(child["rect"], av, fill_a_v)

            if ch_fill_oa is not False:
                if ch_fill_oa is True:
                    ch_fill_oa = "100"
                fill_oa_v = _coreutils._abs_perc(ch_fill_oa, getattr(rect, oav))
                setattr(child["rect"], oav, fill_oa_v)

            if ch_fill_a is not False or ch_fill_oa is not False:
                changed.append(child)

        for child in children:
            ch_rect = child["rect"]
            add = spacea
            if line_size_a <= 0:
                add = 0
            hypot_length_a = line_size_a + add + getattr(ch_rect, av)

            if hypot_length_a <= padded_a:
                line_elements.append(child)
                line_size_a = hypot_length_a
                if line_size_a > longest_line_size_a:
                    longest_line_size_a = line_size_a
                if getattr(ch_rect, oav) > longest_line_size_oa:
                    longest_line_size_oa = getattr(ch_rect, oav)
            else:
                if (
                    resizea
                    and hypot_length_a + pada * 2 <= maxresizea
                    and hypot_length_a + pada * 2 >= minresizea
                    and hypot_length_a > longest_line_size_a
                ):
                    longest_line_size_a = hypot_length_a
                    setattr(rect, av, hypot_length_a + pada * 2)
                    padded_a = hypot_length_a
                    line_elements.append(child)
                    line_size_a = hypot_length_a
                    if getattr(ch_rect, oav) > longest_line_size_oa:
                        longest_line_size_oa = getattr(ch_rect, oav)
                else:
                    lines.append([line_elements, longest_line_size_oa, line_size_a])
                    line_elements = []

                    line_elements.append(child)
                    longest_line_size_oa = getattr(ch_rect, oav)
                    line_size_a = getattr(ch_rect, av)
                    if current_pos_oa != padoa:
                        current_pos_oa += spaceoa
                    current_pos_oa += longest_line_size_oa

                    if (
                        resizeoa
                        and current_pos_oa + padoa * 2 <= maxresizeoa
                        and current_pos_oa + padoa * 2 >= minresizeoa
                    ):
                        setattr(rect, oav, current_pos_oa + padoa * 2)
                        padded_oa = current_pos_oa

        if len(line_elements) > 0:
            lines.append([line_elements, longest_line_size_oa, line_size_a])
            if current_pos_oa != padoa:
                current_pos_oa += spaceoa
            current_pos_oa += longest_line_size_oa
            if (
                resizeoa
                and current_pos_oa + padoa * 2 <= maxresizeoa
                and current_pos_oa + padoa * 2 >= minresizeoa
            ):
                setattr(rect, oav, current_pos_oa + padoa * 2)
                padded_oa = current_pos_oa

        lines_size_oa = current_pos_oa
        current_pos_oa = padoa
        spacing = spaceoa
        if anchor == "max_spacing":
            if len(lines) > 1:
                spacing = max(
                    0,
                    ((padded_oa - sum([line[1] for line in lines])) / (len(lines) - 1)),
                )
            else:
                anchor = "center"
        if anchor == "center":
            current_pos_oa = getattr(rect, oav) / 2 - lines_size_oa / 2
        if anchor == "last":
            lines = list(reversed(lines))
            current_pos_oa = padded_oa - lines_size_oa

        for elements, biggest_size, line_size in lines:
            current_pos_a = pada
            spacinga = spacea
            if grid_align == "max_spacing":
                if len(elements) > 1:
                    spacinga = max(
                        0,
                        (padded_a - sum([getattr(e["rect"], av) for e in elements]))
                        / (len(elements) - 1),
                    )
                else:
                    grid_align = "center"
            if grid_align == "last":
                current_pos_a = padded_a - line_size
            if grid_align == "center":
                current_pos_a = getattr(rect, av) / 2 - line_size / 2
            for el in elements:
                el_rect = el["rect"]
                setattr(el_rect, oa, current_pos_oa)
                setattr(el_rect, a, current_pos_a)
                current_pos_a += getattr(el_rect, av)
                current_pos_a += spacinga
            current_pos_oa += biggest_size
            current_pos_oa += spacing

        element["grid"] = {
            f"overflow{oa}": max(0, lines_size_oa - padded_oa),
            f"overflow{a}": max(0, longest_line_size_a - padded_a),
            f"pad{a}": pada,
            f"pad{oa}": padoa,
            "spacing": space,
        }

        for el in list(changed):
            self._organize_element(el)

    def _organize_element(self, element: dict[str, typing.Any]):
        style = element["style"]
        rect = element["rect"]
        children = element["children_grid"]
        a = self._style_val(style, "element", "axis", "y")
        if a not in ["x", "y"]:
            raise error.MILIValueError(f"Invalid axis {a}")
        oa = "x" if a == "y" else "y"
        av = "w" if a == "x" else "h"
        oav = "w" if av == "h" else "h"
        pad = self._style_val(style, "text", "pad", 5)
        pada = self._style_val(style, "element", f"pad{a}", pad)
        padoa = self._style_val(style, "element", f"pad{oa}", pad)
        pada, padoa = (
            _coreutils._abs_perc(pada, getattr(rect, av)),
            _coreutils._abs_perc(padoa, getattr(rect, oav)),
        )
        space = _coreutils._abs_perc(
            self._style_val(style, "element", "spacing", 3), getattr(rect, av)
        )
        anchor = self._style_val(style, "element", "anchor", "first")
        def_align = self._style_val(style, "element", "default_align", "first")
        _coreutils._check_align(anchor)
        resizeoa = self._style_val(style, "element", f"resize{oa}", False)
        resizea = self._style_val(style, "element", f"resize{a}", False)
        if isinstance(resizea, dict):
            maxv = resizea.get("max", float("inf"))
            minv = resizea.get("min", 0)
            minresizea = _coreutils._abs_perc(minv, getattr(rect, av))
            maxresizea = _coreutils._abs_perc(maxv, getattr(rect, av))
            resizea = True
        else:
            resizea = bool(resizea)
            minresizea = 0
            maxresizea = float("inf")
        if isinstance(resizeoa, dict):
            maxv = resizeoa.get("max", float("inf"))
            minv = resizeoa.get("min", 0)
            minresizeoa = _coreutils._abs_perc(minv, getattr(rect, oav))
            maxresizeoa = _coreutils._abs_perc(maxv, getattr(rect, oav))
            resizeoa = True
        else:
            resizeoa = bool(resizeoa)
            minresizeoa = 0
            maxresizeoa = float("inf")
        _filloa, _filla = (
            self._style_val(style, "element", f"fill{oa}", False),
            self._style_val(style, "element", f"fill{a}", False),
        )
        if resizeoa and bool(_filloa) is not False:
            raise error.MILIIncompatibleStylesError(
                f"Cannot have resize{oa} True and fill{oa} not False"
            )
        if resizea and bool(_filla) is not False:
            raise error.MILIIncompatibleStylesError(
                f"Cannot have resize{a} True and fill{a} not False"
            )

        padded_oa = getattr(rect, oav) - padoa * 2
        padded_a = getattr(rect, av) - pada * 2

        grid = self._style_val(style, "element", "grid", False)
        if grid:
            self._organize_grid(
                element,
                a,
                oa,
                av,
                oav,
                rect,
                style,
                pada,
                padoa,
                space,
                anchor,
                resizeoa,
                resizea,
                minresizeoa,
                minresizea,
                maxresizea,
                maxresizeoa,
                padded_oa,
                padded_a,
                children,
            )
            return

        elements_with_filloa = []
        elements_with_filla = []
        biggest_oa = 0
        fixed_elements_a = 0

        for el in children:
            el_rect = el["rect"]
            el_style = el["style"]
            el_filloa = self._style_val(el_style, "element", f"fill{oa}", False)
            el_filla = self._style_val(el_style, "element", f"fill{a}", False)
            if bool(el_filloa) is False and getattr(el_rect, oav) > biggest_oa:
                biggest_oa = getattr(el_rect, oav)
            if bool(el_filloa) is True:
                elements_with_filloa.append(el)
            fixed_elements_a += space
            if bool(el_filla) is False:
                fixed_elements_a += getattr(el_rect, av)
            else:
                elements_with_filla.append(el)
        fixed_elements_a -= space
        available_to_filla = max(0, padded_a - fixed_elements_a)

        if resizeoa and biggest_oa > 0:
            setattr(
                rect, oav, min(max(biggest_oa + padoa * 2, minresizeoa), maxresizeoa)
            )
            padded_oa = getattr(rect, oav) - padoa * 2
        if resizea and fixed_elements_a > 0:
            setattr(
                rect, av, min(max(fixed_elements_a + pada * 2, minresizea), maxresizea)
            )
            padded_a = getattr(rect, av) - pada * 2
            available_to_filla = 0

        changed = []

        for filloa_el in elements_with_filloa:
            el_rect = filloa_el["rect"]
            el_style = filloa_el["style"]
            filloa = self._style_val(el_style, "element", f"fill{oa}", False)
            if filloa is True:
                filloa = "100"
            el_filloa = _coreutils._abs_perc(filloa, padded_oa)
            setattr(el_rect, oav, el_filloa)
            changed.append(filloa_el)

        filla_totalsize = 0
        for filla_el in elements_with_filla:
            el_rect = filla_el["rect"]
            el_style = filla_el["style"]
            filla = self._style_val(el_style, "element", f"fill{a}", False)
            if filla is True:
                filla = "100"
            el_filla = _coreutils._abs_perc(
                filla,
                available_to_filla,
            )
            filla_el["filla"] = el_filla
            filla_totalsize += el_filla

        total_a = fixed_elements_a
        if filla_totalsize != 0:
            if fixed_elements_a <= padded_a:
                total_a = padded_a
            else:
                total_a = fixed_elements_a
            multiplier = 1
            if filla_totalsize > available_to_filla:
                multiplier = available_to_filla / filla_totalsize
            else:
                total_a = fixed_elements_a + filla_totalsize
            for filla_el in elements_with_filla:
                el_rect = filla_el["rect"]
                setattr(el_rect, av, filla_el["filla"] * multiplier)
                changed.append(filla_el)
                del filla_el["filla"]

        current_a = pada
        spacing = space
        if anchor == "max_spacing":
            if len(children) > 1:
                spacing = max(
                    0,
                    (
                        (padded_a - sum([getattr(e["rect"], av) for e in children]))
                        / (len(children) - 1)
                    ),
                )
            else:
                anchor = "center"
        if anchor == "last":
            current_a = getattr(rect, av) - pada - total_a
        if anchor == "center":
            current_a = getattr(rect, av) / 2 - total_a / 2
        for el in children:
            el_rect = el["rect"]
            el_style = el["style"]
            el_align = self._style_val(el_style, "element", "align", def_align)
            _coreutils._check_align(el_align)
            setattr(el_rect, a, current_a)
            current_a += getattr(el_rect, av)
            current_a += spacing
            if el_align == "first":
                setattr(el_rect, oa, padoa)
            if el_align == "last":
                setattr(
                    el_rect, "right" if a == "y" else "left", getattr(rect, oav) - padoa
                )
            if el_align == "center":
                setattr(el_rect, f"center{oa}", getattr(rect, oav) / 2)

        element["grid"] = {
            f"overflow{oa}": max(0, biggest_oa - padded_oa),
            f"overflow{a}": max(0, total_a - padded_a),
            f"pad{a}": pada,
            f"pad{oa}": padoa,
            "spacing": space,
        }

        for el in list(changed):
            self._organize_element(el)

    def _start(self, style, winpos):
        if self._canva is None:
            return
        self._parent = {
            "rect": self._canva.get_rect(),
            "abs_rect": self._canva.get_rect(),
            "style": style,
            "id": 0,
            "children": [],
            "children_grid": [],
            "components": [],
            "parent": None,
            "top": False,
            "z": 0,
            "hovered": False,
        }
        self._id = 1
        self._element = self._parent
        self._stack = self._parent
        self._parents_stack = [self._stack]
        self._abs_hovered = []
        self._started = True
        self._z = 0
        mouse_pos = (
            pygame.Vector2(pygame.mouse.get_pos(self._global_mouse)) - self._offset
        )
        if self._global_mouse:
            if winpos:
                mouse_pos -= winpos
            else:
                raise error.MILIStatusError(
                    "The window position must be provided when using the global mouse state"
                )
        self._mouse_rel = mouse_pos - self._mouse_pos
        self._mouse_pos = mouse_pos
        if 0 in self._memory:
            self._get_old_el(self._stack)
        self._memory[0] = self._stack

        if self._global_mouse:
            global_pressed = pygame.mouse.get_pressed(5, True)
            for i, (old, new) in enumerate(zip(self._gmouse_pressed, global_pressed)):
                if old == new:
                    self._gmouse_just_pressed[i] = False
                    self._gmouse_just_released[i] = False
                elif old and not new:
                    self._gmouse_just_released[i] = True
                    self._gmouse_just_pressed[i] = False
                elif new and not old:
                    self._gmouse_just_pressed[i] = True
                    self._gmouse_just_released[i] = False
            self._gmouse_pressed = global_pressed

        if (btn := _coreutils._get_first_button(self._get_just_pressed_func())) > -1:
            self._started_pressing_button = btn
        if (
            _coreutils._get_first_button(self._get_just_released_func())
            == self._started_pressing_button
        ):
            self._started_pressing_button = -1
            self._started_pressing_element = None
        for layer_cache in self._image_layer_caches:
            layer_cache._caches_activity = {}
            layer_cache._rendered = False

    def _get_just_pressed(self):
        return self._gmouse_just_pressed

    def _get_just_released(self):
        return self._gmouse_just_released

    def _check_interaction(self, element: dict[str, typing.Any]):
        blocking = self._style_val(element["style"], "element", "blocking", True)
        if not blocking and blocking is not None:
            return
        parent = element["parent"]
        clipdraw = (
            True
            if parent is None
            else self._style_val(parent["style"], "element", "clip_draw", True)
        )
        hover = element["abs_rect"].collidepoint(self._mouse_pos)
        parent_hover = True
        if parent is not None and clipdraw:
            parent_hover = parent["abs_rect"].collidepoint(self._mouse_pos)
        if hover and parent_hover:
            self._abs_hovered.append(element)

    def _get_old_el(self, element):
        old_el = self._memory[element["id"]]
        self._old_data[element["id"]] = {
            "rect": old_el["rect"],
            "abs_rect": old_el["abs_rect"],
            "components": old_el["components"],
            "children_ids": [ch["id"] for ch in old_el["children"]],
            "parent_id": old_el["parent"]["id"] if old_el["parent"] else -1,
            "grid": old_el["grid"] if "grid" in old_el else None,
        }
        return old_el

    def _get_interaction(self, element: dict[str, typing.Any]) -> "_data.Interaction":
        if element["id"] not in self._memory:
            return _coreutils._partial_interaction(self, element, False)
        old_el = self._get_old_el(element)
        absolute_hover = old_el["abs_rect"].collidepoint(self._mouse_pos)
        if old_el["top"]:
            if self._style_val(element["style"], "element", "blocking", True) is None:
                self._dummy_interaction._raw_data = element
                self._dummy_interaction._data = None
                return self._dummy_interaction
            if (
                self._started_pressing_button > -1
                and self._started_pressing_element is None
            ):
                self._started_pressing_element = element["id"]
                return _coreutils._total_interaction(
                    self,
                    element,
                    absolute_hover,
                    absolute_hover,
                    False,
                    old_el,
                )
            if (
                self._started_pressing_button > -1
                and element["id"] != self._started_pressing_element
            ):
                return _coreutils._partial_interaction(self, element, absolute_hover)
            return _coreutils._total_interaction(
                self,
                element,
                absolute_hover,
                absolute_hover,
                False,
                old_el,
            )
        else:
            if (
                self._started_pressing_button > -1
                and element["id"] == self._started_pressing_element
            ):
                return _coreutils._total_interaction(
                    self,
                    element,
                    absolute_hover,
                    False,
                    True,
                    old_el,
                )
            return _coreutils._partial_interaction(self, element, absolute_hover)

    def _add_component(self, type, data, arg_style):
        self._start_check()
        if arg_style is None:
            arg_style = {}
        style = self._default_styles[type].copy()
        style.update(arg_style)
        if not self._element:
            raise error.MILIStatusError(
                "Cannot add component if no element was created"
            )
        if type == "text":
            self._text_resize(self._element["rect"], data, style)
        compobj = _globalctx._component_types[type]
        if not isinstance(compobj, str):
            compobj.added(self, data, style, self._element)
        self._element["components"].append({"type": type, "data": data, "style": style})

    def _get_font(self, style) -> pygame.Font:
        path = self._style_val(style, "text", "name", None)
        size = self._style_val(style, "text", "size", 20)
        key = f"{path}_{size}"
        if key not in _globalctx._font_cache:
            sysfont = self._style_val(style, "text", "sysfont", False)
            func = pygame.font.SysFont if sysfont else pygame.font.Font
            font = func(path, size)
            _globalctx._font_cache[key] = font
        return _globalctx._font_cache[key]

    def _draw_comp_rect(self, data, style, el, rect: pygame.Rect):
        if self._canva is None:
            return
        pad = self._style_val(style, "rect", "pad", 0)
        padx = self._style_val(style, "rect", "padx", pad)
        pady = self._style_val(style, "rect", "pady", pad)
        padx, pady = (
            int(_coreutils._abs_perc(padx, rect.w)),
            int(_coreutils._abs_perc(pady, rect.h)),
        )
        outline = int(
            _coreutils._abs_perc(
                self._style_val(style, "rect", "outline", 0), min(rect.w, rect.h)
            )
        )
        br_style = self._style_val(style, "rect", "border_radius", 7)
        if isinstance(br_style, (int, float, str)):
            border_radius = int(_coreutils._abs_perc(br_style, min(rect.w, rect.h)))
        else:
            border_radius = [
                int(_coreutils._abs_perc(br, min(rect.w, rect.h))) for br in br_style
            ]
        color = self._style_val(style, "rect", "color", "black")
        aspect_ratio = self._style_val(style, "rect", "aspect_ratio", None)
        if aspect_ratio is None:
            draw_rect = rect.inflate(-padx * 2, -pady * 2)
        else:
            align = self._style_val(style, "rect", "align", "center")
            availx, availy = rect.w - padx * 2, rect.h - pady * 2
            rx, ry = availx, availy
            rx = availy * aspect_ratio
            if rx > availx:
                ry = availx * (1 / aspect_ratio)
                rx = availx
            draw_rect = pygame.Rect((0, 0), (rx, ry)).move_to(
                **_coreutils._align_rect(align, rect, padx, pady)
            )
        dash_size = self._style_val(style, "line", "dash_size", None)
        dash_offset = self._style_val(style, "line", "dash_offset", 0)
        _coreutils._draw_rect(
            self._canva,
            color,
            draw_rect,
            outline,
            border_radius,
            dash_size,
            dash_offset,
        )

    def _draw_comp_circle(self, data, style, el, rect: pygame.Rect):
        if self._canva is None:
            return
        pad = self._style_val(style, "circle", "pad", 0)
        padx = self._style_val(style, "circle", "padx", pad)
        pady = self._style_val(style, "circle", "pady", pad)
        padx, pady = (
            int(_coreutils._abs_perc(padx, rect.w)),
            int(_coreutils._abs_perc(pady, rect.h)),
        )
        outline = int(
            _coreutils._abs_perc(
                self._style_val(style, "circle", "outline", 0), min(rect.w, rect.h)
            )
        )
        color = self._style_val(style, "circle", "color", "black")
        antialias = self._style_val(style, "circle", "antialias", False)
        circle_rect = rect.inflate(-padx * 2, -pady * 2)
        aspect_ratio = self._style_val(style, "circle", "aspect_ratio", None)
        corners = self._style_val(style, "circle", "corners", None)
        if aspect_ratio is not None:
            align = self._style_val(style, "circle", "align", "center")
            rx, ry = circle_rect.w, circle_rect.h
            rx = circle_rect.h * aspect_ratio
            if rx > circle_rect.w:
                ry = circle_rect.w * (1 / aspect_ratio)
                rx = circle_rect.w
            circle_rect = pygame.Rect((0, 0), (rx, ry)).move_to(
                **_coreutils._align_rect(align, rect, padx, pady)
            )
        dash_size = self._style_val(style, "line", "dash_size", None)
        dash_anchor = self._style_val(style, "line", "dash_anchor", 25)
        _coreutils._draw_circle(
            self._canva,
            circle_rect,
            antialias,
            color,
            outline,
            corners,
            dash_size,
            dash_anchor,
        )

    def _draw_comp_polygon(
        self, data: list[tuple[int, int]], style, el, rect: pygame.Rect
    ):
        if self._canva is None:
            return
        points = []
        for raw_p in data:
            rx, ry = raw_p
            rx, ry = _coreutils._abs_perc(rx, rect.w), _coreutils._abs_perc(ry, rect.h)
            points.append((rect.centerx + rx, rect.centery + ry))
        color = self._style_val(style, "polygon", "color", "black")
        outline = int(
            _coreutils._abs_perc(
                self._style_val(style, "polygon", "outline", 0), min(rect.w, rect.h)
            )
        )
        pygame.draw.polygon(self._canva, color, points, outline)

    def _draw_comp_line(
        self, data: list[tuple[int, int]], style, el, rect: pygame.Rect
    ):
        if self._canva is None:
            return
        points = []
        for raw_p in data:
            rx, ry = raw_p
            rx, ry = _coreutils._abs_perc(rx, rect.w), _coreutils._abs_perc(ry, rect.h)
            points.append((rect.centerx + int(rx), rect.centery + int(ry)))
        if len(points) != 2:
            raise error.MILIValueError("Wrong number of points")
        color = self._style_val(style, "line", "color", "black")
        size = _coreutils._abs_perc(
            self._style_val(style, "line", "size", 1), min(rect.w, rect.h)
        )
        antialias = self._style_val(style, "line", "antialias", False)
        dash_size = self._style_val(style, "line", "dash_size", None)
        dash_offset = self._style_val(style, "line", "dash_offset", 0)
        width = max(1, int(size))
        _coreutils._draw_line(
            self._canva, antialias, width, color, points, dash_size, dash_offset
        )

    def _draw_comp_text(self, data: str, style, el, rect: pygame.Rect):
        if self._canva is None:
            return
        font = self._get_font(style)
        font.align = self._style_val(style, "text", "font_align", pygame.FONT_CENTER)
        font.bold = self._style_val(style, "text", "bold", False)
        font.italic = self._style_val(style, "text", "italic", False)
        font.underline = self._style_val(style, "text", "underline", False)
        font.strikethrough = self._style_val(style, "text", "strikethrough", False)
        antialias = self._style_val(style, "text", "antialias", True)
        color = self._style_val(style, "text", "color", "white")
        bg_color = self._style_val(style, "text", "bg_color", None)
        align = self._style_val(style, "text", "align", "center")
        growx, growy = (
            self._style_val(style, "text", "growx", False),
            self._style_val(style, "text", "growy", True),
        )
        padx = self._style_val(style, "text", "padx", 5)
        pady = self._style_val(style, "text", "pady", 3)
        pad = self._style_val(style, "text", "pad", None)
        if pad is not None:
            padx = pady = pad
        padx, pady = (
            _coreutils._abs_perc(padx, rect.w),
            _coreutils._abs_perc(pady, rect.h),
        )
        wraplen = _coreutils._abs_perc(
            self._style_val(style, "text", "wraplen", 0), rect.w - padx * 2
        )

        surf = font.render(str(data), antialias, color, bg_color, max(0, int(wraplen)))
        sw, sh = surf.size
        if growy and sh > rect.h + pady * 2:
            rect.h = sh + pady * 2
        if growx and sw > rect.w + padx * 2:
            rect.w = sw + padx * 2

        txtrect = surf.get_rect(**_coreutils._align_rect(align, rect, padx, pady))
        self._canva.blit(surf, txtrect)

    def _text_size(self, data: str, style):
        font = self._get_font(style)
        font.align = self._style_val(style, "text", "font_align", pygame.FONT_CENTER)
        font.bold = self._style_val(style, "text", "bold", False)
        font.italic = self._style_val(style, "text", "italic", False)
        font.underline = self._style_val(style, "text", "underline", False)
        font.strikethrough = self._style_val(style, "text", "strikethrough", False)
        if self._style_val(style, "text", "slow_grow", False):
            wraplen = _coreutils._abs_perc(
                self._style_val(style, "text", "wraplen", 0), 0
            )
            return font.render(
                data, True, "white", None, max(0, int(wraplen))
            ).get_size()
        return font.size(data)

    def _text_resize(self, rect: pygame.Rect, data, style):
        growx, growy = (
            self._style_val(style, "text", "growx", False),
            self._style_val(style, "text", "growy", True),
        )
        if not growx and not growy:
            return
        slow_grow = self._style_val(style, "text", "slow_grow", False)
        padx = self._style_val(style, "text", "padx", 5)
        pady = self._style_val(style, "text", "pady", 3)
        pad = self._style_val(style, "text", "pad", None)
        if pad is not None:
            padx = pady = pad
        padx, pady = (
            _coreutils._abs_perc(padx, rect.w),
            _coreutils._abs_perc(pady, rect.h),
        )
        font = self._get_font(style)
        if slow_grow:
            font.align = self._style_val(
                style, "text", "font_align", pygame.FONT_CENTER
            )
            font.bold = self._style_val(style, "text", "bold", False)
            font.italic = self._style_val(style, "text", "italic", False)
            font.underline = self._style_val(style, "text", "underline", False)
            font.strikethrough = self._style_val(style, "text", "strikethrough", False)
            wraplen = _coreutils._abs_perc(
                self._style_val(style, "text", "wraplen", 0), rect.w - padx * 2
            )
            sw, sh = font.render(
                data, True, "white", None, max(0, int(wraplen))
            ).get_size()
        else:
            sw, sh = font.size(str(data))
        if growy and sh > rect.h + pady * 2:
            rect.h = sh + pady * 2
        if growx and sw > rect.w + padx * 2:
            rect.w = sw + padx * 2

    def _draw_comp_image(self, data: pygame.Surface, style, el, rect: pygame.Rect):
        if data is None or self._canva is None:
            return
        ready = self._style_val(style, "image", "ready", False)
        if ready:
            output = data
        else:
            cache = style.get("cache", None)
            layer_cache = style.get("layer_cache", None)
            pad = self._style_val(style, "image", "pad", 0)
            padx = self._style_val(style, "image", "padx", pad)
            pady = self._style_val(style, "image", "pady", pad)
            padx, pady = (
                _coreutils._abs_perc(padx, rect.w),
                _coreutils._abs_perc(pady, rect.h),
            )
            do_fill = self._style_val(style, "image", "fill", False)
            do_stretchx = self._style_val(style, "image", "stretchx", False)
            do_stretchy = self._style_val(style, "image", "stretchy", False)
            fill_color = self._style_val(style, "image", "fill_color", None)
            smoothscale = self._style_val(style, "image", "smoothscale", False)
            border_radius = _coreutils._abs_perc(
                self._style_val(style, "image", "border_radius", 0), min(rect.w, rect.h)
            )
            alpha = self._style_val(style, "image", "alpha", 255)
            nine_patch = _coreutils._abs_perc(
                self._style_val(style, "image", "ninepatch_size", 0),
                min(rect.w, rect.h),
            )
            nine_patch = pygame.math.clamp(nine_patch, 0, min(rect.w, rect.h) / 2)
            if nine_patch != 0 and (do_fill or do_stretchx or do_stretchy):
                raise error.MILIIncompatibleStylesError(
                    "9-patch image mode is incompatible with fill, stretchx, and stretchy styles"
                )
            if layer_cache is not None and cache is None:
                raise error.MILIIncompatibleStylesError(
                    "An ImageCache object must be provided to use the layer_cache style"
                )

            if not cache:
                output = _coreutils._get_image(
                    rect,
                    data,
                    padx,
                    pady,
                    do_fill,
                    do_stretchx,
                    do_stretchy,
                    fill_color,
                    border_radius,
                    alpha,
                    smoothscale,
                    nine_patch,
                )
                if layer_cache:
                    layer_cache._dirty = True
            else:
                new_cache = {
                    "data": data,
                    "padx": padx,
                    "pady": pady,
                    "fill": do_fill,
                    "stretchx": do_stretchx,
                    "stretchy": do_stretchy,
                    "fill_color": fill_color,
                    "border_radius": border_radius,
                    "alpha": alpha,
                    "size": rect.size,
                    "smoothscale": smoothscale,
                    "nine_patch": nine_patch,
                    "pos": None,
                }
                if cache._cache is None:
                    output = _coreutils._get_image(
                        rect,
                        data,
                        padx,
                        pady,
                        do_fill,
                        do_stretchx,
                        do_stretchy,
                        fill_color,
                        border_radius,
                        alpha,
                        smoothscale,
                        nine_patch,
                    )
                    new_cache["output"] = output
                    cache._cache = new_cache
                    if layer_cache:
                        layer_cache._dirty = True
                else:
                    _cache = cache._cache
                    if (
                        data is not _cache["data"]
                        or smoothscale != _cache["smoothscale"]
                        or rect.size != _cache["size"]
                        or padx != _cache["padx"]
                        or pady != _cache["pady"]
                        or do_fill != _cache["fill"]
                        or do_stretchx != _cache["stretchx"]
                        or do_stretchy != _cache["stretchy"]
                        or fill_color != _cache["fill_color"]
                        or border_radius != _cache["border_radius"]
                        or alpha != _cache["alpha"]
                        or nine_patch != _cache["nine_patch"]
                    ):
                        output = _coreutils._get_image(
                            rect,
                            data,
                            padx,
                            pady,
                            do_fill,
                            do_stretchx,
                            do_stretchy,
                            fill_color,
                            border_radius,
                            alpha,
                            smoothscale,
                            nine_patch,
                        )
                        new_cache["output"] = output
                        cache._cache = new_cache
                        if layer_cache:
                            layer_cache._dirty = True
                    else:
                        output = _cache["output"]
        image_rect = output.get_rect(center=rect.center)
        if ready or not layer_cache:
            self._canva.blit(output, image_rect)
        else:
            prev = cache._cache["pos"]
            new = pygame.Vector2(image_rect.topleft)
            if new != prev:
                layer_cache._dirty = True
            cache._cache["pos"] = new
            if cache not in layer_cache._caches_set:
                layer_cache._caches_set.add(cache)
                layer_cache._caches.append(cache)
            layer_cache._caches_activity[cache] = True

    def _draw_update_element(
        self, element: dict[str, typing.Any], parent_pos, parent_clip=None
    ):
        if self._canva is None:
            return
        el_style = element["style"]
        offset = self._style_val(el_style, "element", "offset", (0, 0))
        do_clip = self._style_val(el_style, "element", "clip_draw", True)
        absolute_rect = element["rect"].move(
            (parent_pos[0] + offset[0], parent_pos[1] + offset[1])
        )
        if absolute_rect.w <= 0 or absolute_rect.h <= 0:
            return
        if parent_clip is None:
            parent_clip = absolute_rect
        if not absolute_rect.colliderect(parent_clip):
            return
        if do_clip:
            clip = absolute_rect.clip(parent_clip)
        else:
            clip = parent_clip
        element["abs_rect"] = absolute_rect
        self._check_interaction(element)

        pre_draw, mid_draw, post_draw = [
            self._style_val(el_style, "element", name, None)
            for name in ["pre_draw_func", "mid_draw_func", "post_draw_func"]
        ]
        layer_cache = el_style.get("image_layer_cache", None)
        el_data = None

        self._canva.set_clip(clip)
        if pre_draw:
            if el_data is None:
                el_data = _coreutils._element_data(self, element)
            pre_draw(self._canva, el_data, clip)
            self._canva.set_clip(clip)
        render_above = []
        for component in element["components"]:
            comp_type = component["type"]
            if self._style_val(component["style"], comp_type, "draw_above", False):
                render_above.append(component)
                continue
            compobj = _globalctx._component_types[comp_type]
            if isinstance(compobj, str):
                getattr(self, f"_draw_comp_{comp_type}")(
                    component["data"], component["style"], element, absolute_rect
                )
            else:
                compobj.draw(
                    self, component["data"], component["style"], element, absolute_rect
                )
        if mid_draw:
            if el_data is None:
                el_data = _coreutils._element_data(self, element)
            mid_draw(self._canva, el_data, clip)
            self._canva.set_clip(clip)
        if len(element["children"]) > 0:
            for child in sorted(element["children"], key=lambda c: c["z"]):
                self._canva.set_clip(clip)
                self._draw_update_element(child, absolute_rect.topleft, clip)
                self._canva.set_clip(clip)
        for component in render_above:
            comp_type = component["type"]
            compobj = _globalctx._component_types[comp_type]
            if isinstance(compobj, str):
                getattr(self, f"_draw_comp_{comp_type}")(
                    component["data"], component["style"], element, absolute_rect
                )
            else:
                compobj.draw(
                    self, component["data"], component["style"], element, absolute_rect
                )
        if post_draw:
            if el_data is None:
                el_data = _coreutils._element_data(self, element)
            post_draw(self._canva, el_data, clip)
            self._canva.set_clip(clip)
        if layer_cache is not None:
            self._canva.set_clip(self._canva_rect)
            _coreutils._render_layer_cache(layer_cache, self._canva)
            self._canva.set_clip(clip)

    def _start_check(self):
        if not self._started:
            raise error.MILIStatusError("MILI.start() was not called")
