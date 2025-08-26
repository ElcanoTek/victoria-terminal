# Victoria x ```crush``` setup

This setup configures Victoria (Elcano's AI agent) to work with Crush CLI for analyzing programmatic advertising data.

## Requirements

* ```crush``` (see [github](https://github.com/charmbracelet/crush))
* ```ripgrep``` (see [github](https://github.com/BurntSushi/ripgrep))
* ```uv``` (see [astral.sh](https://docs.astral.sh/uv/getting-started/installation/))
* ```OPENROUTER_API_KEY```: You need this set as an environment variable to run crush, GEMINI and OPENAI are supported as well. Email [brad@elcanotek.com](mailto:brad@elcanotek.com) for a company key.
* ```VICTORIA.md```: Make sure you have an updated VICTORIA.md in this repo, the [```victoria-main```](https://github.com/ElcanoTek/victoria-main) repo has the latest changes, the file has a version number on the top.
* ```ghostty``` (optional but recommended, see [ghostty.org](https://ghostty.org/))

## .csv or excel files in the ```data``` folder

Add your csv or Excel files to the ```./data``` folder in this repository and they will be available for analysis

## Snowflake Integration (Optional)

To enable Snowflake database access through Victoria, configure these environment variables:

```bash
export SNOWFLAKE_ACCOUNT="your_account_identifier"
export SNOWFLAKE_USER="your_username@domain.com"
export SNOWFLAKE_PASSWORD="your_password"
export SNOWFLAKE_WAREHOUSE="your_warehouse"
export SNOWFLAKE_ROLE="your_read_only_role"
```

**Important**: The role should have read-only SELECT permissions across all databases you want to access. Omitting database/schema parameters allows Victoria to query across ALL available databases.

The Snowflake MCP server will be automatically installed via ```uvx``` when first used. No manual installation required.

## Getting Started

### Linux/macOS
* ```cd``` to project folder
* type ```./victoria```
* ask questions!
* try different models!

### Windows
* See **[README-Windows.md](./README-Windows.md)** for complete Windows setup guide
* Use ```victoria.ps1``` (PowerShell) or ```victoria.bat``` (double-click)
* The PowerShell script includes dependency installation and environment setup
* Run with ```-InstallDeps``` or ```-Setup``` flags for specific functions

## Models to try

| Model | Input/Output ($/1M tokens) | Category | Best For |
|-------|---------------------------|----------|----------|
| **gpt-oss-120b** | $0 / $0.45 | 🆓 Free Input | TODO, brad is testing locally |
| **GPT-5 Nano** | $0.05 / $0.40 | ⚡ Ultra Fast | TODO |
| **DeepSeek V3** | $0.27 / $1.10 | 🎯 Best Value | We should try this again |
| **Google Gemini 2.5 Pro** | $1.25 / $10.00 | 🏆 Premium | Current best tested model |


### Quick Wins! Questions to ask

* ```Provide the top 5 performing sites with over 5,000 impressions and the highest CTR, aggregated across the entire site rather than by individual day```

