from typing import Any  # noqa
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal


class Command(BaseModel):
    name: "str" = Field(..., alias="name")
    description: "Optional[str]" = Field(None, alias="description")
    arguments: "Optional[List[CommandArgument]]" = Field(None, alias="arguments")


class CommandArgument(BaseModel):
    name: "str" = Field(..., alias="name")
    is_optional: "Optional[bool]" = Field(None, alias="is_optional")
    description: "Optional[str]" = Field(None, alias="description")


class GetModulesResponse(BaseModel):
    modules: "Dict[str, Module]" = Field(..., alias="modules")


class HTTPValidationError(BaseModel):
    detail: "Optional[List[ValidationError]]" = Field(None, alias="detail")


class Module(BaseModel):
    name: "str" = Field(..., alias="name")
    description: "Optional[str]" = Field(None, alias="description")
    url: "str" = Field(..., alias="url")
    commands: "Dict[str, Command]" = Field(..., alias="commands")
    actions: "Optional[List[str]]" = Field(None, alias="actions")


class SlackRequest(BaseModel):
    method: "Literal['admin_apps_approve', 'admin_apps_requests_list', 'admin_apps_restrict', 'admin_inviteRequests_approve', 'admin_inviteRequests_approved_list', 'admin_inviteRequests_denied_list', 'admin_inviteRequests_deny', 'admin_inviteRequests_list', 'admin_teams_admins_list', 'admin_teams_create', 'admin_teams_list', 'admin_teams_owners_list', 'admin_teams_settings_setDescription', 'admin_teams_settings_setIcon', 'admin_teams_settings_setName', 'admin_users_assign', 'admin_users_invite', 'admin_users_remove', 'admin_users_session_reset', 'admin_users_setAdmin', 'admin_users_setOwner', 'admin_users_setRegular', 'api_test', 'auth_revoke', 'auth_test', 'bots_info', 'channels_archive', 'channels_create', 'channels_history', 'channels_info', 'channels_invite', 'channels_join', 'channels_kick', 'channels_leave', 'channels_list', 'channels_mark', 'channels_rename', 'channels_replies', 'channels_setPurpose', 'channels_setTopic', 'channels_unarchive', 'chat_delete', 'chat_deleteScheduledMessage', 'chat_getPermalink', 'chat_meMessage', 'chat_postEphemeral', 'chat_postMessage', 'chat_scheduleMessage', 'chat_scheduledMessages_list', 'chat_unfurl', 'chat_update', 'conversations_archive', 'conversations_close', 'conversations_create', 'conversations_history', 'conversations_info', 'conversations_invite', 'conversations_join', 'conversations_kick', 'conversations_leave', 'conversations_list', 'conversations_members', 'conversations_open', 'conversations_rename', 'conversations_replies', 'conversations_setPurpose', 'conversations_setTopic', 'conversations_unarchive', 'dialog_open', 'dnd_endDnd', 'dnd_endSnooze', 'dnd_info', 'dnd_setSnooze', 'dnd_teamInfo', 'emoji_list', 'files_comments_delete', 'files_delete', 'files_info', 'files_list', 'files_remote_add', 'files_remote_info', 'files_remote_list', 'files_remote_remove', 'files_remote_share', 'files_remote_update', 'files_revokePublicURL', 'files_sharedPublicURL', 'files_upload', 'groups_archive', 'groups_create', 'groups_createChild', 'groups_history', 'groups_info', 'groups_invite', 'groups_kick', 'groups_leave', 'groups_list', 'groups_mark', 'groups_open', 'groups_rename', 'groups_replies', 'groups_setPurpose', 'groups_setTopic', 'groups_unarchive', 'im_close', 'im_history', 'im_list', 'im_mark', 'im_open', 'im_replies', 'migration_exchange', 'mpim_close', 'mpim_history', 'mpim_list', 'mpim_mark', 'mpim_open', 'mpim_replies', 'oauth_access', 'oauth_v2_access', 'pins_add', 'pins_list', 'pins_remove', 'reactions_add', 'reactions_get', 'reactions_list', 'reactions_remove', 'reminders_add', 'reminders_complete', 'reminders_delete', 'reminders_info', 'reminders_list', 'rtm_connect', 'rtm_start', 'search_all', 'search_files', 'search_messages', 'stars_add', 'stars_list', 'stars_remove', 'team_accessLogs', 'team_billableInfo', 'team_info', 'team_integrationLogs', 'team_profile_get', 'usergroups_create', 'usergroups_disable', 'usergroups_enable', 'usergroups_list', 'usergroups_update', 'usergroups_users_list', 'usergroups_users_update', 'users_conversations', 'users_deletePhoto', 'users_getPresence', 'users_identity', 'users_info', 'users_list', 'users_lookupByEmail', 'users_profile_get', 'users_profile_set', 'users_setPhoto', 'users_setPresence', 'views_open', 'views_publish', 'views_push', 'views_update']" = Field(
        ..., alias="method"
    )
    payload: "Any" = Field(..., alias="payload")


class SlackResponse(BaseModel):
    data: "Any" = Field(..., alias="data")


class ValidationError(BaseModel):
    loc: "List[str]" = Field(..., alias="loc")
    msg: "str" = Field(..., alias="msg")
    type: "str" = Field(..., alias="type")
