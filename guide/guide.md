# MILI Guide

MILI is a lightweight immediate mode user interface library. This means that UI elements are created during the game loop and feedback is immediate (it actually has one frame of delay).

The library version can be accessed using `VERSION` or `VERSION_STR`.

The core features of MILI can be found in the MILI object along with the data classes:

## [MILI Class](https://github.com/damusss/mili/blob/main/guide/mili.md)

## [MILI Interaction Data](https://github.com/damusss/mili/blob/main/guide/data.md)

To learn about the styles to use with elements and components, read the style guide:

## [MILI Style](https://github.com/damusss/mili/blob/main/guide/style.md)

MILI also provides useful utilities to manage elements and animations:

## [MILI Utilities](https://github.com/damusss/mili/blob/main/guide/utility.md)

## [MILI Animation](https://github.com/damusss/mili/blob/main/guide/animation.md)

Finally, there are common errors and typehints:

## [MILI Errors and Typehints](https://github.com/damusss/mili/blob/main/guide/extra.md)

# Immediate Mode

Subjective preference is excluded from the comparison.

## Pros

-   More control, more flexible structure
-   Interaction is immediate bypassing callbacks and events
-   UI layout can seemelessly change between frames
-   Quickly change styles, layout and parenting without rebuilding
-   Element prefabs can be made with mere functions
-   Easily make conditional layouts with more logic between elements
-   UI layout runs on functions and is easier to follow and organize
-   Easier implementation of animations
-   Highly responsive to changes

## Cons (against OO UI)

-   Less access to some internal mechanics
-   Less freedom to override internal mechanics
-   While possible, caching is harder and requires user-made long living objects
-   Higher number of repetitive checks and calls
-   Higher number of objects created
-   Generally less performant for stable and very large layouts
