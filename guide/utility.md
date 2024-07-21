[<- BACK](guide.md)

# MILI Utilities Guide

The `mili.utility` module contains functions and classes to simplify managing elements while still being independent. Everything from this module is also exported to the `mili` package.

## Functions

- `mili.percentage`: Calculates the percentage of a value and returns it. The same calculation is used internally for percentage strings.
- `mili.gray`: Return a tuple where the input value is repeated three times. `mili.gray(50)` -> `(50, 50, 50)`. Useful to make black to white colors for styles, hence the name.
- `mili.indent`: This function doesn't do anything, but you can use the python syntax to put lines on different indentations, for example:
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

## `Dragger`

An object that changes a position attribute when an element is dragged around. You can then pass the position to the element rect. This object will work if you call the `update` function passing the target element's interaction object (or element data object) to it, like below:

```py
interaction = mili.element((dragger.position, size), style)
dragger.update(interaction)
```

That function will return the value it was passed in, but you can use the `changed` attribute to know if the user actually dragged the element.

You can also lock the x axis or the x axis in the constructor and you can clamp the position in the update function or `clamp` function. This object is used internally by the scrollbar object.

## `Selectable`

An object that checks an element interaction and sets the `selected` flag appropriately, working like a checkbox. You can then modify the styles if the object is selected. Similarly to the dragger object, you need to call `update` passing the target element's interaction object (or element data object) to it.

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
            # ui structure

    def event(self, event):
        if event.type == pygame.X:... # handle events

    def on_quit(self):
        with open("save.txt", "w") as file:...
            # quit logic

if __name__ == "__main__":
    MyApp().run()
```

## `Scroll`

This is an object that keeps a scroll offset and automatically clamps it. To update the clamp area, you need to call the `update` method passing the container's element data as argument (interaction objects are not allowed). The grid data overflow is used internally to clap the scroll.

To see the scroll, you need to use the `get_offset` method, and passing the result to the children's offset style. You can update or set the scroll offset with the `scroll` and `set_scroll` methods (automatically clamped).

The object also provides a few advanced methods (`get_handle_size`, `get_rel_handle_pos_from_scroll`, `set_scroll_from_rel_handle_pos`) which are utilities for scrollbars. You can avoid using them using the `Scrollbar` utility.

Example scroll usage:

```py
scroll = mili.Scroll()

# game loop
with my_mili.begin((0, 0, 500, 500), get_data=True) as container:
    scroll.update(container)

    for i in range(50):
        my_mili.element((0, 0, 0, 30), {"fillx": True, "offset": scroll.get_offset()})
        my_mili.rect({"color": mili.gray(50)})
        my_mili.text(f"element {i}")

# event loop
if event.type == pygame.MOUSEWHEEL:
    scroll.scroll(event.x*2, event.y*2)
```

## `Scrollbar`

The scrollbar extends the scroll functionality supporting scrollbar utilities. It can work at one axis at a time and it needs an **independent** scroll object to rely on.

You can specify the axis and a few styling parameters in the constructor. A `Dragger` is used internally for the handle.

Note that this utility cannot create the scrollbar nor the handle elements, you need to create them, but you can use the `bar_rect`, ○
`bar_style`, `handle_rect`, `handle_style` attributes to simplify the process. They will only work if the handle is a children of the scrollbar.

To update the scroll you need to use the associated `Scroll` object and call `Scrollbar.scroll_moved` immediately after.

To update the scrollbar, you need to call `Scrollbar.update` passing the target container's element data (the same one you pass to `Scroll.update`, also required) and you then need to call `Scrollbar.update_handle` passing the handle's interaction or element data.

The `needed` property signals you if the container needs to be scrolled or if the children fit inside.

Scrollbar example usage:

```py
scroll = mili.Scroll() # scroll is independent
scrollbar = mili.Scrollbar(scroll, 12)

# game loop
with my_mili.begin((0, 0, 500, 500), get_data=True) as container:
    scroll.update(container)
    scrollbar.update(container)

    for i in range(50):
        my_mili.element((0, 0, 0, 30), {"fillx": ("96.5" if scrollbar.needed else "100"), "offset": scroll.get_offset()})
        my_mili.rect({"color": mili.gray(50)})
        my_mili.text(f"element {i}")

    if scrollbar.needed:
        with my_mili.begin(scrollbar.bar_rect, scrollbar.bar_style):
            my_mili.rect({"color": mili.gray(40)})

            handle_interaction = my_mili.element(scrollbar.handle_rect, scrollbar.handle_style)
            scrollbar.update_handle(handle_interaction)

# event loop
if event.type == pygame.MOUSEWHEEL:
    scroll.scroll(event.x*2, event.y*2)
    scrollbar.scroll_moved()
```
