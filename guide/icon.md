[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

# MILI Icon Guide

The `mili.icon` module contains functions to easily manage icons, svg icons and google icons.

## `mili.icon.setup`

With this function you setup default arguments for using icons. The customizable settings are the following:

-   `path`: the folder that contains the icons and where to (optionally) save google icons.
-   `color`: the color of the icon surface. If None, the icon's original color will not be changed.
-   `source_color`: the color that the original icon has for opaque pixels. Can be either white or black. This will change how the surface color is applied.
-   `svg_size`: the size that the surfaces loaded from svgs (including google ones) will have. higher values will have an higher resolution.
-   `google_cache`: wether to save the downloaded google icons to the path for faster next loads or not.
-   `file_type`: the extension type of file icons (defaults/recommended is png) excluding svgs.

## File Icons

Using `mili.icon.get`, `mili.icon.get_svg` and `mili.icon.preload` will work with icons that are already existing as files. The icon name must be the name of the file. You can customize the output color and weather to load it asyncronously (in that case a dummy surface will be returned until it is loaded). `mili.icon.get_svg` is a shortcut for `mili.icon.get` with svg set to True. `mili.icon.preload` will load/start loading a batch of icons at the same time.

## Google Icons

The icon module allows support to use google icons by using a very simple google API to download them and (optionally) caching them. Both `mili.icon.get_google` and `mili.icon.preload_google` work similarly with their file counterparts but will occasionally make requests with urllib to fetch the icon data. Note that the API cannot use the latest google icons versions, so the downloaded ones might be different or they might be missing entirely. The `cache` argument can override the default setting. Support for more icon APIs might come in the future.
