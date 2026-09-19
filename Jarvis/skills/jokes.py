import pyjokes


def tell_joke(_: str) -> tuple[str, str, str | None]:
    return pyjokes.get_joke(), "speak", None
