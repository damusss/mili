[<- BACK](https://github.com/damusss/mili/blob/main/guide/guide.md)

## MILI Errors

MILI can raise the following errors found in the `mili.error` module:

- `MILIError`: Base class for MILI errors
- `MILIValueError`: Inherits from `ValueError` aswell, raised when an invalid value is passed
- `MILIIncompatibleStylesError`: Raised when incompatible styles are both defined for an element
- `MILIStatusError`: Raised when an action is invalidated from another action (i.e. if you don't call `MILI.start`)

## MILI Typehints

In the `mili.typing` module you can find many type aliases useful for typehints:

- `SmartNumber`/`SmartNumberOrPercentage`: Used to represent an int, float, or a percentage string/smart number string.
- `BoundingAlignLike`: The possible aligment values that can be used with rects, circles and text (check the style guide for more details).
- `PointsLike`, `AnimValueLike`, `EasingLike`: Represents allowed types for common values.
- `ComponentProtocol`: Defines methods a custom component object must implement and must match the signature of.
- `IconLike`: A value that is interpreted as an icon. It can be:
    - A `Surface` (used as-is)
    - A string: Assumed to be a google icon
    - A callable that returns a `Surface`: Can be custom or created with the `mili.icon.lazy` and `mili.icon.lazy_colored` functions.

The rest of the typehints are the style dicts allowed by the various components and utilities. They are type hinted as typed dicts but are regular dictionaries at runtime.
