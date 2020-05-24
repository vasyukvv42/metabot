from fastapi_metabot.module import Module


# noinspection PyProtectedMember
def test_smoke(module: Module) -> None:
    assert len(module._commands) > 0
    assert len(module._actions) > 0
    assert len(module._views) > 0
