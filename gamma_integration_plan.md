# Gamma API Integration Plan for Victoria Terminal

This document outlines the plan for integrating the Gamma Generate API into the Victoria Terminal application. The integration will enable users to generate presentations programmatically from their data and analyses within the terminal.

## 1. Architecture and Design

The integration will follow a modular design, separating the Gamma API client from the main application logic. This approach will enhance maintainability and allow for future extensions.

### 1.1. Core Components

- **`gamma_client.py`**: A new module responsible for all communication with the Gamma API. It will handle API requests, authentication, and response parsing.
- **`victoria_terminal.py`**: The main application file will be modified to include a new command for presentation generation. It will orchestrate the workflow, from user input to file output.
- **`~/.env`**: The existing environment file will be used to store the Gamma API key, ensuring secure credential management.

### 1.2. Data Flow

1. The user invokes a new command in Victoria Terminal, providing input text and optional parameters.
2. `victoria_terminal.py` parses the command and retrieves the Gamma API key from the `.env` file.
3. It then calls the `gamma_client.py` module to initiate the presentation generation.
4. `gamma_client.py` sends a `POST` request to the Gamma API and receives a `generationId`.
5. The client polls the API with the `generationId` until the presentation is ready.
6. Once generated, the client downloads the presentation file (PDF or PPTX) to the user's `~/Victoria` directory.
7. `victoria_terminal.py` informs the user of the successful generation and the file's location.

## 2. Implementation Details

### 2.1. Configuration

- A new entry, `GAMMA_API_KEY`, will be added to the `~/.env` file.
- The configuration wizard in `victoria_terminal.py` will be updated to prompt the user for their Gamma API key during the initial setup.

### 2.2. Command-Line Interface (CLI)

A new command will be added to `victoria_terminal.py`:

```bash
victoria generate:presentation --input <file_path> [options]
```

**Options:**

- `--input`: Path to a text file containing the content for the presentation.
- `--theme`: Name of the Gamma theme to use.
- `--output-format`: The desired output format (`pdf` or `pptx`).
- Additional options will be available to map to the Gamma API's parameters, such as `numCards`, `textMode`, etc.

### 2.3. Gamma API Client (`gamma_client.py`)

This module will contain a `GammaClient` class with the following methods:

- `__init__(api_key)`: Initializes the client with the API key.
- `generate_presentation(params)`: Sends the initial `POST` request to the API.
- `check_generation_status(generation_id)`: Polls the API for the generation status.
- `download_presentation(url, file_path)`: Downloads the final presentation file.

### 2.4. Error Handling and User Feedback

- The integration will handle potential API errors, such as invalid API keys, rate limits, and generation failures.
- The `rich` library will be used to provide informative feedback to the user, including progress spinners and status messages.

## 3. Development Phases

1. **Phase 1: Setup and Configuration**: Implement the API key configuration in `victoria_terminal.py` and the `.env` file.
2. **Phase 2: Gamma API Client**: Develop the `gamma_client.py` module with all the necessary methods for API interaction.
3. **Phase 3: CLI Integration**: Add the `generate:presentation` command to `victoria_terminal.py` and connect it to the `gamma_client`.
4. **Phase 4: Testing and Refinement**: Thoroughly test the integration with various inputs and options, and refine the user experience.

## 4. Dependencies

- The `requests` library will be added to `requirements.txt` for making HTTP requests to the Gamma API.

