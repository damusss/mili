[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

# MILI Interaction Data Guide

The `mili.data` submodule contains 4 classes that represent data.

# `Interaction`

The interaction object is returned by all elements by default. It contains all information you can need to understand how the user is interacting with the element:

-   `Interaction.data`: The `ElementData` object holding more detailed information about the element.
-   `Interaction.parent`: The `Interaction` object returned by the parent of this one.
-   `Interaction.hovered`: The user pointer is over this element which is also the highest element.
-   `Interaction.absolute_hover`: The user pointer is over this element but other elements might be covering it.
-   `Interaction.just_hovered`: The hovered status becomes True this frame meaning the user has started hovering
-   `Interaction.just_unhovered`: The hovered status becomes False this frame meaning the user pointer left the element
-   `Interaction.press_button`: The button the user is clicking on this element. If the pointer leaves the element while being held, this will keep being set until the pointer releases. -1 means no button is pressed.
-   `Interaction.just_pressed_button`: Same as `press_button` but is only set the first frame it happens.
-   `Interaction.just_released_button`: Same as `press_button` but is only set the last frame it happens. Corresponds to the "click" event.

There are also some shortcuts for the left, right, middle mouse buttons (most common): `left_pressed`, `left_just_pressed`, `left_just_released`, `right_pressed`, `right_just_pressed`, `right_just_released`, `middle_pressed`, `middle_just_pressed`, `middle_just_released`.
The `*_just_released` properties are also exported as `*_clicked` as it is more intuitive.

# `ElementData`

The element data object holds more information than the interaction and since it's slower to compute it will be evaluated lazily. It keeps the ID, the relative rect, the absolute rect, the z index, the style, the components, the parent ID and the children IDs. Changing any field will not effect the element.

The `grid` attribute contains information about its parental behaviour such as the overflow, the padding, and the spacing (needed for scrolling) which are contained in the `ElementGridData` object, only accessible using the `mili.data` module (the others are exported to the `mili` package)

The attributes might not be accurate every frame and might have some delay.

# `ImageCache`

This object is incredibly useful to massively speed up the image component. Since MILI is immediate mode, after the surface is modified using the styles it cannot be cached. This object, passed in the cache style, provides a permanent location the result can be stored in. Using `get_output`, it's also the only way to retrieve the processed image (might be None in the first iterations).

You can also simplify the cache creation process by making MILI automatically allocate image caches when they are needed and store them automatically to reuse them. So instead of creating the instances yourself you can call `mili.ImageCache.get_next_cache()` and pass it as the image cache style or pass the cache style as `"auto"` and MILI will immediately call it automatically. If not enough caches exist MILI will allocate a new one.

Example usage:

```py
my_special_cache = mili.ImageCache()

def ui():
    my_mili.image_element(special_surface, {"cache": my_special_cache}, rect)

    for i in range(30):
        my_mili.image_element(surface, {"cache": mili.ImageCache.get_next_cache()}, rect)
        my_mili.image_element(other_surface, {"cache": "auto"}, rect) # this is the same thing
```

# `TextCache`

This object works the same way of `ImageCache` by caching the rendered text while nothing changes to speed it up. The performance benefit isn't as great as the image one but might be worth it for large amount of text. Just like the other object it must be stored permanently (creating a new one every frame won't cache anything). You can also use `mili.TextCache.get_next_cache()` and pass it as the text cache style or pass the cache style as `"auto"` and MILI will immediately call it automatically. If not enough caches exist MILI will allocate a new one.

Example usage:

```py
my_special_cache = mili.TextCache()

def ui():
    my_mili.text_element(special_text, {"cache": my_special_cache}, rect)

    for i in range(300):
        my_mili.text_element(text, {"cache": mili.TextCache.get_next_cache()}, rect)
        my_mili.text_element(other_text, {"cache": "auto"}, rect) # this is the same thing
```

# `ImageLayerCache`

This object is an highly specialized optimization tool for image rendering. It finds a purpose whenever the UI application has to render a large number of images that are on the same UI Z layer (for example, a grid of cards, a list of icons, etc). Normally every frame a draw call is performed for every one of those images, and the repetitiveness of the operation can impact performance. This object will cache images and their position and draw them to an intermediate surface (refreshed whenever something changes) which is then drawn on the canva. The object also supports a size and an offset. To use the object you must create and store an instance of it, and assign the instance to the `layer_cache` style of the image components you want to apply the layer to. The same image components must also be provided a valid `ImageCache` object (otherwise an exception is raised). As stated before the images sharing an image layer will be drawn at the same z index. By default every image layer cache is automatically drawn after every element. If you wish to draw it between elements (avoiding overlappings) you must use the component `MILI.image_layer_renderer` passing the `ImageLayerCache` instance to it after the element after which the layer should be rendered.

Example usage:

```py
mili.ImageCache.preallocate_caches(...)
layer_cache = mili.ImageLayerCache(my_mili, window.size)

# UI loop

for image in ...:
    my_mili.element(...)
    my_mili.image(surface, {"cache": mili.ImageCache.get_next_cache(), "layer_cache": layer_cache}) # this image will be cached and rendered by the layer among the other images

my_mili.element(..., {"image_layer_cache": layer_cache}) # the layer will render all of the images after this element and before the next elements

my_mili.element(...)
my_mili.element(...)
...
```

# `ParentCache`

This is a delicate object that can improve performance of some UI layouts. Usually every frame every elements starts with no children, and they are added to lists when they are created. This allows for 100% flexibility but isn't the fastest methods. If you know the children of your parent will not change, you should pass a permanent `mili.ParentCache` object as the `cache` element style (creating it every frame will have the opposite result).

The cache can be either static or not. The only thing that they share is that the number of elements MUST stay the same while the cache is active. If you know that the layout of the parent will change, you should call `mili.ParentCache.refresh` so that the cache will be updated. Not doing so will likely cause unexpected errors.

## Static Cache

If the cache is static, it means nothing inside the parent can change. Components won't be updated, the style of the children won't be updated and the children won't have any interaction, so accessing any field of the returned `Interaction` object is useless and will error if accessing the `data` property. For this reason if the cache is active it is pointless to create the children - you should not do so, and you can check wether you should create them with the `MILI.cache_should_create_children` method, like so:

```py
cache = mili.ParentCache(True) # NOT every frame
with my_mili.begin(..., {..., "cache": cache}):
    if my_mili.cache_should_create_children():
        # create the children
        ...
```

## Non-static Cache

If the cache is not static, the parent will inherit the previous data of the children, but:

-   Children will receive interactions, meaning the `Interaction` object wil be up to date
-   The style of the children can change (for example the offset)
-   The children can have different/updated components.
    For this reasons you should always create the children for non-static caches, and there will still be performance improvements.
