# Gamma API Integration for Victoria Terminal

This document describes the integration of the Gamma Generate API into Victoria Terminal, enabling users to create presentations programmatically from their data analysis results.

## Overview

The Gamma integration adds presentation generation capabilities to Victoria Terminal through a modular design that includes:

- **Gamma API Client** (`gamma_client.py`): A Python client for interacting with the Gamma Generate API
- **Command-Line Interface** (`gamma_cli.py`): A CLI tool for generating presentations from text files
- **Configuration Integration**: Seamless integration with Victoria's existing configuration system
- **Comprehensive Testing** (`test_gamma_integration.py`): Unit tests covering all functionality

## Features

### Presentation Generation
- Create presentations, documents, and social media content from text input
- Support for multiple export formats (PDF, PPTX, native Gamma)
- Customizable themes and visual styling
- AI-generated images with multiple model options
- Flexible content structuring and card division

### Integration with Victoria Terminal
- Automatic API key management through Victoria's configuration system
- Seamless workflow integration with existing data analysis tools
- Rich console output with progress indicators and status updates
- Error handling and user-friendly feedback

## Prerequisites

### Gamma Account Requirements
1. **Gamma Pro Account or Higher**: The API is only available to Pro, Ultra, Team, and Business account holders
2. **API Key**: Generate an API key from your Gamma account settings
3. **Rate Limits**: Pro users can generate up to 50 presentations per day during beta

### Victoria Terminal Setup
1. Ensure Victoria Terminal is properly installed and configured
2. The integration requires the `requests` library (automatically included in requirements.txt)

## Installation and Configuration

### 1. API Key Setup

The Gamma API key is configured through Victoria's existing setup wizard:

```bash
# Run the configuration wizard
python3 victoria_terminal.py --reconfigure
```

When prompted, enter your Gamma API key (format: `sk-gamma-xxxxxxxx`). The key will be securely stored in your `~/Victoria/.env` file.

### 2. Verify Installation

Run the test suite to ensure everything is working correctly:

```bash
python3 test_gamma_integration.py
```

All tests should pass, indicating successful integration.

## Usage

### Command-Line Interface

The primary way to use the Gamma integration is through the CLI:

```bash
python3 gamma_cli.py --input <file_path> [options]
```

#### Basic Examples

Generate a presentation from a text file:
```bash
python3 gamma_cli.py --input sample_presentation.txt
```

Export as PDF with a specific theme:
```bash
python3 gamma_cli.py --input analysis.txt --export-as pdf --theme "Night Sky"
```

Create a detailed presentation with custom settings:
```bash
python3 gamma_cli.py --input report.txt \
  --num-cards 15 \
  --text-tone "professional, inspiring" \
  --text-audience "executives, stakeholders" \
  --image-style photorealistic \
  --export-as pptx
```

#### Advanced Options

**Text Processing:**
- `--text-mode`: How to modify input text (`generate`, `condense`, `preserve`)
- `--text-amount`: Amount of text per card (`brief`, `medium`, `detailed`, `extensive`)
- `--text-tone`: Voice and mood for the content
- `--text-audience`: Target audience description
- `--text-language`: Output language code

**Content Structure:**
- `--format`: Content type (`presentation`, `document`, `social`)
- `--num-cards`: Number of slides/cards to create
- `--card-split`: Content division method (`auto`, `inputTextBreaks`)
- `--instructions`: Additional generation instructions

**Visual Styling:**
- `--theme`: Gamma theme name (supports custom themes)
- `--image-source`: Image source (`aiGenerated`)
- `--image-model`: AI model for images (e.g., `imagen-4-pro`)
- `--image-style`: Image style (e.g., `photorealistic`)

### Programmatic Usage

You can also use the Gamma client directly in Python code:

```python
from gamma_client import GammaClient
import os

# Initialize client
client = GammaClient(os.environ['GAMMA_API_KEY'])

# Generate presentation
generation_id = client.generate_presentation(
    input_text="Your presentation content here",
    theme_name="Modern",
    export_as="pdf"
)

# Wait for completion and get result
result = client.wait_for_completion(generation_id)
print(f"Presentation URL: {result['url']}")
```

## Input Text Format

The Gamma API accepts various text formats:

### Simple Text
```
Best practices for data visualization in advertising analytics
```

### Structured Content with Manual Breaks
Use `\n---\n` to manually divide content into cards:

```
# Executive Summary
Key findings from our Q3 analysis

---

# Performance Metrics
* CTR increased by 23%
* Conversion rate improved by 15%
* Cost per acquisition decreased by 8%

---

# Recommendations
1. Increase budget for high-performing campaigns
2. Optimize targeting parameters
3. A/B test new creative formats
```

### Rich Markdown Content
The API handles Markdown formatting:

```markdown
# AdTech Analysis Results

## Key Insights
Our analysis reveals **significant opportunities** for optimization:

- Mobile traffic: 67% of impressions
- Video ads: 40% higher conversion rates
- Peak hours: 23% CTR improvement

## Next Steps
1. Implement dynamic creative optimization
2. Expand successful campaigns
3. Develop predictive models
```

## File Output

Generated presentations are saved to your Victoria directory (`~/Victoria` by default):

- **PDF/PPTX exports**: `filename_presentation.pdf` or `filename_presentation.pptx`
- **Gamma URLs**: `filename_presentation_url.txt` (contains the Gamma app URL)

## Error Handling

The integration includes comprehensive error handling:

- **Missing API Key**: Clear instructions to run the configuration wizard
- **API Errors**: Detailed error messages with request IDs for support
- **File Errors**: Validation of input files and output directories
- **Network Issues**: Retry logic and timeout handling
- **Rate Limiting**: Informative messages about usage limits

## Testing

The integration includes a comprehensive test suite covering:

- API client functionality
- Error handling scenarios
- File operations
- CLI argument parsing
- Environment configuration

Run tests with:
```bash
python3 test_gamma_integration.py
```

## Troubleshooting

### Common Issues

**"Gamma API key not found"**
- Run `python3 victoria_terminal.py --reconfigure` to set up your API key
- Ensure your API key follows the format `sk-gamma-xxxxxxxx`

**"Generation failed" errors**
- Check your Gamma account status and subscription level
- Verify you haven't exceeded the daily rate limit (50 presentations for Pro users)
- Ensure your input text is within the character limit (1-750,000 characters)

**File not found errors**
- Verify the input file path is correct and the file exists
- Ensure you have write permissions to the output directory

### Getting Help

For Gamma API-specific issues:
- Check the [Gamma API documentation](https://developers.gamma.app/)
- Contact Gamma support with your request ID from error messages

For Victoria Terminal integration issues:
- Review the test output for specific error details
- Check the Victoria Terminal logs for additional context

## API Reference

### GammaClient Class

#### Methods

**`__init__(api_key: str)`**
Initialize the client with your Gamma API key.

**`generate_presentation(input_text: str, **kwargs) -> str`**
Generate a presentation and return the generation ID.

**`check_generation_status(generation_id: str) -> Dict`**
Check the status of a generation request.

**`wait_for_completion(generation_id: str, timeout: int = 300) -> Dict`**
Wait for a generation to complete with timeout handling.

**`download_file(url: str, file_path: Path) -> None`**
Download a file from a URL to a local path.

**`create_presentation_from_file(input_file: Path, output_dir: Path, **kwargs) -> Path`**
Complete workflow: read file, generate presentation, download result.

### Error Classes

**`GammaAPIError`**
Custom exception for all Gamma API-related errors.

## Integration Architecture

```
Victoria Terminal
├── victoria_terminal.py (main application)
│   ├── Configuration wizard integration
│   └── Environment variable management
├── gamma_client.py (API client)
│   ├── HTTP request handling
│   ├── Authentication management
│   ├── Response parsing
│   └── File download capabilities
├── gamma_cli.py (command-line interface)
│   ├── Argument parsing
│   ├── User interaction
│   └── Workflow orchestration
└── test_gamma_integration.py (test suite)
    ├── Unit tests for all components
    ├── Mock API responses
    └── Error scenario testing
```

## Future Enhancements

Potential improvements for future versions:

1. **Batch Processing**: Generate multiple presentations from a directory of files
2. **Template Management**: Create and manage custom Gamma themes
3. **Data Integration**: Direct integration with Victoria's data analysis results
4. **Scheduling**: Automated presentation generation on data updates
5. **Collaboration**: Team sharing and review workflows
6. **Analytics**: Usage tracking and performance metrics

## License and Support

This integration is part of Victoria Terminal and follows the same licensing terms. For support:

1. Check this documentation and the test suite
2. Review the Gamma API documentation
3. Contact the Victoria Terminal development team
4. Submit issues through the appropriate channels

---

**Author**: Manus AI  
**Last Updated**: September 2025  
**Version**: 1.0.0
