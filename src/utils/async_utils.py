import asyncio

try:
    from qasync import QEventLoop, asyncSlot
    HAS_QASYNC = True
except ImportError:
    HAS_QASYNC = False
    # Fallback decorator when qasync is not available
    def asyncSlot():
        def decorator(func):
            def wrapper(*args, **kwargs):
                return asyncio.create_task(func(*args, **kwargs))
            return wrapper
        return decorator
