# Gamma API Research Findings

## Overview

Gamma is an AI-powered presentation, document, and social media content creation platform that offers a Generate API for programmatic content creation. The API is currently in **beta** and available to Pro, Ultra, Team, and Business account holders.

## API Capabilities

### Core Features
- **Programmatic presentation generation** from text input
- **Multiple output formats**: presentations, documents, social media posts
- **Export options**: PDF, PPTX, and native Gamma format
- **AI-generated images** with multiple model options
- **Custom themes** support
- **Bulk generation** capabilities for scaling content creation

### Key Use Cases
- Automation workflows using tools like Zapier, Make, or Workato
- Integration into custom applications for design capabilities
- Backend code integration for bulk presentation creation
- Personalized content generation at scale

## API Technical Specifications

### Base URL
```
https://public-api.gamma.app/v0.2/generations
```

### Authentication
- **Header**: `X-API-KEY` (not Bearer token format)
- **API Key Format**: `sk-gamma-xxxxxxxx`
- **Access**: Requires Pro account or higher

### Main Endpoint: POST /generations

#### Required Parameters
- `inputText` (string): Text content for generation (1-750,000 characters)
- `X-API-KEY` (header): Authentication key

#### Key Optional Parameters
- `textMode`: How to modify input text
  - `generate`: Expand and rewrite content (default)
  - `condense`: Summarize content
  - `preserve`: Keep exact text with minimal structuring
- `format`: Output type
  - `presentation` (default)
  - `document`
  - `social`
- `themeName`: Visual theme (can use custom themes)
- `numCards`: Number of slides/cards (1-50 for Pro, 1-75 for Ultra)
- `cardSplit`: Content division method
  - `auto`: Divide based on numCards
  - `inputTextBreaks`: Use `\n---\n` breaks in text
- `exportAs`: Additional export format (`pdf` or `pptx`)

#### Advanced Options
- `textOptions`: Control text generation
  - `amount`: `brief`, `medium`, `detailed`, `extensive`
  - `tone`: Voice/mood specification
  - `audience`: Target audience description
  - `language`: Output language (multiple supported)
- `imageOptions`: Image generation settings
  - `source`: `aiGenerated` or other sources
  - `model`: Various AI models including `imagen-4-pro`
  - `style`: `photorealistic` and other styles
- `cardOptions`: Layout specifications
  - `dimensions`: `fluid` and other options
- `sharingOptions`: Access control settings

### Response Format
```json
{
  "generationId": "xxxxxxxxxxx"
}
```

### Status Checking: GET /generations/{id}
Check generation status and retrieve results once complete.

## Current Limitations (Beta)

### Rate Limits
- **Pro users**: 50 presentations per day
- **No additional cost** during beta period
- Rate limits subject to change post-beta

### Feature Limitations
- Some advanced features not yet available
- Template support limited to visual themes
- Content structure templates in development

## Integration Requirements for Victoria Terminal

### Prerequisites
1. **Gamma Pro Account**: Required for API access
2. **API Key Generation**: Through Gamma account settings
3. **Environment Variables**: Store API key securely

### Potential Integration Points
1. **Command Interface**: Add Gamma presentation generation commands
2. **Data Visualization**: Convert analysis results to presentations
3. **Report Generation**: Transform data insights into formatted presentations
4. **Bulk Operations**: Generate multiple presentations from datasets

### Technical Considerations
- **Asynchronous Operations**: API uses generation IDs for status checking
- **File Handling**: Support for PDF/PPTX downloads
- **Error Handling**: Comprehensive error codes and warnings available
- **Rate Limiting**: Implement proper throttling for Pro account limits

## Next Steps for Integration
1. Design command interface for Victoria Terminal
2. Implement authentication and configuration management
3. Create presentation generation workflows
4. Add export and file management capabilities
5. Integrate with existing data analysis features

## References
- [Gamma API Help Center](https://help.gamma.app/en/articles/11962420-does-gamma-have-an-api)
- [API Parameters Documentation](https://developers.gamma.app/docs/how-does-the-generations-api-work)
- [API Reference](https://developers.gamma.app/reference/generate-a-gamma)
