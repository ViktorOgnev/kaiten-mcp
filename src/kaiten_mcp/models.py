"""Kaiten domain constants and enums extracted from kaiten-lib source."""
from enum import IntEnum, Enum


class CardCondition(IntEnum):
    ACTIVE = 1
    ARCHIVED = 2
    DELETED = 3


class CardState(IntEnum):
    QUEUED = 1
    IN_PROGRESS = 2
    DONE = 3


class ColumnType(IntEnum):
    QUEUE = 1
    IN_PROGRESS = 2
    DONE = 3


class CardUserType(IntEnum):
    MEMBER = 1
    RESPONSIBLE = 2


class CommentType(IntEnum):
    MARKDOWN = 1
    HTML = 2


class TextFormatType(IntEnum):
    MARKDOWN = 1
    HTML = 2
    JIRA_WIKI = 3


class CardSource(str, Enum):
    APP = "app"
    API = "api"
    EMAIL = "email"
    TELEGRAM = "telegram"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IMPORT = "import"
    SCHEDULE = "schedule"
    AUTOMATION = "automation"


class CustomPropertyType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"
    CHECKBOX = "checkbox"
    SELECT = "select"
    FORMULA = "formula"
    URL = "url"
    COLLECTIVE_SCORE = "collective_score"
    VOTE = "vote"
    COLLECTIVE_VOTE = "collective_vote"
    CATALOG = "catalog"
    PHONE = "phone"
    USER = "user"
    ATTACHMENT = "attachment"


class FileType(IntEnum):
    ATTACHMENT = 1
    GOOGLE_DRIVE = 2
    DROPBOX = 3
    BOX = 4
    ONE_DRIVE = 5
    YANDEX_DISK = 6
    COMMENT_EMAIL = 7
    COMMENT_ATTACHMENT = 8
    VIDEO_WITH_TRANSCRIPTION = 9
    VOICE_WITH_TRANSCRIPTION = 10
