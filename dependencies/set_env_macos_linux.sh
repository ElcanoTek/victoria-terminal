#!/bin/bash
# Environment variable setup for Victoria (macOS/Linux)
set -e

# Define the environment file path
VICTORIA_HOME="$HOME/Victoria"
ENV_FILE="$VICTORIA_HOME/.env"
mkdir -p "$VICTORIA_HOME"

SKIP_OPENROUTER=false
if [[ "$1" == "--skip-openrouter" ]]; then
  SKIP_OPENROUTER=true
fi

if [ "$SKIP_OPENROUTER" = false ]; then
  read -p "Enter your OPENROUTER_API_KEY (leave blank to skip): " OPENROUTER_API_KEY
  if [ -n "$OPENROUTER_API_KEY" ]; then
    # Remove existing key and append new one to ensure it's not duplicated
    if grep -q "OPENROUTER_API_KEY" "$ENV_FILE" 2>/dev/null; then
      sed -i.bak '/OPENROUTER_API_KEY/d' "$ENV_FILE"
    fi
    echo "OPENROUTER_API_KEY=\"$OPENROUTER_API_KEY\"" >> "$ENV_FILE"
    echo "OPENROUTER_API_KEY saved to $ENV_FILE"
  else
    echo "Skipping OpenRouter API key configuration."
  fi
else
  echo "Skipping OpenRouter API key configuration."
fi

read -p "Configure Snowflake variables? (y/N): " ANSWER
if [[ $ANSWER =~ ^[Yy]$ ]]; then
  read -p "SNOWFLAKE_ACCOUNT: " SNOWFLAKE_ACCOUNT
  read -p "SNOWFLAKE_USER: " SNOWFLAKE_USER
  read -p "SNOWFLAKE_PASSWORD: " SNOWFLAKE_PASSWORD
  read -p "SNOWFLAKE_WAREHOUSE: " SNOWFLAKE_WAREHOUSE
  read -p "SNOWFLAKE_ROLE: " SNOWFLAKE_ROLE

  # Remove existing keys and append new ones
  if grep -q "SNOWFLAKE_" "$ENV_FILE" 2>/dev/null; then
      sed -i.bak '/SNOWFLAKE_/d' "$ENV_FILE"
  fi

  {
    echo "SNOWFLAKE_ACCOUNT=\"$SNOWFLAKE_ACCOUNT\""
    echo "SNOWFLAKE_USER=\"$SNOWFLAKE_USER\""
    echo "SNOWFLAKE_PASSWORD=\"$SNOWFLAKE_PASSWORD\""
    echo "SNOWFLAKE_WAREHOUSE=\"$SNOWFLAKE_WAREHOUSE\""
    echo "SNOWFLAKE_ROLE=\"$SNOWFLAKE_ROLE\""
  } >> "$ENV_FILE"
  echo "Snowflake variables saved to $ENV_FILE"
fi

# Clean up backup files created by sed
find "$VICTORIA_HOME" -name "*.bak" -delete >/dev/null 2>&1 || true

echo "Done. Environment variables are configured for Victoria."
