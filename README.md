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
* ```cd``` to project folder
* type ```./victoria```
* ask questions!
* try different models!

## Models to try

| Model | Input/Output ($/1M tokens) | Category | Best For |
|-------|---------------------------|----------|----------|
| **gpt-oss-20b (free)** | $0 / $0 | 🆓 Free | Learning, testing, minimal usage |
| **gpt-oss-120b** | $0 / $0.45 | 🆓 Free Input | Free prompts, cheap responses |
| **GPT-5 Nano** | $0.05 / $0.40 | ⚡ Ultra Fast | Speed + minimal cost |
| **gpt-oss-20b** | $0.04 / $0.16 | 💰 Ultra Budget | Cheapest paid option |
| **GLM 4.5** | $0.20 / $0.20 | 💰 Budget | Best balanced budget choice |
| **Qwen3 30B A3B** | $0.20 / $0.80 | 💰 Budget | Open source, good performance |
| **GPT-5 Mini** | $0.25 / $2.00 | 🎯 Balanced | Compact GPT-5, great value |
| **DeepSeek V3** | $0.27 / $1.10 | 🎯 Best Value | Top recommendation for most users |
| **Codestral** | $0.30 / $0.90 | 🔧 Coding | Specialized for programming |
| **DeepSeek R1** | $0.55 / $2.19 | 🧠 Reasoning | Advanced reasoning tasks |
| **GPT-5** | $1.25 / $10.00 | 🏆 Premium | Best overall performance |

### Quick Picks

- **🎯 Start Here**: DeepSeek V3 ($0.27/$1.10) - Best overall value
- **💰 Budget**: GLM 4.5 ($0.20/$0.20) - Cheapest balanced option
- **🆓 Free**: gpt-oss-20b (free) ($0/$0) - Completely free
- **🏆 Best**: GPT-5 ($1.25/$10) - Top performance
- **⚡ Fast**: GPT-5 Nano ($0.05/$0.40) - Ultra-fast responses

### Quick Wins! Questions to ask

* ```Provide the top 5 performing sites with over 5,000 impressions and the highest CTR, aggregated across the entire site rather than by individual day```

