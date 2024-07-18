# MILI General Guide

MILI is an immediate mode user interface library. This means that you don't have to create objects beforehands, you just need to call some functions in the gameloop and you will have immediate feedback. The other kind of libraries are probably slightly more performant, but it's still very fast. In reality, the interaction respons happen with one frame of delay, which can't be noticed unless the framerate is incredibly low. You can find a guide about the styling in [this](mili/style.md) page, so this one won't cover them.

Unlike most user interface libraries, mili has no prefabricated elements, rather it focuses on a barebone structure that will require a few more lines for basic elements but will allow for any kind of customization.

In MILI, like you would expect, the elements that are created later (that automatically increases their z index) have priority of interaction. When you create a MILI instance, you need to provide to it the surface it can draw on (you can change it later) and at the start of the gameloop you need to call the `start` function (a special version of the element function) and to update and draw the elements you need the `update_draw` function.

MILI revolves around elements. Elements hold information like their parent, a relative rect, their z index (how much they are at the front) and their children. Elements on their own have no associated graphics, and only exist to provide a box for interaction and to organize children.

To create an element you need to call the `element` function (the rect position is relative to the parent). If you want to create a parent instead, you must use the `begin` function (you can create any other elements or parents after it) and to annotate the parent has ended, call the `end` function or use begin on a context manager with the `with` keyword.

The element and begin function can either return an `Interaction` instance or an `ElementData` instance depending on the `get_data` parameter. The first contains interaction information such as the hover status or press status, while the element data holds more information like the rect, the parent and so on.

Parent elements organize their children by default. To know about all kinds of customization, check the [style guide](mili/style.md).

To give life to elements and add graphics to it, you have to use the components. You can access those with their respective functions such as `rect` and `text`. When you call such functions, the components are going to be attached to the most recently created element.

Remember that the components are always drawn before the children. If you want a component do act differently, you should attach it to a children of the same size as the parent that with the styles `ignore_grid` True and `blocking` False (for example an outline).

The MILI object has a few other utility functions and properties. For ease of coding, each built in component has a corrisponding element version (such as `text_element`), where an element with a single component of said type is created.

The `ImageCache` object is highly suggested to increase performance of image components. Since it's immediate mode, the component can't cache the output automatically, rather it needs an object provided by the user.
To make the cache process easier, you can preallocate a set amount of caches with the `ImageCache.preallocate_caches` function and every time you need an unique cache you can use the `ImageCache.get_next_cache` function. The index is reset when `start` is called.

All errors raised by MILI are found in the `mili.error` submodule.

There are a few utility functions such as `percentage`, `gray`, and `indent` but mainly a few utility classes:

- `Selectable`: Manages the behaviour of a checkbox. You can also provide a list of selectables which will force only one checkbox to be active at any time. You should call the `update` function after you called the element or begin function passing to it its result value.
- `Dragger`: Automatically manages mouse dragging. You can lock some axis and you can clamp the position. You should call the `update` function after you called the element or begin function passing to it its result value.
- `Scroll`: Keeps track of the scroll offset for a container and automatically clamps it. This is done for every axis. You should call the `update` function after you created the container element, passing its element data to it (note: you have to strictly pass an `ElementData` object, meaning `get_data` must be set to True). To see the scroll, pass the result of `get_offset` to the children you want to be scrolled. It also has a few utility functions used for scrollbars, see below.
- `Scrollbar`: An extension of the scroll functionality to represent a scrollbar, one axis per object. It must be connected to an existing and independent `Scroll` object. When you manually scroll the scroll object you must call `scroll_moved`. You should call `update` after you create your container element (you should call `Scroll.update` and `Scrollbar.update` in the same place) and you should call `update_handle` after you create your handle element. You must create the scrollbar and handle elements yourself, but you can use the `bar_rect` and `handle_rect` attributes to make the process easier. The handle element must be a children of the scrollbar. Don't forget to set the `ignore_grid` style to True for both.

If you plan on adding more graphics option that means more component, you can do that. You need to create an object that implements the `added` (called when the component is added) and `draw` (called to draw the component) methods (check the signature in `mili.typing.ComponentProtocol`) and pass it to the `mili.register_custom_component` function along with the name. You'll then be able to call `custom_component` on a MILI instance and your custom methods will be called. On an important note, the first argument of said method is an undocumented object intended to be internal, so finding exactly what you need won't be super easy, but you can experiment with it.
