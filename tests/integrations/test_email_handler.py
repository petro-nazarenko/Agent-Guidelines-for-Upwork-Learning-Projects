"""Tests for email handler."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.integrations.email_handler import (
    Email,
    EmailClient,
    EmailConfig,
    ReceivedEmail,
)


class TestEmailConfig:
    """Tests for email configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = EmailConfig()
        assert config.smtp_host == "smtp.gmail.com"
        assert config.smtp_port == 587
        assert config.imap_host == "imap.gmail.com"
        assert config.imap_port == 993

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = EmailConfig(
            smtp_host="smtp.custom.com",
            smtp_port=465,
            smtp_user="test@test.com",
            smtp_password="secret",
        )
        assert config.smtp_host == "smtp.custom.com"
        assert config.smtp_port == 465
        assert config.smtp_user == "test@test.com"


class TestEmail:
    """Tests for email dataclass."""

    def test_email_creation(self) -> None:
        """Test creating an email."""
        email_msg = Email(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="Test body",
        )
        assert email_msg.to == ["recipient@example.com"]
        assert email_msg.subject == "Test Subject"
        assert email_msg.body == "Test body"
        assert email_msg.cc == []
        assert email_msg.bcc == []
        assert email_msg.attachments == []
        assert email_msg.html is False


class TestReceivedEmail:
    """Tests for received email dataclass."""

    def test_received_email_creation(self) -> None:
        """Test creating a received email."""
        email = ReceivedEmail(
            uid=123,
            subject="Test",
            from_address="sender@example.com",
            to=["recipient@example.com"],
            date=datetime.now(),
            body="Body",
        )
        assert email.uid == 123
        assert email.from_address == "sender@example.com"
        assert email.attachments == []
        assert email.flags == []


class TestEmailClient:
    """Tests for email client."""

    @pytest.fixture
    def config(self) -> EmailConfig:
        """Create test configuration."""
        return EmailConfig(
            smtp_user="test@gmail.com",
            smtp_password="test_password",
            imap_user="test@gmail.com",
            imap_password="test_password",
        )

    @pytest.fixture
    def client(self, config: EmailConfig) -> EmailClient:
        """Create test client."""
        return EmailClient(config=config)

    def test_service_name(self, client: EmailClient) -> None:
        """Test service name property."""
        assert client.service_name == "email"

    def test_initial_state(self, client: EmailClient) -> None:
        """Test initial client state."""
        assert client._connected is False
        assert client._smtp is None
        assert client._imap is None

    @patch("src.integrations.email_handler.smtplib.SMTP")
    def test_connect_smtp(self, mock_smtp_class: MagicMock, client: EmailClient) -> None:
        """Test connecting to SMTP."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp

        client.connect_smtp()

        assert client._smtp is mock_smtp
        mock_smtp.ehlo.assert_called()
        mock_smtp.starttls.assert_called()
        mock_smtp.login.assert_called()

    @patch("src.integrations.email_handler.imapclient.IMAPClient")
    def test_connect_imap(self, mock_imap_class: MagicMock, client: EmailClient) -> None:
        """Test connecting to IMAP."""
        mock_imap = MagicMock()
        mock_imap_class.return_value = mock_imap

        client.connect_imap()

        assert client._imap is mock_imap
        mock_imap.start_tls.assert_called()
        mock_imap.login.assert_called()

    @patch("src.integrations.email_handler.smtplib.SMTP")
    def test_disconnect_smtp(self, mock_smtp_class: MagicMock, client: EmailClient) -> None:
        """Test disconnecting SMTP."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        client._smtp = mock_smtp

        client.disconnect_smtp()

        mock_smtp.quit.assert_called()
        assert client._smtp is None

    def test_disconnect_imap(self, client: EmailClient) -> None:
        """Test disconnecting IMAP."""
        mock_imap = MagicMock()
        client._imap = mock_imap

        client.disconnect_imap()

        mock_imap.logout.assert_called()
        assert client._imap is None

    @patch("src.integrations.email_handler.smtplib.SMTP")
    def test_send_email(self, mock_smtp_class: MagicMock, client: EmailClient) -> None:
        """Test sending an email."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        client._smtp = mock_smtp

        email_msg = Email(
            to=["recipient@example.com"],
            subject="Test",
            body="Test body",
        )
        result = client.send_email(email_msg)

        assert result.get("status") == "sent"
        mock_smtp.send_message.assert_called()

    @patch("src.integrations.email_handler.smtplib.SMTP")
    def test_send_email_simple(self, mock_smtp_class: MagicMock, client: EmailClient) -> None:
        """Test sending a simple email."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        client._smtp = mock_smtp

        result = client.send_email_simple(
            to="recipient@example.com",
            subject="Test",
            body="Test body",
        )

        assert result.get("status") == "sent"

    @patch("src.integrations.email_handler.smtplib.SMTP")
    def test_send_email_multiple_recipients(self, mock_smtp_class: MagicMock, client: EmailClient) -> None:
        """Test sending to multiple recipients."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        client._smtp = mock_smtp

        email_msg = Email(
            to=["a@example.com", "b@example.com"],
            subject="Test",
            body="Test body",
            cc=["cc@example.com"],
        )
        client.send_email(email_msg)

        mock_smtp.send_message.assert_called()

    @patch("src.integrations.email_handler.imapclient.IMAPClient")
    def test_fetch_emails(self, mock_imap_class: MagicMock, client: EmailClient) -> None:
        """Test fetching emails."""
        mock_imap = MagicMock()
        mock_imap.search.return_value = [1, 2, 3]
        mock_imap.fetch.return_value = {
            1: {b"BODY[]": b"From: sender@test.com\r\nSubject: Test\r\n\r\nBody"},
            2: {b"BODY[]": b"From: sender2@test.com\r\nSubject: Test2\r\n\r\nBody2"},
            3: {b"BODY[]": b"From: sender3@test.com\r\nSubject: Test3\r\n\r\nBody3"},
        }
        mock_imap_class.return_value = mock_imap
        client._imap = mock_imap

        emails = client.fetch_emails(limit=10)

        assert len(emails) == 3
        mock_imap.select_folder.assert_called_with("INBOX", readonly=False)

    @patch("src.integrations.email_handler.imapclient.IMAPClient")
    def test_mark_as_read(self, mock_imap_class: MagicMock, client: EmailClient) -> None:
        """Test marking email as read."""
        mock_imap = MagicMock()
        mock_imap_class.return_value = mock_imap
        client._imap = mock_imap

        client.mark_as_read(123)

        mock_imap.add_flags.assert_called_with(123, ["\\Seen"])

    @patch("src.integrations.email_handler.imapclient.IMAPClient")
    def test_delete_email(self, mock_imap_class: MagicMock, client: EmailClient) -> None:
        """Test deleting an email."""
        mock_imap = MagicMock()
        mock_imap_class.return_value = mock_imap
        client._imap = mock_imap

        client.delete_email(123)

        mock_imap.move.assert_called_with(123, "[Gmail]/Trash")

    @patch("src.integrations.email_handler.imapclient.IMAPClient")
    def test_get_folders(self, mock_imap_class: MagicMock, client: EmailClient) -> None:
        """Test getting folder list."""
        mock_imap = MagicMock()
        mock_imap.list_folders.return_value = [
            (b"\\HasNoChildren", b"/", "INBOX"),
            (b"\\HasNoChildren", b"/", "Sent"),
        ]
        mock_imap_class.return_value = mock_imap
        client._imap = mock_imap

        folders = client.get_folders()

        assert "INBOX" in folders
        assert "Sent" in folders

    def test_context_manager(self, config: EmailConfig) -> None:
        """Test context manager usage."""
        with patch("src.integrations.email_handler.smtplib.SMTP"):
            with patch("src.integrations.email_handler.imapclient.IMAPClient"):
                client = EmailClient(config=config)
                with client:
                    assert client._connected is True
