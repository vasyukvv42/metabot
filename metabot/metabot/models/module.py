from typing import Optional, List, Dict

from pydantic import BaseModel, Field, validator, AnyHttpUrl

SAMPLE_MODULE = {
    'name': 'help',
    'description': 'Help module',
    'url': 'http://help-module:8000',
    'commands': {
        'me': {
            'name': 'me',
            'description': 'Get help',
            'arguments': [
                {
                    'name': 'module_name',
                    'is_optional': True,
                    'description': 'Module name'
                }
            ]
        }
    },
    'actions': [],
}


class CommandArgument(BaseModel):
    name: str = Field(regex=r'[\w\d]+', min_length=1, max_length=255)
    is_optional: bool = False
    description: Optional[str]


class Command(BaseModel):
    name: str = Field(regex=r'[\w\d]*', max_length=255)
    description: Optional[str]
    arguments: List[CommandArgument] = Field(default_factory=list)

    @validator('arguments')
    def no_required_args_after_optional(
            cls,  # noqa
            v: List[CommandArgument],
    ) -> List[CommandArgument]:
        has_optional = False
        for arg in v:
            if has_optional and not arg.is_optional:
                raise ValueError('Required argument follows optional argument')

            has_optional = has_optional or arg.is_optional
        return v


class Module(BaseModel):
    name: str = Field(regex=r'[\w\d]+', min_length=1, max_length=255)
    description: Optional[str]
    url: AnyHttpUrl

    commands: Dict[str, Command]
    actions: List[str] = Field(default_factory=list)

    @validator('commands')
    def command_names_match(
            cls,  # noqa
            v: Dict[str, Command],
    ) -> Dict[str, Command]:
        if not all(key == command.name for key, command in v.items()):
            raise ValueError('Keys and command names must match')
        return v

    class Config:
        schema_extra = {
            'example': SAMPLE_MODULE
        }
