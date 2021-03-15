import warnings
import functools


def deprecated(reason: str, version: str, last: str):
    """
    Used to mark API as deprecated
    The reason of deprecation should be specified:
        - if there is an alternative, this is a reason enough
        - otherwise, the reason can be empty
    It holds the version it was deprecated on, and the version it will no longer be available

    Automatic testing should verify that it doesn't exist on version that it shouldn't exist
    """

    # TODO: throw exception if current version > last

    def deprecated_decorator(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            warnings.warn(f"deprecated since {version}: {reason}", category=DeprecationWarning)
            return func(*args, **kwargs)

        return func_wrapper

    return deprecated_decorator
