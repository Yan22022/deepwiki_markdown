# DeepWiki Crawler

A modular Python crawler for extracting documentation from DeepWiki sites and converting to Markdown format with preserved flowcharts.

## Features

- Extracts content from DeepWiki pages
- Converts HTML to clean Markdown
- Preserves and converts flowcharts to Mermaid format
- Handles internal links properly
- Modular architecture for easy maintenance

## Project Structure

```
src/
├── __init__.py          # Package initialization
├── constants.py        # Constants (user agents, regex patterns)
├── crawler.py          # Main crawler class
├── file_utils.py       # File system operations
├── flowchart.py        # Flowchart extraction and processing
├── url_utils.py        # URL handling utilities
└── cli.py              # Command line interface
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/deepwiki-crawler.git
cd deepwiki-crawler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Crawling

```bash
python src/cli.py https://deepwiki.com/qemu/qemu -d 2 -o docs
```

Arguments:
- `url`: Starting URL (required)
- `-d/--depth`: Crawl depth (default: 2)
- `-o/--output`: Output directory (default: "output")
- `-t/--timeout`: Request timeout in seconds (default: 10)
- `-s/--sleep`: Delay between requests in seconds (default: 1.0)
- `--test-flowchart`: Test flowchart extraction only

### Module Usage

You can also use the modules programmatically:

```python
from src import DeepWikiCrawler

crawler = DeepWikiCrawler(
    base_url="https://deepwiki.com/qemu/qemu",
    max_depth=2,
    output_dir="docs",
    timeout=10,
    delay=1.0
)
crawler.crawl()
```

## Configuration

Modify `src/constants.py` to:
- Add/change user agents
- Update flowchart detection patterns
- Adjust other constants

## Testing

Run unit tests:
```bash
python -m unittest discover tests
```

Test flowchart extraction:
```bash
python src/flowchart.py
```

## Development

The project follows a modular architecture:

1. **crawler.py** - Main crawler logic
2. **url_utils.py** - URL parsing and normalization
3. **file_utils.py** - File system operations
4. **flowchart.py** - Flowchart processing
5. **cli.py** - Command line interface

To add new features:
1. Create a new module if needed
2. Add unit tests
3. Update the CLI if necessary

## License

MIT