[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

## MILI Errors

MILI can raise the following errors found in the `mili.error` module:

- `MILIError`: Base class for MILI errors
- `MILIValueError`: Inherits from `ValueError` aswell, raised when an invalid value is passed
- `MILIIncompatibleStylesError`: Raised when incompatible styles are both defined for an element
- `MILIStatusError`: Raised when an action is invalidated from another action (i.e. if you don't call `MILI.start`)

## MILI Typehints

In the `mili.typing` module you can find many type aliases useful for typehints:

- `NumberOrPercentage`: Used to represent an int, float, or a percentage string.
- `BoundingAlignLike`: The possible aligment values that can be used with rects, circles and text (check the style guide for more details).
- `RectLike`, `ColorLike`: Represents valid rectangles and colors supported by pygame.
- `PointsLike`, `AnimValueLike`, `EasingLike`: Represents allowed types for common values.
- `X_StyleLike`: A typed dictionary (a normal dictionary at runtime) containing the allowed keys and types for each style, useful for autocompletion.
- `ComponentProtocol`: Defines methods a custom component object must implement and must match the signature of.
