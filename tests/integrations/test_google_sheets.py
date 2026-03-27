"""Tests for Google Sheets integration."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.integrations.google_sheets import (
    GoogleSheetsClient,
    GoogleSheetsConfig,
    WriteOptions,
)


class TestGoogleSheetsConfig:
    """Tests for Google Sheets configuration."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = GoogleSheetsConfig()
        assert config.max_retries == 3
        assert config.timeout == 30.0
        assert config.rate_limit_delay == 1.0
        assert config.credentials_path == Path.home() / '.config' / 'upwork-learn' / 'credentials.json'

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = GoogleSheetsConfig(
            max_retries=5,
            timeout=60.0,
            credentials_path=Path("/custom/path.json"),
        )
        assert config.max_retries == 5
        assert config.timeout == 60.0
        assert config.credentials_path == Path("/custom/path.json")


class TestWriteOptions:
    """Tests for write options."""

    def test_default_values(self) -> None:
        """Test default write options."""
        options = WriteOptions()
        assert options.raw is True
        assert options.major_dimension == "ROWS"

    def test_custom_values(self) -> None:
        """Test custom write options."""
        options = WriteOptions(raw=False, major_dimension="COLUMNS")
        assert options.raw is False
        assert options.major_dimension == "COLUMNS"


class TestGoogleSheetsClient:
    """Tests for Google Sheets client."""

    @pytest.fixture
    def config(self) -> GoogleSheetsConfig:
        """Create test configuration."""
        return GoogleSheetsConfig(
            credentials_path=Path("tests/fixtures/credentials.json"),
            spreadsheet_id="test_spreadsheet_id",
        )

    @pytest.fixture
    def client(self, config: GoogleSheetsConfig) -> GoogleSheetsClient:
        """Create test client."""
        return GoogleSheetsClient(config=config)

    def test_service_name(self, client: GoogleSheetsClient) -> None:
        """Test service name property."""
        assert client.service_name == "google-sheets"

    def test_initial_state(self, client: GoogleSheetsClient) -> None:
        """Test initial client state."""
        assert client._connected is False
        assert client._spreadsheet is None
        assert client._client is None

    @patch("src.integrations.google_sheets.gspread")
    @patch("src.integrations.google_sheets.Credentials")
    def test_connect_success(self, mock_credentials: MagicMock, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test successful connection."""
        mock_creds = MagicMock()
        mock_credentials.from_service_account_file.return_value = mock_creds
        mock_gspread.authorize.return_value = MagicMock()

        client.connect()

        assert client._connected is True
        assert client._client is not None
        mock_gspread.authorize.assert_called_once()

    def test_disconnect(self, client: GoogleSheetsClient) -> None:
        """Test disconnect clears state."""
        client._connected = True
        client._client = MagicMock()
        client._spreadsheet = MagicMock()

        client.disconnect()

        assert client._connected is False
        assert client._client is None
        assert client._spreadsheet is None

    def test_context_manager(self, config: GoogleSheetsConfig) -> None:
        """Test context manager usage."""
        with patch("src.integrations.google_sheets.gspread"):
            with patch("src.integrations.google_sheets.Credentials"):
                client = GoogleSheetsClient(config=config)
                with client:
                    pass

    @patch("src.integrations.google_sheets.gspread")
    def test_read_range(self, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test reading a range."""
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.values_get.return_value = {
            "values": [["A1", "B1"], ["A2", "B2"]]
        }
        client._client = MagicMock()
        client._spreadsheet = mock_spreadsheet
        client._spreadsheet_id = "test_id"

        result = client.read_range("Sheet1!A1:B2")

        assert result == [["A1", "B1"], ["A2", "B2"]]
        mock_spreadsheet.values_get.assert_called_once()

    @patch("src.integrations.google_sheets.gspread")
    def test_write_range(self, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test writing to a range."""
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.values_update.return_value = {"updatedCells": 4}
        client._client = MagicMock()
        client._spreadsheet = mock_spreadsheet
        client._spreadsheet_id = "test_id"

        values = [["X1", "Y1"], ["X2", "Y2"]]
        result = client.write_range("Sheet1!A1:B2", values)

        assert result["updatedCells"] == 4
        mock_spreadsheet.values_update.assert_called_once()

    @patch("src.integrations.google_sheets.gspread")
    def test_append_row(self, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test appending a row."""
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_worksheet.append_row.return_value = {"spreadsheetId": "test"}
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        client._client = MagicMock()
        client._spreadsheet = mock_spreadsheet
        client._spreadsheet_id = "test_id"

        result = client.append_row(["A", "B", "C"])

        assert "spreadsheetId" in result
        mock_worksheet.append_row.assert_called_once_with(["A", "B", "C"])

    @patch("src.integrations.google_sheets.gspread")
    def test_update_cell(self, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test updating a single cell."""
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_worksheet.update.return_value = {"updatedCells": 1}
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        client._client = MagicMock()
        client._spreadsheet = mock_spreadsheet
        client._spreadsheet_id = "test_id"

        result = client.update_cell(row=1, col=1, value="Test")

        assert result["updatedCells"] == 1
        mock_worksheet.update.assert_called_once()

    @patch("src.integrations.google_sheets.gspread")
    def test_get_worksheets(self, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test getting worksheet names."""
        mock_spreadsheet = MagicMock()
        mock_ws1 = MagicMock()
        mock_ws1.title = "Sheet1"
        mock_ws2 = MagicMock()
        mock_ws2.title = "Sheet2"
        mock_spreadsheet.worksheets.return_value = [mock_ws1, mock_ws2]
        client._client = MagicMock()
        client._spreadsheet = mock_spreadsheet
        client._spreadsheet_id = "test_id"

        result = client.get_worksheets()

        assert result == ["Sheet1", "Sheet2"]

    @patch("src.integrations.google_sheets.gspread")
    def test_batch_write(self, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test batch writing multiple ranges."""
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.values_batch_update.return_value = {"totalUpdatedCells": 4}
        client._client = MagicMock()
        client._spreadsheet = mock_spreadsheet
        client._spreadsheet_id = "test_id"

        data = [{"range": "Sheet1!A1:B1", "values": [["X", "Y"]]}]
        result = client.batch_write(data)

        assert result["totalUpdatedCells"] == 4
        mock_spreadsheet.values_batch_update.assert_called_once()

    @patch("src.integrations.google_sheets.gspread")
    def test_create_worksheet(self, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test creating a new worksheet."""
        mock_spreadsheet = MagicMock()
        mock_ws = MagicMock()
        mock_spreadsheet.add_worksheet.return_value = mock_ws
        client._client = MagicMock()
        client._spreadsheet = mock_spreadsheet
        client._spreadsheet_id = "test_id"

        ws = client.create_worksheet("NewSheet")

        assert ws is mock_ws
        mock_spreadsheet.add_worksheet.assert_called_once_with("NewSheet", 100, 26)

    @patch("src.integrations.google_sheets.gspread")
    def test_delete_worksheet(self, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test deleting a worksheet."""
        mock_spreadsheet = MagicMock()
        mock_ws = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_ws
        client._client = MagicMock()
        client._spreadsheet = mock_spreadsheet
        client._spreadsheet_id = "test_id"

        client.delete_worksheet("OldSheet")

        mock_spreadsheet.del_worksheet.assert_called_once_with(mock_ws)

    @patch("src.integrations.google_sheets.gspread")
    def test_clear_sheet(self, mock_gspread: MagicMock, client: GoogleSheetsClient) -> None:
        """Test clearing all data from a sheet."""
        mock_spreadsheet = MagicMock()
        mock_ws = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_ws
        client._client = MagicMock()
        client._spreadsheet = mock_spreadsheet
        client._spreadsheet_id = "test_id"

        client.clear_sheet("Sheet1")

        mock_ws.clear.assert_called_once()

    @patch("src.integrations.google_sheets.Credentials")
    def test_load_credentials_from_env(self, mock_creds_class: MagicMock, client: GoogleSheetsClient, monkeypatch: "pytest.MonkeyPatch") -> None:
        """Test loading credentials from GOOGLE_SHEETS_CREDENTIALS_JSON env var."""
        import base64, json
        dummy = {"type": "service_account", "project_id": "test"}
        encoded = base64.b64encode(json.dumps(dummy).encode()).decode()
        monkeypatch.setenv("GOOGLE_SHEETS_CREDENTIALS_JSON", encoded)

        mock_creds_class.from_service_account_info.return_value = MagicMock()
        client._load_credentials()

        mock_creds_class.from_service_account_info.assert_called_once()

    def test_open_spreadsheet_generic_error(self, client: GoogleSheetsClient) -> None:
        """Test open_spreadsheet wraps unexpected errors in IntegrationConnectionError."""
        from src.integrations.base import IntegrationConnectionError

        mock_client = MagicMock()
        mock_client.open_by_key.side_effect = RuntimeError("network failure")
        client._client = mock_client
        client._spreadsheet_id = "test_id"

        with pytest.raises(IntegrationConnectionError):
            client.open_spreadsheet("test_id")
