import pygame
import mili
import os

COL_DEFAULT = (40, 40, 40)
COL_HOVER = (60, 60, 60)
COL_PRESS = (32, 32, 32)
COL_BG = (25, 25, 25)
COL_OUTLINE = (70, 70, 70)
COL_BG_OUTLINE = (50, 50, 50)
ALPHAS = 180, 255, 150
COL_DISABLED = (180,) * 3


class MILIUIDemo(mili.GenericApp):
    def __init__(self):
        pygame.init()
        super().__init__(
            pygame.Window("MILI-ui Demo", (1000, 850), borderless=True),
            start_style={"pad": 0, "spacing": 0},
        )
        self.window.minimum_size = (500, 300)
        self.borders = mili.CustomWindowBorders(self.window, titlebar_height=25)
        self.custom_behaviour = mili.CustomWindowBehavior(
            self.window, self.borders, pygame.display.get_desktop_sizes()[0]
        )
        self.scaler = mili.AdaptiveUIScaler(
            self.window, self.window.size, height_weight=0.1
        )
        self.mult = self.scaler.scale
        self.mili.default_styles(
            rect={"border_radius": 0},
            text={
                "growx": True,
                "growy": True,
                "name": "Segoe UI",
                "sysfont": True,
                "cache": "auto",
            },
            image={"cache": "auto", "smoothscale": True},
        )
        self.scroll = mili.Scroll("scroll")
        self.scrollbar = mili.Scrollbar(
            self.scroll,
            {"handle_update_id": "sbar_handle"},
        )
        if not os.path.exists("demo_cache"):
            os.mkdir("demo_cache")
        mili.icon.setup("demo_cache", "white")
        mili.InteractionCursor.setup(update_id="cursor")
        self.sections = {
            "layout": False,
            "text": False,
            "shapes": False,
            "images": False,
            "animations": False,
            "prefab examples": False,
            "markdown": False,
        }

    def update(self):
        self.borders.update()
        self.scaler.update()
        mili.animation.update_all()
        self.scrollbar.style["short_size"] = self.mult(8)

    def ui(self):
        self.mili.rect(mili.style.color(COL_BG))
        self.mili.rect(mili.style.outline(COL_BG_OUTLINE))
        needed = self.scrollbar.needed
        sbar_space = (
            self.scrollbar.style["short_size"] + self.scrollbar.style["border_dist"] * 2
            if needed
            else 0
        )
        self.ui_titlebar()
        with self.mili.begin(
            (
                (0, self.borders.titlebar_height),
                (
                    self.window.size[0],
                    self.window.size[1] - self.borders.titlebar_height,
                ),
            ),  # can be achieved with "fillx" and "filly" : True
            {"update_id": "scroll", "pad": 0},
        ):
            with self.mili.begin(
                (0, 0, self.window.size[0] - sbar_space, 0),
                {"resizey": True, "offset": self.scroll.get_offset(), "align": "first", "pad": 0},
            ):
                self.mili.text_element(
                    "MILI-ui Demo",
                    {"size": self.mult(35)},
                    None,
                    {"align": "center"},
                )
                self.mili.text_element(
                    "Everything inside this window, including the window movements are done with mili-ui.",
                    {
                        "size": self.mult(16),
                        "color": COL_DISABLED,
                        "slow_grow": True,
                        "wraplen": "100",
                    },
                    None,
                    {"align": "center", "fillx": True},
                )
                self.ui_sections()
            if needed:
                self.ui_scrollbar()
        mili.InteractionCursor.apply()

    def can_interact(self):
        return self.window.focused and self.borders.cumulative_relative.length() == 0

    def ui_sections(self):
        for name, active in list(self.sections.items()):
            with self.mili.element(None, {"fillx": True, "update_id": "cursor"}) as btn:
                self.mili.rect(
                    mili.style.color(
                        mili.style.cond_value(btn, COL_DEFAULT, COL_HOVER, COL_PRESS)
                    )
                )
                self.mili.text(name.title(), {"growx": False, "size": self.mult(20)})
                if btn.left_clicked and self.can_interact():
                    self.sections[name] = not active

    def ui_titlebar(self):
        with self.mili.begin(
            (0, 0, 0, self.borders.titlebar_height),
            {
                "spacing": 0,
                "pad": 0,
                "axis": "x",
                "fillx": True,
                "default_align": "center",
            },
        ):
            self.mili.rect(mili.style.color(COL_DEFAULT))
            self.mili.text_element("MILI-ui Demo", {"size": 17, "color": COL_DISABLED})
            self.mili.element(None, {"fillx": True})
            self.ui_titlebar_btn(
                self.custom_behaviour.minimize, "minimize", False, pady=3
            )
            self.ui_titlebar_btn(self.custom_behaviour.toggle_maximize, "stop", False)
            self.ui_titlebar_btn(self.quit, "close", True)

    def ui_titlebar_btn(self, action, icon_name, hover_red=False, pady=0):
        with self.mili.element(
            (0, 0, self.borders.titlebar_height, self.borders.titlebar_height)
        ) as btn:
            self.mili.rect(
                mili.style.color(
                    mili.style.cond_value(
                        btn, COL_DEFAULT, "red" if hover_red else COL_HOVER, COL_PRESS
                    )
                )
            )
            self.mili.image(
                mili.icon.get_google(icon_name),
                {
                    "alpha": mili.style.cond_value(btn, *ALPHAS),
                    "pady": pady,
                    "stretchx": True,
                },
            )
            if btn.left_clicked and self.can_interact():
                action()

    def ui_scrollbar(self):
        with self.mili.begin(self.scrollbar.bar_rect, self.scrollbar.bar_style):
            with self.mili.element(
                self.scrollbar.handle_rect, self.scrollbar.handle_style|{"update_id": ["cursor", "sbar_handle"]}
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


if __name__ == "__main__":
    MILIUIDemo().run()
