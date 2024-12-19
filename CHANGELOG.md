# 1.0.2

### Fixes

-   Using urllib instead of requests, guarded an extra error case in `mili.icon`.
-   Fixed the style guide formatting.

### Enhancements

-   Added lazy access to `Interaction.data.grid` to save performance.

### New API

-   Added `spacex` and `spacey` attributes to `Interaction.data.grid` in case they are different for grid containers.

# 1.0.1

Now requires `pygame-ce 2.5.2` or newer.

### Fixes

-   Fixed/Updated the guide.
-   Fixed the color animations erroring out of bounds.

### Enhancements

-   Optimized non-interacting elements by also adding the ability for the `blocking` element style to be `None` and an interaction cache.
-   Added the press button to `mili.style.conditional` and considered unhover pressing.
-   Rewrote `mili.CustomWindowBorders` to use the global mouse state, completely removing freaky behaviours.
-   Added the `version` command to the CLI.

### New API

-   Added the ability to use the global mouse state along with the `MILI.use_global_mouse` property and argument.
-   Added the `mili.icon` submodule with 5 new functions.
-   Added the update ID system adding new arguments to many utilities and the `update_id` element style.
-   Added the `ready` style of the image component.
-   Added the `mili.animation.StepsAnimation` and `mili.animation.StatusAnimation` classes.
-   Added the `mili.ImageLayerCache` optimization class and the `layer_cache` & `image_layer_cache` image and element styles respectively.
-   Added the `mili.GenericApp.post_draw` virtual method called after the UI has been drawn.

### API-breaking

-   Removed `mili.typing.RectLike` and `mili.typing.ColorLike`. Use `pygame.typing.RectLike` and `pygame.typing.ColorLike` instead.

# 1.0.0

Requires `pygame-ce 2.5.0` or newer.

### Fixes

-   Fixed/Updated the guide, refactored some code.
-   Fixed draw clipping issues.
-   Fixed the slider not properly setting the starting value.
-   Fixed the slider not centering the handle.
-   Fixed the codebase to be type safe.

### Enhancements

-   Added the `changelog` command to the cli.
-   Allowed `%` characters in percentage strings.
-   Allowed `fillx` and `filly` values for grid containers.
-   Allowed a list of floats for the `border_radius` style of the rect component.
-   You can now get the `ElementData` of the stack element.
-   The element's `blocking` style can be set to `None` to save performance.

### New API

-   Added the `MILI.canva_offset` property.
-   Added the `mili.get_font_cache` and `mili.clear_font_cache` functions.
-   Added the `pad` style to elements and components.
-   Added the `aspect_ratio` and `align` styles to the rect and circle component.
-   Added the `corners` style to the circle component.
-   Added the `BoundingAlignLike` typing alias.
-   Added the `dash_size` and `dash_offset` styles to the line component.
-   Added the `dash_size` and `dash_anchor` styles to the circle component.
-   Added the `dash_size` and `dash_offset` styles to the rect component.
-   Added the `mili.FILL` style helper.

### API-breaking

-   Removed `MILI.basic_element`.
-   Removed `MILI.set_canva` (redundant after `MILI.canva`)

    ### <small>`ElementData` refactor</small>

    -   Added the lazy property `Interaction.data` to retrieve the element data.
    -   Removed the `MILI.always_get_data` attribute.
    -   Removed the `get_data` parameter from every `MILI` function
    -   Every `MILI` function can only return `Interaction`.
    -   Utility functions that allowed `ElementData` only allow `Interaction`.
    -   Removed the `Interaction.id` and `ElementData.interaction` attributes.
