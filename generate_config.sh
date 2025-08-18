#!/bin/bash

# Function to generate crush configuration
generate_crush_config() {
    local include_snowflake="$1"
    local output_file="$2"
    
    # Read the template
    local template_content
    template_content=$(cat crush.template.json)
    
    if [[ "$include_snowflake" == "true" ]]; then
        # Check if snowflake.mcp.json exists
        if [[ ! -f "snowflake.mcp.json" ]]; then
            echo "Error: snowflake.mcp.json not found!"
            return 1
        fi
        
        # Read Snowflake MCP configuration from separate file
        local snowflake_config
        snowflake_config=$(cat snowflake.mcp.json)
        
        # Extract just the snowflake MCP part (remove outer braces)
        local snowflake_mcp
        snowflake_mcp=$(echo "$snowflake_config" | sed '1d;$d' | sed 's/^/    /')
        
        # Add comma prefix for JSON syntax
        snowflake_mcp=",
$snowflake_mcp"
        
        # Replace the placeholder with Snowflake configuration
        echo "${template_content//\{\{SNOWFLAKE_MCP\}\}/$snowflake_mcp}" > "$output_file"
    else
        # Remove the placeholder (no Snowflake configuration)
        echo "${template_content//\{\{SNOWFLAKE_MCP\}\}/}" > "$output_file"
    fi
}

# If script is called directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -ne 2 ]]; then
        echo "Usage: $0 <include_snowflake:true|false> <output_file>"
        exit 1
    fi
    
    generate_crush_config "$1" "$2"
    echo "Configuration generated: $2"
fi

