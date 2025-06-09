import pygame
import typing
import math
from mili import error
from mili import data as _data

if typing.TYPE_CHECKING:
    from mili._core import _ctx

__all__ = ()

_VALID_ALIGN = set(["first", "last", "center"])
_VALID_ANCHOR = set(["first", "last", "center", "max_spacing"])
_VALID_ALIGN_GRID = set(["first", "last", "center", "first_center", "last_center"])
_OUTLINE_OFFSETS = [(0, 0), (2, 0), (0, 2), (2, 2), (1, 0), (1, 2), (0, 1), (2, 1)]
_OUTLINE_OFFSETS_CENTERED = [
    (offset[0] - 1, offset[1] - 1) for offset in _OUTLINE_OFFSETS
]
_FONT_ALIGNS = {
    "left": pygame.FONT_LEFT,
    "center": pygame.FONT_CENTER,
    "right": pygame.FONT_RIGHT,
    pygame.FONT_LEFT: pygame.FONT_LEFT,
    pygame.FONT_CENTER: pygame.FONT_CENTER,
    pygame.FONT_RIGHT: pygame.FONT_RIGHT,
}
_FONT_DIRS = {
    "ltr": pygame.DIRECTION_LTR,
    "rtl": pygame.DIRECTION_RTL,
    "ttb": pygame.DIRECTION_TTB,
    "btt": pygame.DIRECTION_BTT,
    pygame.DIRECTION_LTR: pygame.DIRECTION_LTR,
    pygame.DIRECTION_RTL: pygame.DIRECTION_RTL,
    pygame.DIRECTION_TTB: pygame.DIRECTION_TTB,
    pygame.DIRECTION_BTT: pygame.DIRECTION_BTT,
}
_number_mods = {}


def _render_layer_cache(self: _data.ImageLayerCache, canva: pygame.Surface | None):
    if canva is None or not self.active or self._rendered:
        return
    remove = []
    if self._dirty:
        self._surface.fill(0)
        for cache in self._caches:
            if not self._caches_activity.get(cache, False):
                remove.append(cache)
                continue
            self._surface.blit(
                cache._cache["output"], cache._cache["pos"] - self._offset
            )
        if self._erase_rects is not None:
            for rect in self._erase_rects:
                r = rect.copy()
                r.topleft -= self._offset
                self._surface.fill((0, 0, 0, 0), r)
        self._dirty = False
    else:
        for cache in self._caches:
            if not self._caches_activity.get(cache, False):
                remove.append(cache)
    for cache in remove:
        self._caches.remove(cache)
        self._caches_set.remove(cache)
    canva.blit(self._surface, self._offset, special_flags=self.blit_flags)
    self._rendered = True


def _abs_perc(val, dim) -> float:
    if isinstance(val, str):
        val = val.strip()
        sign = 1
        if val.startswith("-"):
            val = val.removeprefix("-")
            sign = -1
        if val.endswith("%"):
            val = val.removesuffix("%")
        elif not (key := val[0]).isnumeric():
            if key in _number_mods:
                number = float(val.removeprefix(key))
                return _number_mods[key](number) * sign
            else:
                raise error.MILIValueError(
                    f"The character prefix '{key}' of the value '{val}' is not registered as a number modifier and cannot be evaluated"
                )
        try:
            val = float(val)
        except ValueError:
            raise error.MILIValueError(f"Invalid percentage value '{val}'")
        return ((dim * float(val)) / 100) * sign
    return val


def _abs_mod(val) -> float:
    if isinstance(val, str):
        val = val.strip()
        sign = 1
        if val.startswith("-"):
            val = val.removeprefix("-")
            sign = -1
        if not (key := val[0]).isnumeric():
            if key in _number_mods:
                number = float(val.removeprefix(key))
                return _number_mods[key](number) * sign
            else:
                raise error.MILIValueError(
                    f"The character prefix '{key}' of the value '{val}' is not registered as a number modifier and cannot be evaluated"
                )
        try:
            val = float(val)
        except ValueError:
            raise error.MILIValueError(f"Invalid number in string '{val}'")
        return val * sign
    return val


def _get_first_button(buttons):
    bid = -1
    for i, b in enumerate(buttons):
        if b:
            bid = i + 1
            break
    return bid


def _nine_patch(image: pygame.Surface, w, h, s, smoothscale):
    ow, oh = image.get_size()
    scale_func = pygame.transform.smoothscale if smoothscale else pygame.transform.scale
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
        base.blit(scale_func(subsurf((0, s, s, ovsize)), (s, vsize)), (0, s))  # left
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


def _render_text(
    data,
    font: pygame.Font,
    fontalign,
    fontdir,
    antialias,
    color,
    bg_color,
    bold,
    italic,
    underline,
    strikethrough,
    wraplen,
    outline_color,
):
    font.align = fontalign
    font.bold = bold
    font.italic = italic
    font.underline = underline
    font.strikethrough = strikethrough
    font.set_direction(fontdir)
    if outline_color is None:
        return font.render(str(data), antialias, color, bg_color, max(0, int(wraplen)))
    middle = font.render(str(data), antialias, color, None, max(0, int(wraplen)))
    outline = font.render(
        str(data), antialias, outline_color, bg_color, max(0, int(wraplen))
    )
    output = pygame.Surface((middle.width + 2, middle.height + 2), pygame.SRCALPHA)
    for offset in _OUTLINE_OFFSETS:
        output.blit(outline, offset)
    output.blit(middle, (1, 1))
    return output


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
    transforms,
    filters,
) -> pygame.Surface:
    if transforms is not None:
        for transform in transforms:
            if callable(transform):
                res = transform(data)
            else:
                func, *args = transform
                res = func(data, *args)
            if not isinstance(res, pygame.Surface):
                raise error.MILIValueError(
                    "Image transform must return a new Surface or the same Surface"
                )
            data = res
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
        image = _nine_patch(data, tw, th, nine_patch, smoothscale)

    w, h = image.size
    if fill_color is not None:
        image.fill(fill_color)
    if not isinstance(border_radius, float | int) or border_radius > 0:
        mask_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        if isinstance(border_radius, float | int):
            border_radius = int(border_radius)
            if w == h and border_radius == w // 2:
                if smoothscale:
                    pygame.draw.aacircle(
                        mask_surf, (255, 255, 255, 255), (w // 2, h // 2), w // 2
                    )
                else:
                    pygame.draw.circle(
                        mask_surf, (255, 255, 255, 255), (w // 2, h // 2), w // 2
                    )
            else:
                pygame.draw.rect(
                    mask_surf, (255, 255, 255, 255), (0, 0, w, h), 0, border_radius
                )
        else:
            pygame.draw.rect(
                mask_surf, (255, 255, 255, 255), (0, 0, w, h), 0, 0, *border_radius
            )
        image.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if alpha != 255:
        image.set_alpha(alpha)
    if filters is not None:
        for ifilter in filters:
            if callable(ifilter):
                res = ifilter(image)
            else:
                func, *args = ifilter
                res = func(image, *args)
            if not isinstance(res, pygame.Surface):
                raise error.MILIValueError(
                    "Image filter must return a new Surface or the same Surface"
                )
            image = res
    return image


def _element_data(ctx: "_ctx", el: dict[str, typing.Any]) -> "_data.ElementData":
    if el["id"] in ctx._old_data:
        old_data = ctx._old_data[el["id"]]
    else:
        old_data = {
            "rect": pygame.Rect(),
            "abs_rect": pygame.Rect(),
            "children": [],
            "components": [],
            "parent_id": 0,
            "grid": None,
        }
    grid = old_data["grid"]
    return _data.ElementData(
        rect=old_data["rect"].copy(),
        absolute_rect=old_data["abs_rect"].copy(),
        z=el["z"],
        id=el["id"],
        style=el["style"],
        _children=old_data["children"],
        parent_id=old_data["parent_id"],
        components=old_data["components"],
        _grid=grid,
    )


def _align_rect(align, rect: pygame.Rect, padx, pady):
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


def _check_align(align):
    if align not in _VALID_ALIGN:
        didyoumean = ""
        if align == "left" or align == "top":
            didyoumean = ". Did you mean 'first'?"
        elif align == "right" or align == "bottom":
            didyoumean = ". Did you mean 'last'?"
        raise error.MILIValueError(f"Invalid alignment '{align}'{didyoumean}")


def _check_anchor(align):
    if align not in _VALID_ANCHOR:
        didyoumean = ""
        if align == "left" or align == "top":
            didyoumean = ". Did you mean 'first'?"
        elif align == "right" or align == "bottom":
            didyoumean = ". Did you mean 'last'?"
        raise error.MILIValueError(f"Invalid anchoring '{align}'{didyoumean}")


def _check_align_grid(align):
    if align not in _VALID_ALIGN_GRID:
        didyoumean = ""
        if align == "left" or align == "top":
            didyoumean = ". Did you mean 'first'?"
        elif align == "right" or align == "bottom":
            didyoumean = ". Did you mean 'last'?"
        raise error.MILIValueError(f"Invalid grid alignment '{align}'{didyoumean}")


def _partial_interaction(ctx, element, absolute_hover):
    element["hovered"] = False
    if (eid := element["id"]) in ctx._interaction_cache:
        i = ctx._interaction_cache[eid]
        (
            i.hovered,
            i.press_button,
            i.just_pressed_button,
            i.just_released_button,
            i.absolute_hover,
            i.unhover_pressed,
            i._just_hover,
            i._raw_data,
            i._data,
        ) = (False, -1, -1, -1, absolute_hover, False, 0, element, None)
        return i

    i = _data.Interaction(
        ctx._mili,
        False,
        -1,
        -1,
        -1,
        absolute_hover,
        False,
        0,
        element,
    )
    ctx._interaction_cache[eid] = i
    return i


def _total_interaction(ctx, element, absolute_hover, hovered, unhovered, old_el):
    if (eid := element["id"]) in ctx._interaction_cache:
        i = ctx._interaction_cache[eid]
        (
            i.hovered,
            i.press_button,
            i.just_pressed_button,
            i.just_released_button,
            i.absolute_hover,
            i.unhover_pressed,
            i._just_hover,
            i._raw_data,
            i._data,
        ) = (
            absolute_hover and hovered,
            _get_first_button(pygame.mouse.get_pressed(5, ctx._global_mouse)),
            _get_first_button(ctx._get_just_pressed_func()),
            _get_first_button(ctx._get_just_released_func()) if absolute_hover else -1,
            absolute_hover,
            unhovered,
            0,
            old_el,
            None,
        )
    else:
        i = _data.Interaction(
            ctx._mili,
            absolute_hover and hovered,
            _get_first_button(pygame.mouse.get_pressed(5, ctx._global_mouse)),
            _get_first_button(ctx._get_just_pressed_func()),
            _get_first_button(ctx._get_just_released_func()) if absolute_hover else -1,
            absolute_hover,
            unhovered,
            0,
            old_el,
        )
        ctx._interaction_cache[eid] = i
    if i.hovered and not old_el["hovered"]:
        i._just_hover = 1
    if not i.hovered and old_el["hovered"]:
        i._just_hover = -1
    element["hovered"] = i.hovered
    return i


def _border_radius(style, w, h):
    if isinstance(style, (int, float, str)):
        return int(_abs_perc(style, min(w, h)))
    else:
        return [int(_abs_perc(br, min(w, h))) for br in style]


def _get_conditional_color(it, color):
    if it.left_pressed:
        return color["press"]
    if it.hovered:
        return color["hover"]
    return color["default"]


def _draw_line(canva, antialias, width, color, points, dash_size, dash_offset):
    if dash_size is None:
        if antialias and (width == 1 or pygame.vernum >= (2, 5, 6)):
            if pygame.vernum >= (2, 5, 6):
                pygame.draw.aaline(
                    canva,
                    color,
                    points[0],
                    points[1],
                    width,
                )
            else:
                pygame.draw.aaline(
                    canva,
                    color,
                    points[0],
                    points[1],
                )
        else:
            pygame.draw.line(canva, color, points[0], points[1], width)
    else:
        if isinstance(dash_size, (str, int, float)):
            fill_size = space_size = dash_size
        else:
            fill_size, space_size = dash_size

        p1 = pygame.Vector2(points[0])
        p2 = pygame.Vector2(points[1])
        line_len = p1.distance_to(p2)
        fill_size = _abs_perc(fill_size, line_len)
        space_size = _abs_perc(space_size, line_len)
        dash_offset = _abs_perc(dash_offset, line_len)
        if dash_offset >= line_len:
            return
        direction = p2 - p1
        if direction.magnitude() != 0:
            direction.normalize_ip()

        cur_point = p1 + direction * dash_offset
        do_fill = True
        cur_size = fill_size
        while True:
            if cur_size == 0:
                break
            do_break = False
            next_point = cur_point + cur_size * direction
            next_len = p1.distance_to(next_point)
            if next_len >= line_len:
                next_point = p2.copy()
                do_break = True
            if do_fill:
                if antialias and (width == 1 or pygame.vernum >= (2, 5, 6)):
                    if pygame.vernum >= (2, 5, 6):
                        pygame.draw.aaline(canva, color, cur_point, next_point, width)
                    else:
                        pygame.draw.aaline(canva, color, cur_point, next_point)
                else:
                    pygame.draw.line(canva, color, cur_point, next_point, width)
                do_fill = False
                cur_size = space_size
            else:
                do_fill = True
                cur_size = fill_size
            cur_point = next_point
            if do_break:
                break


def _draw_circle(
    canva, circle_rect, antialias, color, outline, corners, dash_size, dash_anchor
):
    if dash_size is None or outline <= 0:
        if circle_rect.w == circle_rect.h:
            if corners is None:
                (pygame.draw.aacircle if antialias else pygame.draw.circle)(
                    canva,
                    color,
                    circle_rect.center,
                    circle_rect.w / 2,
                    outline,
                )
            else:
                (pygame.draw.aacircle if antialias else pygame.draw.circle)(
                    canva,
                    color,
                    circle_rect.center,
                    circle_rect.w / 2,
                    outline,
                    *corners,
                )
        else:
            pygame.draw.ellipse(canva, color, circle_rect, outline)
    else:
        pi2 = math.pi * 2
        if isinstance(dash_size, (int, float)):
            fill_size = space_size = dash_size
        else:
            fill_size, space_size = dash_size
        if isinstance(dash_anchor, (int, float)):
            start_ang = end_ang = dash_anchor
        else:
            start_ang, end_ang = dash_anchor

        start_ang = (start_ang / 100) * pi2
        end_ang = (end_ang / 100) * pi2
        fill_size = (fill_size / 100) * pi2
        space_size = (space_size / 100) * pi2
        real_end = end_ang
        if start_ang >= end_ang:
            real_end = pi2 + end_ang

        cur_ang = start_ang
        do_fill = True
        cur_size = fill_size
        while True:
            if cur_size == 0:
                break
            do_break = False
            next_ang = cur_ang + cur_size
            if next_ang >= real_end:
                next_ang = real_end
                do_break = True
            if do_fill:
                pygame.draw.arc(canva, color, circle_rect, cur_ang, next_ang, outline)
                do_fill = False
                cur_size = space_size
            else:
                do_fill = True
                cur_size = fill_size
            cur_ang = next_ang
            if do_break:
                break


def _dash_get_side(pos, rect):
    if pos <= rect.w:
        return "t", pos
    elif pos <= rect.w + rect.h:
        return "r", pos - rect.w
    elif pos <= rect.w * 2 + rect.h:
        return "b", pos - rect.w - rect.h
    elif pos <= rect.w * 2 + rect.h * 2:
        return "l", pos - rect.w * 2 - rect.h
    else:
        return "o", pos - (rect.w * 2 + rect.h * 2)
    return "", 0


def _draw_rect(canva, color, base_rect, outline, border_radius, dash_size, dash_offset):
    if dash_size is None or outline <= 0:
        if isinstance(border_radius, list):
            pygame.draw.rect(
                canva,
                color,
                base_rect,
                int(outline),
                0,
                *border_radius,
            )
        else:
            pygame.draw.rect(
                canva,
                color,
                base_rect,
                int(outline),
                int(border_radius),
            )
    else:
        if isinstance(dash_size, (str, int, float)):
            fill_size = space_size = dash_size
        else:
            fill_size, space_size = dash_size

        perimeter = base_rect.w * 2 + base_rect.h * 2
        fill_size = _abs_perc(fill_size, perimeter)
        space_size = _abs_perc(space_size, perimeter)
        dash_offset = _abs_perc(dash_offset, perimeter)

        cur_len = dash_offset
        do_draw = True
        step_len = fill_size
        i = 0

        while i < perimeter + 1:
            do_break = False
            next_len = cur_len + step_len
            if next_len > perimeter + dash_offset:
                next_len = perimeter + dash_offset
                do_break = True
            if do_draw:
                a_side, ar = _dash_get_side(cur_len, base_rect)
                b_side, br = _dash_get_side(next_len, base_rect)
                func = _dash_FUNCS[f"{a_side}{b_side}"]
                func(canva, ar, br, base_rect, color, outline)
                step_len = space_size
                do_draw = False
            else:
                step_len = fill_size
                do_draw = True
            cur_len = next_len
            i += 1
            if do_break:
                break


def _dash_tt(canva, a, b, rect, color, size):
    pygame.draw.rect(canva, color, (rect.x + a, rect.y, b - a, size))


def _dash_tr(canva, a, b, rect, color, size):
    _dash_tt(canva, a, rect.w, rect, color, size)
    _dash_rr(canva, 0, b, rect, color, size)


def _dash_tb(canva, a, b, rect, color, size):
    _dash_tt(canva, a, rect.w, rect, color, size)
    _dash_rr(canva, 0, rect.h, rect, color, size)
    _dash_bb(canva, 0, b, rect, color, size)


def _dash_tl(canva, a, b, rect, color, size):
    _dash_tt(canva, a, rect.w, rect, color, size)
    _dash_rr(canva, 0, rect.h, rect, color, size)
    _dash_bb(canva, 0, rect.w, rect, color, size)
    _dash_ll(canva, 0, b, rect, color, size)


def _dash_to(canva, a, b, rect, color, size):
    _dash_tt(canva, a, rect.w, rect, color, size)
    _dash_rr(canva, 0, rect.h, rect, color, size)
    _dash_bb(canva, 0, rect.w, rect, color, size)
    _dash_ll(canva, 0, rect.h, rect, color, size)
    _dash_tt(canva, 0, b, rect, color, size)


def _dash_rr(canva, a, b, rect, color, size):
    pygame.draw.rect(canva, color, (rect.right - size, rect.y + a, size, b - a))


def _dash_rb(canva, a, b, rect, color, size):
    _dash_rr(canva, a, rect.h, rect, color, size)
    _dash_bb(canva, 0, b, rect, color, size)


def _dash_rl(canva, a, b, rect, color, size):
    _dash_rr(canva, a, rect.h, rect, color, size)
    _dash_bb(canva, 0, rect.w, rect, color, size)
    _dash_ll(canva, 0, b, rect, color, size)


def _dash_ro(canva, a, b, rect, color, size):
    _dash_rr(canva, a, rect.h, rect, color, size)
    _dash_bb(canva, 0, rect.w, rect, color, size)
    _dash_ll(canva, 0, rect.h, rect, color, size)
    _dash_tt(canva, 0, b, rect, color, size)


def _dash_bb(canva, a, b, rect, color, size):
    pygame.draw.rect(
        canva, color, (rect.x + (rect.w - b), rect.bottom - size, b - a, size)
    )


def _dash_bl(canva, a, b, rect, color, size):
    _dash_bb(canva, a, rect.w, rect, color, size)
    _dash_ll(canva, 0, b, rect, color, size)


def _dash_bo(canva, a, b, rect, color, size):
    _dash_bb(canva, a, rect.w, rect, color, size)
    _dash_ll(canva, 0, rect.h, rect, color, size)
    _dash_tt(canva, 0, b, rect, color, size)


def _dash_ll(canva, a, b, rect, color, size):
    pygame.draw.rect(canva, color, (rect.x, rect.y + (rect.h - b), size, b - a))


def _dash_lo(canva, a, b, rect, color, size):
    _dash_ll(canva, a, rect.h, rect, color, size)
    _dash_tt(canva, 0, b, rect, color, size)


_dash_FUNCS = {
    "tt": _dash_tt,
    "tr": _dash_tr,
    "tb": _dash_tb,
    "tl": _dash_tl,
    "to": _dash_to,
    "rr": _dash_rr,
    "rb": _dash_rb,
    "rl": _dash_rl,
    "ro": _dash_ro,
    "bb": _dash_bb,
    "bl": _dash_bl,
    "bo": _dash_bo,
    "ll": _dash_ll,
    "lo": _dash_lo,
    "oo": _dash_tt,
}
