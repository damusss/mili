# 1.0.4

### Fixes

-   Fixed `MILI.clear_memory()` so it actually clears all that needs to be cleared.
-   Added the missing component stubs in `mili.typing`.
-   Fixed a ZeroDivisionError happening with scrollbars

### Enhancements

-   Added a bunch of micro and medium optimizations to massively speed up the UI.
-   Reorganized the utility objects for code robustness (no user changes).
-   Added the utility styles in the guide.

### New API

-   Added the `mili.DropMenu` utility object.
-   Added the `mili.style.cond_value` function.
-   Added the `erase_rects` property to the `mili.ImageLayerCache` object.
-   Added the `mili.typing.ScrollbarStyleLike` object after the scrollbar changes.
-   Added the `mili.typing.SliderStyleLike` objectr after the slider changes.
-   Added the `blit_flags` style to the image and text components, aswell as an `ImageLayerCache.blit_flags` attribute.

### API-Breaking

-   Refreshed the scrollbar styling: added the `mili.Scrollbar.style` attribute and removed the `short_size`, `padding`, `border_dist`, `size_reduce` attributes and constructor arguments (accessible from the style). The `bar_update_id` and `handle_update_id` constructor arguments are added in the style argument.
-   Refreshed the slider styling: added the `mili.Slider.style` attribute and removed the `lock_x`, `lock_y`, `handle_size`, `strict_borders` attrbutes and constructor arguments (accessible from the style). The `area_update_id` and `handle_update_id` constructor arguments are added in the style argument.

# 1.0.3

### Fixes

-   Fixed the absolute rect of an element being empty when it was outside of the parent hitbox.

### New API

-   Added `mili.TextCache` similarly to `mili.ImageCache`.
-   Added the `cache` style of the text component, accepting a `mili.TextCache` object.
-   Added the `"auto"` option to the cache style of the text and image components.

### API-Breaking

-   Removed `mili.ImageCache.preallocate_caches`. Now the preallocated caches list will get bigger if more caches are required, so it's automatic.

# 1.0.2

### Fixes

-   Using urllib instead of requests, guarded an extra error case in `mili.icon`.
-   Fixed the style guide formatting.

### Enhancements

-   Added lazy access to `Interaction.data.grid` to save performance.
-   Partially enhanced the image layer cache system

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
