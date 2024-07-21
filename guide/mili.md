[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

# MILI Class Guide

The MILI class is the UI manager.

Each instance is independent and will manage its own elements.
Each instance has an internal context instance.

A MILI instance must be associated with a surface to draw on. You can retrieve it or change it:

- `MILI.set_canva(Surface)`
- `MILI.canva: Surface` (property)

MILI has a few methods related to styling:

- `MILI.default_style`/`MILI.default_styles`: Set the default styles for the style resolution
- `MILI.reset_style`: Reset the default styles

The following are two essential functions in the game loop:

- `MILI.start(style)`: Must be called at the start of the game loop. Acts like the parent of all elements, so it supports styling and components.
- `MILI.update_draw`: Update the interaction and draws all elements. Elements are sorted using their z index which automatically increases when new elements are created.

Boilerplate example code for MILI (it's better to use classes):

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

- `MILI.element(rect, style, get_data=True/False)`: Create an element with no children
- `MILI.begin(rect, style, get_data=True/False)`: Create an element and set it as the current parent
- `MILI.end()`: Signal that the current parent has ended

Elements created after the begin call will be assigned to that parent. The end call will set the parent to the previous one.
You can avoid calling end using the context manager on the return value of begin.

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

Elements and parents return an `Interaction` object by default. If the `get_data` argument is set to True, an `ElementData` object is returned instead (all fields from the interaction are also available in this object).

## Components

Since elements have no graphics, to give the user visual feedback you need to use components. There are six built in components, each with its method:

- `MILI.rect(style)`
- `MILI.circle(style)`
- `MILI.line([start, end], style)`
- `MILI.polygon(points, style)`
- `MILI.text(text, style)`
- `MILI.image(surface, style)`

Components are attached to the most recent element. They are contained within the hitbox of the element (customizable with styles).
You should change the style of components based on interaction for visual feeback.

Example usage of components:

```py
my_mili.start(mili.CENTER)
my_mili.rect({"color": mili.gray(30)}) # component attached to the start element

with my_mili.begin(None, {"fillx": "50", "filly": "80"}) as container:
    my_mili.rect({"color": mili.gray(50)}) # component attached to container
    my_mili.rect({"color": mili.gray(100), "outline": 1, "draw_above": True}) # component attached to container

    for i in range(5):
        if interaction:=my_mili.element((0, 0, 0, 50), {"fillx": True}): # if used for indentation, always True
            my_mili.rect({"color": mili.gray(80 if interaction.hovered else 60)}) # component attached to element, conditionally changes color
            my_mili.text(f"Button {i}", {"size": 30}) # component attached to element
            my_mili.rect({"color": mili.gray(120), "outline": 1}) # component attached to element

            if interaction.left_just_released:...
                # action on button press

    # NOTE: calling my_mili.component here will attach it to the last button, not container!
```

To reduce boilerplate code, for every component there is a shortcut that creates an element with a single component of said type, for example `MILI.text_element` will create an element with a text component.

`MILI.basic_element` does the same but adds a background and an outline automatically.

## Advanced Usage

### Advanced Properties

MILI instances have a couple advanced properties:

- `MILI.stack_id`: The ID of the main parent element
- `MILI.current_parent_id`: The ID of the current parent
- `MILI.all_elements_ids`: A list with the IDs of all created elements in memory
- `MILI.data_from_id()`: Get an `ElementData` object from an element ID

### Packing Components

You can pack components in dictionary to store them and add them later without repeating code:

- `mili.pack_component(name, data, style)`: Return a packed dictionary
- `MILI.packed_component(comp1, comp2, ...)`: Add a component from a packed dictionary

### Custom Components

If the builtin components are not enough, You can create your custom components.

To do so, you need to create an object that supports the `mili.typing.ComponentProtocol`. The `added` function will be called when your component is added to an element while the `draw` function will be called to draw your component.
You can then use the following functions:

- `mili.register_custom_component(name, component_object)`: Register your component so it can be added to elements
- `MILI.custom_component(name, data, style)`: Add your custom component to an element (builtins are allowed in this call)

Interacting with the context object might be challenging as it's undocumented and not annotated.

If you are extending MILI, consider subclassing the MILI class adding a shortcut for your component.
