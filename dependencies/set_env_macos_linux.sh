#!/bin/bash
# Environment variable setup for Victoria (macOS/Linux)
set -e

PROFILE_FILES=("$HOME/.bashrc" "$HOME/.zshrc")

read -p "Enter your OPENROUTER_API_KEY: " OPENROUTER_API_KEY
for file in "${PROFILE_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "export OPENROUTER_API_KEY=\"$OPENROUTER_API_KEY\"" >> "$file"
  fi
done

echo "OPENROUTER_API_KEY saved to shell profile."

read -p "Configure Snowflake variables? (y/N): " ANSWER
if [[ $ANSWER =~ ^[Yy]$ ]]; then
  read -p "SNOWFLAKE_ACCOUNT: " SNOWFLAKE_ACCOUNT
  read -p "SNOWFLAKE_USER: " SNOWFLAKE_USER
  read -p "SNOWFLAKE_PASSWORD: " SNOWFLAKE_PASSWORD
  read -p "SNOWFLAKE_WAREHOUSE: " SNOWFLAKE_WAREHOUSE
  read -p "SNOWFLAKE_ROLE: " SNOWFLAKE_ROLE
  for file in "${PROFILE_FILES[@]}"; do
    if [ -f "$file" ]; then
      {
        echo "export SNOWFLAKE_ACCOUNT=\"$SNOWFLAKE_ACCOUNT\""
        echo "export SNOWFLAKE_USER=\"$SNOWFLAKE_USER\""
        echo "export SNOWFLAKE_PASSWORD=\"$SNOWFLAKE_PASSWORD\""
        echo "export SNOWFLAKE_WAREHOUSE=\"$SNOWFLAKE_WAREHOUSE\""
        echo "export SNOWFLAKE_ROLE=\"$SNOWFLAKE_ROLE\""
      } >> "$file"
    fi
  done
  echo "Snowflake variables saved."
fi

echo "Done. Restart your terminal or source your profile to apply changes."
