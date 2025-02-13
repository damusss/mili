[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

# MILI Utilities Guide

The `mili.utility` module contains functions and classes to simplify managing elements while still being independent. Everything from this module is also exported to the `mili` package. Utilities that have a style argument in their constructor have the style explained in the style guide.

## Functions

-   `mili.percentage`: Calculates the percentage of a value and returns it. The same calculation is used internally for percentage strings.
-   `mili.indent`: This function doesn't do anything, but you can use the python syntax to put lines on different indentations, for example:
    ```py
    mili.indent(
    mili.element(rect, style), # 1 indentation for element
        mili.rect(style),
        mili.text(text, style),
        mili.rect(style),
        # 2 indentations for components of this element.
    )
    ```
    You can really achieve the same by using the if statement, as the return value of element or begin will always compute to True.
-   `mili.fit_image`: Return a surface that is constrained inside the provided rectangle plus extra applied styles which are the same that you would provide to an image component and work the same.

Keep in mind that to make gray colors (generally to repeat a value in a tuple) you can use the multiply operator. `(50,) * 3` -> `(50, 50, 50)`

## `Dragger`

An object that changes the position attribute when an element is dragged around. You can use the position in the element rect to see the position. It's advised to set the ignore grid style to True. You can use the shortcut `Dragger.style` attribute for it.

You can use the following methods to make the dragger work:

-   `Dragger.update`: Responsible for moving the element, the input is returned as output. Can be avoided using the **update ID system**.
-   `Dragger.clamp`: Clamp the position. You can provide new clamp values or use the previously stored ones

If you don't use the **update ID system**, update must always be called after the element creation:

```py
interaction = mili.element((dragger.position, size), style)
dragger.update(interaction) # or use the update ID system
```

Since the update function returns the element as output, the flag stating if the position changed or not is stored in `Dragger.changed`. You can also lock the x or y axis to restrict the position even more.

## `Selectable`

An object that checks an element interaction and sets the `selected` flag appropriately, working like a checkbox. You can then modify the styles if the object is selected. Similarly to the dragger object, you need to call `update` passing the target element's interaction object to it or use the **update ID system**.

You can also provide a list of `Selectable` instances to the update method, and they will be organized in a way where only one object in the list is allowed to be selected at any time. If the `can_deselect_group` flag is True, the user will be able to deselect all selectables.

## `GenericApp`

An utility object that handles a simple pygame loop to avoid boilerplate code. Your app should inherit it and customize the `update` (called before ui) method, the `ui` method, the `event` method and the `on_quit` method. It automatically creates one `MILI` instance that you should use in the `ui` method. You can customize the game loop with the `start_style` and `target_framerate` attributes. Start the app by calling the `run` method.

Example usage:

```py
import mili
import pygame

class MyApp(mili.GenericApp):
    def __init__(self):
        super().__init__(pygame.Window("title", (500, 500)))
        self.start_style = mili.CENTER
        self.target_framerate = 120

    def update(self):...
        # update logic

    def ui(self):
        with self.mili.begin(rect, style):...
            # UI structure

    def event(self, event):
        if event.type == pygame.X:... # handle events

    def on_quit(self):
        with open("save.txt", "w") as file:...
            # quit logic

if __name__ == "__main__":
    MyApp().run()
```

## `Scroll`

This is an object that keeps a scroll offset and automatically clamps it. To update the clamp area, you need to call the `update` method passing the container's interaction or element data or use the **update ID system**. The grid data overflow is used internally to clap the scroll.

To see the scroll, you need to use the `get_offset` method, and passing the result to the children's offset style. You can update or set the scroll offset with the `scroll` and `set_scroll` methods (automatically clamped).

The object also provides a few advanced methods (`get_handle_size`, `get_rel_handle_pos_from_scroll`, `set_scroll_from_rel_handle_pos`) which are utilities for scrollbars. You can avoid using them using the `Scrollbar` utility.

Example scroll usage:

```py
scroll = mili.Scroll()

# game loop
with my_mili.begin((0, 0, 500, 500)) as container:
    scroll.update(container) # or use the update ID system

    for i in range(50):
        my_mili.element((0, 0, 0, 30), {"fillx": True, "offset": scroll.get_offset()})
        my_mili.rect({"color": (50,) * 3})
        my_mili.text(f"element {i}")

# event loop
if event.type == pygame.MOUSEWHEEL:
    scroll.scroll(event.x*2, event.y*2)
```

## `Scrollbar`

The scrollbar extends the scroll functionality supporting scrollbar utilities. It can work at one axis at a time and it needs an **independent** scroll object to rely on.

You can specify the axis and a few styling parameters in the style of the constructor. A `Dragger` is used internally for the handle. For that reason, the axis attribute cannot be changed dynamically and requires the `Scrollbar.axis` property setter. Removing any field from the `style` attribute will result in a KeyError.

Note that this utility cannot create the scrollbar nor the handle elements, you need to create them, but you can use the `bar_rect`, ○
`bar_style`, `handle_rect`, `handle_style` attributes to simplify the process. They will only work if the handle is a children of the scrollbar.

To update the scroll you need to use the associated `Scroll` object and call `Scrollbar.scroll_moved` immediately after.

To update the scrollbar either use the **update ID system** or you need to call `Scrollbar.update` passing the target container's interaction or element data (the same one you pass to `Scroll.update`, also required) and you then need to call `Scrollbar.update_handle` passing the handle's interaction.

The `needed` property signals you if the container needs to be scrolled or if the children fit inside.

Scrollbar example usage:

```py
scroll = mili.Scroll() # scroll is independent
scrollbar = mili.Scrollbar(scroll, {"short_size": 12, "axis": "y"})

# game loop
with my_mili.begin((0, 0, 500, 500)) as container:
    scroll.update(container) # or use the update ID system
    scrollbar.update(container) # or use the update ID system

    for i in range(50):
        my_mili.element((0, 0, 0, 30), {"fillx": ("96.5" if scrollbar.needed else "100"), "offset": scroll.get_offset()})
        my_mili.rect({"color": (50,) * 3})
        my_mili.text(f"element {i}")

    if scrollbar.needed:
        with my_mili.begin(scrollbar.bar_rect, scrollbar.bar_style):
            my_mili.rect({"color": (40,) * 3})

            handle_interaction = my_mili.element(scrollbar.handle_rect, scrollbar.handle_style)
            scrollbar.update_handle(handle_interaction) # or use the update ID system

# event loop
if event.type == pygame.MOUSEWHEEL:
    scroll.scroll(event.x*2, event.y*2)
    scrollbar.scroll_moved()
```

## `Slider`

An object that simplifies the implementation of 1D or 2D sliders. The axis locks can turn a 2D slider in a single-axis slider. To make the construction easier, the classmethod `Slider.from_axis` can be used. The handle size must be specified for both dimentions.

The `strict_borders` style specifies wether the handle can exceed the area borders by half its size or if it should be perfectly contained. Changing the slider axis locking dynamically is allowed without undefined behaviour. Removing any field from the `style` attribute will result in a KeyError.

The `area_style` and `handle_style` are shortcuts with the required styles for a correct slider appearance and functionality. The `handle_rect` attribute should be passed as-is to the handle element.
For the handle rect position to be accurate, the handle **must** be a children of the area without grid sorting. The slider won't make the elements for you, but it will manage them. The `Slider.update_area` and `Slider.update_handle` must be called sequentially with the appropriate interaction objects if the **update ID system** is not used:

```py
slider = mili.Slider({"lock_x": False, "lock_y": False, "handle_size": (30, 30), "strict_borders": True})

# UI loop
with self.mili.begin((0, 0, 300, 100), mili.CENTER|slider.area_style) as area:
    slider.update_area(area) # or use the update ID system

    self.mili.rect({"color": (40,)*3})
    self.mili.rect({"color": (60,)*3, "outline": 1})

    if handle:=self.mili.element(slider.handle_rect, slider.handle_style):
        self.slider.update_handle(handle) # or use the update ID system

        self.mili.rect({"color": (50,)*3})
        self.mili.rect({"color": (70,)*3, "outline": 1})

        if self.slider.moved:
            print(self.slider.value)
```

Since the update function returns the input as output, wether the handle moved is stored in the `Slider.moved` attribute. You can also retrieve or change the 2-component `value` in range 0-1. Modifying the value x and y attributes directly won't affect the position, therefore the `valuex` and `valuey` shortcuts can be used.

## `DropMenu`

An object that simplifies the implementation of drop menus, supporting down and ups menu along with a few extra styles. The utility won't create the element, instead it will calculate the menu position (in the `topleft` attribute) and handle opening and closing (do it manually with the show, hide and toggle methods). It is adviced to use the **update ID system** to automatically update the menu components. The menu container is expected to have the `ignore_grid` style set to True. To know the frame when an option is selected use the `just_selected` boolean attribute after an option has been updated. Finally use the `shown` attribute to decide wether to create the menu element or not. For example:

```py
menu = mili.DropMenu(["a", "b", "c", "d"], "a",
    {
        "direction": "down",
        "anchor": "center",
        "padding": 5,
        "selected_update_id": "sel",
        "menu_update_id": "menu",
        "option_update_id": "opt",
    }
)

# UI loop
sel_btn =my_mili.element((0, 0, 200, 50), {"update_id": "sel"})
my_mili.rect({"color": f"gray{mili.style.cond_value(sel_btn, 20, 30, 15)}"})
my_mili.text(menu.selected)
if menu.shown:
    with my_mili.begin((menu.topleft, (sel_btn.data.rect.w*2, 0)), {"resizey": True, "update_id": "menu"}|menu.menu_style): # ensure correct position and ignore_grid style
        for option in menu.options:
            opt_btn = my_mili.element((0, 0, 0, 30), {"fillx": True, "update_id": "opt"})
            my_mili.rect({"color": f"gray{mili.style.cond_value(opt_btn, 20, 30, 15)}"})
            my_mili.text(option)
            if menu.just_selected:
                print("Selected: ", menu.selected)
```

## `InteractionSound`

This utility class allows you to play sounds when elements are interacted. You have to create an instance of it for every sounds collection. Not to complicate the implementation, an instance will only play click sounds for a selected mouse button, you need multiple instances for multiple mouse buttons. Every sound is optional.

You can pass the sound objects to the constructor or change the attributes at runtime. To hear the sounds you need to call `InteractionSound.play()` passing the interaction as the main argument (the same object is returned for stacked calls) or you can use the **update ID system**. An optional channel and play settings can be specified to customize it more. The function will check the interaction and play the correct sounds.

Example usage:

```py
hover = pygame.mixer.Sound("hover.ogg")
press = pygame.mixer.Sound("press.ogg")

sound = mili.InteractionSound(hover=hover, press=press)

# UI loop
for i in range(30):
    if interaction:=self.mili.element(rect, style):
        self.mili.rect({"color": (50,) * 3})
        self.mili.text(f"button {i}")
        self.mili.rect({"color": (80,) * 3, "outline": 1})

        sound.play(interaction) # or use the update ID system
```

## `InteractionCursor`

This utility static class makes the process of changing cursor based on interaction easier. This class is not supposed to be instantiated, as every method is static. The class exports the following static methods:

-   `setup()`: Change the default cursors with custom values.
-   `update()`: Should be called for every element that should change cursor based on interaction or you can use the **update ID system**. The disabled flag will select the disabled cursor appropriately. For special elements each cursor can be overridden using keyword arguments that match the class variable names.
-   `apply()`: Must be called at the end of the UI loop, after all the update calls have been made. This method is responsible for changing the cursor. It will return the cursor that has been applied or `None` if the cursor was left unchanged.

The following cursors can be customized, each having less priority than the previous one. A value of `None` will signal the specified cursor is disabled.

-   `disabled_cursor`: Set when an element with the disabled flag is hovered or pressed.
-   `press_cursor`: Set when an element is pressed. If the cursor is a valid pygame cursor only the left mouse button will have an effect. To change this behaviour this cursor can be set to a dictionary where each button key corresponds to a cursor value.
-   `hover_cursor`: Set when an element is hovered, but not pressed.
-   `idle_cursor`: Default cursor when no element is hovered or pressed.

Example usage:

```py
mili.InteractionCursor.setup(
    hover_cursor=pygame.SYSTEM_CURSOR_IBEAM,
    press_cursor={
        pygame.BUTTON_LEFT: pygame.SYSTEM_CURSOR_HAND,
        pygame.BUTTON_RIGHT: pygame.SYSTEM_CURSOR_CROSSHAIR,
    }
)

# UI loop
for i in range(30):
    if interaction:=self.mili.element(rect, style):
        self.mili.rect({"color": (50,) * 3})
        self.mili.text(f"button {i}")
        self.mili.rect({"color": (80,) * 3, "outline": 1})
        mili.InteractionCursor.update(interaction, disabled=i%2==0)

mili.InteractionCursor.apply()
```

## `CustomWindowBorders`

An object utility that implements window resizing and dragging for a borderless window. Every non-private attribute can be changed at any moment.

After constructing the object, the `update()` method must be called every frame. Callbacks, flags, and attributes are modified in this method, meaning any logic relying on them should be added after. It is advised to call the `update` method before drawing the UI, to stop interactions while the window is resizing or being moved.

When the user hovers over the allowed sides or corners or titlebar, it will be able to resize the window or move it. Optionally the cursor will be changed. The `update` method will return a `bool` indicating if the cursor has been changed by the utility.

### Construction Parameters

-   `window`: The `pygame.Window` object that will be modified.
-   `border_size`, `corner_size`: The size in pixels of the resize areas for the sides and corners.
-   `titlebar_height`: The height of the custom titlebar that the user will be able to drag. If this value is set to 0, the window won't be able to be dragged.
-   `change_cursor`: Wether to actually change the cursor on hover.
-   `minimum_ratio`, `ratio_axis`: While the window's `minimum_size` will be considered by default, this setting forces the window ratio on the specified axis not to get too small to preserve UI inside the window. A value of `None` signals no restrictions.
-   `uniform_resize_key`: A key that when pressed will resize the window in both directions by the same amount. A value of `None` disables this functionality.
-   `allowed_directions`: A list of strings or the string `"all"` specifiying what directions allow resizing.
-   `on_(move|resize)`: Callback called while the window is being moved/resized.
-   `on_start_(move|resize)`: Callback called the first frame the window is moved/resized.
-   `on_end_(move|resize)`: Callback called the last frame the window is moved/resized.

### Utility Attributes

-   `dragging`: Wether the window is being dragged.
-   `resizing`: Wether the window is being resized.
-   `relative`: The current frame's relative value (for example the relative size compared to the last frame). The same attribute is used for moving and resizing.
-   `cumulative_relative`: The relative value from the moment the action started (for example the relative size compared to the moment the user started resizing). The same attribute is used for moving and resizing.

The `relative` and `cumulative_relative` flags are always up-to-date when the callbacks are called.
