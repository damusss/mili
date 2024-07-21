[<- BACK](guide.md)

# MILI Animation Guide

The `mili.animation` module contains classes to simplify animations. Animations are not directly connected to elements, but you can use the values in the styles.

# `Animator`

This is the object that actually calculates the new value from the start and the end value. The start and end value must be of the same protocol. You can either animate numbers, colors (only pygame.Color objects supported) or sequences of numbers like `(0, 1, 2, 3)`. You can start and stop the animation with the appropriate methods, but the value will only update if you call the update method. The finish callback is called when the animation stops naturally.

To update all existing animators at once, you can use the `mili.animation.update_all` function.

# Easings

An easing is a function that changes how the value changes over time. An easing-like object must be a callable that accepts a float number in the range 0-1 and returns another float in the range 0-1. The default easing is linear, meaning the input is left unchanged. There are many builtin easings in the animation module, named `mili.animation.Ease_X`. Those are classes, so remember to call them to create an instance. Some of the easings also take an optional argument `n` which is a power used in the calculation (to make it quadratic, cubic, quartic etc.)

# `ABAnimation`

The `ABAnimation` object is a wrapper for the `Animator` object to easily control an animation from value A to value B. You can use the `goto_a`, `goto_b` and `flip_direction` methods to manage the animation flow. Some methods and properties are added as a shortcut to the animator instance. Note that `update_all` will also update this objects.
