# Snowflake Docker Workaround

We are currently experiencing a **bug with the Snowflake MCP server** that prevents us from connecting via Studio.  

As a temporary workaround, we run the **Snowflake MCP server inside Docker** and connect via HTTP through Victoria Terminal.

---

## Current Hack / Testing Setup
To test locally, you need to run the Snowflake MCP server in Docker at the same time as Victoria.  

- MCP server repo: [Snowflake-Labs/mcp](https://github.com/Snowflake-Labs/mcp?tab=readme-ov-file)  
- Follow the Docker install instructions here: [Docker Deployment Guide](https://github.com/Snowflake-Labs/mcp?tab=readme-ov-file#docker-deployment)

### Required Environment Variables
Before starting Docker, set the following environment variables:  

```bash
export SNOWFLAKE_ACCOUNT="your-snowflake-account-here"
export SNOWFLAKE_USER="your-snowflake-username-here"
export SNOWFLAKE_PASSWORD="your-pat-token-here"
````

### Configuration File

Ensure that the config file located at:

```
${HOME}/.mcp/tools_config.yaml
```

matches the expected setup from:

```
./configs/mcp/snowflake_services.yaml
```

### Running the MCP Server in Docker

Use the following Docker command to start the MCP server:

```bash
docker run --rm \
  --name mcp-server-snowflake \
  -p 9000:9000 \
  -e SNOWFLAKE_ACCOUNT=${SNOWFLAKE_ACCOUNT} \
  -e SNOWFLAKE_USER=${SNOWFLAKE_USER} \
  -e SNOWFLAKE_PASSWORD=${SNOWFLAKE_PASSWORD} \
  -v ${HOME}/.mcp/tools_config.yaml:/app/services/tools_config.yaml:ro \
  mcp-server-snowflake
```

---

## Future State

* A bug report has been logged with Snowflake MCP (link TBD).
* Potentially, we could run this Dockerized MCP server in a controlled cloud environment rather than requiring local hacks.
