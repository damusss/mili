# 1.0.0

### Fixes

- Fixed/Updated the guide, refactored some code.
- Fixed draw clipping issues.
- Fixed the slider not properly setting the starting value
- Fixed the slider not centering the handle
- Fixed the codebase to be type safe

### Enhancements

- Added the `changelog` command to the cli.
- Allowed `%` characters in percentage strings.
- Allowed `fillx` and `filly` values for grid containers.
- Allowed a list of floats for the `border_radius` style of the rect component.
- You can now get the `ElementData` of the stack element.
- The element's `blocking` style can be set to `None` to save performance.

### New API

- Added the `MILI.canva_offset` property.
- Added the `mili.get_font_cache` and `mili.clear_font_cache` functions.
- Added the `pad` style to elements and components.
- Added the `aspect_ratio` and `align` styles to the rect and circle component.
- Added the `corners` style to the circle component.
- Added the `BoundingAlignLike` typing alias.
- Added the `dash_size` and `dash_offset` styles to the line component.
- Added the `dash_size` and `dash_anchor` styles to the circle component.
- Added the `dash_size` and `dash_offset` styles to the rect component.
- Added the `mili.FILL` style helper.

### API-breaking

- Removed `MILI.basic_element`.
- Removed `MILI.set_canva` (redundant after `MILI.canva`)

  ### <small>`ElementData` refactor</small>

  - Added the lazy property `Interaction.data` to retrieve the element data.
  - Removed the `MILI.always_get_data` attribute.
  - Removed the `get_data` parameter from every `MILI` function
  - Every `MILI` function can only return `Interaction`.
  - Utility functions that allowed `ElementData` only allow `Interaction`.
  - Removed the `Interaction.id` and `ElementData.interaction` attributes.
