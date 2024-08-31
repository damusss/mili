import pygame
import typing
from mili import error
from mili import data as _data
from mili import typing as _typing

if typing.TYPE_CHECKING:
    from mili import MILI as _MILI

__all__ = ()


class _globalctx:
    _font_cache = {}
    _component_types: dict[str, str | _typing.ComponentProtocol] = dict.fromkeys(
        ["rect", "circle", "line", "polygon", "line", "text", "image"], "builtin"
    )
    _mili_stack = []
    _mili: "_MILI" = None

    @staticmethod
    def _abs_perc(val, dim) -> float:
        if isinstance(val, str):
            sign = 1
            if val.startswith("-"):
                val = val.replace("-", "")
                sign = -1
            try:
                val = float(val)
            except ValueError:
                raise error.MILIValueError(f"Invalid percentage value '{val}'")
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
    def _nine_patch(image: pygame.Surface, w, h, s, smoothscale):
        ow, oh = image.get_size()
        scale_func = (
            pygame.transform.smoothscale if smoothscale else pygame.transform.scale
        )
        subsurf = image.subsurface
        ohsize, hsize = ow - s * 2, w - s * 2
        ovsize, vsize = oh - s * 2, h - s * 2
        base = pygame.Surface((w, h), pygame.SRCALPHA)
        base.blit(subsurf((0, 0, s, s)), (0, 0))  # topleft
        base.blit(subsurf((ow - s, 0, s, s)), (w - s, 0))  # topright
        base.blit(subsurf((0, oh - s, s, s)), (0, h - s))  # bottomleft
        base.blit(subsurf((ow - s, oh - s, s, s)), (w - s, h - s))  # bottomright
        if ohsize > 0:
            base.blit(scale_func(subsurf((s, 0, ohsize, s)), (hsize, s)), (s, 0))  # top
            base.blit(
                scale_func(subsurf((s, oh - s, ohsize, s)), (hsize, s)),
                (s, h - s),
            )  # bottom
        if ovsize > 0:
            base.blit(
                scale_func(subsurf((0, s, s, ovsize)), (s, vsize)), (0, s)
            )  # left
            base.blit(
                scale_func(subsurf((ow - s, s, s, ovsize)), (s, vsize)),
                (w - s, s),
            )  # right
        if ohsize > 0 and ovsize > 0:
            base.blit(
                scale_func(subsurf((s, s, ohsize, ovsize)), (hsize, vsize)),
                (s, s),
            )  # inner
        return base

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
        nine_patch,
    ) -> pygame.Surface:
        iw, ih = data.size
        tw, th = max(rect.w - padx * 2, 1), max(rect.h - pady * 2, 1)

        if nine_patch == 0:
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
        else:
            image = _globalctx._nine_patch(data, tw, th, nine_patch, smoothscale)

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
        mili: "_MILI", el: dict[str, typing.Any], interaction: "_data.Interaction"
    ) -> "_data.ElementData":
        if el["id"] in mili._ctx._old_data:
            old_data = mili._ctx._old_data[el["id"]]
        else:
            old_data = {
                "rect": pygame.Rect(),
                "abs_rect": pygame.Rect(),
                "children_ids": [],
                "components": [],
                "parent_id": 0,
                "grid": None,
            }
        grid = old_data["grid"]
        return _data.ElementData(
            mili,
            interaction=interaction,
            rect=old_data["rect"].copy(),
            absolute_rect=old_data["abs_rect"].copy(),
            z=el["z"],
            id=el["id"],
            style=el["style"].copy(),
            children_ids=list(old_data["children_ids"]),
            parent_id=old_data["parent_id"],
            components=old_data["components"].copy(),
            grid=(
                _data.ElementGridData(
                    overflowx=-1, overflowy=-1, padx=0, pady=0, spacing=0
                )
                if grid is None
                else _data.ElementGridData(
                    overflowx=grid["overflowx"],
                    overflowy=grid["overflowy"],
                    padx=grid["padx"],
                    pady=grid["pady"],
                    spacing=grid["spacing"],
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
            raise error.MILIValueError("Invalid text alignment")
        return {align: (x, y)}


class _ctx:
    def __init__(self, mili: "_MILI"):
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
        }
        self._stack: dict[str, typing.Any] = self._parent
        self._parents_stack = [self._stack]
        self._id = 1
        self._memory: dict[int, dict[str, typing.Any]] = {}
        self._old_data: dict[int, dict[str, typing.Any]] = {}
        self._element: dict[str, typing.Any] = self._parent
        self._canva: pygame.Surface = None
        self._canva_rect: pygame.Rect = None
        self._abs_hovered: list[dict[str, typing.Any]] = []
        self._started = False
        self._started_pressing_element = None
        self._started_pressing_button = -1
        self._z = 0
        self._mouse_pos = pygame.Vector2()
        self._mouse_rel = pygame.Vector2()
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
        self, rect: _typing.RectLike, arg_style
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
            f"overflow{oa}": max(0, lines_size_oa - padded_oa),
            f"overflow{a}": max(0, longest_line_size_a - padded_a),
            f"pad{a}": pada,
            f"pad{oa}": padoa,
            "spacing": space,
        }

    def _check_align(self, align):
        if align not in ["first", "last", "center", "max_spacing"]:
            raise error.MILIValueError(f"Invalid alignment/anchoring '{align}'")

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
            el_filloa = _globalctx._abs_perc(filloa, padded_oa)
            setattr(el_rect, oav, el_filloa)
            changed.append(filloa_el)

        filla_totalsize = 0
        for filla_el in elements_with_filla:
            el_rect = filla_el["rect"]
            el_style = filla_el["style"]
            filla = self._style_val(el_style, "element", f"fill{a}", False)
            if filla is True:
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
            f"overflow{oa}": max(0, biggest_oa - padded_oa),
            f"overflow{a}": max(0, total_a - padded_a),
            f"pad{a}": pada,
            f"pad{oa}": padoa,
            "spacing": space,
        }

        for el in list(changed):
            self._organize_element(el)

    def _start(self, style):
        self._parent = {
            "rect": pygame.Rect((0, 0), self._canva.size),
            "style": style,
            "id": 0,
            "children": [],
            "children_grid": [],
            "components": [],
            "parent": None,
            "top": False,
            "z": 0,
        }
        self._id = 1
        self._element = self._parent
        self._stack = self._parent
        self._parents_stack = [self._stack]
        self._abs_hovered = []
        self._started = True
        self._z = 0

        if (btn := _globalctx._get_first_button(pygame.mouse.get_just_pressed())) > -1:
            self._started_pressing_button = btn
        if (
            _globalctx._get_first_button(pygame.mouse.get_just_released())
            == self._started_pressing_button
        ):
            self._started_pressing_button = -1
            self._started_pressing_element = None

    def _check_interaction(self, element: dict[str, typing.Any]):
        if not self._style_val(element["style"], "element", "blocking", True):
            return
        clipdraw = self._style_val(element["style"], "element", "clip_draw", True)
        hover = element["abs_rect"].collidepoint(pygame.mouse.get_pos())
        parent_hover = True
        if element["parent"] is not None:
            parent_hover = element["parent"]["abs_rect"].collidepoint(
                pygame.mouse.get_pos()
            )
            if clipdraw:
                parent_hover = True
        if hover and parent_hover:
            self._abs_hovered.append(element)

    def _get_interaction(self, element: dict[str, typing.Any]) -> "_data.Interaction":
        if element["id"] not in self._memory:
            return _data.Interaction(
                self._mili, -1, False, -1, -1, -1, False, False, False, False
            )
        old_el = self._memory[element["id"]]
        self._old_data[element["id"]] = {
            "rect": old_el["rect"],
            "abs_rect": old_el["abs_rect"],
            "components": old_el["components"],
            "children_ids": [ch["id"] for ch in old_el["children"]],
            "parent_id": old_el["parent"]["id"] if old_el["parent"] else 0,
            "grid": old_el["grid"] if "grid" in old_el else None,
        }
        absolute_hover = old_el["abs_rect"].collidepoint(pygame.mouse.get_pos())
        if old_el["top"]:
            if (
                self._started_pressing_button > -1
                and self._started_pressing_element is None
            ):
                self._started_pressing_element = element["id"]
                return self._total_interaction(
                    element, absolute_hover, absolute_hover, False, old_el
                )
            if (
                self._started_pressing_button > -1
                and element["id"] != self._started_pressing_element
            ):
                return self._partial_interaction(element, absolute_hover)
            return self._total_interaction(
                element, absolute_hover, absolute_hover, False, old_el
            )
        else:
            if (
                self._started_pressing_button > -1
                and element["id"] == self._started_pressing_element
            ):
                return self._total_interaction(
                    element, absolute_hover, False, True, old_el
                )
            return self._partial_interaction(element, absolute_hover)

    def _partial_interaction(self, element, absolute_hover):
        element["hovered"] = False
        return _data.Interaction(
            self._mili,
            element["id"],
            False,
            -1,
            -1,
            -1,
            absolute_hover,
            False,
            False,
            False,
        )

    def _total_interaction(self, element, absolute_hover, hovered, unhovered, old_el):
        i = _data.Interaction(
            self._mili,
            element["id"],
            absolute_hover and hovered,
            _globalctx._get_first_button(pygame.mouse.get_pressed(5)),
            _globalctx._get_first_button(pygame.mouse.get_just_pressed()),
            _globalctx._get_first_button(pygame.mouse.get_just_released()),
            absolute_hover,
            unhovered,
            False,
            False,
        )
        if i.hovered and not old_el["hovered"]:
            i.just_hovered = True
        if not i.hovered and old_el["hovered"]:
            i.just_unhovered = True
        element["hovered"] = i.hovered
        return i

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
        if _globalctx._component_types[type] != "builtin":
            _globalctx._component_types[type].added(self, data, style, self._element)
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
            self._style_val(style, "rect", "outline", 0), min(rect.w, rect.h)
        )
        border_radius = _globalctx._abs_perc(
            self._style_val(style, "rect", "border_radius", 7), min(rect.w, rect.h)
        )
        color = self._style_val(style, "rect", "color", "black")
        pygame.draw.rect(
            self._canva,
            color,
            rect.inflate(-padx, -pady),
            int(outline),
            int(border_radius),
        )

    def _draw_comp_circle(self, data, style, el, rect: pygame.Rect):
        padx = self._style_val(style, "circle", "padx", 0)
        pady = self._style_val(style, "circle", "pady", padx)
        padx, pady = (
            _globalctx._abs_perc(padx, rect.w),
            _globalctx._abs_perc(pady, rect.h),
        )
        outline = _globalctx._abs_perc(
            self._style_val(style, "circle", "outline", 0), min(rect.w, rect.h)
        )
        color = self._style_val(style, "circle", "color", "black")
        antialias = self._style_val(style, "circle", "antialias", False)
        if padx == pady:
            (pygame.draw.aacircle if antialias else pygame.draw.circle)(
                self._canva, color, rect.center, rect.w / 2 - padx, int(outline)
            )
        else:
            pygame.draw.ellipse(
                self._canva, color, rect.inflate(-padx, -pady), int(outline)
            )

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
            self._style_val(style, "polygon", "outline", 0), min(rect.w, rect.h)
        )
        pygame.draw.polygon(self._canva, color, points, int(outline))

    def _draw_comp_line(
        self, data: list[tuple[int, int]], style, el, rect: pygame.Rect
    ):
        points = []
        for raw_p in data:
            rx, ry = raw_p
            rx, ry = _globalctx._abs_perc(rx, rect.w), _globalctx._abs_perc(ry, rect.h)
            points.append((rect.centerx + int(rx), rect.centery + int(ry)))
        if len(points) != 2:
            raise error.MILIValueError("Wrong number of points")
        color = self._style_val(style, "line", "color", "black")
        size = _globalctx._abs_perc(
            self._style_val(style, "line", "size", 1), min(rect.w, rect.h)
        )
        antialias = self._style_val(style, "line", "antialias", False)
        (pygame.draw.aaline if antialias else pygame.draw.line)(
            self._canva, color, points[0], points[1], max(1, int(size))
        )

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

        surf = font.render(str(data), antialias, color, bg_color, max(0, int(wraplen)))
        sw, sh = surf.size
        if growy and sh > rect.h + pady * 2:
            rect.h = sh + pady * 2
        if growx and sw > rect.w + padx * 2:
            rect.w = sw + padx * 2

        txtrect = surf.get_rect(**_globalctx._text_align(align, rect, padx, pady))
        self._canva.blit(surf, txtrect)

    def _text_size(self, data: str, style):
        font = self._get_font(style)
        font.align = self._style_val(style, "text", "font_align", pygame.FONT_CENTER)
        font.bold = self._style_val(style, "text", "bold", False)
        font.italic = self._style_val(style, "text", "italic", False)
        font.underline = self._style_val(style, "text", "underline", False)
        font.strikethrough = self._style_val(style, "text", "strikethrough", False)
        if self._style_val(style, "text", "slow_grow", False):
            wraplen = _globalctx._abs_perc(
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
        padx, pady = (
            _globalctx._abs_perc(padx, rect.w),
            _globalctx._abs_perc(pady, rect.h),
        )
        font = self._get_font(style)
        if slow_grow and not growx:
            font.align = self._style_val(
                style, "text", "font_align", pygame.FONT_CENTER
            )
            font.bold = self._style_val(style, "text", "bold", False)
            font.italic = self._style_val(style, "text", "italic", False)
            font.underline = self._style_val(style, "text", "underline", False)
            font.strikethrough = self._style_val(style, "text", "strikethrough", False)
            wraplen = _globalctx._abs_perc(
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
        nine_patch = _globalctx._abs_perc(
            self._style_val(style, "image", "ninepatch_size", 0), min(rect.w, rect.h)
        )
        nine_patch = pygame.math.clamp(nine_patch, 0, min(rect.w, rect.h) / 2)
        if nine_patch != 0 and (do_fill or do_stretchx or do_stretchy):
            raise error.MILIIncompatibleStylesError(
                "9-patch image mode is incompatible with fill, stretchx, and stretchy styles"
            )

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
                nine_patch,
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
                "nine_patch": nine_patch,
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
                    nine_patch,
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
                    or nine_patch != _cache["nine_patch"]
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
                        nine_patch,
                    )
                    new_cache["output"] = output
                    cache._cache = new_cache
                else:
                    output = _cache["output"]

        image_rect = output.get_rect(center=rect.center)
        self._canva.blit(output, image_rect)

    def _draw_update_element(
        self, element: dict[str, typing.Any], parent_pos, parent_clip=None
    ):
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
        el_data = None

        self._canva.set_clip(clip)
        if pre_draw:
            if el_data is None:
                el_data = _globalctx._element_data(self._mili, element, None)
            pre_draw(self._canva, el_data, clip)
            self._canva.set_clip(clip)
        render_above = []
        for component in element["components"]:
            comp_type = component["type"]
            if self._style_val(component["style"], comp_type, "draw_above", False):
                render_above.append(component)
                continue
            if _globalctx._component_types[comp_type] == "builtin":
                getattr(self, f"_draw_comp_{comp_type}")(
                    component["data"], component["style"], element, absolute_rect
                )
            else:
                _globalctx._component_types[comp_type].draw(
                    self, component["data"], component["style"], element, absolute_rect
                )
        if mid_draw:
            if el_data is None:
                el_data = _globalctx._element_data(self._mili, element, None)
            mid_draw(self._canva, el_data, clip)
            self._canva.set_clip(clip)
        if len(element["children"]) > 0:
            for child in sorted(element["children"], key=lambda c: c["z"]):
                self._canva.set_clip(clip)
                self._draw_update_element(child, absolute_rect.topleft, clip)
                self._canva.set_clip(clip)
        for component in render_above:
            comp_type = component["type"]
            if _globalctx._component_types[comp_type] == "builtin":
                getattr(self, f"_draw_comp_{comp_type}")(
                    component["data"], component["style"], element, absolute_rect
                )
            else:
                _globalctx._component_types[comp_type].draw(
                    self, component["data"], component["style"], element, absolute_rect
                )
        if post_draw:
            if el_data is None:
                el_data = _globalctx._element_data(self._mili, element, None)
            post_draw(self._canva, el_data, clip)
            self._canva.set_clip(clip)

    def _start_check(self):
        if not self._started:
            raise error.MILIStatusError("MILI.start() was not called")
