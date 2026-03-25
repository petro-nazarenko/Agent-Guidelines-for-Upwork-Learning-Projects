# Agent Guidelines for Upwork Learning Projects

This repository contains automation and integration projects including Google Sheets integrations, PDF processing, email automation, and API-based tools.

## Project Structure

```
project/
├── src/                    # Source code
├── tests/                  # Test files (mirror src structure)
├── scripts/                # Utility scripts
├── config/                 # Configuration files
├── data/                   # Data files (input/output)
├── logs/                   # Log files
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies
├── pyproject.toml          # Python project config
└── README.md               # Project documentation
```

## Build, Lint, and Test Commands

### Python Projects

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .                    # Install in editable mode

# Virtual environment
python -m venv venv
source venv/bin/activate            # Linux/Mac
.\venv\Scripts\activate             # Windows

# Linting
flake8 src/ tests/                 # Run flake8
ruff check src/ tests/             # Run ruff (preferred)
ruff check --fix src/ tests/       # Auto-fix issues

# Type checking
mypy src/                          # Run mypy type checker
mypy --strict src/                 # Strict mode

# Formatting
black src/ tests/                  # Format code
isort src/ tests/                  # Sort imports

# Testing
pytest                              # Run all tests
pytest tests/test_specific.py       # Run single test file
pytest tests/test_specific.py::test_function_name  # Run single test
pytest -v                           # Verbose output
pytest -k "test_name"              # Run tests matching pattern
pytest --cov=src/                  # With coverage report
pytest --cov=src/ --cov-report=html  # HTML coverage report

# All checks (CI simulation)
python -m pytest && ruff check src/ && mypy src/
```

### JavaScript/TypeScript Projects

```bash
# Install dependencies
npm install
yarn install

# Linting
npm run lint                        # Run ESLint
npm run lint:fix                    # Auto-fix issues

# Type checking
npm run typecheck                  # Run TypeScript compiler
npx tsc --noEmit                   # Type check without emitting

# Formatting
npm run format                      # Run Prettier
npm run format:check               # Check formatting

# Testing
npm test                           # Run all tests
npm test -- --testPathPattern=test_file  # Run specific test file
npm test -- --testNamePattern="test name"  # Run tests matching name
npm run test:coverage              # With coverage
npm run test:watch                 # Watch mode

# Build
npm run build                      # Production build
npm run dev                        # Development server
```

### Running a Single Test

```bash
# Python
pytest tests/integrations/test_google_sheets.py::TestGoogleSheets::test_update_cell
pytest -k "test_update_cell" tests/

# JavaScript/TypeScript
npm test -- --testPathPattern="google-sheets"
npm test -- --testNamePattern="should update cell"
```

## Code Style Guidelines

### General Principles

- **Readability first**: Code is read more often than written
- **Explicit over implicit**: Be clear about what code does
- **Fail fast**: Validate inputs early and clearly
- **Single responsibility**: Each function/module does one thing well
- **DRY**: Don't repeat yourself; extract common logic

### Python Style

#### Imports
```python
# Standard library imports
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Third-party imports
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Local imports
from src.utils.helpers import format_date
from src.integrations.sheets import GoogleSheetsClient
```

#### Naming Conventions
```python
# Classes: PascalCase
class GoogleSheetsClient:
class PDFProcessor:

# Functions/methods: snake_case
def get_spreadsheet_data():
def process_pdf_file():

# Constants: SCREAMING_SNAKE_CASE
MAX_RETRIES = 3
API_SCOPE = ['https://www.googleapis.com/auth/spreadsheets']

# Variables: snake_case
spreadsheet_id = "abc123"
user_credentials = {}

# Private methods: _leading_underscore
def _validate_credentials(self):
```

#### Type Annotations
```python
from typing import Optional, List, Dict, Union, Callable

def process_data(
    data: List[Dict[str, Any]],
    callback: Optional[Callable[[str], None]] = None
) -> Dict[str, int]:
    ...

def get_value(key: str) -> Optional[str]:
    ...
```

#### Error Handling
```python
# Specific exceptions
try:
    result = api.call()
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    raise
except TimeoutError as e:
    logger.warning(f"Request timed out, retrying: {e}")
    # Handle retry logic
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise  # Re-raise unexpected errors
```

### JavaScript/TypeScript Style

#### Imports
```typescript
// Named imports
import { Google Sheets } from '@google-cloud/sheets';
import { readFile } from 'fs/promises';

// Default imports
import express, { Application, Request, Response } from 'express';

// Type imports
import type { Config, Credentials } from './types';
```

#### Naming Conventions
```typescript
// Classes: PascalCase
class GoogleSheetsService {
class PDFProcessor {

// Functions/methods: camelCase
function getSpreadsheetData(): Promise<any> {
function processPdfFile(path: string): Result {

// Constants: SCREAMING_SNAKE_CASE or camelCase
const MAX_RETRIES = 3;
const apiScope = ['https://www.googleapis.com/auth/spreadsheets'];

// Variables/interfaces: camelCase
let spreadsheetId: string;
interface UserData {
    name: string;
    email: string;
}
```

#### Type Annotations
```typescript
interface SheetData {
    values: string[][];
    range: string;
}

function processData(
    data: SheetData[],
    callback?: (result: string) => void
): Promise<Map<string, number>> {
    // implementation
}

type Result = SuccessResult | ErrorResult;
```

#### Error Handling
```typescript
try {
    const result = await api.call();
    return result;
} catch (error) {
    if (error instanceof ConnectionError) {
        logger.error('Connection failed', { error });
        throw error;
    }
    if (error instanceof TimeoutError) {
        logger.warn('Request timed out, retrying', { error });
        // Handle retry
    }
    logger.error('Unexpected error', { error });
    throw error;
}
```

### Google Sheets Integration Guidelines

- Always use service account credentials for server-side operations
- Implement exponential backoff for rate limiting
- Batch requests when possible using `valueRanges`
- Cache spreadsheet metadata to reduce API calls
- Handle missing/null cells gracefully
- Log all write operations for debugging

### PDF Processing Guidelines

- Use `pdfplumber` or `PyPDF2` for Python, `pdf-parse` for Node.js
- Extract text before tables for better accuracy
- Validate PDF structure before processing
- Handle password-protected PDFs appropriately
- Clean extracted data (remove extra whitespace, normalize)

### API Integration Guidelines

- Store all credentials in environment variables
- Never hardcode API keys or tokens
- Implement proper error handling with specific exception types
- Add logging for all external API calls
- Use retry logic with exponential backoff
- Respect rate limits and implement queuing if needed
- Cache responses when appropriate

### Environment Configuration

```bash
# .env.example
GOOGLE_SHEETS_CREDENTIALS_PATH=./config/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
API_KEY=your_api_key
LOG_LEVEL=INFO
MAX_RETRIES=3
```

### Logging Standards

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Detailed debugging info")
logger.info("Normal operation info")
logger.warning("Something unexpected but handled")
logger.error("Something failed")
logger.exception("Error with traceback")  # Use for exceptions
```

### Testing Guidelines

- Write tests that mirror source structure: `tests/integrations/test_sheets.py`
- Use descriptive test names: `test_update_cell_creates_new_row`
- Mock external APIs (Google Sheets, email services)
- Test edge cases (empty data, invalid input, rate limits)
- Use fixtures for common test data
- Aim for 80%+ code coverage on core logic

```python
# Example test structure
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_sheets_client():
    return Mock()

def test_update_cell_creates_new_row(mock_sheets_client):
    """Test that updating a cell creates a new row if needed."""
    client = mock_sheets_client
    client.update_cell = Mock(return_value={"updatedCells": 1})
    
    result = update_cell(client, "Sheet1", "A1", "Value")
    
    assert result["updatedCells"] == 1
    client.update_cell.assert_called_once()
```

### Documentation

- Document all public APIs with docstrings (Python) or JSDoc (JS)
- Include usage examples in docstrings
- Keep README.md updated with setup and usage instructions
- Add inline comments for non-obvious logic
