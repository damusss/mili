# MILI Style Guide

To specify percentage use a string. The value to apply the percentage to is chosen based on the style and usually relies on the element rect. Percentage can be negative.<br>

padx of value "20" will result in padding x which is 20% of the element width while pady of "20" results in padding y which is 20% of the element height.

## Style Resolution Method

- 1. search in the provided style

  ```py
  my_mili.text("Example", {"size": 50})
  # result: the size is 50
  ```

- 2. search in the default style

  ```py
  my_mili.default_style("text", {"size": 30})
  my_mili.text("Example")
  # result: the size is 30
  ```

- 3. use the internal default value

  ```py
  my_mili.text("Example")
  # result: the size is 20
  ```

## Element Style

The following styles apply to the current element.

| Name             | Type/Value                                     | Description                                                                                                                                                                                                                                                                                                                                                                                    | Default |
| ---------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| resizex, resizey | `True/False/dict[min, max: number/percentage]` | _control if the element should resize to be the right size to exactly fit all children inside. Optionally the value can be a dictionary specifying the maximum and minimum sizes_ (**children with fillx or filly won't have any space. incompatible with fillx and filly**)                                                                                                                   | `False` |
| fillx, filly     | `True/False/number/percentage`                 | _control if the element should resize to fill all the space possible in the parent or the space defined by the percentage (`True` is 100% and `False` is disabled). The actual space occupied is scaled based on the amount of elements with fillx and filly_ (**incompatible with resizex and resizey. elements without fillx and filly have priority. ineffective if the parent is a grid**) | `False` |
| blocking         | `True/False`                                   | _control wether the element can be interacted by the mouse pointer_                                                                                                                                                                                                                                                                                                                            | `True`  |
| ignore_grid      | `True/False`                                   | _control wether this element should not be moved or resized by the parent layout_                                                                                                                                                                                                                                                                                                              | `False` |
| align            | `first/last/center`                            | _control how this element is aligned in the opposite axis of the parent, similar to anchor_ (**ineffective if the parent is a grid**)                                                                                                                                                                                                                                                          | `first` |
| z                | `integer`                                      | _manually set the z layer that controls interaction and rendering priority. normally the value automatically increases_                                                                                                                                                                                                                                                                        | auto    |
| parent_id        | `integer`                                      | _ignore the current parent and manually set the element parent using the ID_                                                                                                                                                                                                                                                                                                                   | auto    |
| offset | `Sequence[float]` | _draw and interaction offset from its relative position_ | `(0, 0)` |
| pre_draw_func | `(Surface, ElementData, Rect) -> None / None` | _a function that takes the canvas, the element data and the clip rect to be called before the components are drawn_ | `None` |
| mid_draw_func | `(Surface, ElementData, Rect) -> None / None` | _a function that takes the canvas, the element data and the clip rect to be called after the components are drawn and before the children are drawn_ | `None` |
| post_draw_func | `(Surface, ElementData, Rect) -> None / None` | _a function that takes the canvas, the element data and the clip rect to be called after the children are drawn_ | `None` |

### Children Style

The following styles only apply to the children of this element.
|Name|Type/Value|Description|Default|
|---------|----------|---------|---------|
| axis | `x/y` | _control the axis along where children are placed_|`y`|
| spacing | `number/percentage` | _control the space between children_|`3`|
| padx, pady | `number/percentage` | _control the space between the children and the element borders_|`5`|
|anchor|`first/center/last/max_spacing`| _control how children are aligned along the element axis_|`first`|
|grid|`True/False`|_control wether the children should be organized in both directions_ (**children alignment or fillx or filly are ignored**)|`False`|
| grid\_align |`first/center/last/max_spacing`| _control how children are aligned along the rows of the element axis, while the anchor controls the alignement of the rows themselves_ (**only effective if the element is a grid**)|`first`|
| grid\_spacex, grid\_spacey |`number/percentage`| _control the space between children along the row and between the rows depending on the axis separately_ (**only effective if the element is a grid**) |same as spacing|

### Anchoring

- center<br>
  ` |-----C1-C2-C3-C4-----|`
- first<br>
  ` |C1-C2-C3-C4---------|`
- last<br>
  ` |---------C1-C2-C3-C4|`
- max_spacing<br>
  ` |C1----C2----C3----C4|`

## Rect Style

The following styles modify the appearance of the rect component (draws using `pygame.draw.rect`)

| Name          | Type/Value          | Description                                                        | Default |
| ------------- | ------------------- | ------------------------------------------------------------------ | ------- |
| padx, pady    | `number/percentage` | _control the space between the drawn rect and the element borders_ | `0`     |
| outline  | `number/percentage` | _control the size of the outline. 0 means no outline_              | `0`     |
| border_radius | `number/percentage` | _control how round are the corners_                                | `0`     |
| color         | `color value`       | _control the rect color_                                           | `black` |
| draw_above    | `True/False`        | _the rect is drawn above the children_                             | `False` |

## Circle Style

The following styles modify the appearance of the circle/ellipse component (draws using `pygame.draw.circle` and `pygame.draw.ellipse`)

| Name         | Type/Value          | Description                                                                                                   | Default |
| ------------ | ------------------- | ------------------------------------------------------------------------------------------------------------- | ------- |
| padx, pady   | `number/percentage` | _control the space between the circle and the element borders. if padx differs from pady an ellipse is drawn_ | `0`     |
| outline | `number/percentage` | _control the size of the outline. 0 means no outline_                                                         | `0`     |
| color        | `color value`       | _control the circle color_                                                                                    | `black` |
| draw_above    | `True/False`        | _the circle is drawn above the children_                             | `False` |

## Text Style

The following styes modify the appearance of the text component.
<br>
For every combination of font name and size a font object is created and cached.

| Name          | Type/Value              | Description                                                                                 | Default              |
| ------------- | ----------------------- | ------------------------------------------------------------------------------------------- | -------------------- |
| name          | `string/None`           | _control the font name or path_ (**system fonts only work with the sysfont style `True`**)  | `None`               |
| size          | `integer`               | _control the font size_                                                                     | `20`                 |
| align         | `center/topleft/top...` | _control how the drawn text is aligned inside the element_                                  | `center`             |
| font_align    | `pygame.FONT_*`         | _control the font alignment_                                                                | `pygame.FONT_CENTER` |
| bold          | `True/False`            | _control the font bold style_                                                               | `False`              |
| italic        | `True/False`            | _control the font italic style_                                                             | `False`              |
| underline     | `True/False`            | _control the font underline style_                                                          | `False`              |
| strikethrough | `True/False`            | _control the font strikethrough style_                                                      | `False`              |
| antialias     | `True/False`            | _control the antialiasing of the font, pixel fonts should set this to `False`_              | `True`               |
| color         | `color value`           | _control the text color_                                                                    | `black`              |
| bg_color      | `color value/None`      | _control the color behind the text. `None` disables this_                                     | `None`               |
| growx, growy  | `True/False`            | _control whether the element size can grow if the rendered text is bigger than the element_ | `False`              |
| padx, pady    | `number/percentage`     | _control the space between the text and the element borders_                                | `5/3`                |
| wraplen       | `number/percentage`     | _manually control the maximum width the text can have. 0 means the text is not restricted_  | `0`                  |
| draw_above    | `True/False`        | _the text is drawn above the children_                             | `False` |

## Image Style

The following styles modify the appearance of the image component.<br>

By default the surface keeps its aspect ratio while fitting in the element area.

| Name               | Type/Value          | Description                                                                                                                      | Default |
| ------------------ | ------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------- |
| cache              | `ImageCache/None`   | _provides an `ImageCache` to massively speed up image rendering_ (**the cache can't be set as a default style**)                 | `None`  |
| padx, pady         | `number/percentage` | _control the space between the image and the element borders_                                                                    | `0`     |
| fill               | `True/False`        | _control whether the image should be cropped/scaled to match the aspect ratio of the element while keeping its own aspect ratio_ | `False` |
| stretchx, stretchy | `True/False`        | _control whether the image should loose its aspect ratio and be resized to match the aspect ratio of the element_                | `False` |
| fill_color         | `color value/None`  | _if not `None`, fill the surface with this color_                                                                                | `None`  |
| smoothscale        | `True/False`        | _control the scale backend to use_                                                                                               | `False` |
| border_radius      | `number/percentage` | _control how rounded are the corners of the surface_                                                                             | `0`     |
| alpha              | `integer 0-255`     | _control the surface alpha_                                                                                                      | `255`   |
| ninepatch_size     | `number/percentage` | _if > 0, the surface will be scaled to fit the element but the 4 corners of the specified size will be preserved_ (**incompatible with fill, stretchx, and stretchy**) | `0` |
| draw_above    | `True/False`        | _the image is drawn above the children_                             | `False` |

## Line Style

The following styles modify the appearance of the line component (draws using `pygame.draw.line`)<br>

The start_end should be a sequence of 2 sequences where the x and y values can be numbers or percentages relative to the element center.

| Name  | Type/Value          | Description                 | Default |
| ----- | ------------------- | --------------------------- | ------- |
| size  | `number/percentage` | _control the size the line_ | `1`     |
| color | `color value`       | _control the line color_    | `black` |
| draw_above    | `True/False`        | _the line is drawn above the children_                             | `False` |

## Polygon Style

The following styles modify the appearance of the polygon component (draws using `pygame.draw.polygon`)<br>

The points should be a sequence of at least 2 sequences where the x and y values can be numbers or percentages relative to the element center.

| Name         | Type/Value          | Description                                           | Default |
| ------------ | ------------------- | ----------------------------------------------------- | ------- |
| outline | `number/percentage` | _control the size of the outline. 0 means no outline_ | `0`     |
| color        | `color value`       | _control the polygon color_                           | `black` |
| draw_above    | `True/False`        | _the polygon is drawn above the children_                             | `False` |

## Style Helpers

you can find typehinting helpers in the `mili.typing` submodule.

`mili.percentage()` will help you with element sizes<br>

`mili.gray()` will shorten the gray colors, expanding your value to a tuple of the same value 3 times<br>

`mili.style.filter()` will help you select the style names you want using a whitelist and a blacklist<br>

`mili.style.same()` creates a dictionary with the same value for different style names<br>

`mili.style.conditional()` will use the base style and expand it with the hover and press style based on the interaction status and selection status<br>

`my_mili.default_style()` and `my_mili.default_styles()` sets the default styles for a mili object<br>

`mili.style.Style` will help you cache common styles. you can retrieve them with `get(type)` or use the shortcuts like `get_rect()`<br>

`mili.style.StyleStatus` will help you cache styles for different interactions, using `mili.style.Style` objects for base, hover and press statuses that you can retrieve with the `get(type, interaction)` or use the shortcuts like `get_rect(interaction)` (similar to `mili.style.conditional()`)
