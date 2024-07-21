[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

# MILI Interaction Data Guide

The `mili.data` submodule contains 4 classes that represent data.

# `Interaction`

The interaction object is returned by all elements by default. It contains all information you can need to understand how the user is interacting with the element:

- `Interaction.id`: The ID of the element.
- `Interaction.hovered`: The user pointer is over this element which is also the highest element.
- `Interaction.absolute_hover`: The user pointer is over this element but other elements might be covering it.
- `Interaction.just_hovered`: The hovered status becomes True this frame meaning the user has started hovering
- `Interaction.just_unhovered`: The hovered status becomes False this frame meaning the user pointer left the element
- `Interaction.press_button`: The button the user is clicking on this element. If the pointer leaves the element while being held, this will keep being set until the pointer releases. -1 means no button is pressed.
- `Interaction.just_pressed_button`: Same as `press_button` but is only set the first frame it happens.
- `Interaction.just_released_button`: Same as `press_button` but is only set the last frame it happens. Corresponds to the "click" event.

There are also three shortcuts for the left mouse button (most common): `left_pressed`, `left_just_pressed`, `left_just_released`

# `ElementData`

The element data object holds a lot more information than the interaction object, but is a bit slower to compute. It keeps the relative rect, the absolute rect, the z index, the ID, the style, the components, the parent ID and the children ID. Changing any field will not effect the element.

The `grid` attributes contains information about its parental behaviour such as the overflow, the padding, and the spacing (needed for scrolling) which are contained in the `ElementGridData` object, only accessible using the `mili.data` module (the others are exported to the `mili` package)

This object is required by some utilities. The attributes might not be super accurate and might have some delay.

# `ImageCache`

This object is incredibly useful to massively speed up the image component. Since MILI is immediate mode, after the surface is modified using the styles it cannot be cached. This object, passed in the cache style, provides a permanent location the result can be stored in. Using  `get_output`, it's also the only way to retrieve the processed image (might be None in the first iterations).

You can also simplify the cache creation process:
- `ImageCache.preallocate_caches(amount)`: Creates and stores a set amount of image caches
- `ImageCache.get_next_cache()`: Retrieve a free cache and increase the internal index

Example usage:
```py
my_special_cache = mili.ImageCache()
mili.ImageCache.preallocate_caches(30)

def ui():
    my_mili.image_element(special_surface, {"cache": my_special_cache}, rect)

    for i in range(30):
        my_mili.image_element(surface, {"cache": mili.ImageCache.get_next_cache()}, rect)
```
