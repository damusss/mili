import os
import io
import urllib.request
import urllib.error
import threading
import pygame
import typing
import html.parser
from mili import _coreutils
from mili import icon as mili_icon
from mili.data import TextCache, ImageCache
from pygame._sdl2 import video as pgvideo

if typing.TYPE_CHECKING:
    from mili.mili import MILI, MarkDown
    from mili.typing import MarkDownStyleLike, _TextRichMarkdownStyleLike
    from mili.canva import _AbstractCanva


def _markdown_ui(mili: "MILI", markdown: "MarkDown"):
    if markdown._parse_result is None:
        return
    parent = mili._ctx._parent
    pad = mili._ctx._style_val(parent["style"], "element", "pad", 0)
    padx = _coreutils._abs_perc(
        mili._ctx._style_val(parent["style"], "element", "padx", pad), parent["rect"].w
    )
    actions = {
        "link_hover": markdown._link_hover,
        "link_click": markdown._link_click,
    }
    parent_w = parent["rect"].w - padx * 2
    state = {
        "bottom": 0,
        "skiph": False,
        "h": markdown._heights,
        "actions": actions,
        "images": markdown._images,
    }
    for element in markdown._parse_result:
        _md_ui_element(
            mili,
            element,
            markdown.style,
            parent_w,
            False,
            state,
        )


def _md_ui_element(
    mili,
    element: "_MDElement",
    style: "MarkDownStyleLike",
    parent_w,
    inside_quote,
    state,
):
    do_conts = True
    if state["skiph"]:
        do_conts = False
        parent_w -= style["indent_width"] * element.indent
    if element.indent > 0 and do_conts:
        mili.begin(
            None,
            {
                "resizey": True,
                "pad": 0,
                "fillx": True,
                "axis": "x",
                "clip_draw": False,
                "blocking": False,
            },
        )
        mili.element(
            (0, 0, style["indent_width"] * element.indent, 0), {"blocking": False}
        )
        inner = mili.begin(
            None,
            {
                "fillx": True,
                "resizey": True,
                "pad": 0,
                "clip_draw": False,
                "blocking": False,
            },
        )
        parent_w = inner.data.rect.w - inner.data.grid.padx * 2
    if element.type == "paragraph":
        _md_ui_paragraph(mili, element, style, parent_w, inside_quote, state)
    elif element.type == "title":
        _md_ui_title(mili, element, style, parent_w, inside_quote, state)
    elif element.type == "break-line":
        _md_ui_line_break(mili, style, state)
    elif element.type == "separator":
        mili.element((0, 0, 0, style["separator_height"]))
    elif element.type == "bullet-list":
        _md_ui_bullet_list(mili, element, style, parent_w, inside_quote, state)
    elif element.type == "quote":
        _md_ui_quote(mili, element, style, parent_w, state)
    elif element.type == "code-block":
        _md_ui_code_block(mili, element, style, parent_w, inside_quote, state)
    elif element.type == "image":
        _md_ui_image(mili, element, style, parent_w, inside_quote, state)
    elif element.type == "table":
        _md_ui_table(mili, element, style, inside_quote, state)
    if element.indent > 0 and do_conts:
        mili.end()
        mili.end()


def _md_ui_table(
    mili: "MILI",
    element: "_MDElement",
    style: "MarkDownStyleLike",
    inside_quote,
    state,
):
    eid = id(element)
    h = state["h"].get(eid, None)
    if h and (state["skiph"] or state["bottom" + h < 0]):
        it = mili.element((0, 0, 0, h), {"blocking": False})
    else:
        def_align = {
            "left": "first",
            "center": "center",
            "right": "last",
        }[style["table_alignx"]]
        with mili.begin(
            None,
            {"fillx": True, "resizey": True, "padx": 0, "pady": 0, "spacing": 0},
        ) as it:
            if style["table_bg_color"] is not None:
                mili.rect(
                    {
                        "color": style["table_bg_color"],
                        "border_radius": style["table_border_radius"],
                    }
                )
            tos = style["table_outline_size"]
            if tos > 0:
                mili.rect(
                    {
                        "color": style["line_break_color"],
                        "border_radius": style["table_border_radius"],
                        "outline": tos,
                        "draw_above": True,
                    }
                )
            for ri, row in enumerate(element.content["rows"]):
                if ri > 0:
                    mili.line_element(
                        [("-50", 0), ("50", 0)],
                        {
                            "size": style["line_break_size"],
                            "color": style["line_break_color"],
                        },
                        (0, 0, 0, style["line_break_size"]),
                        {"fillx": True},
                    )
                with mili.begin(
                    None,
                    {
                        "fillx": True,
                        "padx": 0,
                        "pady": 0,
                        "resizey": True,
                        "axis": "x",
                        "spacing": 0,
                        "default_align": {
                            "top": "first",
                            "center": "center",
                            "bottom": "last",
                        }[style["table_aligny"]],
                    },
                ):
                    for ci in range(element.content["count"]):
                        if ci > 0:
                            mili.line_element(
                                [(0, "-50"), (0, "50")],
                                {
                                    "size": style["line_break_size"],
                                    "color": style["line_break_color"],
                                },
                                (0, 0, style["line_break_size"], 0),
                                {"filly": True},
                            )
                        align = def_align
                        tab_align = element.content["aligns"][ci]
                        if tab_align != "default":
                            align = tab_align
                        with mili.begin(
                            None,
                            {
                                "padx": 0,
                                "pady": 0,
                                "fillx": True,
                                "resizey": True,
                                "default_align": align,
                            },
                        ) as cell:
                            if ci >= len(row):
                                continue
                            iel = row[ci]
                            if iel.type == "paragraph":
                                _md_ui_paragraph(
                                    mili,
                                    iel,
                                    style,
                                    cell.data.rect.w - cell.data.grid.padx * 2,
                                    inside_quote,
                                    state,
                                    {
                                        "first": pygame.FONT_LEFT,
                                        "center": pygame.FONT_CENTER,
                                        "last": pygame.FONT_RIGHT,
                                    }[align],
                                )
                            else:
                                _md_ui_image(
                                    mili,
                                    iel,
                                    style,
                                    cell.data.rect.w - cell.data.grid.padx * 2,
                                    inside_quote,
                                    state,
                                )
    _md_update_state(it, mili, state)


def _md_image_link_async(url, storage):
    try:
        with urllib.request.urlopen(url) as response:
            image_data = response.read()
            image = pygame.image.load(io.BytesIO(image_data)).convert_alpha()
            storage[url] = image
    except (urllib.error.HTTPError, urllib.error.URLError, pygame.error):
        storage[url] = None


def _md_image_disk_async(path, storage):
    try:
        image = pygame.image.load(path).convert_alpha()
        storage[path] = image
    except (urllib.error.HTTPError, urllib.error.URLError, pygame.error):
        storage[path] = None


def _md_ui_image(
    mili: "MILI",
    element: "_MDElement",
    style: "MarkDownStyleLike",
    parent_w,
    inside_quote,
    state,
):
    url = element.content["url"]
    click = element.content["click_url"]
    surface = None
    use_alt = False
    images = state["images"]
    if url in images:
        surface = images[url]
        if surface is None:
            use_alt = True
    else:
        use_alt = True
        images[url] = None
        if url.startswith("https"):
            if style["allow_image_link"]:
                if style["load_images_async"]:
                    thread = threading.Thread(
                        target=_md_image_link_async, args=(url, images)
                    )
                    thread.daemon = True
                    thread.start()
                else:
                    _md_image_link_async(url, images)
                    surface = images[url]
                    if surface is not None:
                        use_alt = False
        else:
            if os.path.exists(url):
                if style["load_images_async"]:
                    thread = threading.Thread(
                        target=_md_image_disk_async, args=(url, images)
                    )
                    thread.daemon = True
                    thread.start()
                else:
                    _md_image_disk_async(url, images)
                    surface = images[url]
                    if surface is not None:
                        use_alt = False
    if use_alt or surface is None:
        _md_ui_paragraph(
            mili,
            element.alt_element,
            style,
            parent_w,
            inside_quote,
            state,
        )
    else:
        sw, sh = surface.width, surface.height
        ratio = sh / sw
        oratio = sw / sh
        real_w = min(sw, parent_w)
        real_h = real_w * ratio
        if mili._ctx._canva._rect is not None:
            if real_h > mili._ctx._canva._rect.height:
                real_h = mili._ctx._canva._rect.height
                real_w = real_h * oratio
        it = mili.image_element(
            surface,
            {"cache": element.image_cache},
            (0, 0, real_w, real_h),
            {"blocking": click is not None},
        )
        if click is not None:
            if it.hovered:
                state["actions"]["link_hover"](click)
            if it.left_just_released:
                state["actions"]["link_click"](click)
        _md_update_state(it, mili, state)


def _md_ui_bullet_list(
    mili: "MILI",
    element: "_MDElement",
    style: "MarkDownStyleLike",
    parent_w,
    inside_quote,
    state,
):
    parent_w_decr = 0
    do_conts = True
    if state["skiph"]:
        do_conts = False
        parent_w_decr = style["indent_width"] * element.level
    inner = None
    if do_conts:
        mili.begin(
            None,
            {
                "resizey": True,
                "pad": 0,
                "fillx": True,
                "axis": "x",
                "clip_draw": False,
                "blocking": False,
            },
        )
        mili.begin(
            (0, 0, style["indent_width"], 0),
            {
                "filly": True,
                "pad": 0,
                "anchor": "center",
                "clip_draw": False,
                "blocking": False,
            },
        )
        mili.circle_element(
            {"color": style["bullet_color"], "antialias": True},
            (0, 0, style["bullet_diameter"], style["bullet_diameter"]),
            {
                "align": "center",
                "blocking": False,
            },
        )
        mili.end()

        inner = mili.begin(
            None,
            {
                "fillx": True,
                "resizey": True,
                "pad": 0,
                "clip_draw": False,
                "blocking": False,
            },
        )
    _md_ui_element(
        mili,
        element.content,
        style,
        (inner.data.rect.w - inner.data.grid.padx * 2 if inner else parent_w)
        - parent_w_decr,
        inside_quote,
        state,
    )
    if do_conts:
        mili.end()
        mili.end()


def _md_ui_quote(
    mili: "MILI",
    element: "_MDElement",
    style: "MarkDownStyleLike",
    parent_w,
    state,
):
    parent_w_decr = 0
    do_conts = True
    if state["skiph"]:
        do_conts = False
        parent_w_decr = style["indent_width"] * element.level
    inner = None
    if do_conts:
        mili.begin(
            None,
            {
                "resizey": True,
                "pad": 0,
                "fillx": True,
                "axis": "x",
                "clip_draw": False,
                "blocking": False,
            },
        )
        mili.begin(
            (0, 0, style["indent_width"] * element.level, 0),
            {
                "filly": True,
                "pad": 0,
                "anchor": "center",
                "axis": "x",
                "clip_draw": False,
                "blocking": False,
            },
        )
        for i in range(element.level):
            mili.rect_element(
                {
                    "color": style["line_break_color"],
                    "pady": -(style["separator_height"]) * 1.5,
                    "padx": (style["indent_width"] - style["quote_width"]) / 2,
                    "border_radius": style["quote_border_radius"],
                },
                None,
                {"fillx": True, "filly": True, "clip_draw": False, "blocking": False},
            )
        mili.end()
        inner = mili.begin(
            None,
            {"fillx": True, "resizey": True, "pad": 0, "blocking": False},
        )
    _md_ui_element(
        mili,
        element.content,
        style,
        (inner.data.rect.w - inner.data.grid.padx * 2 if inner else parent_w)
        - parent_w_decr,
        True,
        state,
    )
    if do_conts:
        mili.end()
        mili.end()


def _md_ui_paragraph(
    mili: "MILI",
    element: "_MDElement",
    style: "MarkDownStyleLike",
    parent_w,
    inside_quote,
    state,
    force_align=None,
):
    eid = id(element)
    h = state["h"].get(eid, None)
    if h and (state["skiph"] or state["bottom"] + h < 0):
        it = mili.element((0, 0, 0, h), {"blocking": False})
    else:
        it = mili.element(None, {"blocking": False})
        tstyle = {
            "growx": True,
            "growy": True,
            "rich": True,
            "wraplen": parent_w - style["indent_width"],
            "cache": element.cache,
            "rich_markdown": True,
            "rich_actions": state["actions"],
        }
        if inside_quote:
            tstyle["color"] = style["quote_color"]
        if force_align is not None:
            tstyle["font_align"] = force_align
        mili.text(
            element.content,
            tstyle,
        )
        assert element.cache is not None and element.cache._rich is not None
        state["h"][eid] = element.cache._rich["size"][1]
    _md_update_state(it, mili, state)


def _md_ui_code_block(
    mili: "MILI",
    element: "_MDElement",
    style: "MarkDownStyleLike",
    parent_w,
    inside_quote,
    state,
):
    eid = id(element)
    h = state["h"].get(eid, None)
    if h and (state["skiph"] or state["bottom"] + h < 0):
        it = mili.element((0, 0, 0, h), {"blocking": False})
        for i in range(3):
            mili.element(None, {"blocking": False, "ignore_grid": True})
    else:
        it = mili.begin(
            None,
            {"fillx": True, "blocking": False, "pad": 0, "resizey": True},
        )
        outside = it.data.absolute_rect.bottom < 0
        if not state["skiph"] and not outside:
            mili.rect(
                {
                    "color": style["code_bg_color"],
                    "border_radius": style["code_border_radius"],
                }
            )
            mili.rect(
                {
                    "color": style["code_outline_color"],
                    "border_radius": style["code_border_radius"],
                    "outline": 1,
                    "draw_above": True,
                }
            )
        element.scroll.update(it)
        element.scrollbar.update(it)
        mili.element(None, {"offset": element.scroll.get_offset()})
        mili.text(
            element.content,
            {
                "growx": True,
                "growy": True,
                "rich": True,
                "wraplen": 0,
                "cache": element.cache,
                "padx": style["indent_width"] / 2,
                "pady": style["indent_width"] / 2,
                "align": "left",
            }
            | ({"color": style["quote_color"]} if inside_quote else {}),
        )
        if it.absolute_hover:
            bs = style["code_copy_style"]
            bit = mili.element(
                pygame.Rect(0, 0, bs["size"], bs["size"]).move_to(
                    topright=(it.data.rect.w, 0)
                ),
                {"ignore_grid": True},
            )
            icon_col = _coreutils._get_conditional_color(bit, bs["icon_color"])
            if icon_col:
                icon = mili_icon._get_icon(bs["icon"], icon_col)
                if icon:
                    mili.image(
                        icon,
                        {"cache": element.image_cache, "pad": bs["icon_pad"]},
                    )
            if bit.hovered:
                state["actions"]["link_hover"](None)
            if bit.left_just_released:
                pygame.scrap.put_text(element.content)
        else:
            mili.element(None, {"blocking": False, "ignore_grid": True})
        if element.scrollbar.needed:
            sbc = style["code_scrollbar_style"]
            element.scrollbar.style["short_size"] = sbc["height"]
            element.scrollbar.style["padding"] = sbc["padx"]
            element.scrollbar.style["border_dist"] = sbc["pady"]
            with mili.begin(element.scrollbar.bar_rect, element.scrollbar.bar_style):
                bar = sbc["bar_color"]
                if bar:
                    mili.rect({"color": bar, "border_radius": sbc["border_radius"]})
                hit = mili.element(
                    element.scrollbar.handle_rect, element.scrollbar.handle_style
                )
                element.scrollbar.update_handle(hit)
                if hit.hovered or hit.left_pressed:
                    state["actions"]["link_hover"](None)
                handle = _coreutils._get_conditional_color(hit, sbc["handle_color"])
                if handle:
                    mili.rect({"color": handle, "border_radius": sbc["border_radius"]})
        else:
            for i in range(2):
                mili.element(None, {"blocking": False, "ignore_grid": True})
        mili.end()
        assert element.cache is not None and element.cache._rich is not None
        state["h"][eid] = element.cache._rich["size"][1]
    _md_update_state(it, mili, state)





def _md_ui_title(
    mili: "MILI",
    element: "_MDElement",
    style: "MarkDownStyleLike",
    parent_w,
    inside_quote,
    state,
):
    eid = id(element)
    h = state["h"].get(eid, None)
    if h and (state["skiph"] or state["bottom"] + h < 0):
        it = mili.element((0, 0, 0, h), {"blocking": False})
    else:
        it = mili.element(None, {"blocking": False})
        mili.text(
            f"<b>{element.content.content}</b>",
            {
                "growx": True,
                "growy": True,
                "rich": True,
                "wraplen": parent_w - style["indent_width"],
                "cache": element.content.cache,
                "size": style[f"title{element.level}_size"],
                "rich_markdown": True,
                "rich_actions": state["actions"],
            }
            | ({"color": style["quote_color"]} if inside_quote else {}),
        )
        # if not h:
        content = element.content
        assert content.cache is not None
        state["h"][eid] = content.cache._rich["size"][1]
    _md_update_state(it, mili, state)
    if element.level < 3:
        _md_ui_line_break(mili, style, state)


def _md_ui_line_break(mili, style, state):
    it = mili.element(
        (0, 0, 0, style["separator_height"]),
        {"fillx": True, "blocking": False},
    )
    outside = it.data.absolute_rect.bottom < 0
    if not outside and not state["skiph"]:
        mili.line(
            [("-50", 0), ("50", 0)],
            {"size": style["line_break_size"], "color": style["line_break_color"]},
        )
    _md_update_state(it, mili, state)


def _md_update_state(it, mili, state):
    if not state["skiph"]:
        state["bottom"] = it.data.absolute_rect.bottom
        if state["bottom"] > mili._ctx._canva._rect.h * 2:
            state["skiph"] = True


ScrollClass = None
ScrollbarClass = None


def _markdown_parse(source: str, markdown: "MarkDown"):
    global ScrollClass, ScrollbarClass
    if not source:
        return None
    # source = source.replace("<br>", "\n\n").replace("<hr>", "\n---\n")
    style = markdown.style["code_scrollbar_style"]
    if style is None:
        style = {}
    parser = _MarkDownParser(
        source,
        {
            "axis": "x",
            "short_size": style["height"],
            "padding": style["padx"],
            "border_dist": style["pady"],
        },
    )
    parser._parse()
    markdown._parse_result = parser.stack


def _color_str(col):
    col = pygame.Color(col)
    return f"({col.r}, {col.g}, {col.b}, {col.a})"


class _MDElement:
    def __init__(
        self, type_, content, indent=0, level=0, cache=None, scrollbar_style=None
    ):
        self.type = type_
        self.content: typing.Any = content
        self.indent = indent
        self.level = level
        self.cache = cache
        if cache is None and (self.type == "paragraph" or self.type == "code-block"):
            self.cache = TextCache()
        if self.type == "image":
            self.image_cache = ImageCache()
            self.alt_element = _MDElement(
                "paragraph",
                f"[{self.content['alt']}]"
                if self.content["click_url"] is None
                else f'<a href="{self.content["click_url"]}">[{self.content["alt"]}]</a>',
                self.indent,
                self.level,
            )
        if (
            self.type == "code-block"
            and ScrollClass is not None
            and ScrollbarClass is not None
        ):
            self.image_cache = ImageCache()
            self.scroll = ScrollClass()
            self.scrollbar = ScrollbarClass(self.scroll, scrollbar_style)
        if self.type == "table":
            self.content = {
                "aligns": self.content["aligns"],
                "count": len(self.content["titles"]),
                "rows": [
                    [
                        dt
                        if isinstance(dt, _MDElement)
                        else _MDElement("paragraph", dt, 0, 0)
                        for dt in self.content["titles"]
                    ]
                ]
                + [
                    [
                        dt
                        if isinstance(dt, _MDElement)
                        else _MDElement("paragraph", dt, 0, 0)
                        for dt in row
                    ]
                    for row in self.content["rows"]
                ],
            }

    def __str__(self):
        if self.level > 1:
            return f"<{self.indent}-{self.type}:{self.level}>: {self.content}"
        return f"<{self.indent}-{self.type}: {self.content}>"


# d_n_b = double_newline_break
class _MarkDownParser:
    def __init__(self, source: str, scrollbar_style):
        self.scrollbar_style = scrollbar_style
        self.source = source
        self.idx = 0
        self.char = self.source[self.idx]
        self.last_char = None
        self.last_last_char = None
        self.last_last_last_char = None
        self.eof = False
        self.stack = []
        self.last_paragraph: _MDElement | None = None
        self.ignore_start = False
        self.d_n_b = False
        self.trail = ""
        self.inside_code = False
        self.inside_cblock = False

    def _advance(self):
        self.idx += 1
        if self.idx > len(self.source) - 1:
            self.eof = True
            self.char = "\0"
            self.ignore_start = False
            return True
        self.last_last_last_char = self.last_last_char
        self.last_last_char = self.last_char
        self.last_char = self.char
        self.char = self.source[self.idx]
        if self.char == "`":
            self.inside_code = not self.inside_code
        self.trail += self.char
        if len(self.trail) > 4:
            self.trail = self.trail[1:]
        if not self.inside_code and not self.inside_cblock:
            if self.trail == "<br>":
                self.source = (
                    self.source[: self.idx + 1] + "\n" + self.source[self.idx + 1 :]
                )
            elif self.trail == "<hr>":
                self.source = (
                    self.source[: self.idx + 1]
                    + "\n---\n"
                    + self.source[self.idx + 1 :]
                )

    def _start_paragraph_or_append(self, buffer, add_newline=True):
        if self.last_paragraph is not None:
            if self.ignore_start:
                count = 0
                for char in buffer:
                    if char not in " \t":
                        break
                    count += 1
                if count > 0:
                    buffer = " " + buffer[count:]
            if add_newline:
                self.last_paragraph.content += "\n" + buffer
            else:
                self.last_paragraph.content += buffer
        else:
            paragraph = _MDElement("paragraph", buffer)
            self.last_paragraph = paragraph
            return self.last_paragraph

    def _parse_element(self, d_n_b=False, ignore_tabs=False):
        indent = 0
        buf = ""
        while self.char == "\t":
            indent += 1
            if not ignore_tabs:
                buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        if self.char == "\n":
            self._advance()
            return self._start_paragraph_or_append(buf)
        count = 0
        while self.char == " ":
            if not ignore_tabs:
                buf += self.char
            count += 1
            if count == 2:
                indent += 1
                count = 0
            self._advance()
        if self.char == "\n":
            self._advance()
            return self._start_paragraph_or_append(buf)
        if self.char in "-#>*_+!`[|":
            if self.char == "-":
                return self._parse_bullet_list(buf, indent, "-", d_n_b)
            elif self.char == "*":
                return self._parse_bullet_list(buf, indent, "*", d_n_b)
            elif self.char == "+":
                return self._parse_bullet_list_strict(buf, indent, d_n_b)
            elif self.char == "_":
                return self._parse_break_line_strict(buf, "_", d_n_b)
            elif self.char == ">":
                return self._parse_quote(buf, indent)
            elif self.char == "#":
                return self._parse_title(buf, indent, d_n_b)
            elif self.char == "!":
                return self._parse_image(buf, indent, d_n_b)
            elif self.char == "[":
                return self._parse_link_image(buf, indent, d_n_b)
            elif self.char == "`":
                return self._parse_code_block(buf, indent, d_n_b)
            if self.char == "|" and buf == "":
                return self._parse_table(buf, indent, d_n_b)
            else:
                return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        else:
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)

    def _advance_newline_check(self, buf):
        if self._advance():
            return self._start_paragraph_or_append(buf)
        if self.char == "\n":
            return self._start_paragraph_or_append(buf)
        return None

    def _parse_table(self, start_buf, indent, d_n_b):
        buf = start_buf
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        titles = []
        ctitle = ""
        while self.char != "\n":
            buf += self.char
            if self.char == "|":
                if self.last_char == "\\":
                    ctitle = ctitle.removesuffix("\\")
                    ctitle += self.char
                else:
                    titles.append(f"<b>{ctitle.strip()}</b>")
                    ctitle = ""
            else:
                ctitle += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        if ctitle:
            titles.append(f"<b>{ctitle.strip()}</b>")
            ctitle = ""
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        while self.char in " \t":
            buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        if self.char == "|":
            buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        divscount = 0
        divcount = 0
        divalign = "default"
        aligns = []
        one_different = False
        while self.char != "\n":
            buf += self.char
            if self.char == "|" and self.last_char != "\\":
                if divcount < 3:
                    return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
                else:
                    divscount += 1
                    aligns.append(divalign)
                    if divalign != "default":
                        one_different = True
                    divalign = "default"
                    divcount = 0
            else:
                if self.char != "-" and self.char != " " and self.char != ":":
                    return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
                else:
                    if self.char == ":" and divcount == 0:
                        divalign = "first"
                    elif self.char == ":":
                        divalign = "last"
                    if self.char == "-":
                        if (
                            divcount == 0
                            and divalign != "first"
                            and self.last_char == ":"
                        ):
                            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
                        divcount += 1
            if self._advance():
                return self._start_paragraph_or_append(buf)
        if divcount and divcount >= 3:
            divscount += 1
            aligns.append(divalign)
            if divalign != "default":
                one_different = True
            divalign = "default"
            divcount = 0
        if divscount != len(titles):
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        if one_different:
            aligns = ["center" if align == "default" else align for align in aligns]
        data = {"titles": titles, "rows": [], "aligns": aligns}
        self._advance()
        buf += self.char
        if self.char in "\n\0":
            self.last_paragraph = None
            return _MDElement("table", data, indent, 0)
        while True:
            cols = []
            ccol = ""
            count = 0
            while self.char != "\n":
                buf += self.char
                if self.char == "|":
                    if self.last_char == "\\":
                        ccol = ccol.removesuffix("\\")
                        ccol += self.char
                    else:
                        if count > 0:
                            ccol = ccol.strip()
                            if len(ccol) >= 4:
                                if ccol[0] == "!":
                                    ccol = self._table_image(ccol)
                                elif len(ccol) >= 9 and ccol[0] == "[":
                                    ccol = self._table_link_image(ccol)
                            cols.append(ccol)
                            ccol = ""
                        count += 1
                else:
                    count += 1
                    ccol += self.char
                if self._advance():
                    if ccol:
                        cols.append(ccol)
                    self.last_paragraph = None
                    data["rows"].append(cols)
                    return _MDElement("table", data, indent, 0)
            if ccol:
                ccol = ccol.strip()
                if len(ccol) >= 4:
                    if ccol[0] == "!" and ccol[1] == "[":
                        ccol = self._table_image(ccol)
                    elif len(ccol) >= 9 and ccol[0] == "[":
                        ccol = self._table_link_image(ccol)
                cols.append(ccol)
            data["rows"].append(cols)
            if self._advance():
                self.last_paragraph = None
                return _MDElement("table", data, indent, 0)
            if self.char == "\n":
                break
            else:
                if self._advance():
                    self.last_paragraph = None
                    return _MDElement("table", data, indent, 0)
        self.last_paragraph = None
        return _MDElement("table", data, indent, 0)

    def _table_image(self, string):
        par = _MarkDownParser(string, None)
        par._advance()
        par._advance()
        alt = ""
        while par.char != "]" or par.last_char == "\\":
            alt += par.char
            if par._advance():
                return string
        if par._advance():
            return string
        if par.char != "(":
            return string
        par._advance()
        link = ""
        while par.char != ")" or par.last_char == "\\":
            link += par.char
            if par._advance():
                return string
        return _MDElement(
            "image",
            {
                "alt": alt,
                "url": link.removeprefix('"').removesuffix('"'),
                "click_url": None,
            },
        )

    def _table_link_image(self, string):
        par = _MarkDownParser(string, None)
        par._advance()
        while par.char in "\t ":
            if par._advance():
                return string
        if par.char != "!":
            return string
        par._advance()
        if par.char != "[":
            return string
        par._advance()
        alt = ""
        while par.char != "]" or par.last_char == "\\":
            alt += par.char
            if par._advance():
                return string
        if par._advance():
            return string
        if par.char != "(":
            return string
        par._advance()
        link = ""
        while par.char != ")" or par.last_char == "\\":
            link += par.char
            if par._advance():
                return string
        if par._advance():
            return string
        while par.char in " \t":
            if par._advance():
                return string
        if par.char != "]":
            return string
        par._advance()
        if par.char != "(":
            return string
        par._advance()
        click_url = ""
        while par.char != ")" or par.last_char == "\\":
            click_url += par.char
            if par._advance():
                return string
        return _MDElement(
            "image",
            {
                "alt": alt,
                "url": link.removeprefix('"').removesuffix('"'),
                "click_url": click_url,
            },
        )

    def _parse_code_block(self, start_buf, indent, d_n_b):
        buf = start_buf
        buf += self.char
        self.inside_cblock = True
        if cr := self._advance_newline_check(buf):
            self.inside_cblock = False
            return cr
        for _ in range(2):
            if self.eof:
                self.inside_cblock = False
                return self._start_paragraph_or_append(buf)
            buf += self.char
            if self._advance():
                self.inside_cblock = False
                return self._start_paragraph_or_append(buf)
            if self.last_char != "`":
                self.inside_cblock = False
                return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        count = 0
        while self.char != "\n":
            buf += self.char
            count += 1
            if self._advance():
                self.inside_cblock = False
                return self._start_paragraph_or_append(buf)
        if (
            count > 0
            and self.last_char == "`"
            and self.last_last_char == "`"
            and self.last_last_last_char == "`"
        ):
            self.inside_cblock = False
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        buf += self.char
        if self._advance():
            self.inside_cblock = False
            return self._start_paragraph_or_append(buf)
        content = ""
        while (
            self.char != "`" or self.last_char != "`" or self.last_last_char != "`"
        ) or self.last_last_last_char == "\\":
            content += self.char
            buf += self.char
            if self._advance():
                self.inside_cblock = False
                return self._start_paragraph_or_append(buf)
        content = content[:-2]
        buf += self.char
        self._advance()
        self.last_paragraph = None
        self.ignore_start = False
        if self.char == "\n":
            self._advance()
        self.inside_cblock = False
        return _MDElement(
            "code-block",
            content.replace("<", "&lt;").replace(">", "&gt;"),
            indent,
            scrollbar_style=self.scrollbar_style,
        )

    def _parse_link_image(self, start_buf, indent, d_n_b):
        buf = start_buf
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        while self.char == " ":
            buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        if self.char != "!":
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        if self.char != "[":
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        alt_buf = ""
        while self.char != "]" or self.last_char == "\\":
            buf += self.char
            alt_buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        if self.char != "(":
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        if cr := self._advance_newline_check(buf):
            return cr
        link_buf = ""
        while self.char != ")" or self.last_char == "\\":
            buf += self.char
            link_buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        while self.char == " ":
            buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        if self.char != "]":
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        if self.char != "(":
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        click_link_buf = ""
        while self.char != ")" or self.last_char == "\\":
            buf += self.char
            click_link_buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        buf += self.char
        data = {
            "alt": alt_buf,
            "url": link_buf.removeprefix('"').removesuffix('"'),
            "click_url": click_link_buf,
        }
        self._advance()
        self.last_paragraph = None
        self.ignore_start = False
        return _MDElement("image", data, indent)

    def _parse_image(self, start_buf, indent, d_n_b):
        buf = start_buf
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr

        if self.char != "[":
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        alt_buf = ""
        while self.char != "]" or self.last_char == "\\":
            buf += self.char
            alt_buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        buf += self.char
        if cr := self._advance_newline_check(buf):
            return cr
        if self.char != "(":
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        if cr := self._advance_newline_check(buf):
            return cr
        link_buf = ""
        while self.char != ")" or self.last_char == "\\":
            buf += self.char
            link_buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        buf += self.char
        data = {
            "alt": alt_buf,
            "url": link_buf.removeprefix('"').removesuffix('"'),
            "click_url": None,
        }
        self._advance()
        self.last_paragraph = None
        self.ignore_start = False
        return _MDElement("image", data, indent)

    def _parse_quote(self, start_buf, indent):
        buf = start_buf
        buf += self.char
        level = 1
        if self._advance():
            return self._start_paragraph_or_append(buf)
        while self.char == ">":
            buf += self.char
            level += 1
            if self._advance():
                return self._start_paragraph_or_append(buf)
        if self.char == "\n":
            return self._start_paragraph_or_append(buf)
        self.last_paragraph = None
        self.ignore_start = False
        content = self._parse_element(True, True)
        if content:
            content.indent = 0
        return _MDElement("quote", content, indent, level)

    def _parse_title(self, start_buf, indent, d_n_b):
        buf = start_buf
        buf += self.char
        level = 1
        if self._advance():
            return self._start_paragraph_or_append(buf)
        while self.char == "#":
            buf += self.char
            level += 1
            if self._advance():
                return self._start_paragraph_or_append(buf)
        if self.char == "\n":
            return self._start_paragraph_or_append(buf)
        if level > 6:
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        if self.char != " ":
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
        if cr := self._advance_newline_check(buf):
            return cr
        self.last_paragraph = None
        self.ignore_start = False
        content = self._keep_parsing_as_paragraph("", True)
        return _MDElement("title", content, indent, level)

    def _parse_break_line_strict(self, start_buf, keychar, d_n_b):
        buf = start_buf
        buf += self.char
        if self._advance():
            return self._start_paragraph_or_append(buf)
        if self.char == keychar:
            return self._parse_break_line_detail(buf, keychar, d_n_b)
        else:
            self.ignore_start = False
            if self.char == "\n":
                return self._start_paragraph_or_append(buf)
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)

    def _parse_bullet_list_strict(self, start_buf, indent, d_n_b):
        buf = start_buf
        buf += self.char
        if self._advance():
            return self._start_paragraph_or_append(buf)
        if self.char == " ":
            if self._advance():
                return self._start_paragraph_or_append(buf)
            if self.char == "\n":
                return self._start_paragraph_or_append(buf)
            self.last_paragraph = None
            self.ignore_start = False
            content = self._parse_element(True, True)
            if content:
                content.indent = 0
            return _MDElement("bullet-list", content, indent)
        else:
            self.ignore_start = False
            if self.char == "\n":
                return self._start_paragraph_or_append(buf)
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)

    def _parse_bullet_list(self, start_buf, indent, keychar, d_n_b):
        buf = start_buf
        buf += self.char
        if self._advance():
            return self._start_paragraph_or_append(buf)
        if self.char == " ":
            if self._advance():
                return self._start_paragraph_or_append(buf)
            if self.char == "\n":
                return self._start_paragraph_or_append(buf)
            self.last_paragraph = None
            self.ignore_start = False
            content = self._parse_element(True, True)
            if content:
                content.indent = 0
            return _MDElement("bullet-list", content, indent)
        elif self.char == keychar:
            return self._parse_break_line_detail(buf, keychar, d_n_b)
        else:
            self.ignore_start = False
            if self.char == "\n":
                return self._start_paragraph_or_append(buf)
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)

    def _parse_break_line_detail(self, buf, keychar, d_n_b):
        buf += self.char
        if self._advance():
            return self._start_paragraph_or_append(buf)
        if self.char == keychar:
            buf += self.char
            while self.char == keychar:
                buf += self.char
                if self._advance():
                    self.last_paragraph = None
                    self.ignore_start = False
                    return _MDElement("break-line", None)
            if self.char != "\n":
                return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)
            else:
                self._advance()
                self.last_paragraph = None
                self.ignore_start = False
                return _MDElement("break-line", None)
        else:
            self.ignore_start = False
            if self.char == "\n":
                return self._start_paragraph_or_append(buf)
            return self._keep_parsing_as_paragraph(buf, d_n_b=d_n_b)

    def _keep_parsing_as_paragraph(self, start_buf, newline_break=False, d_n_b=False):
        buf = start_buf
        while self.char != "\n":
            buf += self.char
            if self._advance():
                return self._start_paragraph_or_append(buf)
        if newline_break:
            if self._advance():
                return self._start_paragraph_or_append(buf)
            ret = self._start_paragraph_or_append(buf)
            self.last_paragraph = None
            return ret
        else:
            if d_n_b:
                if self._advance():
                    return self._start_paragraph_or_append(buf)
                ret = self._start_paragraph_or_append(buf)
                if self.char == "\n":
                    self.last_paragraph = None
                else:
                    self.ignore_start = True
                    self.d_n_b = True
                return ret
            else:
                return self._start_paragraph_or_append(buf, False)

    def _parse(self):
        if self.char == "\n":
            while self.char == "\n":
                self._advance()
        while not self.eof:
            result = self._parse_element(d_n_b=self.d_n_b)
            if self.last_paragraph is None:
                self.d_n_b = False
            if result:
                self.stack.append(result)
            while self.char == "\n":
                if self.last_paragraph is not None:
                    self.last_paragraph.content += self.char
                else:
                    self.stack.append(_MDElement("separator", ""))
                if self._advance():
                    break


_SYM_CHARS = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\0"


class _MarkDownToHTMLParser:
    def __init__(self, source: str, style: "_TextRichMarkdownStyleLike|dict"):
        self.style = style
        self.source = source
        self.idx = 0
        self.char = self.source[self.idx]
        self.last_char = None
        self.last_last_char = None
        self.eof = False
        self.stack = []
        self.output = ""
        self.open_i = False
        self.i_char = None
        self.b_char = None
        self.open_b = False
        self.open_s = False
        self.open_h = False
        self.open_spoiler = False

    def _advance(self):
        self.idx += 1
        if self.idx > len(self.source) - 1:
            self.eof = True
            self.char = "\0"
            return True
        self.last_last_char = self.last_char
        self.last_char = self.char
        self.char = self.source[self.idx]

    def _add(self, buf):
        self.output += buf

    def _parse_mul_underscore(self, keychar):
        previous = self.last_char
        buf = self.char
        mode = "i"
        self._advance()
        if self.char == keychar:
            mode = "b"
            buf += self.char
            self._advance()
        if previous == "\\":
            return self._add(buf)
        if mode == "i":
            if self.open_i:
                if self.i_char == keychar:
                    if previous == " " or (
                        (previous is not None and previous not in _SYM_CHARS)
                        and self.char not in _SYM_CHARS
                    ):
                        return self._add(buf)
                    self.open_i = False
                    return self._add("</i>")
                else:
                    return self._add(buf)
            else:
                if self.char == " " or (
                    (previous is not None and previous not in _SYM_CHARS)
                    and self.char not in _SYM_CHARS
                ):
                    return self._add(buf)
                self.open_i = True
                self.i_char = keychar
                return self._add("<i>")
        elif mode == "b":
            if self.open_b:
                if self.b_char == keychar:
                    if previous == " " or (
                        (previous is not None and previous not in _SYM_CHARS)
                        and self.char not in _SYM_CHARS
                    ):
                        return self._add(buf)
                    self.open_b = False
                    return self._add("</b>")
                else:
                    return self._add(buf)
            else:
                if self.char == " " or (
                    (previous is not None and previous not in _SYM_CHARS)
                    and self.char not in _SYM_CHARS
                ):
                    return self._add(buf)
                self.open_b = True
                self.b_char = keychar
                return self._add("<b>")

    def _parse_tilde(self):
        previous = self.last_char
        buf = self.char
        if self._advance():
            return self._add(buf)
        if self.char != "~":
            return self._add(buf)
        if self._advance():
            return self._add(buf)
        if previous == "\\":
            return self._add(buf)
        if self.open_s:
            if previous == " " or (
                (previous is not None and previous not in _SYM_CHARS)
                and self.char not in _SYM_CHARS
            ):
                return self._add(buf)
            self.open_s = False
            return self._add("</s>")
        else:
            if self.char == " " or (
                (previous is not None and previous not in _SYM_CHARS)
                and self.char not in _SYM_CHARS
            ):
                return self._add(buf)
            self.open_s = True
            return self._add("<s>")

    def _parse_equals(self):
        previous = self.last_char
        buf = self.char
        if self._advance():
            return self._add(buf)
        if self.char != "=":
            return self._add(buf)
        if self._advance():
            return self._add(buf)
        if previous == "\\":
            return self._add(buf)
        if self.open_s:
            if previous == " " or (
                (previous is not None and previous not in _SYM_CHARS)
                and self.char not in _SYM_CHARS
            ):
                return self._add(buf)
            self.open_s = False
            return self._add("</color>")
        else:
            if self.char == " " or (
                (previous is not None and previous not in _SYM_CHARS)
                and self.char not in _SYM_CHARS
            ):
                return self._add(buf)
            self.open_s = True
            return self._add(
                f'<color bg="{_color_str(self.style["highlight_color"])}">'
            )

    def _parse_pipe(self):
        previous = self.last_char
        buf = self.char
        if self._advance():
            return self._add(buf)
        if previous == "\\":
            return self._add(buf)
        if self.char != "|":
            return self._add(buf)
        buf += self.char
        self._advance()
        if self.open_spoiler:
            if previous == " ":
                return self._add(buf)
            self.open_spoiler = False
            return self._add("</color></color></action>")
        else:
            if self.char == " ":
                return self._add(buf)
            self.open_spoiler = True
            return self._add(
                f'<action name="link_hover" condition="hover"><color fg="{_color_str(self.style["spoiler_color"])}" bg="{_color_str(self.style["spoiler_color"])}"><color fg="{_color_str(self.style["spoiler_text_color"])}" bg="null" condition="just-released">'
            )

    def _parse_backtick(self):
        previous = self.last_char
        buf = self.char
        if self._advance():
            return self._add(buf)
        if previous == "\\":
            return self._add(buf)
        code_buf = ""
        while self.char != "`" or self.last_char == "\\":
            code_buf += self.char
            buf += self.char
            if self._advance():
                return self._add(buf)
        self._advance()
        code_buf = code_buf.replace("<", "&lt;").replace(">", "&gt;")
        self.output += f'<color fg="{_color_str(self.style["code_text_color"])}" bg="{_color_str(self.style["code_bg_color"])}"> {code_buf} </color>'

    def _parse_lessthan(self):
        previous = self.last_char
        buf = self.char
        if self._advance():
            return self._add(buf)
        if previous == "\\":
            return self._add(buf)
        link_buf = ""
        string1 = "http://|"
        string2 = "https://"
        for i in range(8):
            if (self.char != string1[i] and i < 7) and self.char != string2[i]:
                return self._add(buf)
            link_buf += self.char
            buf += self.char
            if self._advance():
                return self._add(buf)
        while self.char != ">" or self.last_char == "\\":
            link_buf += self.char
            buf += self.char
            if self._advance():
                return self._add(buf)
        self._advance()
        self.output += f'<a href="{link_buf}">{link_buf}</a>'

    def _parse_link(self):
        previous = self.last_char
        buf = self.char
        if self._advance():
            return self._add(buf)
        if previous == "\\":
            return self._add(buf)
        txt_buf = ""
        while self.char != "]" or self.last_char == "\\":
            txt_buf += self.char
            if self._advance():
                return self._add("[" + _markdown_to_html(txt_buf, self.style))
        if self._advance():
            return self._add(f"[{_markdown_to_html(txt_buf, self.style)}]")
        if self.char != "(":
            return self._add(f"[{_markdown_to_html(txt_buf, self.style)}]")
        if self._advance():
            return self._add(f"[{_markdown_to_html(txt_buf, self.style)}](")
        link_buf = ""
        while self.char != ")" or self.last_char == "\\":
            link_buf += self.char
            if self._advance():
                return self._add(
                    f"[{_markdown_to_html(txt_buf, self.style)}]({_markdown_to_html(link_buf, self.style)}"
                )
        self._advance()
        return self._add(
            f'<a href="{link_buf}">{_markdown_to_html(txt_buf, self.style)}</a>'
        )

    def _parse_backslash(self):
        buf = self.char
        if self._advance():
            return self._add(buf)
        if self.char not in "_*|[`<=":
            return self._add(buf)

    def _parse(self):
        while not self.eof:
            if self.last_char != "\\":
                if self.char == "*":
                    self._parse_mul_underscore("*")
                elif self.char == "_":
                    self._parse_mul_underscore("_")
                elif self.char == "|":
                    self._parse_pipe()
                elif self.char == "[":
                    self._parse_link()
                elif self.char == "`":
                    self._parse_backtick()
                elif self.char == "<":
                    self._parse_lessthan()
                elif self.char == "~":
                    self._parse_tilde()
                elif self.char == "=":
                    self._parse_equals()
                elif self.char == "\\":
                    self._parse_backslash()
                else:
                    self.output += self.char
                    self._advance()
            else:
                self.output += self.char
                self._advance()
        return self.output


def _markdown_to_html(
    source: str,
    style: "_TextRichMarkdownStyleLike|dict",
):
    if not source:
        return ""
    return _MarkDownToHTMLParser(source, style)._parse()


def _comp_init(ctx, raw_text: str, style: dict, cache: "TextCache", user_size):
    rebuild = False
    parse_html = False
    padx = ctx._style_val(style, "text", "padx", 5)
    pad = ctx._style_val(style, "text", "pad", None)
    if pad is not None:
        padx = pad
    padx = _coreutils._abs_perc(padx, user_size[0])
    wraplen = _coreutils._abs_perc(
        ctx._style_val(style, "text", "wraplen", 0), user_size[0] - padx * 2
    )
    if "wraplen" in style:
        style.pop("wraplen")
    default_text = ctx._default_styles["text"]
    if cache._rich is None:
        rebuild = True
        parse_html = True
        cache._rich = {
            "active_tags": set(),
            "wraplen": wraplen,
            "wrap_overflow": False,
            "default_style": default_text.copy(),
        }
    else:
        if (
            (diff_txt := cache._rich["raw_text"] != raw_text)
            or (diff_style := cache._rich["user_style"] != style)
            or (diff_def_style := cache._rich["default_style"] != default_text)
            or cache._rich["conds_changed"]
        ):
            rebuild = True
            parse_html = (
                diff_txt or diff_style or diff_def_style or cache._rich["conds_changed"]
            )
            if diff_txt:
                cache._rich["active_tags"] = set()
        if not rebuild:
            oldwraplen = cache._rich["wraplen"]
            if wraplen != oldwraplen:
                if wraplen == 0 or oldwraplen == 0 or cache._rich["wrap_overflow"]:
                    rebuild = True
                else:
                    if wraplen < cache._rich["size"][0]:
                        rebuild = True

    if rebuild:
        cache._rich["raw_text"] = raw_text
        cache._rich["user_style"] = style
        cache._rich["user_size"] = user_size
        cache._rich["wraplen"] = wraplen
        cache._rich["default_style"] = default_text.copy()
        _process(ctx, raw_text, style, cache, user_size[1], parse_html, wraplen)


def _process(
    ctx, raw_text: str, style: dict, cache: "TextCache", uh, parse_html, wraplen
):
    rich = cache._rich
    if rich is None:
        return
    rich["render_data"] = {}
    rich["full_surf"] = None
    rich["render_full"] = False
    rich["conds_changed"] = False
    (
        fontalign,
        y_align,
        line_space,
        link_color,
        markdown,
        markdown_style,
        default_mods,
        textbox,
    ) = _process_styles(ctx, style, uh)
    if parse_html:
        if textbox:
            raw_text = raw_text.replace("<", "&lt;").replace(">", "&gt;")
        if markdown:
            raw_text = _markdown_to_html(raw_text, markdown_style)
        clean_text, chars_mods, any_tag = _RICH_TEXT_PARSER.rich_text_parse(
            raw_text, default_mods, rich["active_tags"], link_color
        )
        rich["clean_text"] = clean_text
        rich["chars_mods"] = chars_mods
        if not any_tag and line_space == 0:
            rich["render_full"] = True
            rich["full_surf"], rich["size"] = _process_render_full(
                ctx, clean_text, default_mods, wraplen, fontalign
            )
            return
    clean_text, chars_mods = rich["clean_text"], rich["chars_mods"]
    lines, overflow = _process_lines_wrap(
        ctx, clean_text, chars_mods, default_mods, wraplen
    )
    lines_data, longest_line = _process_lines_blocks(
        lines, ctx, chars_mods, default_mods
    )
    if default_mods["oc"] is not None:
        longest_line += 1
    output_blocks, total_h = _process_block_rects(
        lines_data, longest_line, fontalign, y_align, line_space, default_mods["oc"] is not None
    )
    rich["wrap_overflow"] = overflow
    rich["size"] = (longest_line, total_h)
    rich["blocks"] = output_blocks


def _process_render_full(ctx, txt, mods, wraplen, fontalign):
    font = ctx._get_font_from(mods["fn"], mods["fs"], mods["sf"])
    font.align = fontalign
    font.bold = mods["b"]
    font.italic = mods["i"]
    font.underline = mods["u"]
    font.strikethrough = mods["s"]
    oc = mods["oc"]
    size = font.render(txt, mods["fa"], "white").size
    wraplen = min(max(0, int(wraplen)), int(size[0] * 1.1))
    surf = ctx._canva._get_image(font.render(
        txt, mods["fa"], mods["fc"], mods["bc"] if oc is None else None, int(wraplen)
    ))
    size = surf.width, surf.height
    if oc is not None:
        surf2 = ctx._canva._get_image(font.render(txt, mods["fa"], oc, mods["bc"], int(wraplen)))
        surf = (surf2, surf)
    return surf, size


def _process_styles(ctx, style, uh):
    _style_val = ctx._style_val
    fontalign = _coreutils._FONT_ALIGNS[
        _style_val(style, "text", "font_align", pygame.FONT_CENTER)
    ]
    y_align = _style_val(style, "text", "rich_aligny", "center")
    line_space = _coreutils._abs_perc(
        _style_val(style, "text", "rich_linespace", 0), uh
    )
    link_color = _style_val(style, "text", "rich_link_color", (144, 154, 255))
    markdown = _style_val(style, "text", "rich_markdown", False)
    markdown_style = {}
    if markdown:
        mdstyle = _style_val(style, "text", "rich_markdown_style", {})
        markdown_style = {
            "spoiler_color": mdstyle.get("spoiler_color", "gray20"),
            "spoiler_text_color": mdstyle.get("spoiler_text_color", (150,) * 3),
            "code_bg_color": mdstyle.get("code_bg_color", (60,) * 3),
            "code_text_color": mdstyle.get("code_text_color", "white"),
            "highlight_color": mdstyle.get("highlight_color", "#604c44"),
        }

    default_mods = _process_default_mods(ctx, style)
    return (
        fontalign,
        y_align,
        line_space,
        link_color,
        markdown,
        markdown_style,
        default_mods,
        _style_val(style, "text", "_textbox", False),
    )


def _process_block_rects(lines_data, longest_line, fontalign, y_align, line_space, outlined):
    output_blocks = []
    cur_h = int(outlined)
    for line in lines_data:
        cur_w = int(outlined)
        for block in line["blocks"]:
            posx = cur_w
            if fontalign == pygame.FONT_RIGHT:
                posx = longest_line - line["w"] + cur_w
            elif fontalign == pygame.FONT_CENTER:
                posx = longest_line / 2 - line["w"] / 2 + cur_w
            posy = cur_h
            if y_align == "bottom":
                posy = cur_h + line["h"] - block["h"]
            elif y_align == "center":
                posy = cur_h + line["h"] / 2 - block["h"] / 2
            rect = pygame.Rect(posx, posy, block["w"], block["h"])
            output_blocks.append(
                {
                    "text": block["text"],
                    "rect": rect,
                    "mods": block["mods"],
                    "font": block["font"],
                }
            )
            cur_w += block["w"]
        cur_h += line["h"] + line_space
    cur_h -= line_space
    return output_blocks, cur_h+2*outlined


def _process_lines_blocks(
    lines,
    ctx,
    chars_mods,
    default_mods,
):
    lines_data = []
    ci = 0
    longest_line = 0
    prev_mods: dict | None = None
    prev_font: pygame.Font | None = None
    for lsi, line in enumerate(lines):
        line_blocks = []
        block = ""
        line_w = 0
        line_h = 0
        if line == "\n":
            cur_mods = chars_mods.get(ci, default_mods)
            cur_font = ctx._get_font_from(
                cur_mods["fn"], cur_mods["fs"], cur_mods["sf"]
            )
            line_blocks = [
                {
                    "text": "",
                    "w": 0,
                    "h": cur_font.get_height(),
                    "mods": cur_mods,
                    "font": cur_font,
                }
            ]
            line_h = cur_font.get_height()
            prev_mods = cur_mods
            prev_font = cur_font
            ci += 1
        else:
            for li, char in enumerate(line):
                cur_mods = chars_mods.get(ci, default_mods)
                cur_font = ctx._get_font_from(
                    cur_mods["fn"], cur_mods["fs"], cur_mods["sf"]
                )
                if prev_mods is None:
                    prev_mods = cur_mods
                if prev_font is None:
                    prev_font = cur_font
                cur_font.bold = cur_mods["b"]
                cur_font.italic = cur_mods["i"]
                cur_font.underline = cur_mods["u"]
                cur_font.strikethrough = cur_mods["s"]
                if char == "\n":
                    char = ""
                if char == " " and (
                    (li == 0 and lsi != 0)
                    or (li == len(line) - 1 and lsi < len(lines) - 1)
                ):
                    char = ""
                if cur_mods == prev_mods:
                    block += char
                else:
                    assert prev_font is not None and prev_mods is not None
                    prev_font.bold = prev_mods["b"]
                    prev_font.italic = prev_mods["i"]
                    prev_font.underline = prev_mods["u"]
                    prev_font.strikethrough = prev_mods["s"]
                    block_w = prev_font.size(block)[0]
                    block_h = prev_font.get_height()
                    line_w += block_w
                    if block_h > line_h:
                        line_h = block_h
                    line_blocks.append(
                        {
                            "text": block,
                            "w": block_w,
                            "h": block_h,
                            "mods": prev_mods,
                            "font": prev_font,
                        }
                    )
                    block = char
                prev_mods = cur_mods
                prev_font = cur_font
                ci += 1
            if block and prev_font is not None:
                block_w = prev_font.size(block)[0]
                block_h = prev_font.get_height()
                line_w += block_w
                if block_h > line_h:
                    line_h = block_h
                line_blocks.append(
                    {
                        "text": block,
                        "w": block_w,
                        "h": block_h,
                        "mods": prev_mods,
                        "font": prev_font,
                    }
                )
        if line_w > longest_line:
            longest_line = line_w
        lines_data.append({"blocks": line_blocks, "w": line_w, "h": line_h})
    return lines_data, longest_line


def _process_lines_wrap(ctx, clean_text, chars_mods, default_mods, wraplen):
    lines = []
    word = ""
    line = ""
    block = ""
    block_w = 0
    line_w = 0
    prev_font = None
    word_start_line = True
    overflow = False
    for i, char in enumerate(clean_text):
        cur_mods = chars_mods.get(i, default_mods)
        cur_font = ctx._get_font_from(cur_mods["fn"], cur_mods["fs"], cur_mods["sf"])
        cur_font.bold = cur_mods["b"]
        cur_font.italic = cur_mods["i"]
        cur_font.underline = cur_mods["u"]
        cur_font.strikethrough = cur_mods["s"]
        if char == "\n":
            lines.append(line + "\n")
            line_w = 0
            block_w = 0
            block = ""
            word = ""
            line = ""
            prev_font = cur_font
            continue
        if char == " ":
            word = ""
            new_word = ""
            word_start_line = False
        else:
            new_word = word + char
        if cur_font == prev_font:
            new_block = block + char
        else:
            line_w += block_w
            new_block = char
        new_block_w = cur_font.size(block)[0]
        if wraplen > 0 and line_w + new_block_w > wraplen:
            overflow = True
            if word and not word_start_line:
                line = line[: -len(word)]
                lines.append(line)
                word = new_word
                line = new_word
                block = new_word
                block_w = cur_font.size(block)[0]
                line_w = 0
                word_start_line = True
                prev_font = cur_font
            else:
                lines.append(line)
                line = char
                block = char
                word = char if char != " " else ""
                block_w = cur_font.size(char)[0]
                line_w = 0
                prev_font = cur_font
        else:
            block = new_block
            block_w = new_block_w
            word = new_word
            line += char
            prev_font = cur_font
    if line:
        lines.append(line)
    return lines, overflow


def _process_default_mods(ctx, style):
    _style_val = ctx._style_val
    return {
        "b": _style_val(style, "text", "bold", False),
        "i": _style_val(style, "text", "italic", False),
        "u": _style_val(style, "text", "underline", False),
        "s": _style_val(style, "text", "strikethrough", False),
        "fa": _style_val(style, "text", "antialias", True),
        "fc": _style_val(style, "text", "color", "white"),
        "bc": _style_val(style, "text", "bg_color", None),
        "oc": _style_val(style, "text", "outline_color", None),
        "fn": _style_val(style, "text", "name", None),
        "fs": _style_val(style, "text", "size", 20),
        "sf": _style_val(style, "text", "sysfont", False),
        "conds": {},
        "actions": [],
    }


def _render(
    ctx, cache: "TextCache", absr: pygame.Rect, blit_flags, align, padx, pady, actions
):
    canva: "_AbstractCanva" = ctx._canva
    rich = cache._rich
    if rich is None:
        return
    if rich["render_full"]:
        surf = rich["full_surf"]
        if isinstance(surf, pygame.Surface|pgvideo.Texture):
            rect = surf.get_rect(**_coreutils._align_rect(align, absr, padx, pady))
            canva._blit(surf, rect, special_flags=blit_flags)
        else:
            rect = surf[1].get_rect(**_coreutils._align_rect(align, absr, padx, pady))
            for direction in _coreutils._OUTLINE_OFFSETS_CENTERED:
                canva._blit(
                    surf[0],
                    (rect.x + direction[0], rect.y + direction[1]),
                    special_flags=blit_flags,
                )
            canva._blit(surf[1], rect, special_flags=blit_flags)
        return
    clip = canva._get_clip()
    full_rect = pygame.Rect((0, 0), rich["size"]).move_to(
        **_coreutils._align_rect(align, absr, padx, pady)
    )
    tags_changed = False
    tags_stats = {}
    active_tags = rich["active_tags"]
    offset = pygame.Vector2(full_rect.topleft)
    render_data = rich["render_data"]
    mpos = pygame.Vector2(pygame.mouse.get_pos())
    pressed = pygame.mouse.get_pressed()
    just_pressed = pygame.mouse.get_just_pressed()
    just_released = pygame.mouse.get_just_released()
    for i, block in enumerate(rich["blocks"]):
        rect = block["rect"]
        rect = rect.move_to(topleft=rect.topleft + offset)
        mods = block["mods"]
        if not rect.colliderect(clip):
            for tagid, condition in mods["conds"].items():
                if tagid not in tags_stats:
                    tags_stats[tagid] = {"add": 0, "remove": 0}
                if condition in ["hovered", "pressed"]:
                    if tagid in active_tags:
                        tags_stats[tagid]["remove"] += 1
            continue
        if i in render_data:
            surface = render_data[i]
        else:
            font: pygame.Font = block["font"]
            font.bold = mods["b"]
            font.italic = mods["i"]
            font.underline = mods["u"]
            font.strikethrough = mods["s"]
            outline_col = mods["oc"]
            surface = canva._get_image(font.render(
                block["text"],
                mods["fa"],
                mods["fc"],
                mods["bc"] if outline_col is None else None,
            ))
            if outline_col is not None:
                outline_surf = canva._get_image(font.render(
                    block["text"], mods["fa"], outline_col, mods["bc"]
                ))
                surface = (outline_surf, surface)
            render_data[i] = surface
        if isinstance(surface, pygame.Surface|pgvideo.Texture):
            canva._blit(surface, rect, special_flags=blit_flags)
        else:
            for direction in _coreutils._OUTLINE_OFFSETS_CENTERED:
                canva._blit(
                    surface[0],
                    (rect.x + direction[0], rect.y + direction[1]),
                    special_flags=blit_flags,
                )
            canva._blit(surface[1], rect, special_flags=blit_flags)
        hovered = rect.collidepoint(mpos)
        for tagid, condition in mods["conds"].items():
            if tagid not in tags_stats:
                tags_stats[tagid] = {"add": 0, "remove": 0}
            match condition:
                case "hovered" | "hover":
                    if hovered:
                        tags_stats[tagid]["add"] += 1
                    else:
                        tags_stats[tagid]["remove"] += 1
                case "pressed" | "press":
                    if hovered and pressed[0]:
                        tags_stats[tagid]["add"] += 1
                    else:
                        tags_stats[tagid]["remove"] += 1
                case "just-pressed":
                    if hovered and just_pressed[0]:
                        if tagid not in active_tags:
                            tags_stats[tagid]["add"] += 1
                        else:
                            tags_stats[tagid]["remove"] += 1
                case "just-released":
                    if hovered and just_released[0]:
                        if tagid not in active_tags:
                            tags_stats[tagid]["add"] += 1
                        else:
                            tags_stats[tagid]["remove"] += 1
        if not hovered:
            continue
        for actiond in mods["actions"]:
            aname, acond, abtn, adat = (
                actiond["name"],
                actiond["cond"],
                actiond["btn"],
                actiond["data"],
            )
            if aname not in actions:
                continue
            action = actions[aname]
            if aname is None or acond is None:
                continue
            match acond:
                case "hovered" | "hover":
                    action(adat)
                case "pressed" | "press":
                    if pressed[abtn - 1]:
                        action(adat)
                case "just-pressed":
                    if just_pressed[abtn - 1]:
                        action(adat)
                case "just-released":
                    if just_released[abtn - 1]:
                        action(adat)
    for tagid, stats in tags_stats.items():
        add = stats["add"]
        remove = stats["remove"]
        if add > 0:
            if tagid not in active_tags:
                active_tags.add(tagid)
                tags_changed = True
        elif remove > 0:
            if tagid in active_tags:
                active_tags.remove(tagid)
                tags_changed = True
    rich["conds_changed"] = tags_changed


class _RichTextParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()

    def rich_text_parse(self, raw_text, default_mods, active_tags, link_color):
        self.active_tags = active_tags
        self.clean_text = ""
        self.mods_stack: dict[str, list] = {}
        self.link_color = _color_str(link_color)
        for key in [
            "b",
            "i",
            "u",
            "s",
            "fa",
            "fc",
            "bc",
            "oc",
            "fn",
            "fs",
            "sf",
            "conds",
            "actions",
        ]:
            self.mods_stack[key] = [default_mods[key]]
        self.any_tag = False
        self.mods = default_mods.copy()
        self.chars_mods = {}
        self.font_keys_stack = []
        self.color_keys_stack = []
        self.tag_indent = 0
        self.tag_id = 0
        self.inactive_ids = set()
        self.conditioned_ids = set()
        self.tag_stack = {
            "b": [],
            "i": [],
            "u": [],
            "s": [],
            "font": [],
            "color": [],
            "action": [],
        }

        self.feed(raw_text)
        self.close()
        return self.clean_text, self.chars_mods, self.any_tag

    def handle_data(self, data):
        starti = len(self.clean_text)
        self.clean_text += data
        if self.tag_indent <= 0:
            return
        mods = self.mods.copy()
        mods["conds"] = self.mods["conds"].copy()
        mods["actions"] = self.mods["actions"].copy()
        for i in range(starti, len(self.clean_text)):
            self.chars_mods[i] = mods

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.any_tag = True
            data = None
            for aname, aval in attrs:
                if aname == "href":
                    data = aval
                    break
            self.handle_starttag(
                "action",
                [
                    ("name", "link_click"),
                    ("condition", "just-released"),
                    ("data", data),
                ],
            )
            self.handle_starttag(
                "action", [("name", "link_hover"), ("condition", "hovered")]
            )
            self.handle_starttag("color", [("fg", self.link_color)])
            self.handle_starttag("u", [("condition", "hovered")])
            return
        self.tag_id += 1
        self.tag_indent += 1
        if tag in self.tag_stack:
            self.tag_stack[tag].append(self.tag_id)
        else:
            self.tag_id -= 1
            return
        self.any_tag = True
        values = {}
        keys = []
        font = False
        color = False
        action = False

        if tag in ["b", "i", "s", "u"]:
            bool_mult = True
            for attr, _ in attrs:
                if attr == "null":
                    bool_mult = False
                    break
            keys.append(tag)
            values[tag] = True and bool_mult
        elif tag == "font":
            font = True
            for aname, aval in attrs:
                if aname == "name":
                    keys.append("fn")
                    values["fn"] = str(aval)
                elif aname == "size" and aval is not None:
                    try:
                        value = int(aval)
                        keys.append("fs")
                        values["fs"] = value
                    except ValueError:
                        ...
                elif aname == "antialias":
                    keys.append("fa")
                    values["fa"] = False if aval == "null" else True
                elif aname == "sysfont":
                    keys.append("sf")
                    values["sf"] = False if aval == "null" else True
        elif tag == "color":
            color = True
            for aname, aval in attrs:
                if aname in ["fg", "bg", "outline"] and aval is not None:
                    key = aname.replace("g", "c")
                    if key == "outline":
                        key = "oc"
                    if aval == "null" and key == "bc":
                        keys.append("bc")
                        values["bc"] = None
                        continue
                    elif aval == "null" and key == "oc":
                        keys.append("oc")
                        values["oc"] = None
                        continue
                    try:
                        value = eval(f"pygame.Color({aval})", {"pygame": pygame})
                        keys.append(key)
                        values[key] = value
                    except Exception:
                        try:
                            value = eval(f'pygame.Color("{aval}")', {"pygame": pygame})
                            keys.append(key)
                            values[key] = value
                        except Exception:
                            ...
        elif tag == "action":
            action = True
            action_data = {}
            for aname, aval in attrs:
                if aname == "name":
                    action_data["name"] = aval
                elif aname == "condition":
                    action_data["cond"] = aval
                elif aname == "button":
                    action_data["btn"] = aval
                elif aname == "data":
                    action_data["data"] = aval
            if "name" not in action_data:
                action_data["name"] = None
            if "cond" not in action_data:
                action_data["cond"] = None
            if "btn" not in action_data:
                action_data["btn"] = 1
            if "data" not in action_data:
                action_data["data"] = None

        cond_value = None
        for aname, aval in attrs:
            if aname == "condition" and tag != "action":
                cond_value = aval
                break
        if cond_value is not None:
            self.mods["conds"][self.tag_id] = cond_value
            self.conditioned_ids.add(self.tag_id)
            if self.tag_id not in self.active_tags:
                self.inactive_ids.add(self.tag_id)
                return
        if action:
            self.mods["actions"].append(action_data)
        else:
            for key in keys:
                self.mods_stack[key].append(values[key])
                self.mods[key] = values[key]
            if font:
                self.font_keys_stack.append(keys)
            if color:
                self.color_keys_stack.append(keys)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.handle_endtag("u")
            self.handle_endtag("color")
            self.handle_endtag("action")
            self.handle_endtag("action")
            return
        self.tag_indent -= 1
        if tag in self.tag_stack:
            try:
                start_id = self.tag_stack[tag].pop()
                if start_id in self.conditioned_ids:
                    del self.mods["conds"][start_id]
                    if start_id in self.inactive_ids:
                        return
            except IndexError:
                return
        else:
            return
        if tag == "action":
            if len(self.mods["actions"]) > 0:
                self.mods["actions"].pop()
            return
        keys = []
        try:
            if tag in ["b", "i", "s", "u"]:
                keys = [tag]
            elif tag == "font":
                keys = self.font_keys_stack.pop(-1)
            elif tag == "color":
                keys = self.color_keys_stack.pop(-1)
            for key in keys:
                self.mods_stack[key].pop(-1)
                self.mods[key] = self.mods_stack[key][-1]
        except IndexError:
            ...


_RICH_TEXT_PARSER = _RichTextParser()
