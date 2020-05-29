from fastapi_metabot.module import Module


# noinspection PyProtectedMember
def test_smoke(module: Module) -> None:
    assert len(module._commands) > 0
    assert len(module._actions) > 0
    assert len(module._views) > 0


def test_smoke_announce_script() -> None:
    from vacations.scripts import announce  # noqa F401


def test_smoke_increment_script() -> None:
    from vacations.scripts import increment_leaves  # noqa F401
