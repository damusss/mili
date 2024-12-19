[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

# MILI Style Guide

Style is represented by a dictionary. Non-existent style keys won't raise an exception.

To specify percentage use a string. The value to apply the percentage to is chosen based on the style and usually relies on the element rect. Percentage can be negative. The trailing `%` in percentage strings is optional.<br>

padx of value `"20%"` will result in padding x which is 20% of the element width while pady of `"20%"` results in padding y which is 20% of the element height.

Available bounding alignment values are: `center`, `topleft`, `bottomleft`, `topright`, `bottomright`, `midleft`/`left`, `midright`/`right`, `midtop`/`top`, `midbottom`/`bottom`.

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

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | ------------------- | ------------------- |
| resizex, resizey | `True/False/dict[min, max: number/percentage]` | _control if the element should resize to be the right size to exactly fit all children inside. Optionally the value can be a dictionary specifying the maximum and minimum sizes_ (**children with fillx or filly won't have any space. incompatible with fillx and filly**) | `False` |
| fillx, filly | `True/False/number/percentage` | _control if the element should resize to fill all the space possible in the parent or the space defined by the percentage (`True` is 100% and `False` is disabled). The actual space occupied is scaled based on the amount of elements with fillx and filly_ (**incompatible with resizex and resizey. elements without fillx and filly have priority. ineffective if the parent is a grid**) | `False` |
| blocking | `True/False/None` | _control wether the element can be interacted by the mouse pointer. if set to the sentinel None, the element will be blocking but no interaction will be calculated (if blocking is False or None only one interaction object is shared between all elements, so the data will only be reliable immediately after the element is created)_ | `True` |
| ignore_grid | `True/False` | _control wether this element should not be moved or resized by the parent layout_ | `False` |
| align | `first/last/center` | _control how this element is aligned in the opposite axis of the parent, similar to anchor_ (**ineffective if the parent is a grid**) | `first` |
| z | `integer` | _manually set the z layer that controls interaction and rendering priority. normally the value automatically increases_ | auto |
| parent_id | `integer` | _ignore the current parent and manually set the element parent using the ID_ | auto |
| offset | `Sequence[float]` | _draw and interaction offset from its relative position_ | `(0, 0)` |
| clip_draw | `True/False` | _if False, disable the clip rect allowing components and children to be visible outside of the element rect_ | `True` |
| pre_draw_func | `(Surface, ElementData, Rect) -> None / None` | _a function that takes the canvas, the element data and the clip rect to be called before the components are drawn_ | `None` |
| mid_draw_func | `(Surface, ElementData, Rect) -> None / None` | _a function that takes the canvas, the element data and the clip rect to be called after the components are drawn and before the children are drawn_ | `None` |
| post_draw_func | `(Surface, ElementData, Rect) -> None / None` | _a function that takes the canvas, the element data and the clip rect to be called after the children are drawn_ | `None` |
| update_id | `string/list[string]` | _the update ID(s) that will be used to automatically update utilities associated with it_ | `None` |
| image_layer_cache | `ImageLayerCache/None` | _draws the provided `ImageLayerCache` when this element is done rendering, instead of doing it on top of everything_ (**cannot be set as a default style**) | `None` |

### Children Style

The following styles only apply to the children of this element.
| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | ------------------- | ------------------- |
| axis | `x/y` | _control the axis along where children are placed_ | `y` |
| spacing | `number/percentage` | _control the space between children_ | `3` |
| pad | `number/percentage` | _control the space between the children and the element borders in both directions_ | `5` |
| padx, pady | `number/percentage` | _control the space between the children and the element borders_ | same as `pad` |
| anchor | `first/center/last/max_spacing` | _control how children are aligned along the element axis_ | `first` |
| default_align | `first/center/last` | _control the default opposite axis alignment of every children_ | `first` |
| grid | `True/False` | _control wether the children should be organized in both directions_ (**children alignment is ignored. fillx and filly values for children are calculated based on the parent size alone**) | `False` |
| grid_align | `first/center/last/max_spacing` | _control how children are aligned along the rows of the element axis, while the anchor controls the alignement of the rows themselves_ (**only effective if the element is a grid**) | `first` |
| grid_spacex, grid_spacey | `number/percentage` | _control the space between children along the row and between the rows depending on the axis separately_ (**only effective if the element is a grid**) | same as `spacing` |

### Anchoring

- center<br>
  ` |-----C1-C2-C3-C4-----|`
- first<br>
  ` |C1-C2-C3-C4---------|`
- last<br>
  ` |---------C1-C2-C3-C4|`
- max_spacing<br>
  ` |C1----C2----C3----C4|`

## Common Component Styles

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | ------------------- | ------------------- |
| draw_above | `True/False` | _control wether the component is drawn above the children_ | `False` |
| element_id | `int` | _select the element this component should be attached to instead of the most recently created element_ (**cannot be set as a default style**) | `None` |

## Rect Style

The following styles modify the appearance of the rect component (draws using `pygame.draw.rect`)

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | ------------------- | ------------------- |
| pad | `number/percentage` | _control the space between the drawn rect and the element borders in both directions_ | `0` |
| padx, pady | `number/percentage` | _control the space between the drawn rect and the element borders_ | same as `pad` |
| outline | `number/percentage` | _control the size of the outline. 0 means no outline_ | `0` |
| border_radius | `number/percentage/[number/percentage x4]` | _control how round are the corners. an iterable value controls each corner separately_ | `0` |
| color | `color value` | _control the rect color_ | `black` |
| aspect_ratio | `float/None` | _forces the aspect ratio on the rect instead of filling the available area_ | `None` |
| align | `bounding alignment` | _control how the rect is aligned inside the element when the aspect ratio is specified_ | `center` |
| dash_size | `number/percentage/[number/percentage x2]/None` | _enables the dashed style. a single value or an iterable for fill and space segment sizes can be provided. the percentage will be relative to the rect permiter._ (**border radius will be ignored. outline must be > 0**) | `None` |
| dash_offset | `number/percentage` | _when the style is dashed, controls the offset after which to draw the first segment. the percentage will be relative to the rect perimeter_ | `0` |


## Circle Style

The following styles modify the appearance of the circle/ellipse component (draws using `pygame.draw.(aa)circle`, `pygame.draw.ellipse`, and `pygame.draw.arc`).
An ellipse is drawn when the calculated bounding area of the circle is not a square. Arcs are drawn when the style is dashed.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | ------------------- | ------------------- |
| pad | `number/percentage` | _control the space between the circle and the element borders in both directions_ | `0` |
| padx, pady | `number/percentage` | _control the space between the circle and the element borders_ | same as `pad` |
| outline | `number/percentage` | _control the size of the outline. 0 means no outline_ | same as `pad` |
| color | `color value` | _control the circle color_ | `black` |
| antialias | `True/False` | _wether the circle is antialiased. currently not supported for ellipse_ | `False` |
| aspect_ratio | `float/None` | _forces the aspect ratio on the circle instead of filling the available area_ | `None` |
| align | `bounding alignment` | _control how the circle is aligned inside the element when the aspect ratio is specified_ | `center` |
| corners | `[bool, bool, bool, bool]/None` | _control which corners should be drawn when specified. currently not supported for ellipse_ | `None` |
| dash_size | `number/[number x2]/None` | _enables the dashed style. a single value or an iterable for fill and space segment sizes can be provided. the sizes are expected to be floats representing a percentage of 2PI (the circumference). the outline must be >= 1_ | `None` |
| dash_anchor | `number/[number x2]` | _when the style is dashed, a single of double float representing a percentage of 2PI (the circumference) that represent the start and end angles of the dashed segment_ | `25` |
| draw_above | `True/False` | _control wether the circle is drawn above the children_ | `False` |

## Text Style

The following styes modify the appearance of the text component.
<br>
For every combination of font name and size a font object is created and cached.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | ------------------- | ------------------- |
| name | `string/None` | _control the font name or path_ (**system fonts only work with the sysfont style `True`**) | `None` |
| size | `integer` | _control the font size_ | `20` |
| align | `bounding alignment` | _control how the drawn text is aligned inside the element_ | `center` |
| font_align | `pygame.FONT_*` | _control the font alignment_ | `pygame.FONT_CENTER` |
| bold | `True/False` | _control the font bold style_ | `False` |
| italic | `True/False` | _control the font italic style_ | `False` |
| underline | `True/False` | _control the font underline style_ | `False` |
| strikethrough | `True/False` | _control the font strikethrough style_ | `False` |
| antialias | `True/False` | _control the antialiasing of the font, pixel fonts should set this to `False`_ | `True` |
| color | `color value` | _control the text color_ | `black` |
| bg_color | `color value/None` | _control the color behind the text. `None` disables this_ | `None` |
| growx, growy | `True/False` | _control whether the element size can grow if the rendered text is bigger than the element_ | `False` |
| padx, pady | `number/percentage` | _control the space between the text and the element borders_ | `5/3` |
| pad | `number/percentage/None` | _override the space between the text and the element borders for both directions_ | `None` |
| wraplen | `number/percentage` | _manually control the maximum width the text can have. 0 means the text is not restricted_ | `0` |
| draw_above | `True/False` | _control wether the text is drawn above the children_ | `False` |
| slow_grow | `True/False` | _temporary style, since Font.size() does not implement wrapline or newlines, if slow_grow is set to True Font.render will be used (which is slower). incompatible with growx_ | `False` |

## Image Style

The following styles modify the appearance of the image component.<br>

By default the surface keeps its aspect ratio while fitting in the element area.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | ------------------- | ------------------- |
| cache | `ImageCache/None` | _provides an `ImageCache` to massively speed up image rendering_ (**the cache can't be set as a default style**) | `None` |
| layer_cache | `ImageLayerCache/None` | _provides an `ImageLayerCache` to speed up special cases of concurrent image rendering_ (**cannot be set as a default style. requires a valid `ImageCache` object aswell**) | `None` |
| pad | `number/percentage` | _control the space between the image and the element borders in both directions_ | `0` |
| padx, pady | `number/percentage` | _control the space between the image and the element borders_ | same as `pad` |
| fill | `True/False` | _control whether the image should be cropped/scaled to match the aspect ratio of the element while keeping its own aspect ratio_ | `False` |
| stretchx, stretchy | `True/False` | _control whether the image should loose its aspect ratio and be resized to match the aspect ratio of the element_ | `False` |
| fill_color | `color value/None` | _if not `None`, fill the surface with this color_ | `None` |
| smoothscale | `True/False` | _control the scale backend to use_ | `False` |
| border_radius | `number/percentage` | _control how rounded are the corners of the surface_ | `0` |
| alpha | `integer 0-255` | _control the surface alpha_ | `255` |
| ninepatch_size | `number/percentage` | _if > 0, the surface will be scaled to fit the element but the 4 corners of the specified size will be preserved_ (**incompatible with fill, stretchx, and stretchy**) | `0` |
| draw_above | `True/False` | _control wether the image is drawn above the children_ | `False` |
| ready | `True/False` | _if true, mili will assume the image was already modified and scaled to be inside the element by the user so no operations and useless checks will be performed. useful when combining mili.fit\_image and multithreading_ | `False` |

## Line Style

The following styles modify the appearance of the line component (draws using `pygame.draw.(aa)line`)<br>

The start_end should be a sequence of 2 sequences where the x and y values can be numbers or percentages relative to the element center.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | ------------------- | ------------------- |
| size | `number/percentage` | _control the size the line_ | `1` |
| color | `color value` | _control the line color_ | `black` |
| antialias | `True/False` | _wether the line is antialiased. currently not supported for sizes different from 1_ | `False` |
| dash_size | `number/percentage/[number/percentage x2]/None` | _enables the dashed style. a single value or an iterable for fill and space segment sizes can be provided. the percentage will be relative to the line length_ | `None` |
| dash_offset | `number/percentage` | _when the style is dashed, controls the offset after which to draw the first segment. the percentage will be relative to the line length_ | `0` |
| draw_above | `True/False` | _control wether the line is drawn above the children_ | `False` |

## Polygon Style

The following styles modify the appearance of the polygon component (draws using `pygame.draw.polygon`)<br>

The points should be a sequence of at least 2 sequences where the x and y values can be numbers or percentages relative to the element center.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | ------------------- | ------------------- |
| outline | `number/percentage` | _control the size of the outline. 0 means no outline_ | `0` |
| color | `color value` | _control the polygon color_ | `black` |
| draw_above | `True/False` | _control wether the polygon is drawn above the children_ | `False` |

## Style Helpers

### (exported in the `mili.style` module)

- `mili.CENTER`: Centers text, anchoring and aligment

- `mili.X`: Expands to `{"axis": "x"}`

- `mili.PADLESS`: Sets padding to zero on both axis

- `mili.RESIZE`: Sets resizing to true on both axis

- `mili.FILL`: Sets filling to true on both axis

- `mili.FLOATING`: Styles to ignore the parent and have the stack as parent

- `mili.style.filter()` will help you select the style names you want using a whitelist and a blacklist<br>

- `mili.style.same()` creates a dictionary with the same value for different style names<br>

- `mili.style.conditional()` will use the base style and expand it with the hover and press style based on the interaction status and selection status<br>

- `mili.style.Style` will help you cache common styles. you can retrieve them with `get(type)` or use the shortcuts like `get_rect()`<br>

- `mili.style.StyleStatus` will help you cache styles for different interactions, using `mili.style.Style` objects for base, hover and press statuses that you can retrieve with the `get(type, interaction)` or use the shortcuts like `get_rect(interaction)` (similar to `mili.style.conditional()`)

Keep in mind that you can merge styles using the pipe operator, for example `mili.CENTER | mili.PADLESS`
