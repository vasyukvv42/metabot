import logging
from typing import Dict, Optional, List

from metabot.lib.models import Module

log = logging.getLogger(__name__)

MODULES: Dict[str, Module] = {}


def add_module(module: Module) -> None:
    if module.name in MODULES:
        log.info(f'Replacing module "{module.name}" with {module}')
    else:
        log.info(f'Adding new module {module}')

    MODULES[module.name] = module


def get_module(module_name: str) -> Optional[Module]:
    return MODULES.get(module_name)


def get_all_modules() -> Dict[str, Module]:
    return MODULES


def get_module_names() -> List[str]:
    return list(MODULES.keys())
