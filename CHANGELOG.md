# 1.0.6

### Deprecation

-   Element style `grid` has been deprecated. Use the new layout style and set it to grid. The old will work for a few versions.

### New API

-   Added the `mili.CustomWindowBehavior` window utility.
-   Added the `mili.UIApp` window utility.
-   Added the `mili.SPACELESS` style shortcut.
-   Added the `MILI.id_jump()` method.
-   Added the following attributes to `mili.CustomWindowBorders`: `active`, `active_drag`, `active_resize`.
-   Added the `MILI.push_styles`, `MILI.pop_styles` and `MILI.reset_styles` methods.
-   Added the `MILI.cache_should_create_children()` method.
-   Added support for iconify icons in `mili.icon`.
-   Added the `mili.ParentCache` object.
-   Added the `layout` element style.
-   Added the `first_center` and `last_center` options for the grid_align element style.
-   Added the `register_prefab`, `prefab` and `image_layer_renderer` methods to the `MILI` class.
-   Added the `pad`, `padx`, `pady` styles to the `line` and `polygon` components.
-   Added the `transparent_rect`, `vline`, `hline` component shortcuts along with their `*_element` version.
-   Added the `characters_limit` and `text_anchor` styles to `mili.Entryline`.

### Enhancements

-   `MILI.id_checkpoint` can now raise `MILIStatusError` (check the guide).

### Fixes

-   Fixed the handling of update ids of scrollbars. There was never a bar update, and now `Scrollbar.update` uses the same update id of the scroll object. The scrollbar style has been updated to fix it aswell.
-   Fixed the handling of the `<br>` and `<hr>` markdown tags.

### API-Breaking

-   Renamed `MILI.reset_style` to `MILI.reset_default_styles`.

### Behaviour-Changing:

-   Removed the `X_style` styles of markdown. Use context styles instead.
-   Removed the `X_draw_func` element styles. Use custom components instead.
-   Removed the `image_layer_cache` element style. Use the available component instead.
-   When a parent's end() is called components will be added to it.

# 1.0.5

### New API

-   Added the `mili.MarkDown` object, the `MILI.markdown` method and markdown rendering (added it to the guide).
-   Added the `mili.EntryLine` rich utility object and a section on the utility and style guide for it.
-   Added rich text support: added the `rich`, `rich_y_align`, `rich_linespace`, `rich_actions`, `rich_link_color`, `rich_markdown`, `rich_markdown_style` text styles.
-   Added the `mili.CustomWindowBorders.constraint_rect` attribute and constructor parameter.
-   Added the `mili.Scroll.wheel_event` method.
-   Added the `size_clamp` element style, to constrain the element size after fillx|y and resizex|y operations.
-   Added the `MarkDownStyleLike` and `EntryLineStyleLike` objects in `mili.typing`.
-   Added the `ready_rect` rect style.
-   Added the `svg` parameter to `mili.icon.get` and `mili.icon.preload` to properly load svg icons.
-   Added the `mili.icon.get_svg` shortcut to call `mili.icon.get` with `svg=True`.
-   Added the cache parameter when getting google icons to override the setting.
-   Added the `cache_rect_size` style to the elements.
-   Added the `keep_ids` argument to `MILI.clear_memory()`
-   Added the `MILI.id` property.
-   Added the `MILI.last_interaction` and `mili.current_parent_interaction` attributes.
-   Added the `Interaction.parent` attribute.
-   Added the `mili.style.color` and `mili.style.outline` functions
-   Added an equivalent of `mili.Interaction.left_pressed` etc for right and middle mouse buttons.
-   Added the `mili.style.DefaultStyle` context manager object.
-   Added the `padded` argument to the `MILI.text_size` method.
-   Added the `mili.AdaptiveUIScaler` utility object.

### Enhancements

-   Calling `mili.Scrollbar.scroll_moved` after calling `mili.Scroll.scroll/set_scroll` is redundant as Scroll now keeps a list of scrollbars and automatically calls the method for you.
-   It is allowed to use the with statement with elements and not just parents without errors.
-   `mili.GenericApp.clear_color` can be None to disable clearing the window at the start of the frame.
-   Documented the `mili.icon` module.
-   Refactored some of the internals including the file structure.

### Fixes

-   Added a section for the `mili.icon` module in the guide.
-   Allowed passing `"element"` to the style methods of MILI.

### Behaviour-Changing:

-   `mili.Interaction.just_released_button` is not set anymore when the element was not hovered while releasing the mouse.
-   The `resizex` and `resizey` element styles only recognize boolean values. For min and max check the `size_clamp` new style.
-   Removed `mili.indent`. There are better alternatives now.

### API-Breaking

-   Small break, within `mili.icon` `google_size` has been renamed to svg_size
-   Removed the header argument to `MILI.begin/end`. Always been dumb.

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
