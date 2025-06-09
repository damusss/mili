[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

Index:
-   [MILI](#mili-class-guide)
-   [Element Structure](#element-structure)
-   [Update ID System](#update-id-system)
-   [Components](#components)
-   [Markdown](#markdown)
-   [Advanced Usage](#advanced-usage)

# MILI Class Guide

The MILI class is the UI manager.

Each instance is independent and will manage its own elements.
Each instance has an internal context instance.

A MILI instance must be associated with a surface to draw on. You can retrieve it or change it with the `MILI.canva: Surface` property. If the canva isn't the screen and is not rendered at the topleft, you can seet the `MILI.canva_offset` property to the render position relative to the window so that the mouse clicks are registered correctly.

MILI has 6 methods related to styling. Check the start of [style guide]() to learn about them.

The following are two essential functions in the game loop:

-   `MILI.start(style)`: Must be called at the start of the game loop. Acts like the parent of all elements, so it supports styling and components. If `is_global` is True the `ImageCache`/`TextCache` preallocated index will be reset. You only want one MILI instance to start as global.
-   `MILI.update_draw`: Update the interaction and draws all elements. Elements are sorted using their z index which automatically increases when new elements are created.

Boilerplate example code for MILI (it's a better practice to use classes like `mili.GenericApp`):

```py
import mili
import pygame

pygame.init()
# create window
my_mili = mili.MILI(window_surface)

def ui():
    # your UI structure
    ...

while True:
    my_mili.start()

    # event loop
    # clear window

    ui()
    my_mili.update_draw()

    # update window
```

## Element Structure

In MILI there are no prefabs such as buttons or labels. The skeleton is composed of elements. All elements can be interacted and they can have children, but they do not have intrinsic graphics - they are just hitboxes. You have the following methods to create elements:

-   `MILI.element(rect, style)`: Create an element with no children
-   `MILI.begin(rect, style)`: Create an element and set it as the current parent
-   `MILI.end()`: Signal that the current parent has ended

Elements created after the begin call will be assigned to that parent. The end call will set the parent to the previous one.
You can avoid calling end using the context manager on the returned `Interaction` object. You can use the context manager for elements aswell without errors.

Example of an element structure:

```py
with my_mili.begin(rect, style) as main_container:
    my_mili.element(rect, style) # parent is main_container
    my_mili.element(rect, style) # parent is main_container

    with my_mili.begin(rect, style) as second_container:
        for i in range(3):
            my_mili.element(rect, style) # parent is second_container

        with my_mili.begin(rect, style) as inner_container:
            my_mili.element(rect, style) # parent is inner_container
            my_mili.element(rect, style) # parent is inner_container

        my_mili.element(rect, style) # parent is second_container

    my_mili.element(rect, style) # parent is main_container
    my_mili.element(rect, style) # parent is main_container
```

Parent elements organize their children by default, behaviour which is higly customizable using styles.

## Update ID System

Since, as you saw, the element structure is not remembered by the UI manager and is immediate mode, most utilities have an update method that processes an element every frame to work. To avoid calling all this methods, every object of this kind allows you to provide an update ID to their constructor. Then, in your UI loop, when you create the elements, if you add the `update_id` style to an element MILI is going to automatically and immediately call the update methods that were registered with the same ID.

Note that you can use a list of strings to associate multiple update IDs with the same element.

For example:

```py
# normal approach:
dragger = mili.Dragger()
sound_player = mili.InteractionSound(sound)

# UI loop
el = my_mili.element(rect, style)
dragger.update(el)
sound_player.play(el)

# update ID system approach:
dragger = mili.Dragger(update_id="element1")
sound_player = mili.InteractionSound(sound, update_id="element1")

# UI loop
my_mili.element(rect, {"update_id": "element1"})
# automatically call dragger.update and sound_player.play
```

Use the `mili.register_update_id` function to associate your own function (that must take an `Interaction` object as the only parameter) to an `update_id`. If the update_id passed to it is `None` the call will be ignored.

## Components

Since elements have no graphics, to give the user visual feedback you need to use components. There are six built in components, each with its method:

-   `MILI.rect(style)`
-   `MILI.circle(style)`
-   `MILI.line([start, end], style)`
-   `MILI.polygon(points, style)`
-   `MILI.text(text, style)`
-   `MILI.image(surface, style)`

To have both a filled version and the outline version of a shape you must concatenate two calls, specifying the `"outline"` (size) style for the second.

Components are attached to the most recent element (unless overridden by a style). They are contained within the hitbox of the element (customizable with styles).
You should change the style of components based on interaction for visual feeback.

There are also three built-in shortcut components. They actually call existing components but make them easier for specific usecases. They are:
-   `MILI.transparent_rect(style)` (uses an image component)
-   `MILI.vline(style)`/`MILI.hline(style)` (inserts the start and ending points automatically for the most common lines)

Example usage of components:

```py
my_mili.start(mili.CENTER)
my_mili.rect({"color": (30,) * 3}) # component attached to the start element

with my_mili.begin(None, {"fillx": "50", "filly": "80"}) as container:
    my_mili.rect({"color": (50,) * 3}) # component attached to container
    my_mili.rect({"color": (100,) * 3, "outline": 1, "draw_above": True}) # component attached to container

    for i in range(5):
        if interaction:=my_mili.element((0, 0, 0, 50), {"fillx": True}): # if used for indentation, always True
            my_mili.rect({"color": (80 if interaction.hovered else 60,) * 3}) # component attached to element, conditionally changes color
            my_mili.text(f"Button {i}", {"size": 30}) # component attached to element
            my_mili.rect({"color": (120,) * 3, "outline": 1}) # component attached to element

            if interaction.left_just_released:...
                # action on button press
```

To reduce boilerplate code, for every component there is a shortcut that creates an element with a single component of said type, for example `MILI.text_element` will create an element with a text component.

For text specifically there are also the utilities `MILI.text_size` and `MILI.text_font` that compute and return the size and font a text element would use if it was rendered.

`MILI.image_layer_renderer` is technically also a component, check the interaction data guide for it.

## Markdown

MILI supports rendering markdown with a built in renderer that converts markdown text to MILI native calls. To use it you firstly need to store a `mili.MarkDown` object permanently, to which you give the markdown source and the style (more info in the style guide). Then, in your UI loop just call `MILI.markdown(markdown)`. The markdown will be rendered inside the parent at the time of calling MILI.markdown(). If the style allows it the cursor is changed using the `InteractionCursor` utility. Call `InteractionCursor.apply` to apply the cursor.

You can change the style fields but not remove any field. To apply some style changes you might have to call `mili.MarkDown.rebuild()`.

Other than markdown rich text (check what is supported in the style guide), supported elements are:

-   `# titles` (up to 6 #s)
-   `\n`/`<br>` (separators)
-   `---`/`***`/`___`/`<hr>` (breaklines)
-   \`\`\` multiline code blocks \`\`\`
-   `![alt text](image url/path)` (images)
-   `[![image alt text](image url/path)](click url)` (link images)
-   `- bullet lists` (can nest elements)
-   `> quotes` (can nest elements)
-   Tables (cell content can be: a paragraph, an image, a link image):

```
| title 1 | title 2 |
| :------ | ------: |
| cell 1 | cell 2  |
| cell 3 | cell 4  |
```

Tabs result in indentation.

**NOTE**: Processing markdown has limited efficiency so keep it in mind when rendering giant files.

## Advanced Usage

### Advanced Properties

You can manage the font cache with the provided functions. A font instance will be automatically created for each combination of path/name and size:

-   `mili.get_font_cache()`
-   `mili.clear_font_cache()`

With the `mili.set_number_modifier` you can register callables as number modifier keys to be used in some of the styles, as explained in the style guide. Use the `mili.smart_number` function to calculate the value of a smart string based on the registered modifiers.

MILI instances have a couple advanced properties and methods:

-   `MILI.last_interaction`: The Interaction object returned by the last element/parent
-   `MILI.current_parent_interaction`: The Interaction object of the currently active parent
-   `MILI.id`: The element ID that will be used by the next element. Can be assigned to, having the same behaviour as `MILI.id_checkpoint`
-   `MILI.stack_id`: The ID of the main parent element
-   `MILI.current_parent_id`: The ID of the current parent
-   `MILI.all_elements_ids`: A list with the IDs of all created elements in memory
-   `MILI.data_from_id()`: Get an `ElementData` object from an element ID
-   `MILI.clear_memory(keep_ids=None)`: Clear all the elments in memory. Useful when changing scenes or massively updating them to avoid specific glitches. A list of IDs can be passed wich represent elements that should not be erased from memory.
-   `MILI.id_checkpoint(id)`: Manually set the internal ID. Useful to avoid new elements to inherit the memory of the previous element and be visually unpleasent for a few frames. If the current ID is higher a `MILIStatusError` is raised.
-   `MILI.id_jump(amount)`: Increase the last checkpoint by the amount and sets it as a new checkpoint (similar to `id_checkpoint`). If the current ID is higher than the new checkpoint a `MILIStatusError` is raised.

-   `MILI.add_element_style(style, element_id)`:

    This method allows you to add some styles to an element after it has been created, for example, if conditions on the interactions are met. Due to design constraints, the following style won't have an effect when using this function:

    -   `parent_id`
    -   `ignore_grid`
    -   `fillx`
    -   `filly`

    Changing the z layer will have an effect, but the children won't get updated, so they might be outdated and flicker unless they get updated too.

### Packing Components

You can pack components in dictionaries to store them and add them later without repeating code:

-   `mili.pack_component(name, data, style)`: Return a packed dictionary
-   `MILI.packed_component(comp1, comp2, ...)`: Add a component from a packed dictionary

### Custom Components

If the builtin components are not enough, You can create your custom components.

To do so, you need to create an object that supports the `mili.typing.ComponentProtocol`. The `added` function will be called when your component is added to an element while the `draw` function will be called to draw your component.
You can then use the following functions:

-   `mili.register_custom_component(name, component_object)`: Register your component so it can be added to elements
-   `MILI.custom_component(name, data, style)`: Add your custom component to an element (builtins are allowed in this call)

Interacting with the context object might be challenging as it's undocumented and not annotated.

If you are extending mili, consider subclassing the MILI class adding a shortcut for your component.
