from functools import wraps
from input import PENDING, RUNNING, DONE, FAILED


class FunctionAlreadyTested(ValueError):
    pass


def require_data(*attrs):
    """call the needed data loaders"""
    def wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            for attr in attrs:
                if getattr(self, attr, None) is None:
                    loader = getattr(self, f"load_{attr}", None)
                    if loader is None:
                        raise AttributeError(f'{self.__class__} has no attribute {attr}')
                    loader()
            return func(self, *args, **kwargs)
        return inner
    return wrapper


def log_function(func):
    """log success if the function does not return an error, otherwise fail"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            print(f'{func.__name__} success')
            return result
        except FunctionAlreadyTested:
            print(f'{func.__name__} already tested')
        except Exception:
            print(f'{func.__name__} failed')
            raise
    return wrapper


@log_function
def toto():
    print("Hello world")


def test_dependency(*parents):
    """Handle dependency between tested functions, call the dependency function if needed"""
    def wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            if not hasattr(self, "_test_status"):
                self._test_status = {}

            status = self._test_status.get(func.__name__)
            if status == DONE:
                raise FunctionAlreadyTested
            if status == RUNNING:
                raise ValueError(f"Circular dependency detected for {func.__name__}")
            if status == FAILED:
                raise ValueError(f"failed detected in {func.__name__}")
            self._test_status[func.__name__] = RUNNING
            try:
                for parent_name in parents:
                    if self._test_status.get(parent_name) == DONE:
                        continue
                    parent = getattr(self, parent_name, None)
                    if parent is None or not callable(parent):
                        raise AttributeError(f'{self.__class__} has no method {parent_name}')
                    parent()
                    if self._test_status.get(parent_name) == PENDING:
                        self._test_status[parent_name] = DONE
                    if self._test_status.get(parent_name) == FAILED:
                        self._test_status[func.__name__] = FAILED
                        return
                result = func(self, *args, **kwargs)
                self._test_status[func.__name__] = DONE
            except FunctionAlreadyTested:
                raise
            except Exception:
                self._test_status[func.__name__] = FAILED
                raise
            return result
        return inner
    return wrapper
