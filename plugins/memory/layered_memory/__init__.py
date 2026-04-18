from .provider import LayeredMemoryProvider


def register(ctx):
    ctx.register_memory_provider(LayeredMemoryProvider())


__all__ = ["LayeredMemoryProvider"]
