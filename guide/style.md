[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

# MILI Style Guide

Style is represented by a dictionary. Non-existent style keys won't raise an exception.

To specify percentage use a string. The value to apply the percentage to is chosen based on the style and usually relies on the element rect. Percentage can be negative. The trailing `%` in percentage strings is optional.

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
| ------------------- | ------------------- | :------------------- | ------------------- |
| resizex, resizey | `True/False` | _control if the element should resize to be the right size to exactly fit all children inside_ (**children with fillx or filly won't have any space. incompatible with fillx and filly**) | same as `resize` |
| fillx, filly | `True/False/number/percentage` | _control if the element should resize to fill all the space possible in the parent or the space defined by the percentage (`True` is 100% and `False` is disabled). The actual space occupied is scaled based on the amount of elements with fillx and filly_ (**incompatible with resizex and resizey. elements without fillx and filly have priority. ineffective if the parent is a grid**) | same as `fill` |
| size_clamp | `dict[min/max: (number/None, number/None)]/None` | _control the minimum and maximum sizes the element can be resized to within fillx/y or resizex/y operations_ | `None` |
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
| cache_rect_size | `True/False` | _Control wether the element should inherit the size of the previous holder of the current ID. Always happens for elements that have fillx or filly in the respective axis. Could save performance or be required for things to look right in certain scenarios_ | `False` |

### Children Style

The following styles only apply to the children of this element.
| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
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
| ------------------- | ------------------- | :------------------- | ------------------- |
| draw_above | `True/False` | _control wether the component is drawn above the children_ | `False` |
| element_id | `int` | _select the element this component should be attached to instead of the most recently created element_ (**cannot be set as a default style**) | `None` |

## Rect Style

The following styles modify the appearance of the rect component (draws using `pygame.draw.rect`)

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| pad | `number/percentage` | _control the space between the drawn rect and the element borders in both directions_ | `0` |
| padx, pady | `number/percentage` | _control the space between the drawn rect and the element borders_ | same as `pad` |
| outline | `number/percentage` | _control the size of the outline. 0 means no outline_ | `0` |
| border_radius | `number/percentage/[number/percentage x4]` | _control how round are the corners. an iterable value controls each corner separately_ | `0` |
| color | `color value` | _control the rect color_ | `black` |
| aspect_ratio | `float/None` | _forces the aspect ratio on the rect instead of filling the available area_ | `None` |
| align | `bounding alignment` | _control how the rect is aligned inside the element when the aspect ratio is specified_ | `center` |
| dash_size | `number/percentage/[number/percentage x2]/None` | _enables the dashed style. a single value or an iterable for fill and space segment sizes can be provided. the percentage will be relative to the rect permiter._ (**border radius will be ignored. outline must be > 0**) | `None` |
| dash_offset | `number/percentage` | _when the style is dashed, controls the offset after which to draw the first segment. the percentage will be relative to the rect perimeter_ | `0` |
| ready_rect | `pygame.typing.RectLike/None` | _ignores padding and the element hitbox and uses directly the provided rect (assumed with absolute position)_ | `None` |


## Circle Style

The following styles modify the appearance of the circle/ellipse component (draws using `pygame.draw.(aa)circle`, `pygame.draw.ellipse`, and `pygame.draw.arc`).
An ellipse is drawn when the calculated bounding area of the circle is not a square. Arcs are drawn when the style is dashed.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
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

## Text Style

The following styes modify the appearance of the text component.

For every combination of font name and size a font object is created and cached.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| cache | `mili.TextCache/None/"auto"` | _provides a text cache to speed up text rendering. Setting it to auto will automatically call `mili.TextCache.get_next_cache()` (**can be only set as a default style if it is set to auto**)_ | `None` |
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
| growx, growy | `True/False` | _control whether the element size can grow if the rendered text is bigger than the element_ | `False`, `True` |
| padx, pady | `number/percentage` | _control the space between the text and the element borders_ | `5/3` |
| pad | `number/percentage/None` | _override the space between the text and the element borders for both directions_ | `None` |
| wraplen | `number/percentage` | _manually control the maximum width the text can have. 0 means the text is not restricted_ | `0` |
| blit_flags | `integer` | _flags passed to the special\_flags parameter of Surface.blit to control blending_ | `0` |
| slow_grow | `True/False` | _temporary style, since Font.size() does not implement wrapline or newlines, if slow\_grow is set to True Font.render will be used (which is slower)._ **incompatible with growx, ignored with rich text** | `False` |
| rich | `True/False` | _enables rich text (subset of html), handling text processing, wrapping and rendering to a custom implementation. Other styles are used as a default style in addition to html tags_ | `False` |
| rich_aligny | `top/center/bottom` | _with rich text, controls the alignment of text of different sizes on the same line_ | `center` |
| rich_linespace | `number/percentage` | _with rich text, controls the extra space between lines_ | `0` |
| rich_actions | `dict[name: function(data)]` | _with rich text, provides the functions corresponding to the actions so they can be triggered_ | `{}` |
| rich_link_color | `color value` | _with rich text, controls the color of emulated links_ | `(144, 154, 255)` |
| rich_markdown | `True/False` | _with rich text, mardown styling (bold, italic, spoiler, link, inline codeblock, etc) is converted to HTML tags_ | `False` |
| rich_markdown_style | `rich markdown style dict` | _with rich text & markdown, control a few style details_ | `{rich markdown style defaults}` |

### Rich Markdown Style
| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| spoiler_color | `color value` | _The color of the text background and foreground when the text is hidden_ |  `gray20`|
| spoiler_text_color | `color value` | _The color of the text foreground when the text is shown_ |  `(150, 150, 150)`|
| code_bg_color | `color value` | _The background color of the text in the code_ |  `(60, 60, 60)`|
| code_color | `color value` | _The color of the text inside the code_ |  `white`|
| highlight_color | `color value` | _The background color of highlighted text_ | #604c44 |

### Rich Text

NOTE: Rich text is many times less performant than normal text, especially when the text changes or when the element resizes.

Rich text consists of a subset of html. The MILI rich text parser supports the following basic tags:
- `<b> </b>`: Bold text
- `<i> </i>`: Italic text
- `<u> </u>`: Underlined text
- `<s> </s>`: Text with striketrough

Adding the attribute 'null' to the above tags will apply them as false instead of true.
- `<font name="Name/Path" size="30" sysfont antialias> </font>`: Control text font (name, size, sysfont (true), antialias (true))
- `<color fg="green" bg="black"> </color>`: Control text color (foreground, background)

Providing a value of 'null' to sysfont, antialias or bg will apply them as False, False, None
- `<a href="DATA"> </a>`: Text looks like a link (check below for more details, not a basic tag)

**Markdown Conversion**

With `rich_markdown` a subset of markdown is converted to HTML, which is:
- `*TEXT*`/`_TEXT_` -> `<i>TEXT</i>`
- `**TEXT**`/`__TEXT__` -> `<b>TEXT</b>`
- `~~TEXT~~` -> `<s>TEXT</s>`
- \`TEXT\` -> Text with a different bg and fg color, which's inside is not parsed
- `||TEXT||` -> Emulate spoiler
- `[TEXT](LINK)` -> `<a href="LINK">TEXT</a>`
- `<LINK>` -> `<a href="LINK">LINK</a>` (clear link, LINK must start with http:// or https://)
- `==TEXT==` -> Highlighted text (different text background color)
Special symbols won't work if escaped and they are valid if attached to the text.

**Advanced Rich Text**

To properly emulate rich text, MILI allows for two special usages of tags and attributes:
- `<action name="ACTION NAME" condition="hovered" button="1" data="CUSTOM DATA"> </action>`:
    When the specified action happens to the text, the function corresponding to that name (found in the rich_actions style) will be called passing the data attribute as a parameter. Supported conditions are: hovered/hover, pressed/press, just-pressed, just-released.
- `<X condition="hovered"> </X>` (where tag X be any of the basic html tags above): When the condition attribute is specified, that style modifier will only be applied if the condition is met. Supported conditions are the same that are supported with the action tag.

With the advanced rich text it is possible to emulate links, and since it is a common tag the `<a>` (link) tag is also supported. Instead of being supported natively it is emulated by converting to to a sequence of `<action ...><action ...><color ...><u ...>`. When the link is hovered the action `link_hover` will be called while when it is clicked the action `link_click` is called.

You can emulate something like a spoiler tag by giving the same foreground and background color to the text and change it to no background and visible foreground conditionally with just-released (for example: `<action name="link_hover" condition="hover"><color fg="gray20" bg="gray20"><color fg="(150, 150, 150)" bg="null" condition="just-released"> TEXT </color></color></action>`). You should be able to create all kinds of effects like this. If your effect is repetitive enough (and without variable attributes) you can make your own tag and use `str.replace` to drop-in the correct tag sequence (similar to the link tag).

## Image Style

The following styles modify the appearance of the image component.

By default the surface keeps its aspect ratio while fitting in the element area.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| cache | `ImageCache/None/"auto"` | _provides an `ImageCache` to massively speed up image rendering. Setting it to auto will automatically call `mili.ImageCache.get_next_cache()`_ ((**can be only set as a default style if it is set to auto**)) | `None` |
| layer_cache | `ImageLayerCache/None` | _provides an `ImageLayerCache` to speed up special cases of concurrent image rendering_ (**cannot be set as a default style. requires a valid `ImageCache` object aswell**) | `None` |
| pad | `number/percentage` | _control the space between the image and the element borders in both directions_ | `0` |
| padx, pady | `number/percentage` | _control the space between the image and the element borders_ | same as `pad` |
| fill | `True/False` | _control whether the image should be cropped/scaled to match the aspect ratio of the element while keeping its own aspect ratio_ | `False` |
| stretchx, stretchy | `True/False` | _control whether the image should loose its aspect ratio and be resized to match the aspect ratio of the element_ | `False` |
| fill_color | `color value/None` | _if not `None`, fill the surface with this color_ | `None` |
| smoothscale | `True/False` | _control the scale backend to use_ | `False` |
| border_radius | `number/percentage` | _control how rounded are the corners of the surface_ | `0` |
| ready_border_radius | `number/percentage` | _control how rounded are the corners of the surface (the rounding is applied before the image is resized)_ | `0` |
| alpha | `integer 0-255` | _control the surface alpha_ | `255` |
| blit_flags | `integer` | _flags passed to the special\_flags parameter of Surface.blit to control blending_ | `0` |
| ninepatch_size | `number/percentage` | _if > 0, the surface will be scaled to fit the element but the 4 corners of the specified size will be preserved_ (**incompatible with fill, stretchx, and stretchy**) | `0` |
| ready | `True/False` | _if true, mili will assume the image was already modified and scaled to be inside the element by the user so no operations and useless checks will be performed. useful when combining mili.fit\_image and multithreading_ | `False` |

## Line Style

The following styles modify the appearance of the line component (draws using `pygame.draw.(aa)line`)

The start_end should be a sequence of 2 sequences where the x and y values can be numbers or percentages relative to the element center.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| size | `number/percentage` | _control the size the line_ | `1` |
| color | `color value` | _control the line color_ | `black` |
| antialias | `True/False` | _wether the line is antialiased. currently not supported for sizes different from 1_ | `False` |
| dash_size | `number/percentage/[number/percentage x2]/None` | _enables the dashed style. a single value or an iterable for fill and space segment sizes can be provided. the percentage will be relative to the line length_ | `None` |
| dash_offset | `number/percentage` | _when the style is dashed, controls the offset after which to draw the first segment. the percentage will be relative to the line length_ | `0` |

## Polygon Style

The following styles modify the appearance of the polygon component (draws using `pygame.draw.polygon`)

The points should be a sequence of at least 2 sequences where the x and y values can be numbers or percentages relative to the element center.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| outline | `number/percentage` | _control the size of the outline. 0 means no outline_ | `0` |
| color | `color value` | _control the polygon color_ | `black` |
| draw_above | `True/False` | _control wether the polygon is drawn above the children_ | `False` |

## Markdown Style

Style available for the `mili.MarkDown` object.
Some styles are going to override the values of X_style to ensure markdown renders properly.

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| element_style | `rect style dict` | _the default style for inner elements_ | `{}` |
| rect_style | `rect style dict` | _the default style for rect elements_ | `{}` |
| circle_style | `circle style dict` | _the default style for circle elements_ | `{}` |
| line_style | `line style dict` | _the default style for line elements_ | `{}` |
| image_style | `image style dict` | _the default style for image elements_ | `{}` |
| text_style | `text style dict` | _the default style for text elements_ | `{}` |
| quote_width | `number` | _contrl how wide is the vertical rect preceding a quote block_ | `3` |
| quote_border_radius | `number` | _contrl the border radius of the vertical rect preceding a quote block_ | `3` |
| indent_width | `number` | _control how wide is an indentation_ | `30` |
| separator_height | `number` | _control the height of a vertical separator_ | `5` |
| line_break_size | `number` | _control how tall are break lines. also effects lines separating table cells_ | `1` |
| bullet_diameter | `number` | _control the diameter of the circle of a bullet list element_ | `5` |
| table_outline_size | `number` | _the outline size of tables. 0 disables it. color is the same as the line break color_ | `1` |
| table_border_radius | `number` | _the border radius of the table background and outline_ | `7` |
| table_alignx | `left/center/right` | _controls the default horizontal alignment of text/images inside a table cell_ | `left` |
| table_aligny | `top/center/bottom` | _controls the vertical alignment of text/images inside a table cell_ | `center` |
| line_break_color | `color value` | _the color of breaklines. also effects lines separating table cells_ | `(80, 80, 80)` |
| bullet_color | `color value` | _the color of a bullet list circle_ | `white` |
| table_bg_color | `color value/None` | _the color of the background of a table. None doesn't apply any particular background_ | `(30, 30, 30)` |
| quote_color | `color value` | _the color of text inside a quote_ | `(150, 150, 150)` |
| code_bg_color | `color value` | _the color of the background of multiline code blocks_ | `(40, 40, 40)` |
| code_outline_color | `color value` | _the color of the outline of multiline code blocks_ | `(50, 50, 50)` |
| code_border_radius | `number` | _the border radius of the rect of multiline code blocks_ | `3` |
| code_copy_style | `markdown code copy style dict` | _Controls the style of the copy button that appears when hovering code blocks_ | `markdown code copy style defaults` |
| code_scrollbar_style | `markdown code scrollbar style dict` | _Controls the styling of the scrollbar appearing when not all the code fits horizontally_ | `markdown code scrollbar style defaults` |
| title1/2/3/4/5/6_size | `integer` | _the font size of the titles_ | `26,22,19,16,14,12` |
| allow_image_link | `True/False` | _control wether images can be loaded from https urls_ | `True` |
| change_cursor | `True/False` | _control wether or not the cursor can become an hand when a link is hovered_ | `True` |
| load_images_async | `True/False` | _control wether images should be loaded with threads or not_ | `True` |
| open_links_in_browser | `True/False` | _control wether or not links should be opened in the browser when clicked_ | `True` |
| parse_async | `True/False` | _control wether or not the source should be parsed in threads_ | `True` |

### Mardown Code Copy Style

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| size | `number` | _The size of the copy button_ | `26` |
| icon_pad | `number/percentage` | _The padding of the icon image_ | `10%` |
| icon_color | `conditional color style` | _The colors of the icon when hovered, pressed or neither_ | `default: (120, 120, 120), hover: (180, 180, 180), press: (100, 100, 100)` |

### Markdown Code Scrollbar Style

A modified version of the regular scrollbar style (always horizontal).

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| border_radius | `number` | _The border radius of the scrollbar rects_ | `3` |
| padx | `number` | _The space between the tips of the scrollbar and the code block left and right sides_ | `1` |
| pady | `number` | _The space between the scrollbar and the bottom of the code block_ | `1` |
| height | `number` | _The height of the scrollbar_ | `7` |
| bar_color | `color value/None` | _The color of the bar of the scrollbar. None means invisible_ | `(30, 30, 30)` |
| handle_color | `conditional color style` | _The colors of the handle when hovered, pressed or neither_ | `default: (50, 50, 50), hover: (60, 60, 60), press: (50, 50, 50)` |

### Conditional Color Style

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| default | `color value/None` | _The color when the element is not hovered nor pressed. None means the component is disabled_ | must be set |
| hover | `color value/None` | _The color when the element is hovered. None means the component is disabled_ | must be set |
| press | `color value/None` | _The color when the element is pressed. None means the component is disabled_ | must be set |

## Utility Styles

### mili.Scrollbar

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| axis | `x/y` | _the axis the scrollbar controls_ | `y` |
| short_size | `number` | _how wide is the scrollbar in the opposite axis. It is adviced to customize at least this value_ | `10` |
| border_dist | `number` | _the distance from the right/bottom side of the scrollbar and the border of the container_ | `3` |
| padding | `number` | _the distance from the tips of the scrollbar and the borders of the container_ | `3` |
| size_reduce | `number` | _a value that can reduce the calculated length of the scrollbar. Useful to accomodate a scrollbar of the opposite axis in that space_ | `0` |
| bar_update_id | `str/None` | _the update ID to assign to the bar of the scrollbar to automatically update it_ | `None` |
| handle_update_id | `str/None` | _the update ID to assign to the handle of the scrollbar to automatically update it_ | `None` |

### mili.Slider

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| lock_x | `True/False` | _lock the movement of the slider on the X axis. If the lock\_y style is False this will result in a vertical slider_ | `False` |
| lock_y | `True/False` | _lock the movement of the slider on the Y axis. If the lock\_x style is False this will result in an horizontal slider_ | `False` |
| handle_size | `[number, number]` | _the size of the handle. It is adviced to customize at least this value_ | `(10, 10)` |
| strict_borders | `True/False` | _specify wether the handle can exceed the area borders by half its size or if it should be perfectly contained_ | `False` |
| area_update_id | `str/None` | _the update ID to assign to the area of the slider to automatically update it_ | `None` |
| handle_update_id | `str/None` | _the update ID to assign to the handle of the slider to automatically update it_ | `None` |


### mili.DropMenu

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| direction | `up/down` | _wether it is a drop down or a drop up_ | `down` |
| anchor | `first/center/last` | _wether the menu container should be aligned with the left side of the selected option element, the right side of it or centered to it_ | `first` |
| padding | `number` | _the distance from the selected option element and the menu container_ | `3` |
| selected_update_id | `str/None` | _the update ID to assign to the selected option element to automatically update it_ | `None` |
| menu_update_id | `str/None` | _the update ID to assign to the menu container to automatically update it_ | `None` |
| option_update_id | `str/None` | _the same update ID to assign to each option of the drop menu to automatically update them_ | `None` |

### mili.EntryLine

| Name | Type/Value | Description | Default |
| ------------------- | ------------------- | :------------------- | ------------------- |
| placeholder | `string` | _the text to display when the entryline is empty_ | `Enter text...` |
| placeholder_color | `color value` | _the color of the placeholder text_ | `(180, 180, 180)` |
| text_filly | `True/False/number/percentage` | _the filly style for the text element_ | `"100"` |
| text_style | `text style dict` | _additional style for the text (f.e. text size or font)_ | `{}` |
| bg_rect_style | `rect style dict/None` | _if not None, provide the style for a rect background shortcut_ | `None` |
| outline_rect_style | `rect style dict/None` | _if not None, provide the style for a rect outline shortcut_ | `None` |
| selection_style | `rect style dict/None` | _style override for the selection rect_ | `None` |
| selection_color | `color value` | _the color of the selection rect_ | `(20, 80, 225)` |
| error_color | `color value` | _the color of the text when it is invalid_ | `"red"` |
| cursor_color | `color value` | _the color of the cursor_ | `"white"` |
| cursor_width | `integer` | _control how wide is the cursor_ | `2` |
| blink_interval | `integer` | _control how fast the cursor blinks (in milliseconds)_ | `350` |
| double_click_interval | `integer` | _control the maximum time between clicks for it to be considered a double click (in milliseconds)_ | `250` |
| input_validator | `Callable[str->str/None]/None` | _custom callable returning the input (or modified) if it's valid or None if it's invalid_ | `None` |
| text_validator | `Callable[str->(str, True/False)]` | _custom callable returning the input (or modified) and a boolean indicating if it was valid or not_ | `None` |
| validator_lowercase | `True/False` | _enable or disable the built-in validator converting input to the lowercase counterparts_ | `False` |
| validator_uppercase | `True/False` | _enable or disable the built-in validator converting input to the uppercase counterparts_ | `False` |
| validator_windows_path | `True/False` | _enable or disable the built-in validator discarding input characters that are not allowed in Windows paths_ | `False` |
| target_number | `True/False` | _specify that the content is supposed to be a number restricting allowed input and validating it on enter_ | `False` |
| number_min | `number/None` | _when the target is a number specify the minum allowed value_ | `None` |
| number_max | `number/None` | _when the target is a number specify the maximum allowed value_ | `None` |
| number_integer | `True/False` | _when the target is a number control if it is supposed to be a whole integer_ | `False` |
| enable_history | `True/False` | _enable or disable action history_ | `True` |
| history_limit | `integer/None` | _control the maximum amount of actions that can be saved to history_ | `1000` |
| keymod | `pygame kmod constant` | _control the key modifier to access keyboard shortcuts on the entryline_ | `pygame.KMOD_CTRL` |
| copy_key | `pygame key constant/None` | _control the key used to copy the selection or None to disable the action_ | `pygame.K_c` |
| paste_key | `pygame key constant/None` | _control the key used to paste text or None to disable the action_ | `pygame.K_v` |
| cut_key | `pygame key constant/None` | _control the key used to cut the selection or None to disable the action_ | `pygame.K_x` |
| select_all_key | `pygame key constant/None` | _control the key used to select all the text or None to disable the action_ | `pygame.K_a` |
| delete_all_key | `pygame key constant/None` | _control the key used to delete all the text or None to disable the action_ | `pygame.K_BACKSPACE` |
| undo_key | `pygame key constant/None` | _control the key used to restore the previous action or None to disable the action_ | `pygame.K_c` |
| redo_key | `pygame key constant/None` | _control the key used to restore the previously undone action or None to disable the action_ | `pygame.K_c` |
| scroll | `mili.Scroll/None` | _the scroll "attached" to the entryline container to consider when positioning elements_ | `None` |

## Style Helpers

### (exported in the `mili.style` module)

- `mili.CENTER`: Centers text, anchoring and aligment

- `mili.X`: Expands to `{"axis": "x"}`

- `mili.PADLESS`: Sets padding to zero on both axis

- `mili.RESIZE`: Sets resizing to true on both axis

- `mili.FILL`: Sets filling to true on both axis

- `mili.FLOATING`: Styles to ignore the parent and have the stack as parent

- `mili.style.color(color)`: Returns `{"color": color}` (useful for quick shape styles)

- `mili.style.outline(color, size=1)`: Returns `{"color": color, "outline": size, "draw_above": True}` (quickly add outlines)

- `mili.style.filter()` will help you select the style names you want using a whitelist and a blacklist

- `mili.style.same()` creates a dictionary with the same value for different style names

- `mili.style.conditional()` will use the base style and expand it with the hover and press style based on the interaction status and selection status

- `mili.style.cond_value()` same as `conditional` but works for any value and not only dictionaries with an additional option to repeat the value in a tuple.

- `mili.style.Style` will help you cache common styles. you can retrieve them with `get(type)` or use the shortcuts like `get_rect()`

- `mili.style.StyleStatus` will help you cache styles for different interactions, using `mili.style.Style` objects for base, hover and press statuses that you can retrieve with the `get(type, interaction)` or use the shortcuts like `get_rect(interaction)` (similar to `mili.style.conditional()`)

- `mili.style.DefaultStyle`: A context manager object that applies the default styles only within its context, reverting the previous style when exiting, for example:
  ```py
  my_mili.rect() # rect is black
  with mili.style.DefaultStyle(rect=mili.style.color("white")):
    my_mili.rect() # rect is white
  my_mili.rect() # rect is black
  # this class should be used with more complex styles
  ```

Keep in mind that you can merge styles using the pipe operator, for example `mili.CENTER | mili.PADLESS`
