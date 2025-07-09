__all__ = (
    "MILIError",
    "MILIIncompatibleStylesError",
    "MILIStatusError",
    "MILIValueError",
)


class MILIError(RuntimeError): ...


class MILIIncompatibleStylesError(MILIError): ...


class MILIStatusError(MILIError): ...


class MILIValueError(MILIError, ValueError): ...


class MILIBackendUnsupportedOperation(MILIError):...
