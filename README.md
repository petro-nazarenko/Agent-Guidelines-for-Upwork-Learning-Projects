# Upwork Learning

Automation and Integration Tools for Upwork Projects.

A comprehensive Python library for building automation workflows with Google Sheets, PDF processing, email automation, and API integrations.

## Features

- **Google Sheets Integration** - Read, write, and sync data with Google Sheets
- **PDF Processing** - Extract text, tables, and structured data from PDFs
- **Email Automation** - Send emails, fetch inbox, and auto-reply workflows
- **API Integrations** - Tools for integrating with APIs like Bol.com
- **CLI Tools** - Command-line interface for all operations
- **Best Practices** - Type hints, testing, linting, and documentation

## Installation

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .

# Using pip
pip install -e .
```

## Quick Start

### Python API

```python
from src.integrations.google_sheets import GoogleSheetsClient

# Read from Google Sheets
with GoogleSheetsClient(spreadsheet_id="YOUR_ID") as client:
    data = client.read_range("Sheet1!A1:C10")
    print(data)
```

```python
from src.integrations.pdf_processor import PDFProcessor

# Extract data from PDF
processor = PDFProcessor()
with processor:
    processor.open("invoice.pdf")
    text = processor.extract_all_text()
    tables = processor.extract_tables()
```

### CLI

```bash
# Read from Google Sheets
python -m src.cli sheets-read --spreadsheet-id ID --range "A1:C10"

# Extract text from PDF
python -m src.cli pdf-extract-text document.pdf

# Send email
python -m src.cli email-send --to "a@b.com" --subject "Hi" --body "Hello"
```

## Documentation

Full documentation is available at:
- [English](https://petro-nazarenko.github.io/Agent-Guidelines-for-Upwork-Learning-Projects/)

## Development

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

## Project Structure

```
├── src/
│   ├── integrations/     # Integration modules
│   ├── utils/            # Utility modules
│   └── cli.py            # CLI entry point
├── tests/                # Test suite
├── examples/             # Example usage
├── docs/                 # Documentation
└── pyproject.toml        # Project configuration
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Petr Nazarenko
