import pygame
from functools import partialmethod
from typing import Self as _Self, Literal as _Literal, Sequence as _Sequence
from collections.abc import Callable as _Callable

# todo: scrollbar to scroll helper
# todo: text cache


class _globalctx:
    from typing import TypedDict as _TypedDict

    class _ElementLike(_TypedDict):
        id: int
        rect: pygame.Rect
        abs_rect: pygame.Rect
        z: int
        style: dict[str]
        children: list[_Self]
        children_grid: list[_Self]
        parent: _Self
        components: list[dict[str]]
        top: bool

    _font_cache = {}
    _default_style_names = {
        "element",
        "rect",
        "circle",
        "polygon",
        "line",
        "text",
        "image",
    }

    @staticmethod
    def _abs_perc(val, dim) -> float:
        if isinstance(val, str):
            sign = 1
            if val.startswith("-"):
                val = val.replace("-", "")
                sign = -1
            return ((dim * float(val)) / 100) * sign
        return val

    @staticmethod
    def _get_first_button(buttons):
        bid = -1
        for i, b in enumerate(buttons):
            if b:
                bid = i + 1
                break
        return bid

    @staticmethod
    def _get_image(
        rect: pygame.Rect,
        data: pygame.Surface,
        padx,
        pady,
        do_fill,
        do_stretchx,
        do_stretchy,
        fill_color,
        border_radius,
        alpha,
        smoothscale,
    ) -> pygame.Surface:
        iw, ih = data.size
        tw, th = max(rect.w - padx * 2, 1), max(rect.h - pady * 2, 1)

        if not do_fill:
            w = tw
            h = int(ih * (w / iw))
            if h > th:
                h = th
                w = int(iw * (h / ih))
            w, h = max(w, 1), max(h, 1)
            if w < tw and do_stretchx:
                w = tw
            if h < th and do_stretchy:
                h = th
            if smoothscale:
                image = pygame.transform.smoothscale(data, (w, h))
            else:
                image = pygame.transform.scale(data, (w, h))
        else:
            w = tw
            h = int(ih * (w / iw))
            if h < th:
                h = th
                w = int(iw * (h / ih))
            if smoothscale:
                image = pygame.transform.smoothscale(data, (w, h))
            else:
                image = pygame.transform.scale(data, (w, h))
            image = image.subsurface((w // 2 - tw // 2, h // 2 - th // 2, tw, th))

        w, h = image.size
        if fill_color is not None:
            image.fill(fill_color)
        if border_radius > 0:
            mask_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            mask_surf.fill(0)
            pygame.draw.rect(
                mask_surf, (255, 255, 255, 255), (0, 0, w, h), 0, int(border_radius)
            )
            image.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        if alpha != 255:
            image.set_alpha(alpha)
        return image

    @staticmethod
    def _element_data(
        mili: "MILI", el: _ElementLike, interaction: "Interaction"
    ) -> "ElementData":
        if el["id"] in mili._ctx._old_data:
            old_data = mili._ctx._old_data[el["id"]]
        else:
            old_data = {
                "rect": pygame.Rect(),
                "abs_rect": pygame.Rect(),
                "children_ids": [],
                "parent_id": 0,
                "grid": None,
            }
        grid = old_data["grid"]
        return ElementData(
            mili,
            interaction=interaction,
            rect=old_data["rect"].copy(),
            absolute_rect=old_data["abs_rect"].copy(),
            z=el["z"],
            id=el["id"],
            style=el["style"].copy(),
            children_ids=list(old_data["children_ids"]),
            parent_id=old_data["parent_id"],
            grid=(
                ElementGridData(overflow_x=-1, overflow_y=-1)
                if grid is None
                else ElementGridData(
                    overflow_x=grid["overflow_x"],
                    overflow_y=grid["overflow_y"],
                )
            ),
        )

    @staticmethod
    def _text_align(align, rect: pygame.Rect, padx, pady):
        x, y = 0, 0
        if align == "center":
            x, y = rect.centerx, rect.centery
        elif align == "topleft":
            x, y = rect.x + padx, rect.y + pady
        elif align == "bottomleft":
            x, y = rect.x + padx, rect.bottom - pady
        elif align == "bottomright":
            x, y = rect.right - padx, rect.bottom - pady
        elif align == "topright":
            x, y = rect.right - padx, rect.y + pady
        elif align == "midleft" or align == "left":
            align = "midleft"
            x, y = rect.x + padx, rect.centery
        elif align == "midright" or align == "right":
            align = "midright"
            x, y = rect.right - padx, rect.centery
        elif align == "midtop" or align == "top":
            align = "midtop"
            x, y = rect.centerx, rect.y + pady
        elif align == "midbottom" or align == "bottom":
            align = "midbottom"
            x, y = rect.centerx, rect.bottom - pady
        else:
            raise ValueError("Invalid text alignment")
        return {align: (x, y)}


class _ctx:
    def __init__(self, mili: "MILI"):
        self._mili = mili
        self._parent: _globalctx._ElementLike = {
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
        }
        self._stack: _globalctx._ElementLike = self._parent
        self._parents_stack = [self._stack]
        self._id = 1
        self._memory: dict[int, _globalctx._ElementLike] = {}
        self._old_data: dict[int, _globalctx._ElementLike] = {}
        self._element: _globalctx._ElementLike = self._parent
        self._canva: pygame.Surface = None
        self._canva_rect: pygame.Rect = None
        self._abs_hovered: list[_globalctx._ElementLike] = []
        self._started = False

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
        self, rect: pygame.Rect, arg_style
    ) -> tuple[_globalctx._ElementLike, "Interaction"]:
        if arg_style is None:
            arg_style = {}
        style = self._default_styles["element"].copy()
        style.update(arg_style)
        if rect is None:
            rect = (0, 0, 0, 0)
        rect = pygame.Rect(rect)
        element: _globalctx._ElementLike = {
            "rect": rect,
            "abs_rect": rect.copy(),
            "style": style,
            "id": self._id,
            "children": [],
            "components": [],
            "children_grid": [],
            "parent": self._parent,
            "top": False,
            "z": 1,
        }
        interaction = self._get_interaction(element)
        self._memory[self._id] = element
        parent = self._parent
        if "parent_id" in style:
            if style["parent_id"] in self._memory:
                parent = self._memory[style["parent_id"]]

        if parent:
            z = len(parent["children"])
            if "z" in style:
                z = style["z"]
            parent["children"].append(element)
            if not self._style_val(style, "element", "ignore_grid", False):
                parent["children_grid"].append(element)
            element["z"] = parent["z"] + z + 1
        self._id += 1
        self._element = element
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
        self._check_align(grid_align)
        spacea = _globalctx._abs_perc(
            self._style_val(style, "element", f"grid_space{a}", space),
            getattr(rect, av),
        )
        spaceoa = _globalctx._abs_perc(
            self._style_val(style, "element", f"grid_space{oa}", space),
            getattr(rect, oav),
        )

        line_elements = []
        lines = []
        line_size_a = 0
        longest_line_size_a = 0
        current_pos_oa = padoa
        longest_line_size_oa = 0
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
            f"overflow_{oa}": max(0, lines_size_oa - padded_oa),
            f"overflow_{a}": max(0, longest_line_size_a - padded_a),
        }

    def _check_align(self, align):
        if align not in ["first", "last", "center", "max_spacing"]:
            raise ValueError(f"Invalid alignment/anchoring '{align}'")

    def _organize_element(self, element: _globalctx._ElementLike):
        style = element["style"]
        rect = element["rect"]
        children = element["children_grid"]
        a = self._style_val(style, "element", "axis", "y")
        if a not in ["x", "y"]:
            raise ValueError(f"Invalid axis {a}")
        oa = "x" if a == "y" else "y"
        av = "w" if a == "x" else "h"
        oav = "w" if av == "h" else "h"
        pada = self._style_val(style, "element", f"pad{a}", 5)
        padoa = self._style_val(style, "element", f"pad{oa}", pada)
        pada, padoa = (
            _globalctx._abs_perc(pada, getattr(rect, av)),
            _globalctx._abs_perc(padoa, getattr(rect, oav)),
        )
        space = _globalctx._abs_perc(
            self._style_val(style, "element", "spacing", 3), getattr(rect, av)
        )
        anchor = self._style_val(style, "element", "anchor", "first")
        self._check_align(anchor)
        resizeoa = self._style_val(style, "element", f"resize{oa}", False)
        resizea = self._style_val(style, "element", f"resize{a}", False)
        if isinstance(resizea, dict):
            maxv = resizea.get("max", float("inf"))
            minv = resizea.get("min", 0)
            minresizea = _globalctx._abs_perc(minv, getattr(rect, av))
            maxresizea = _globalctx._abs_perc(maxv, getattr(rect, av))
            resizea = True
        else:
            resizea = bool(resizea)
            minresizea = 0
            maxresizea = float("inf")
        if isinstance(resizeoa, dict):
            maxv = resizeoa.get("max", float("inf"))
            minv = resizeoa.get("min", 0)
            minresizeoa = _globalctx._abs_perc(minv, getattr(rect, oav))
            maxresizeoa = _globalctx._abs_perc(maxv, getattr(rect, oav))
            resizeoa = True
        else:
            resizeoa = bool(resizeoa)
            minresizeoa = 0
            maxresizeoa = float("inf")
        _filloa, _filla = (
            self._style_val(style, "element", f"fill{oa}", False),
            self._style_val(style, "element", f"fill{a}", False),
        )
        if resizeoa and bool(_filloa) != False:
            raise RuntimeError(f"Cannot have resize{oa} True and fill{oa} not False")
        if resizea and bool(_filla) != False:
            raise RuntimeError(f"Cannot have resize{a} True and fill{a} not False")

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
            if bool(el_filloa) == False and getattr(el_rect, oav) > biggest_oa:
                biggest_oa = getattr(el_rect, oav)
            if bool(el_filloa) == True:
                elements_with_filloa.append(el)
            fixed_elements_a += space
            if bool(el_filla) == False:
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
            if filloa == True:
                filloa = "100"
            el_filloa = _globalctx._abs_perc(filloa, padded_oa)
            setattr(el_rect, oav, el_filloa)
            changed.append(el)

        filla_totalsize = 0
        for filla_el in elements_with_filla:
            el_rect = filla_el["rect"]
            el_style = filla_el["style"]
            filla = self._style_val(el_style, "element", f"fill{a}", False)
            if filla == True:
                filla = "100"
            el_filla = _globalctx._abs_perc(
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
            multiplier = available_to_filla / filla_totalsize
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
            el_align = self._style_val(el_style, "element", "align", "first")
            self._check_align(el_align)
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
            f"overflow_{oa}": max(0, biggest_oa - padded_oa),
            f"overflow_{a}": max(0, total_a - padded_a),
        }

        for el in list(changed):
            self._organize_element(el)

    def _check_interaction(self, element: _globalctx._ElementLike):
        if not self._style_val(element["style"], "element", "blocking", True):
            return
        hover = element["abs_rect"].collidepoint(pygame.mouse.get_pos())
        parent_hover = True
        if element["parent"] is not None:
            parent_hover = element["parent"]["abs_rect"].collidepoint(
                pygame.mouse.get_pos()
            )
        if hover and parent_hover:
            self._abs_hovered.append(element)

    def _get_interaction(self, element: _globalctx._ElementLike) -> "Interaction":
        if element["id"] not in self._memory:
            return Interaction(self._mili, -1, False, -1, -1, -1, False)
        old_el = self._memory[element["id"]]
        self._old_data[element["id"]] = {
            "rect": old_el["rect"],
            "abs_rect": old_el["abs_rect"],
            "children_ids": [ch["id"] for ch in old_el["children"]],
            "parent_id": old_el["parent"]["id"] if old_el["parent"] else 0,
            "grid": old_el["grid"] if "grid" in old_el else None,
        }
        absolute_hover = old_el["abs_rect"].collidepoint(pygame.mouse.get_pos())
        if old_el["top"]:
            return Interaction(
                self._mili,
                element["id"],
                absolute_hover,
                _globalctx._get_first_button(pygame.mouse.get_pressed(5)),
                _globalctx._get_first_button(pygame.mouse.get_just_pressed()),
                _globalctx._get_first_button(pygame.mouse.get_just_released()),
                absolute_hover,
            )
        else:
            return Interaction(
                self._mili, element["id"], False, -1, -1, -1, absolute_hover
            )

    def _add_component(self, type, data, arg_style):
        self._start_check()
        if arg_style is None:
            arg_style = {}
        style = self._default_styles[type].copy()
        style.update(arg_style)
        if not self._element:
            raise RuntimeError("Cannot add component if no element was created")
        if type == "text":
            self._text_resize(self._element["rect"], data, style)
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
        padx = self._style_val(style, "rect", "padx", 0)
        pady = self._style_val(style, "rect", "pady", padx)
        padx, pady = (
            _globalctx._abs_perc(padx, rect.w),
            _globalctx._abs_perc(pady, rect.h),
        )
        outline = _globalctx._abs_perc(
            self._style_val(style, "rect", "outline_size", 0), min(rect.w, rect.h)
        )
        border_radius = _globalctx._abs_perc(
            self._style_val(style, "rect", "border_radius", 7), min(rect.w, rect.h)
        )
        color = self._style_val(style, "rect", "color", "black")
        pygame.draw.rect(
            self._canva, color, rect.inflate(-padx, -pady), outline, border_radius
        )

    def _draw_comp_circle(self, data, style, el, rect: pygame.Rect):
        padx = self._style_val(style, "circle", "padx", 0)
        pady = self._style_val(style, "circle", "pady", padx)
        padx, pady = (
            _globalctx._abs_perc(padx, rect.w),
            _globalctx._abs_perc(pady, rect.h),
        )
        outline = _globalctx._abs_perc(
            self._style_val(style, "circle", "outline_size", 0), min(rect.w, rect.h)
        )
        color = self._style_val(style, "circle", "color", "black")
        if padx == pady:
            pygame.draw.circle(
                self._canva, color, rect.center, rect.w / 2 - padx, outline
            )
        else:
            pygame.draw.ellipse(self._canva, color, rect.inflate(-padx, -pady), outline)

    def _draw_comp_polygon(
        self, data: list[tuple[int, int]], style, el, rect: pygame.Rect
    ):
        points = []
        for raw_p in data:
            rx, ry = raw_p
            rx, ry = _globalctx._abs_perc(rx, rect.w), _globalctx._abs_perc(ry, rect.h)
            points.append((rect.centerx + rx, rect.centery + ry))
        color = self._style_val(style, "polygon", "color", "black")
        outline = _globalctx._abs_perc(
            self._style_val(style, "polygon", "outline_size", 0), min(rect.w, rect.h)
        )
        pygame.draw.polygon(self._canva, color, points, outline)

    def _draw_comp_line(
        self, data: list[tuple[int, int]], style, el, rect: pygame.Rect
    ):
        points = []
        for raw_p in data:
            rx, ry = raw_p
            rx, ry = _globalctx._abs_perc(rx, rect.w), _globalctx._abs_perc(ry, rect.h)
            points.append((rect.centerx + rx, rect.centery + ry))
        if len(points) != 2:
            raise ValueError(f"Wrong number of points")
        color = self._style_val(style, "line", "color", "black")
        size = _globalctx._abs_perc(
            self._style_val(style, "line", "size", 1), min(rect.w, rect.h)
        )
        pygame.draw.line(self._canva, color, points[0], points[1], size)

    def _draw_comp_text(self, data: str, style, el, rect: pygame.Rect):
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
        padx, pady = (
            _globalctx._abs_perc(padx, rect.w),
            _globalctx._abs_perc(pady, rect.h),
        )
        wraplen = _globalctx._abs_perc(
            self._style_val(style, "text", "wraplen", 0), rect.w - padx * 2
        )

        surf = font.render(str(data), antialias, color, bg_color, int(wraplen))
        sw, sh = surf.size
        if growy and sh > rect.h + pady * 2:
            rect.h = sh + pady * 2
        if growx and sw > rect.w + padx * 2:
            rect.w = sw + padx * 2

        txtrect = surf.get_rect(**_globalctx._text_align(align, rect, padx, pady))
        self._canva.blit(surf, txtrect)

    def _text_resize(self, rect: pygame.Rect, data, style):
        growx, growy = (
            self._style_val(style, "text", "growx", False),
            self._style_val(style, "text", "growy", True),
        )
        if not growx and not growy:
            return
        padx = self._style_val(style, "text", "padx", 5)
        pady = self._style_val(style, "text", "pady", 3)
        padx, pady = (
            _globalctx._abs_perc(padx, rect.w),
            _globalctx._abs_perc(pady, rect.h),
        )
        font = self._get_font(style)
        sw, sh = font.size(str(data))
        if growy and sh > rect.h + pady * 2:
            rect.h = sh + pady * 2
        if growx and sw > rect.w + padx * 2:
            rect.w = sw + padx * 2

    def _draw_comp_image(self, data: pygame.Surface, style, el, rect: pygame.Rect):
        if data is None:
            return
        cache = style.get("cache", None)
        padx = self._style_val(style, "image", "padx", 0)
        pady = self._style_val(style, "image", "pady", padx)
        padx, pady = (
            _globalctx._abs_perc(padx, rect.w),
            _globalctx._abs_perc(pady, rect.h),
        )
        do_fill = self._style_val(style, "image", "fill", False)
        do_stretchx = self._style_val(style, "image", "stretchx", False)
        do_stretchy = self._style_val(style, "image", "stretchy", False)
        fill_color = self._style_val(style, "image", "fill_color", None)
        smoothscale = self._style_val(style, "image", "smoothscale", False)
        border_radius = _globalctx._abs_perc(
            self._style_val(style, "image", "border_radius", 0), min(rect.w, rect.h)
        )
        alpha = self._style_val(style, "image", "alpha", 255)

        if not cache:
            output = _globalctx._get_image(
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
            )
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
            }
            if cache._cache is None:
                output = _globalctx._get_image(
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
                )
                new_cache["output"] = output
                cache._cache = new_cache
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
                ):
                    output = _globalctx._get_image(
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
                    )
                    new_cache["output"] = output
                    cache._cache = new_cache
                else:
                    output = _cache["output"]

        image_rect = output.get_rect(center=rect.center)
        self._canva.blit(output, image_rect)

    def _draw_element(
        self, element: _globalctx._ElementLike, parent_pos, parent_clip=None
    ):
        offset = self._style_val(element["style"], "element", "offset", (0, 0))
        absolute_rect = element["rect"].move(
            (parent_pos[0] + offset[0], parent_pos[1] + offset[1])
        )
        if absolute_rect.w <= 0 or absolute_rect.h <= 0:
            return
        if parent_clip is None:
            parent_clip = absolute_rect
        if not absolute_rect.colliderect(parent_clip):
            return
        clip = absolute_rect.clip(parent_clip)
        element["abs_rect"] = absolute_rect
        self._check_interaction(element)

        pre_draw, mid_draw, post_draw = [
            self._style_val(element["style"], "element", name, None)
            for name in ["pre_draw_func", "mid_draw_func", "post_draw_func"]
        ]
        el_data = None

        self._canva.set_clip(clip)
        if pre_draw:
            if el_data is None:
                el_data = _globalctx._element_data(self._mili, element, None)
            pre_draw(self._canva, el_data, clip)
            self._canva.set_clip(clip)
        for component in element["components"]:
            getattr(self, f"_draw_comp_{component["type"]}")(
                component["data"], component["style"], element, absolute_rect
            )
        if mid_draw:
            if el_data is None:
                el_data = _globalctx._element_data(self._mili, element, None)
            mid_draw(self._canva, el_data, clip)
            self._canva.set_clip(clip)
        if len(element["children"]) > 0:
            for child in sorted(element["children"], key=lambda c: c["z"]):
                self._canva.set_clip(clip)
                self._draw_element(child, absolute_rect.topleft, clip)
                self._canva.set_clip(clip)
        if post_draw:
            if el_data is None:
                el_data = _globalctx._element_data(self._mili, element, None)
            post_draw(self._canva, el_data, clip)
            self._canva.set_clip(clip)

    def _start_check(self):
        if not self._started:
            raise RuntimeError("MILI.start() was not called")


class ImageCache:
    def __init__(self):
        self._cache = None


class Interaction:
    def __init__(
        self,
        mili: "MILI",
        id: int,
        hovered: bool,
        press_button: bool,
        just_pressed_button: bool,
        just_released_button: bool,
        absolute_hover: bool,
    ):
        self._mili = mili
        self.id = id
        (
            self.hovered,
            self.press_button,
            self.just_pressed_button,
            self.just_released_button,
            self.absolute_hover,
        ) = (
            hovered,
            press_button,
            just_pressed_button,
            just_released_button,
            absolute_hover,
        )

    @property
    def left_pressed(self) -> bool:
        return self.press_button == pygame.BUTTON_LEFT

    @property
    def left_just_pressed(self) -> bool:
        return self.just_pressed_button == pygame.BUTTON_LEFT

    @property
    def left_just_released(self) -> bool:
        return self.just_released_button == pygame.BUTTON_LEFT

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self._mili.end()


class ElementGridData:
    overflow_x: float
    overflow_y: float

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)


class ElementData:
    interaction: Interaction
    rect: pygame.Rect
    absolute_rect: pygame.Rect
    z: int
    id: int
    style: dict[str]
    children_ids: list[int]
    parent_id: int
    grid: ElementGridData | None

    def __init__(self, mili: "MILI", **kwargs):
        self._mili = mili
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self._mili.end()

    def __getattr__(self, name):
        if hasattr(self.interaction, name):
            return getattr(self.interaction, name)
        raise AttributeError


class SelectableHelper:
    def __init__(self, selected: bool = False):
        self.selected: bool = selected

    def update(self, element: Interaction | ElementData) -> Interaction | ElementData:
        interaction = element
        if isinstance(element, ElementData):
            interaction = element.interaction
        if interaction.left_just_released:
            self.selected = not self.selected
        return element


class ScrollHelper:
    def __init__(self):
        self.scroll_offset: pygame.Vector2 = pygame.Vector2()
        self._element_data: ElementData = None

    def update(self, element_data: ElementData) -> ElementData:
        if not isinstance(element_data, ElementData):
            raise TypeError(f"element_data argument must be of type ElementData")
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
            maxx = self._element_data.grid.overflow_x
            maxy = self._element_data.grid.overflow_y
        self.scroll_offset.x = pygame.math.clamp(self.scroll_offset.x, 0, maxx)
        self.scroll_offset.y = pygame.math.clamp(self.scroll_offset.y, 0, maxy)

    def get_offset(self) -> tuple[float, float]:
        return (-self.scroll_offset.x, -self.scroll_offset.y)


class StyleHelper:
    def __init__(
        self,
        element: dict[str] | None = None,
        rect: dict[str] | None = None,
        circle: dict[str] | None = None,
        polygon: dict[str] | None = None,
        line: dict[str] | None = None,
        text: dict[str] | None = None,
        image: dict[str] | None = None,
    ):
        self.styles = {
            "element": element if element else {},
            "rect": rect if rect else {},
            "circle": circle if circle else {},
            "polygon": polygon if polygon else {},
            "line": line if line else {},
            "text": text if text else {},
            "image": image if image else {},
        }

    def set(self, type: str, style: dict[str]):
        if type not in self.styles:
            raise ValueError("Invalid style type")
        self.styles[type] = style

    def get(self, type: str) -> dict[str]:
        if type not in self.styles:
            raise ValueError("Invalid style type")
        return self.styles[type]

    get_element = partialmethod(get, "element")
    get_rect = partialmethod(get, "rect")
    get_circle = partialmethod(get, "circle")
    get_polygon = partialmethod(get, "polygon")
    get_line = partialmethod(get, "line")
    get_text = partialmethod(get, "text")
    get_image = partialmethod(get, "image")

    def set_default(self, mili: "MILI"):
        for name, style in self.styles.items():
            mili.default_style(name, style)


class StyleStatusHelper:
    def __init__(
        self,
        base: StyleHelper | None = None,
        hover: StyleHelper | None = None,
        press: StyleHelper | None = None,
    ):
        self.base = base if base else StyleHelper()
        self.hover = hover if hover else StyleHelper()
        self.press = press if press else StyleHelper()

    def set(self, status: str, style: StyleHelper):
        if status not in ["base", "press", "hover"]:
            raise ValueError("Invalid status type")
        setattr(self, status, style)

    def get(self, type: str, interaction: Interaction) -> dict[str]:
        if type not in _globalctx._default_style_names:
            raise ValueError("Invalid style type")
        return conditional_style(
            interaction, self.base.get(type), self.hover.get(type), self.press.get(type)
        )

    get_element = partialmethod(get, "element")
    get_rect = partialmethod(get, "rect")
    get_circle = partialmethod(get, "circle")
    get_polygon = partialmethod(get, "polygon")
    get_line = partialmethod(get, "line")
    get_text = partialmethod(get, "text")
    get_image = partialmethod(get, "image")


def conditional_style(
    interaction: Interaction | ElementData,
    base: dict[str] | None = None,
    hover: dict[str] | None = None,
    press: dict[str] | None = None,
    selected=False,
) -> dict[str]:
    if isinstance(interaction, ElementData):
        interaction = interaction.interaction
    if hover is None:
        hover = {}
    if press is None:
        press = {}
    if base is None:
        base = {}
    new_base = {}
    new_base.update(base)
    if interaction.hovered:
        if interaction.left_pressed or selected:
            new_base.update(press)
        else:
            new_base.update(hover)
    else:
        if selected:
            new_base.update(press)
    return new_base


def percentage(percentage: float, value: float) -> float:
    return (percentage * value) / 100


def indent(*args): ...


class MILI:
    def __init__(self, canva: pygame.Surface | None = None):
        self._ctx = _ctx(self)
        if canva is not None:
            self.set_canva(canva)

    def default_style(self, type: str, style: dict[str]):
        if type not in self._ctx._default_styles:
            raise ValueError("Invalid style type")
        self._ctx._default_styles[type].update(style)

    def default_styles(self, **types_styles: dict[str]):
        for name, value in types_styles.items():
            self.default_style(name, value)

    def reset_style(self, *types: str):
        for tp in types:
            if tp not in self._ctx._default_styles:
                raise ValueError("Invalid style type")
            self._ctx._default_styles[tp] = {}

    def start(self, style: dict[str] | None = None):
        if style is None:
            style = {}
        style.update(blocking=False)
        self._ctx._parent = {
            "rect": pygame.Rect((0, 0), self._ctx._canva.size),
            "style": style,
            "id": 0,
            "children": [],
            "children_grid": [],
            "components": [],
            "parent": None,
            "top": False,
            "z": 0,
        }
        self._ctx._id = 1
        self._ctx._element = self._ctx._parent
        self._ctx._stack = self._ctx._parent
        self._ctx._parents_stack = [self._ctx._stack]
        self._ctx._abs_hovered = []
        self._ctx._started = True

    def set_canva(self, surface: pygame.Surface):
        self._ctx._canva = surface
        self._ctx._canva_rect = surface.get_rect()

    def update_draw(self):
        self._ctx._organize_element(self._ctx._stack)
        self._ctx._started = False
        self._ctx._draw_element(self._ctx._stack, (0, 0))
        abs_hovered = sorted(self._ctx._abs_hovered, key=lambda e: e["z"], reverse=True)
        if len(abs_hovered) > 0:
            abs_hovered[0]["top"] = True

    def element(
        self,
        rect: pygame.Rect | None,
        style: dict[str] | None = None,
        get_data: bool = False,
    ) -> Interaction | ElementData:
        self._ctx._start_check()
        el, interaction = self._ctx._get_element(rect, style)
        if get_data:
            return _globalctx._element_data(self, el, interaction)
        return interaction

    def begin(
        self,
        rect: pygame.Rect,
        style: dict[str] | None = None,
        header: str = "",
        get_data: bool = False,
    ) -> Interaction | ElementData:
        self._ctx._start_check()
        el, interaction = self._ctx._get_element(rect, style)
        self._ctx._parent = el
        self._ctx._parents_stack.append(el)
        if get_data:
            return _globalctx._element_data(self, el, interaction)
        return interaction

    def end(self, header: str = ""):
        self._ctx._start_check()
        if self._ctx._parent and self._ctx._parent["id"] != 0:
            self._ctx._organize_element(self._ctx._parent)
        else:
            raise RuntimeError("end() called too many times")
        if len(self._ctx._parents_stack) > 1:
            self._ctx._parents_stack.pop()
            self._ctx._parent = self._ctx._parents_stack[-1]
        else:
            self._ctx._parent = self._ctx._parents_stack[0]

    def rect(self, style: dict[str] | None = None):
        self._ctx._add_component("rect", None, style)

    def rect_element(
        self,
        rect_style: dict[str] | None = None,
        element_rect: pygame.Rect = None,
        element_style: dict[str] | None = None,
        get_data: bool = False,
    ) -> Interaction | ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.rect(rect_style)
        return data

    def circle(self, style: dict[str] | None = None):
        self._ctx._add_component("circle", None, style)

    def circle_element(
        self,
        circle_style: dict[str] | None = None,
        element_rect: pygame.Rect = None,
        element_style: dict[str] | None = None,
        get_data: bool = False,
    ) -> Interaction | ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.circle(circle_style)
        return data

    def polygon(
        self, points: list[tuple[int | str, int | str]], style: dict[str] | None = None
    ):
        self._ctx._add_component("polygon", points, style)

    def polygon_element(
        self,
        points: list[tuple[int | str, int | str]],
        polygon_style: dict[str] | None = None,
        element_rect: pygame.Rect = None,
        element_style: dict[str] | None = None,
        get_data: bool = False,
    ) -> Interaction | ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.polygon(points, polygon_style)
        return data

    def line(
        self,
        start_end: list[tuple[int | str, int | str]],
        style: dict[str] | None = None,
    ):
        self._ctx._add_component("line", start_end, style)

    def line_element(
        self,
        start_end: list[tuple[int | str, int | str]],
        line_style: dict[str] | None = None,
        element_rect: pygame.Rect = None,
        element_style: dict[str] | None = None,
        get_data: bool = False,
    ) -> Interaction | ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.line(start_end, line_style)
        return data

    def text(self, text: str, style: dict[str] | None = None):
        self._ctx._add_component("text", text, style)

    def text_element(
        self,
        text: str,
        text_style: dict[str] | None = None,
        element_rect: pygame.Rect = None,
        element_style: dict[str] | None = None,
        get_data: bool = False,
    ) -> Interaction | ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.text(text, text_style)
        return data

    def image(self, surface: pygame.Surface, style: dict[str] | None = None):
        self._ctx._add_component("image", surface, style)

    def image_element(
        self,
        surface: pygame.Surface,
        image_style: dict[str] | None = None,
        element_rect: pygame.Rect = None,
        element_style: dict[str] | None = None,
        get_data: bool = False,
    ) -> Interaction | ElementData:
        data = self.element(element_rect, element_style, get_data)
        self.image(surface, image_style)
        return data

    def basic_element(
        self,
        rect: pygame.Rect,
        style: dict[str] | None = None,
        comp_data=None,
        comp_style: dict[str] | None = None,
        bg_style: dict[str] | None = None,
        outline_style: dict[str] | None = None,
        component="text",
        get_data: bool = False,
    ) -> Interaction | ElementData:
        if not component in ["text", "image", "rect", "circle", "line", "polygon"]:
            raise ValueError(f"Invalid component name")
        if not outline_style:
            outline_style = {}
        if not "outline_size" in outline_style:
            outline_style["outline_size"] = 1
        data = self.element(rect, style, get_data)
        self.rect(bg_style)
        comp = getattr(self, component)
        try:
            comp(comp_data, comp_style)
        except TypeError:
            comp(comp_style)
        self.rect(outline_style)
        return data

    def data_from_id(self, element_id: int) -> ElementData:
        self._ctx._start_check()
        if element_id in self._ctx._memory:
            el = self._ctx._memory[element_id]
            return _globalctx._element_data(el, _ctx._get_interaction(el))
