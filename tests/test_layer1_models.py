"""Layer 1: Models coverage — verify domain enums are importable and correct."""
from kaiten_mcp.models import (
    CardCondition,
    CardState,
    ColumnType,
    CardUserType,
    CommentType,
    TextFormatType,
    CardSource,
    CustomPropertyType,
    FileType,
)


class TestCardCondition:
    def test_values(self):
        assert CardCondition.ACTIVE == 1
        assert CardCondition.ARCHIVED == 2
        assert CardCondition.DELETED == 3


class TestCardState:
    def test_values(self):
        assert CardState.QUEUED == 1
        assert CardState.IN_PROGRESS == 2
        assert CardState.DONE == 3


class TestColumnType:
    def test_values(self):
        assert ColumnType.QUEUE == 1
        assert ColumnType.IN_PROGRESS == 2
        assert ColumnType.DONE == 3


class TestCardUserType:
    def test_values(self):
        assert CardUserType.MEMBER == 1
        assert CardUserType.RESPONSIBLE == 2


class TestCommentType:
    def test_values(self):
        assert CommentType.MARKDOWN == 1
        assert CommentType.HTML == 2


class TestTextFormatType:
    def test_values(self):
        assert TextFormatType.MARKDOWN == 1
        assert TextFormatType.HTML == 2
        assert TextFormatType.JIRA_WIKI == 3


class TestCardSource:
    def test_values(self):
        assert CardSource.APP == "app"
        assert CardSource.API == "api"
        assert CardSource.EMAIL == "email"
        assert CardSource.TELEGRAM == "telegram"
        assert CardSource.SLACK == "slack"
        assert CardSource.WEBHOOK == "webhook"
        assert CardSource.IMPORT == "import"
        assert CardSource.SCHEDULE == "schedule"
        assert CardSource.AUTOMATION == "automation"


class TestCustomPropertyType:
    def test_values(self):
        assert CustomPropertyType.STRING == "string"
        assert CustomPropertyType.NUMBER == "number"
        assert CustomPropertyType.DATE == "date"
        assert CustomPropertyType.EMAIL == "email"
        assert CustomPropertyType.CHECKBOX == "checkbox"
        assert CustomPropertyType.SELECT == "select"
        assert CustomPropertyType.FORMULA == "formula"
        assert CustomPropertyType.URL == "url"
        assert CustomPropertyType.COLLECTIVE_SCORE == "collective_score"
        assert CustomPropertyType.VOTE == "vote"
        assert CustomPropertyType.COLLECTIVE_VOTE == "collective_vote"
        assert CustomPropertyType.CATALOG == "catalog"
        assert CustomPropertyType.PHONE == "phone"
        assert CustomPropertyType.USER == "user"
        assert CustomPropertyType.ATTACHMENT == "attachment"


class TestFileType:
    def test_values(self):
        assert FileType.ATTACHMENT == 1
        assert FileType.GOOGLE_DRIVE == 2
        assert FileType.DROPBOX == 3
        assert FileType.BOX == 4
        assert FileType.ONE_DRIVE == 5
        assert FileType.YANDEX_DISK == 6
        assert FileType.COMMENT_EMAIL == 7
        assert FileType.COMMENT_ATTACHMENT == 8
        assert FileType.VIDEO_WITH_TRANSCRIPTION == 9
        assert FileType.VOICE_WITH_TRANSCRIPTION == 10
