[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

NOTE: _some_ of the contents of this section are slightly outdated. it is being updated as we speak.

# MILI Utilities Guide

The `mili.utility` module contains functions and classes to simplify managing elements while still being independent. Everything from this module is also exported to the `mili` package. Utilities that have a style argument in their constructor have the style explained in the style guide.

Index:

-   [Functions](#functions)
-   [GIF](#gif)
-   [Dragger](#dragger)
-   [Selectable](#selectable)
-   [GenericApp](#genericapp)
-   [UIApp](#uiapp)
-   [Scroll](#scroll)
-   [Scrollbar](#scrollbar)
-   [Slider](#slider)
-   [DropMenu](#dropmenu)
-   [EntryLine](#entryline)
-   [InteractionSound](#interactionsound)
-   [InteractionCursor](#interactioncursor)
-   [CustomWindowBorders](#customwindowborders)
-   [CustomWindowBehavior](#customwindowbehavior)
-   [AdaptiveUIScaler](#adaptiveuiscaler)

## Functions

-   `mili.percentage`: Calculates the percentage of a value and returns it. The same calculation is used internally for percentage strings.
-   `mili.fit_image`: Return a surface that is constrained inside the provided rectangle plus extra applied styles which are the same that you would provide to an image component and work the same.
-   `mili.round_image_borders`: Return a new Surface that has the corners cut by a radius (similar to the border radius argument of pygame.draw.rect). The border radius can be a single value or a sequence of four values representing the Surface corners. Additionally, the value can be a number or a smart/percentage string.
-   `mili.round_image`: Return a new Surface that is cut by a circle, making it round. The antialias argument controls the smoothness of the mask's edge. If the surface's width and height don't make a square, the `allow_ellipse` parameter controls whether the mask should be a centered circle or a stretched ellipse.
-   `mili.dict_push`: Meant to be used with a context manager, overrides the provided dictionary with the override data and when the context is closed or when the `revert()` method on the return value is called the dict is restored to the previous state. Useful to change values and revert them without knowing what they were before, also saving lines of code. Very useful to temporarily change the styles of the utilities, similar to `MILI.push_styles`.

Keep in mind that to make gray colors (generally to repeat a value in a tuple) you can use the multiply operator. `(50,) * 3` -> `(50, 50, 50)`

## `GIF`

The GIF class is a very compact utility for animated images. It is made from a list of frames where each frame is a tuple with the Surface and the delay (the duration before the next frame in milliseconds). To create a GIF from a file using `pygame.image.load_animation` pass None to the frames and provide a file like object to the file argument.

All you need to do is call `get_frame()` and pass the returned Surface to an image component. Being compact, the frames will advance automatically with no additional methods.

The `playing` attribute (can also be changed with `play()` and `pause()`) controls if the animation is playing. When it is false, the current frame will be returned until the gif is resumed. You should still call `get_frame` even when the GIF is paused, that way when it is resumed it will pick up from the right moment in the animation.

You can access the frames with the `frames` property but you can only change them with `set_frames()` since additional operations are required. The `sync()` method is needed to sync the current gif playback to the playback of another gif. If the gifs have the same frames, they will play simoultanely and remove any lag. Use the `playback` property to get or manually control the playback time of the gif. Finally, the `duration` property will return how much time it takes for the gif to complete one cycle.

## `Dragger`

An object that changes the position attribute when an element is dragged around. You can use the position in the element rect to see the position. It's advised to set the ignore grid style to True. You can use the shortcut `Dragger.style` attribute for it.

Use the `Dragger.clamp` method to clamp the position (you can provide new clamp values or use the previously stored ones). You can make the Dragger work by providing an update ID to its constructor and using that ID as the element's update ID. If you don't do that, you need to manually call the `Dragger.update` method.

```py
dragger = mili.Dragger(update_id="dragger1")
interaction = mili.element((dragger.position, size), {..., "update_id": "dragger1"}) # or do dragger.update(interaction)
```

Since the update function returns the element as output, the flag stating if the position changed or not is stored in `Dragger.changed`.
You can also lock the x or y axis to restrict the position even more.

## `Selectable`

An object that checks an element interaction and sets the `selected` flag appropriately, working like a checkbox. You can then modify the styles if the object is selected. Similarly to the Dragger object, you can setup an update ID that you later use on your element.

You can also provide a list of `Selectable` instances to the update method (you can't use the update ID for this feature), and they will be organized in a way where only one object in the list is allowed to be selected at any time. If the `can_deselect_group` flag is True, the user will be able to deselect all selectables.

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

## `UIApp`

The UIApp utility is a progression from the `GenericApp`. While the generic one is only responsible for creating a MILI context and a game loop, the UIApp is intended to be the quickest way of creating all the objects and setup needed to start working on an application. Unlike the other, it takes over some things by, for example, providing a fully functional title bar and window buttons. For that reason, it is mainly meant to be used with a frameless window. Below are the list of actions and objects that the utility makes sure to setup (keep reading this guide to understand all the objects mentioned):

-   call `pygame.init`
-   create a clock and a MILI context like `GenericApp`
-   create and setup a `CustomWindowBorders` and a `CustomWindowBehavior` objects in the respective `win_borders` and `win_behavior` attributes. The `pygame.display.get_desktop_sizes()[0]` monitor sizes are used.
-   create and setup an `AdaptiveUIScaler` object in the `adaptive_scaler` attribute. The window size at init time is used as the relative size. The `adaptive_scaler.scale` method is also added as an UIApp `scale` attribute for quicker access.
-   The `InteractionCursor` utility is setup with the `update_id` parameter set to `"cursor"`. Use this update ID to automatically change the cursor for interactive elements.
-   Set `'s'` as a number modifier key for the `AdaptiveUIScaler.scale` modifier (to be used as `"s20"` for example)
-   If the `"use_appdata_folder"` style is set to True, setup the icon module to use the `./appdata` folder to store icons.

For the buttons to work, icons will be used and it is best to allow it to cache them. Since a lot of things can be customized, this utility also uses a style dictionary. Remember that while most of the entries in the dictionary can be changed safely, no entry shall ever be removed or `KeyError`s will randomly occur.
When running, all the child objects are updated (the interaction cursor is applied. `mili.animation.update_all` is also called here) and the UI is run for the title bar to be properly displayed. Some ui methods can be overridden to add elements on the title bar while it is being built.
The methods you can override to customize your UI are similar to the ones of `GenericApp`.

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

To update the scroll you need to use the associated `Scroll` object and calling `Scrollbar.scroll_moved` is NOT necessary (Scroll does it automatically).

To update the scrollbar either use the **update ID system** or you need to call `Scrollbar.update` passing the target container's interaction or element data (the same one you pass to `Scroll.update`, also required) and you then need to call `Scrollbar.update_handle` passing the handle's interaction. If using the update ID system, `Scrollbar.update` will be associated to the same ID used in the Scroll object.

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

## `EntryLine`

An object that implements a rich entryline (no multiline support) supporting every key and mouse shortcut aswell as selecting, copying, cutting and pasting. By default an history (accessible with ctrl-z and ctrl-y) is enabled.

The style allows for a very high customization (every style field can be changed at any moment without underfined behaviour but removing a style key will result in a KeyError). Check the style guide to use the styles properly. It is adviced to call `pygame.key.set_repeat()` in your app.

For the entryline to work two main methods must be called in your loop:

-   `event(pygame.Event)`: Must be called for every event in your event loop
-   `ui(container)`: Must be called in the UI loop. It will update the entryline and render the text. The container interaction parameter must be a parent. If the bg and outline style rect shortcuts are specified they will be added to that element. By default the inner text element will fill the container on the y axis and will not let the text grow on that axis, but this behaviour can be overridden with the `"text_filly"` and `"text_style"` style fields.

You can get the text with the `text` or `text_strip` properties. If the target is a number, get an (always) valid number within allowed range using the `text_as_number` property.

Most actions accessible with key and mouse shortcuts are accessible with code aswell:

-   `insert(string)`: Add a string at cursor position
-   `move_cursor(amount)`: Move and clamp the cursor (check the cursor with the `cursor` attribute)
-   `delete(amount)`: Delete backwards (with a negative amount) or forward (with a positive amount) from the cursor position
-   `select(start, end)`: Manually set the selection endpoints (right value will also be the cursor)
-   `cancel_selection()`: Keep the cursor position but cancel the selection
-   `delete_selection()`: Erase the selection
-   `get_selection()`: Get the portion of the text selected
-   `undo()`: Restore the previous action
-   `redo()`: Restore the last action that was undone
-   `focus()`/`unfocus()`: Control the entryline focus (access the state with the `focused` attribute)

If you use a `Scroll` object to scroll the text left and right it must be set as the scroll field in the style.

Validators are optional custom callable. The input validator should expect a single character and return it (or modified) if it's valid or None if it should be discarded. The text validator should expect a string and return a tuple with the validated string (or the same string) and a boolean indicating if the string was valid or not.

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

-   `setup()`: Change the default cursors with custom values. The default update ID is `"cursor"`
-   `update()`: Should be called for every element that should change cursor based on interaction or you can use the **update ID system**. The disabled flag will select the disabled cursor appropriately. For special elements each cursor can be overridden using keyword arguments that match the class variable names.
-   `apply()`: Must be called at the end of the UI loop, after all the update calls have been made. This method is responsible for changing the cursor. It will return the cursor that has been applied or `None` if the cursor was left unchanged.
-   `set_status(status)/set_cursor(cursor)`: Use this to notify the class that you something that is not a UI element should trigger a different cursor.

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
    if interaction:=self.mili.element(rect):
        self.mili.rect({"color": (50,) * 3})
        self.mili.text(f"button {i}")
        self.mili.rect({"color": (80,) * 3, "outline": 1})
        mili.InteractionCursor.update(interaction, disabled=i%2==0) # use {"update_id": "cursor"} if you don't need special conditions!

mili.InteractionCursor.apply()
```

## `CustomWindowBorders`

An object utility that implements window resizing and dragging for a borderless window. Every non-private attribute can be changed at any moment.

After constructing the object, the `update()` method must be called every frame. Callbacks, flags, and attributes are modified in this method, meaning any logic relying on them should be added after. It is advised to call the `update` method before drawing the UI, to stop interactions while the window is resizing or being moved. The best way to avoid interactions during dragging/resizing is like follows:

```py
def can_interact(self):
    return self.window.focused and self.borders.cumulative_relative.length() == 0

# somewhere in the UI loop
if interaction.left_clicked and self.can_interact():
    ...
```

When the user hovers over the allowed sides or corners or titlebar, it will be able to resize the window or move it. Optionally the cursor will be changed. The `update` method will return a `bool` indicating if the cursor has been changed by the utility. If the cursor is modified, `InteractionCursor.apply` will not change the cursor (window resizing/dragging takes priority) so you don't need to block it manually.

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

-   `active`: Wether the window can be moved or resized.
-   `active_drag`, `active_resize`: Wether dragging or resizing is enabled.
-   `dragging`: Wether the window is being dragged.
-   `resizing`: Wether the window is being resized.
-   `relative`: The current frame's relative value (for example the relative size compared to the last frame). The same attribute is used for moving and resizing.
-   `cumulative_relative`: The relative value from the moment the action started (for example the relative size compared to the moment the user started resizing). The same attribute is used for moving and resizing.

The `relative` and `cumulative_relative` flags are always up-to-date when the callbacks are called.

Finally, you can use the `mouse_changed()` method if you want to use `pygame.mouse.set_pos()` while the window is being dragged/resized without it glitching.

## `CustomWindowBehavior`

Other than losing the ability to be dragged or resized, borderless windows also loose convenience behaviors like maximizing, restoring, fullscreen, double clicking to maximize or snapping to the sides. This object utility is an extension to `CustomWindowBorders` that implements those exact features.

This object solely works on state changes, meaning you don't need to call any update method. You can customize it in the costrcutor (or changing the associated non-private attributes/properties) like follows:

-   `window`: The `pygame.Window` object to customize.
-   `borders`: The independent `CustomWindowBorders` instance responsible for dragging and resizing. Note that some callbacks will be overridden by this utility.
-   `display_size`: The size of the monitor the window is in, size that will be used for maximizing and snapping.
-   `taskbar_size`: The height (or width, depending on orientation) of the taskbar that will be excluded from calculations.
-   `taskbar_position`: The position of the taskbar, either `left`, `right`, `top` or `bottom` (most common).
-   `double_click_cooldown`: The cooldown that allows the window to be maximized when double clicking the top portion. None means this feature is disabled.
-   `snap_border_size`: The size of the areas that the mouse must collide with to trigger snapping in the left, right, top, bottom sides.
-   `snap_corner_size`: The size of the areas that the mouse must collide with to trigger snapping in the topleft, topright, bottomleft, bottomright corners.
-   `allow_snap`: Wether the window can be snapped to the sides of the monitors.
-   `before_maximized_data`: A tuple of (size, position) before maximing. This is only useful if your app remembers the last window state and you want to restore it correctly. You can access this with the attribute if you want to save it to a file.

The following additional properties are available (can also be set):

-   `maximized`: Wether the window is maximized.
-   `minimized`: Wether the window is minimized.
-   `snapped`: Return the name of the snap position if it is snapped, otherwise None. If the window only has its height snapped, `height` is returned.
-   `fullscreen`: Wether the window is in fullscreen mode.

You can manually control the window state with the following methods:

-   `maximize()`, `unmaximize()`, `toggle_maximize()`: Change the maximized status.
-   `minimize()`, `unminimize()`, `toggle_minimize()`: Change the minimized status.
-   `fullscreen_on()`, `fullscreen_off()`: `toggle_fullscreen()`: Change the fullscreen status. The borders will be deactivated while the fullscreen is on.
-   `snap(position)`: Snap the window to an allowed position. Snapping to the top or bottom is the same as maximizing. `heigt` is allowed.
-   `unsnap()`: Restore the window from a snapped position.
-   `center()`: Center the window inside the display.

## `AdaptiveUIScaler`

This object utility makes the UI sizes of your app dynamic when the window resizes. It works by using some reference sizes (the preferred sizes of your app) and calculate a multiplier based on how smaller or bigger the current window size is compared to the preferred sizes.

For it to work you need to call `update()` every frame (preferrebly before your UI loop) and then call `scale(size)` for every size that you wish to be adaptive. `scalef()` is a copy of `scale` that doesn't convert the result to an integer (unlike `scale`).

If your app has a preferred width of 1920 pixels, and you want a font size of 24, but the current window size is 960 (half) when you use `scale(24)` it will return 12 (half) with default settings.
You can customize the scaler in the constructor as follows:

-   `window`: A pygame.Window or an object with a `size` attribute to use as the up-to-date container.
-   `relative_size`: The preffered application sizes in pixels.
-   `scale_clamp`: A tuple with the minimum and maximum values that the multiplier can have, to avoid making the UI too small or too big. If min or max are None they won't be limited.
-   `width_weight`, `height_weight`: Control how much the container dimentions weight on the multiplier. It depends on the dominant dimention of your application.
-   `min_value`: The minimum value that a scaled size can have. This defaults to `1`, and it is generally suggested not to set it to 0 to avoid errors if the window has zero dimentions. This value can be overridden for each `scale` call.
-   `int_func`: A function that converts a floating point number to an integer. Defaults to the builtin `int` type. Good alternative candidates are: `round`, `math.floor`, `math.ceil` depending on your preference.
-   `extra_scale`: A value that will be used as an extra scaling factor if you need one.
