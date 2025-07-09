import pygame
import mili
import os
from pygame._sdl2 import video as pgvideo

COL_DEFAULT = (30, 30, 30)
COL_HOVER = (40, 40, 40)
COL_PRESS = (28, 28, 28)
COL_BG = (24, 24, 24)
COL_OUTLINE = (40, 40, 40)
COL_BG_OUTLINE = (40, 40, 40)
ALPHAS = 180, 255, 150
COL_DISABLED = (180,) * 3
PAD = 6


def link_hover(_):
    mili.InteractionCursor.set_status("hover")


def link_click(data):
    import webbrowser

    webbrowser.open(data)


MARKDOWN = """
# Markdown Demo

Almost anything can be customized through the markdown settings or the other settings. Use the `MILI.push_styles` context sorrounding `MILI.markdown` to apply specific styles to rendered markdown, as it is composed of regular mili elements and components.

## Basics

In a more intuitive way compared to HTML, you can do the following: *italic text*, useful for _emphasis_. For stronger focus, you can make text **bold**. Both work with asterisks and underscores.

Other stylings are also supported: you can ~~strike through~~ text, ==Highlighted text== to make it super visible or `inline code`. Inlined code won't parse markdown styles (`*this is not italic*`)

> Markdown also supports quotes.
> > That can be nested.
> > > Like this
> ## Anything can be quoted, like this title
<br>

## Lists and Nesting

Bullet lists are supported with all the prefixes and can be nested:

- Basic items
  - Nested item 1
  - Nested item 2
    - Even deeper
- Another root-level item

You can also nest markdown within them (and pretty much any other markdown feature):

- **bold inside a list**
- A [link](https://example.com) inside a list
- An `inline code` inside a list
- ## A title inside a list

---

## Spoilers, Code

A way to hide text is supported even if not in the markdown standards by using spoiler tags ||like this one||.

---

Use fenced code blocks for full code snippets:

```
def greet(name):
        return f"Hello, {name}!"
```

Ideal when showing multi-line code with proper formatting and indentation. Code can be copied with the copy button and can be scrolled if it overflows.
---

## Images and Links

Images are supported:

![A sunset](https://picsum.photos/400/220)

And can work as links aswell by using the proper syntax:

[![Click me!](https://picsum.photos/401/220)](https://example.com)

Of course, links don't have to be images [like this one](https://example.com).
If you want to put a link without an alternative text, you can do so as long as it starts with http:// or https:// like this one: <https://google.com>

---

## Tables

Tables can be used for organized content and can contain a lot of styles and elements:

| Feature         | Description                       |
| :-------------- | -------------------------------: |
| *Italic*        | Italic text              |
| **Bold**        | Bolded text             |
| `Inline code`   | Code-style formatting            |
| [Link](https://example.com)       | Clickable hyperlinks             |
| ![Img](https://picsum.photos/500/300)     | Embed an image in a table cell   |

---

## Breaks and Headings (all levels)

Line breaks can be inserted using `\\n` or `<br>`,
like this one.<br>
Or this.

***

You can also use `---`, `___`, or `***` to draw horizontal rules.

---

# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6

That's pretty much it. This should be able to render pretty much correctly most of github's READMEs.<br>
"""


class MILIUIDemo(mili.UIApp):
    def __init__(self):
        pygame.init()
        print("MILI " + mili.VERSION_STR)
        win = pygame.Window("MILI-ui Demo (incomplete)", (1000, 850), borderless=True)
        renderer = pgvideo.Renderer(win)
        #renderer = None
        super().__init__(
            win,
            {
                "start_style": {"pady": 0, "padx": 0, "spacing": 0},
                "target_framerate": 120,
            },
            canva=renderer
        )
        self.original_title = self.window.title
        self.window.minimum_size = (500, 300)
        self.adaptive_scaler.height_weight = 0.1
        self.mili.default_styles(
            rect={"border_radius": 0},
            text={
                "growx": True,
                "growy": True,
                "name": "Segoe UI",
                "sysfont": True,
                "cache": "auto",
                "pady": 5,
            },
            image={"cache": "auto", "smoothscale": True},
            circle={"pad": 1},
        )
        self.scroll = mili.Scroll("scroll")
        self.scrollbar = mili.Scrollbar(
            self.scroll,
            {"handle_update_id": "sbar_handle"},
        )
        if not os.path.exists("demo_cache"):
            os.mkdir("demo_cache")
        mili.icon.setup("demo_cache", "white")
        self.sections = {
            "layout": False,
            "text": False,
            "shapes": False,
            "images": False,
            "animations": False,
            "prefab examples": False,
            "markdown": False,
        }
        self.rect_offset = 0
        self.rect_size = 0
        self.rect_space = 0
        self.circle_anchor = 0
        self.checkbox_selectables = [
            mili.Selectable(True if i == 1 else False, f"sel{i}") for i in range(4)
        ]
        self.radio_selectables = [
            mili.Selectable(True if i == 2 else False) for i in range(4)
        ]
        self.menu = mili.ContextMenu(
            self.mili,
            {
                "clamp_size": self.window.size,
                "menu_width": 200,
                "text_style": {"size": "s17"},
            },
        )
        self.menu_area_rect = None
        self.menu_pos = None
        self.markdown = mili.MarkDown(MARKDOWN)
        self.dropdown = mili.DropMenu(
            ["A", "B", "C", "D", "E", "F"],
            "B",
            ui_style={
                "text_style": {"size": "s18", "align": "left"},
                "option_text_style": {"size": "s16", "align": "left"},
            },
        )
        self.dropup = mili.DropMenu(
            ["A", "B", "C", "D", "E", "F"],
            "B",
            {"direction": "up"},
            {
                "menu_style": {"pad": 3, "spacing": 0},
                "option_border_radius": 7,
                "text_style": {"size": "s18", "align": "left"},
                "option_text_style": {"size": "s16", "align": "left"},
            },
        )

        self.CMF_autosave = False
        self.CMF_backups = True
        self.CMF_realtime_sync = False
        self.CMF_smart_edit = True
        self.CMF_multi_cursor = False
        self.CMF_highlight_changes = True
        self.CMF_show_line_numbers = True
        self.CMF_show_minimap = False
        self.CMF_word_wrap = True
        self.CMF_code_folding = False
        self.CMF_theme_dark = True
        self.CMF_theme_light = False
        self.CMF_theme_solarized = False
        self.CMF_theme_custom = False
        self.CMF_auto_compile = True
        self.CMF_show_console = True
        self.CMF_live_reload = False
        self.CMF_devtools = False
        self.CMF_experimental = False
        self.CMF_logs_enabled = True
        self.CMF_verbose_mode = False
        self.CMF_extensions_autoupdate = True
        self.CMF_load_external_plugins = False
        self.CMF_stay_logged_in = True
        self.CMF_cloud_sync = False
        self.CMF_check_updates = True
        self.CMF_telemetry = False
        self.CMF_error_reports = True

    def update(self):
        self.scrollbar.style["short_size"] = self.scale(8)
        self.rect_offset += 0.8
        self.circle_anchor += 0.2
        if self.rect_offset >= self.rect_size + self.rect_space:
            self.rect_offset = 0
        if self.circle_anchor > 10:
            self.circle_anchor = 0
        self.mili.default_styles(
            text={
                "size": "s20",
                "growx": True,
                "growy": True,
                "name": "Segoe UI",
                "sysfont": True,
                "cache": "auto",
                "pady": 3,
            },
        )
        if self.menu_area_rect is not None:
            self.menu.style["clamp_size"] = self.menu_area_rect.size
        self.menu.style["menu_width"] = self.scale(200)
        self.window.title = (
            f"{self.original_title} ({self.clock.get_fps():.0f}/120 FPS)"
        )

    def ui(self):
        needed = self.scrollbar.needed
        sbar_space = (
            self.scrollbar.style["short_size"] + self.scrollbar.style["border_dist"] * 2
        )
        with self.mili.begin(
            None,
            {
                "update_id": "scroll",
                "pady": 0,
                "padx": 0,
                "fillx": True,
                "filly": True,
            },
        ):
            if needed:
                self.ui_scrollbar()
            self.mili.id_checkpoint(1000)
            with self.mili.begin(
                (0, 0, self.window.size[0] - sbar_space - PAD * 2, 0),
                {
                    "resizey": True,
                    "offset": self.scroll.get_offset(),
                    "align": "center",
                    "pad": 0,
                    "default_align": "center",
                },
            ):
                self.mili.text_element(
                    "MILI-ui Demo (incomplete)",
                    {"size": "s35"},
                    None,
                    {"align": "center"},
                )
                self.mili.text_element(
                    "Everything inside this window, including the window movements are done with mili-ui. Check this app's code to see how everything is implemented",
                    {
                        "size": "s16",
                        "color": COL_DISABLED,
                        "slow_grow": True,
                        "wraplen": "100",
                    },
                    None,
                    {"align": "center", "fillx": True},
                )
                self.ui_sections()

    def ui_sections(self):
        self.mili.id_checkpoint(10000)
        for name, active in list(self.sections.items()):
            self.mili.id_jump(1000)
            with self.mili.begin(
                None,
                {
                    "resizey": True,
                    "fillx": True,
                    "update_id": "cursor",
                }
                | mili.CENTER
                | mili.PADLESS
                | mili.SPACELESS
                | mili.X,
            ) as row:
                self.mili.rect(
                    mili.style.color(
                        mili.style.cond_value(
                            row, COL_DEFAULT, COL_HOVER, COL_PRESS, force_hover=active
                        )
                    )
                    | {"border_radius": 7}
                )
                self.ui_arrow(active, row.data.rect.h)
                with self.mili.element(None, {"fillx": "100", "blocking": False}):
                    self.mili.text(name.title(), {"growx": False, "size": "s20"})
                if row.left_clicked and self.win_borders.can_interact():
                    self.sections[name] = not active
                self.ui_arrow(active, row.data.rect.h)
            if active:
                func = getattr(self, f"ui_section_{name.replace(' ', '_')}", None)
                if not func:
                    self.mili.text_element("This section is not implemented yet.")
                else:
                    func()

    def ui_menu_bg(self):
        self.mili.rect({"color": COL_BG})
        self.mili.rect({"outline": 1, "color": COL_OUTLINE, "draw_above": True})

    def ui_section_layout(self):
        self.mili.text_element(
            "The following containers will showcase the flexible ways MILI can organize elements. The gray children could be any element, from single components to infinitely layered containers. The containers can resize to fit their elements and can have customizable spacing and padding.",
            {"wraplen": mili.percentage(90, self.window.size[0]), "slow_grow": True},
        )
        width = self.scale(500)
        height = self.scale(180)
        ew = self.scale(30)
        sqh = self.scale(30)
        with self.mili.begin((0, 0, width, height)):
            self.ui_menu_bg()
            self.mili.text_element(
                "Elements ignoring grid",
                {"align": "center", "color": (150,) * 3, "size": "s17"},
            )
            for pos in [
                (123, 45),
                (298, 102),
                (450, 145),
                (35, 88),
                (210, 52),
                (375, 140),
                (60, 130),
                (180, 55),
                (320, 30),
                (10, 120),
            ]:
                self.mili.rect_element(
                    {"color": COL_HOVER},
                    ((self.scale(pos[0]), self.scale(pos[1])), (ew, ew)),
                    {"ignore_grid": True},
                )
        eh = self.scale(30)
        ew = self.scale(50)
        with self.mili.begin((0, 0, width, 0), {"resizey": True}):
            self.ui_menu_bg()
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, self.scale(200), eh), {"align": "first"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, self.scale(110), eh), {"align": "center"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, self.scale(250), eh), {"align": "last"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, self.scale(150), eh), {"align": "first"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, self.scale(230), eh), {"align": "first"}
            )
        with self.mili.begin(
            (0, 0, width, height), {"axis": "x", "anchor": "max_spacing"}
        ):
            self.ui_menu_bg()
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, ew, self.scale(85)), {"align": "first"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, ew, self.scale(145)), {"align": "first"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, ew, self.scale(55)), {"align": "last"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, ew, self.scale(95)), {"align": "last"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, ew, self.scale(100)), {"align": "center"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, ew, self.scale(160)), {"align": "last"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, ew, self.scale(40)), {"align": "first"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, ew, self.scale(85)), {"align": "center"}
            )
            self.mili.rect_element(
                {"color": COL_HOVER}, (0, 0, ew, self.scale(170)), {"align": "center"}
            )
        for anchor in ["center", "first", "last", "max_spacing"]:
            with self.mili.begin(
                (0, 0, width, 0), {"axis": "x", "resizey": True, "anchor": anchor}
            ):
                self.ui_menu_bg()
                for i in range(4):
                    self.mili.rect_element({"color": COL_HOVER}, (0, 0, eh, eh))
        eh = self.scale(80)
        with self.mili.begin((0, 0, width, 0), {"axis": "x", "resizey": True}):
            self.ui_menu_bg()
            with self.mili.element((0, 0, 100, eh)):
                self.mili.rect(
                    {"color": "gray40"},
                )
                self.mili.text("Fixed: 100")
            with self.mili.element(
                (0, 0, 0, eh),
                {"fillx": "100"},
            ):
                self.mili.rect({"color": COL_HOVER})
                self.mili.text("'fillx': '100'")
            with self.mili.element(
                (0, 0, 0, eh),
                {"fillx": "50"},
            ):
                self.mili.rect({"color": COL_HOVER})
                self.mili.text("'fillx': '50'")
            with self.mili.element((0, 0, 50, eh)):
                self.mili.rect(
                    {"color": "gray40"},
                )
                self.mili.text("Fixed: 50")
        with self.mili.element(
            (0, 0, 0, eh), {"fillx": "50", "size_clamp": {"min": (500, None)}}
        ):
            self.mili.rect({"color": "gray40"})
            self.mili.text(
                r"fillx is 50% but is never smaller than 500px (size clamping)",
                {"color": "black"},
            )
        self.mili.text_element("Next use the grid layout with different styling")
        with self.mili.begin(
            (0, 0, width, 0), {"resizey": True, "axis": "x", "layout": "grid"}
        ):
            self.ui_menu_bg()
            for i in range(50):
                self.mili.element((0, 0, sqh, sqh))
                self.mili.rect({"color": COL_HOVER})
                self.mili.text(f"{i}", {"size": "s15"})
        with self.mili.begin((0, 0, width, height), {"layout": "grid"}):
            self.ui_menu_bg()
            for i in range(52):
                self.mili.element((0, 0, sqh, sqh))
                self.mili.rect({"color": COL_HOVER})
                self.mili.text(f"{i}", {"size": "s15"})
        with self.mili.begin(
            (0, 0, width, height),
            {
                "layout": "grid",
                "align": "center",
                "anchor": "max_spacing",
                "grid_align": "center",
            },
        ):
            self.ui_menu_bg()
            for i in range(27):
                self.mili.element((0, 0, sqh, sqh))
                self.mili.rect({"color": COL_HOVER})
                self.mili.text(f"{i}", {"size": "s15"})

    def ui_section_text(self):
        self.mili.text_element("You can easily display text")
        self.mili.text_element("It supports every pygame capability", {"size": "s25"})
        with self.mili.begin(
            None, mili.PADLESS | mili.X | mili.CENTER | mili.SPACELESS | mili.RESIZE
        ):
            self.mili.text_element(
                "Like color or", {"color": "yellow", "bg_color": "red"}
            )
            self.mili.text_element("Bold, ", {"bold": True})
            self.mili.text_element("Italic, ", {"italic": True})
            self.mili.text_element("Striketrough,  ", {"strikethrough": True})
            self.mili.text_element("Underline, ", {"underline": True})
            self.mili.text_element("A different font, ", {"name": "Times New Roman"})
            self.mili.text_element("Not antialiased, ", {"antialias": False})
            self.mili.text_element(
                "Outlined", {"color": "black", "outline_color": "white"}
            )
        self.mili.text_element(
            "And it obviously supports\nmultiline strings\nin the same component\nwith different alignments",
            {
                "font_align": pygame.FONT_RIGHT,
                "slow_grow": True,
                "bg_color": COL_HOVER,
            },
        )
        self.mili.hline_element({"color": COL_HOVER}, (0, 0, 0, 1), {"fillx": True})
        self.mili.text_element(
            f'If you want to apply all kind of <b>different styles</b> to your text in a <i>single element</i> and with <u>properly working</u> text <s>wrapping</s> you can use the custom-made <font size="{self.scale(30)}">rich text mode</font>. It supports tags like <font size="{self.scale(26)}" name="Times New Roman" sysfont>b, i, s, u</font> for <color fg="black" outline="white">text style</color> and can <color fg="green">change font</color> or <color bg="blue">change color.</color> Multiple styles can obviously be <b><i><u><color fg="red" outline="white">combined <font size="{self.scale(20)}">in</color> all kind <color fg="yellow" bg="purple">of </font>different ways</color> by using</b> HTML-like</i> tags</u>',
            {
                "rich": True,
                "wraplen": mili.percentage(self.window.size[0], 85),
                "font_align": "left",
                "align": "left",
            },
        )

        self.mili.hline_element({"color": COL_HOVER}, (0, 0, 0, 1), {"fillx": True})
        self.mili.text_element(
            'The rich text has a few other perks: actions can be performed when certain portions of the text are clicked and certain styles are only applied if certain conditions are met, dinamically. For example, it is possible to add <a href="https://www.google.com">proper links like the current one (it will open google)</a> or easily implement <action name="link_hover" condition="hover"><color fg="gray20" bg="gray20"><color fg="(150, 150, 150)" bg="null" condition="just-released">spoiler tags like the one you just opened</color></color></action>. The same component can also render markdown text styling that is showcased in the below section.',
            {
                "rich": True,
                "rich_actions": {
                    "link_hover": link_hover,
                    "link_click": link_click,
                },
                "wraplen": mili.percentage(self.window.size[0], 85),
            },
        )

    def ui_section_shapes(self):
        self.mili.text_element(
            "MILI can add any shape provided by pygame to any element."
        )
        self.mili.text_element("Lines:")
        self.mili.hline_element({"color": "green"}, (0, 0, 0, 10), {"fillx": True})
        self.mili.hline_element(
            {"color": "yellow", "size": 5}, (0, 0, 0, 10), {"fillx": True}
        )
        self.mili.line_element(
            [("-50", "-50"), ("50", "50")],
            {"size": 2, "color": "red", "pady": 3},
            (0, 0, 0, 40),
            {"fillx": True},
        )
        el = self.mili.line_element(
            [("-50", "50"), ("50", "-50")],
            {"size": 1, "color": "blue", "pady": 3, "antialias": True},
            (0, 0, 0, 40),
            {"fillx": True},
        )
        self.mili.line_element(
            [("-50", "-50"), ("50", "50")],
            {"size": 5, "color": "green", "pady": 3},
            (0, 0, 0, 40),
            {"fillx": True},
        )
        self.mili.line_element(
            [("-50", "50"), ("50", "-50")],
            {"size": 4, "color": "blue", "pady": 3, "antialias": True},
            (0, 0, 0, 40),
            {"fillx": True},
        )
        self.mili.hline_element(
            {
                "size": 3,
                "dash_size": [el.data.rect.w / 10, el.data.rect.w / 20],
                "color": "white",
            },
            (0, 0, 0, 10),
            {"fillx": True},
        )
        self.mili.hline_element(
            {
                "size": 3,
                "dash_size": [el.data.rect.w / 100, el.data.rect.w / 200],
                "color": "pink",
            },
            (0, 0, 0, 10),
            {"fillx": True},
        )
        self.mili.text_element("Rects:")
        width = self.scale(200)
        height = self.scale(120)
        rrect = (0, 0, width, height)
        perimeter = width * 2 + height * 2
        perimeter = perimeter / 20
        self.rect_size = perimeter * (8 / 10)
        self.rect_space = perimeter * (2 / 10)
        with self.mili.begin(
            None,
            {
                "fillx": True,
                "resizey": True,
                "layout": "grid",
                "axis": "x",
                "padx": 10,
                "grid_align": "center",
                "default_align": "center",
            },
        ):
            self.mili.rect_element({"color": "gray30"}, rrect)
            self.mili.rect_element({"color": "white", "outline": 1}, rrect)
            self.mili.rect_element({"color": "green", "outline": "10"}, rrect)
            self.mili.rect_element(
                {"color": "yellow", "outline": 5, "border_radius": "50"}, rrect
            )
            self.mili.rect_element({"color": "pink", "border_radius": "30"}, rrect)
            self.mili.rect_element(
                {"color": "yellow", "outline": 1, "border_radius": 20}, rrect
            )
            self.mili.rect_element(
                {"color": "red", "outline": 2, "border_radius": [0, 20, "10", 50]},
                rrect,
            )
            with self.mili.element(rrect):
                self.mili.rect({"color": "gray20", "outline": 1})
                self.mili.rect({"color": "white", "aspect_ratio": 1, "pady": 10})
            self.mili.rect_element(
                {"color": "white", "outline": 2, "dash_size": ("2", "1")}, rrect
            )
            self.mili.rect_element(
                {
                    "color": "green",
                    "outline": 10,
                    "dash_size": (str(100 / 16), str(100 / 32)),
                },
                rrect,
            )
            self.mili.rect_element(
                {
                    "color": "blue",
                    "outline": 5,
                    "dash_size": (self.rect_size, self.rect_space),
                    "dash_offset": self.rect_offset,
                    "aspect_ratio": 1,
                },
                rrect,
            )
        self.mili.text_element("Circles/Ellipses:")
        width = self.scale(150)
        height = self.scale(150)
        crect = (0, 0, width, height)
        with self.mili.begin(
            None,
            {
                "fillx": True,
                "resizey": True,
                "layout": "grid",
                "axis": "x",
                "padx": 10,
                "grid_align": "center",
                "default_align": "center",
            },
        ):
            self.mili.circle_element({"color": "gray50"}, crect)
            self.mili.circle_element({"color": "gray50", "antialias": True}, crect)
            self.mili.circle_element(
                {"color": "white", "antialias": True, "outline": 1}, crect
            )
            with self.mili.push_styles(circle={"antialias": True}):
                self.mili.circle_element({"color": "yellow", "outline": "10"}, crect)
                self.mili.circle_element(
                    {"color": "green", "corners": [True, False, True, False]}, crect
                )
                self.mili.circle_element(
                    {
                        "color": "green",
                        "corners": [False, True, False, True],
                        "outline": 20,
                    },
                    crect,
                )
                self.mili.circle_element(
                    {"color": "red", "outline": 1, "padx": "1", "pady": "10"}, crect
                )
                self.mili.circle_element(
                    {"color": "red", "padx": "10", "pady": "1"}, crect
                )
                self.mili.circle_element(
                    {"color": "pink", "dash_size": (4, 2), "outline": 2}, crect
                )
                self.mili.circle_element(
                    {"color": "green", "dash_size": (5, 5), "outline": 1}, crect
                )
                self.mili.circle_element(
                    {
                        "color": "red",
                        "dash_size": (5, 5),
                        "dash_anchor": self.circle_anchor,
                        "outline": 1,
                    },
                    crect,
                )
                self.mili.circle_element(
                    {
                        "color": "blue",
                        "dash_size": (5, 5),
                        "dash_anchor": self.circle_anchor,
                        "outline": 1,
                        "pady": "15",
                    },
                    crect,
                )
        self.mili.text_element("Polygons:")
        width = self.scale(200)
        height = self.scale(200)
        prect = (0, 0, width, height)
        points = [
            ("0", "-50"),
            ("14", "-16"),
            ("47", "-16"),
            ("23", "6"),
            ("29", "40"),
            ("0", "20"),
            ("-29", "40"),
            ("-23", "6"),
            ("-47", "-16"),
            ("-14", "-16"),
        ]
        with self.mili.begin(
            None,
            {
                "fillx": True,
                "resizey": True,
                "layout": "grid",
                "axis": "x",
                "padx": 10,
                "grid_align": "center",
                "default_align": "center",
            },
        ):
            self.mili.polygon_element(points, {"color": "green"}, prect)
            self.mili.polygon_element(points, {"color": "yellow", "outline": 2}, prect)

    def ui_section_prefab_examples(self):
        self.mili.push_styles(rect={"border_radius": 7}, circle={"antialias": True})
        self.mili.text_element(
            "All the examples here use objects from the mili.utility submodule, whose members are exported to the mili namespace. The behavior of this window exists because of them, as well as the cursor changing. You can already see the Scroll/Scrollbar utility in action.",
            {"wraplen": mili.percentage(90, self.window.size[0])},
        )
        self.mili.text_element("Selectables:")
        size = self.scale(30)
        with self.mili.begin(
            None, {"fillx": "80", "resizey": True, "axis": "x", "anchor": "max_spacing"}
        ):
            self.ui_menu_bg()
            for i, selectable in enumerate(self.checkbox_selectables):
                with self.mili.begin(
                    None, {"resizex": True, "resizey": True, "axis": "x", "pad": 0}
                ):
                    with self.mili.element(
                        (0, 0, size, size), {"update_id": [f"sel{i}", "cursor"]}
                    ):
                        self.mili.rect(mili.style.outline(COL_OUTLINE))
                        if selectable.selected:
                            self.mili.rect({"color": "blue", "pad": 3})
                    self.mili.text_element(f"Checkbox {i}")
        with self.mili.begin(
            None, {"fillx": "80", "resizey": True, "axis": "x", "anchor": "max_spacing"}
        ):
            self.ui_menu_bg()
            for i, selectable in enumerate(self.radio_selectables):
                with self.mili.begin(
                    None, {"resizex": True, "resizey": True, "axis": "x", "pad": 0}
                ):
                    with selectable.update(
                        self.mili.element((0, 0, size, size), {"update_id": "cursor"}),
                        self.radio_selectables,
                        False,
                    ):
                        self.mili.circle(mili.style.outline(COL_OUTLINE))
                        if selectable.selected:
                            self.mili.circle({"color": "blue", "pad": 4})
                    self.mili.text_element(f"Radio Button {i}")
        self.mili.text_element("Sliders (+Dragger):")
        self.mili.text_element("Drop Menus:")
        self.dropup.ui((0, 0, 0, self.scale(35)), {"fillx": "50"})
        self.dropdown.ui((0, 0, 0, self.scale(35)), {"fillx": "50"})
        self.mili.text_element("Entrylines:")
        self.mili.pop_styles()
        self.mili.text_element("Context Menu (right click in the box below):")
        with self.mili.begin((0, 0, 0, self.scale(600)), {"fillx": True}) as cont:
            self.menu_area_rect = cont.data.absolute_rect
            self.ui_menu_bg()
            if self.menu.opened:
                self.ui_context_menu(cont.data.id)

    def ui_section_markdown(self):
        with self.mili.push_styles(
            text={"align": "left", "font_align": "left"},
            element={"align": "first", "anchor": "first"},
        ):
            self.mili.markdown(self.markdown)

    def ui_arrow(self, active, h):
        self.mili.image_element(
            mili.icon.get_google("arrow_drop_up" if active else "arrow_drop_down"),
            None,
            (0, 0, h, 0),
            {"blocking": False, "filly": True},
        )

    def ui_scrollbar(self):
        with self.mili.begin(self.scrollbar.bar_rect, self.scrollbar.bar_style):
            with self.mili.element(
                self.scrollbar.handle_rect,
                self.scrollbar.handle_style | {"update_id": ["cursor", "sbar_handle"]},
            ) as handle:
                self.mili.rect(
                    {
                        "border_radius": 5,
                        **mili.style.color(
                            mili.style.cond_value(
                                handle, COL_DEFAULT, COL_HOVER, COL_PRESS
                            )
                        ),
                    }
                )

    def event(self, event):
        self.scroll.wheel_event(event)
        if not self.menu_area_rect:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_RIGHT:
                self.menu.close()
                if self.menu_area_rect.collidepoint(event.pos):
                    self.menu.open()
                    self.menu_pos = (
                        pygame.Vector2(event.pos) - self.menu_area_rect.topleft
                    )
            elif event.button == pygame.BUTTON_LEFT and not self.menu.collidepoint(
                pygame.Vector2(event.pos) - self.menu_area_rect.topleft
            ):
                self.menu.close()

    def ui_context_menu(self, parent):
        if not self.menu_pos:
            return
        with self.menu.begin(self.menu_pos, parent):
            self.menu.icon_label("Project Control Center", "psychology")
            if self.menu.label_submenu("File"):
                with self.menu.begin_submenu():
                    self.menu.label("New")
                    self.menu.label("Open")
                    self.menu.label("Open Recent")
                    self.menu.label("Save")
                    self.menu.label("Save As...")
                    self.menu.label("Revert")
                    self.menu.separator()
                    change, self.CMF_autosave = self.menu.checkbox(
                        "Enable Autosave", self.CMF_autosave
                    )
                    change, self.CMF_backups = self.menu.checkbox(
                        "Create Backup on Save", self.CMF_backups
                    )
                    change, self.CMF_realtime_sync = self.menu.checkbox(
                        "Real-Time Sync", self.CMF_realtime_sync
                    )
                    self.menu.separator()
                    if self.menu.label_submenu("Templates"):
                        with self.menu.begin_submenu():
                            self.menu.label("HTML5")
                            self.menu.label("Vue Project")
                            self.menu.label("React Project")
                            self.menu.label("CLI Python Tool")
                            if self.menu.label_submenu("Backend Frameworks"):
                                with self.menu.begin_submenu():
                                    self.menu.label("Flask API")
                                    self.menu.label("Django Site")
                                    self.menu.label("FastAPI")
                                    if self.menu.label_submenu("Django Variants"):
                                        with self.menu.begin_submenu():
                                            self.menu.label("Admin Only")
                                            self.menu.label("API-Only")
                                            self.menu.label("Fullstack")

            if self.menu.label_submenu("Edit"):
                with self.menu.begin_submenu():
                    self.menu.label("Undo")
                    self.menu.label("Redo")
                    self.menu.label("Cut")
                    self.menu.label("Copy")
                    self.menu.label("Paste")
                    self.menu.label("Duplicate Line")
                    change, self.CMF_smart_edit = self.menu.checkbox(
                        "Enable Smart Edit", self.CMF_smart_edit
                    )
                    change, self.CMF_multi_cursor = self.menu.checkbox(
                        "Multi-Cursor Mode", self.CMF_multi_cursor
                    )
                    change, self.CMF_highlight_changes = self.menu.checkbox(
                        "Highlight Changes", self.CMF_highlight_changes
                    )

            if self.menu.label_submenu("View"):
                with self.menu.begin_submenu():
                    change, self.CMF_show_line_numbers = self.menu.checkbox(
                        "Show Line Numbers", self.CMF_show_line_numbers
                    )
                    change, self.CMF_show_minimap = self.menu.checkbox(
                        "Show Minimap", self.CMF_show_minimap
                    )
                    change, self.CMF_word_wrap = self.menu.checkbox(
                        "Enable Word Wrap", self.CMF_word_wrap
                    )
                    change, self.CMF_code_folding = self.menu.checkbox(
                        "Enable Code Folding", self.CMF_code_folding
                    )
                    self.menu.separator()
                    if self.menu.label_submenu("Themes"):
                        with self.menu.begin_submenu():
                            change1, self.CMF_theme_dark = self.menu.checkbox(
                                "Dark Mode", self.CMF_theme_dark
                            )
                            change2, self.CMF_theme_light = self.menu.checkbox(
                                "Light Mode", self.CMF_theme_light
                            )
                            change3, self.CMF_theme_solarized = self.menu.checkbox(
                                "Solarized", self.CMF_theme_solarized
                            )
                            change4, self.CMF_theme_custom = self.menu.checkbox(
                                "Use Custom Theme", self.CMF_theme_custom
                            )
                            if change1:
                                self.CMF_theme_light = self.CMF_theme_solarized = (
                                    self.CMF_theme_custom
                                ) = False
                            if change2:
                                self.CMF_theme_dark = self.CMF_theme_solarized = (
                                    self.CMF_theme_custom
                                ) = False
                            if change3:
                                self.CMF_theme_light = self.CMF_theme_dark = (
                                    self.CMF_theme_custom
                                ) = False
                            if change4:
                                self.CMF_theme_light = self.CMF_theme_solarized = (
                                    self.CMF_theme_dark
                                ) = False

            if self.menu.label_submenu("Run"):
                with self.menu.begin_submenu():
                    self.menu.label("Run Current File")
                    self.menu.label("Build All")
                    self.menu.label("Run Tests")
                    if self.menu.label_submenu("Environment"):
                        with self.menu.begin_submenu():
                            self.menu.label("Python 3.10")
                            self.menu.label("Node v18")
                            self.menu.label("Docker")
                            if self.menu.label_submenu("Docker Images"):
                                with self.menu.begin_submenu():
                                    self.menu.label("Alpine")
                                    self.menu.label("Ubuntu")
                                    self.menu.label("Custom Image")
                    self.menu.separator()
                    change, self.CMF_auto_compile = self.menu.checkbox(
                        "Auto Compile", self.CMF_auto_compile
                    )
                    change, self.CMF_show_console = self.menu.checkbox(
                        "Show Console Output", self.CMF_show_console
                    )
                    change, self.CMF_live_reload = self.menu.checkbox(
                        "Live Reload", self.CMF_live_reload
                    )

            if self.menu.label_submenu("Tools"):
                with self.menu.begin_submenu():
                    self.menu.label("Terminal")
                    self.menu.label("Database Explorer")
                    self.menu.label("API Tester")
                    self.menu.label("Profiler")
                    self.menu.label("Debugger")
                    change, self.CMF_devtools = self.menu.checkbox(
                        "Enable DevTools", self.CMF_devtools
                    )
                    change, self.CMF_experimental = self.menu.checkbox(
                        "Show Experimental Tools", self.CMF_experimental
                    )
                    change, self.CMF_logs_enabled = self.menu.checkbox(
                        "Save Logs", self.CMF_logs_enabled
                    )
                    change, self.CMF_verbose_mode = self.menu.checkbox(
                        "Verbose Mode", self.CMF_verbose_mode
                    )

            if self.menu.label_submenu("Extensions"):
                with self.menu.begin_submenu():
                    self.menu.label("Extension Manager")
                    self.menu.label("Marketplace")
                    self.menu.label("Install from File")
                    self.menu.separator()
                    change, self.CMF_extensions_autoupdate = self.menu.checkbox(
                        "Auto-Update Extensions", self.CMF_extensions_autoupdate
                    )
                    change, self.CMF_load_external_plugins = self.menu.checkbox(
                        "Allow External Plugins", self.CMF_load_external_plugins
                    )

            self.menu.separator()
            if self.menu.label_submenu("Account"):
                with self.menu.begin_submenu():
                    self.menu.label("Login")
                    self.menu.label("Logout")
                    change, self.CMF_stay_logged_in = self.menu.checkbox(
                        "Stay Logged In", self.CMF_stay_logged_in
                    )
                    change, self.CMF_cloud_sync = self.menu.checkbox(
                        "Enable Cloud Sync", self.CMF_cloud_sync
                    )

            self.menu.separator()
            change, self.CMF_check_updates = self.menu.checkbox(
                "Check for Updates", self.CMF_check_updates
            )
            change, self.CMF_telemetry = self.menu.checkbox(
                "Send Telemetry Data", self.CMF_telemetry
            )
            change, self.CMF_error_reports = self.menu.checkbox(
                "Send Error Reports", self.CMF_error_reports
            )

            self.menu.separator()
            self.menu.icon_label("Settings", "settings")
            self.menu.icon_label("Help", "help")
            with (
                mili.dict_push(
                    self.menu.style,
                    google_icon_color="red",
                    item_bg_color=(50, 15, 15),
                    hover_color=(100, 30, 30),
                ),
                self.mili.push_styles(text={"color": "red"}),
            ):
                if self.menu.icon_label("Exit", "close"):
                    self.menu.close()


def main():
    MILIUIDemo().run()


if __name__ == "__main__":
    main()
