# DataForSEO MCP Server

MCP server and CLI for LLM agents to browse DataForSEO API documentation and make authenticated API requests. By default the binary starts an MCP server on stdio; CLI commands are an optional second mode.

## Installation

```bash
npm install dataforseo-mcp
```

## Usage

### MCP Server Mode (Default)

Run the MCP server on stdio:

```bash
dataforseo-mcp
# or
dataforseo
```

The server will start and listen on stdio for MCP protocol messages.

With authentication:

```bash
dataforseo server --api-key YOUR_API_KEY
```

### CLI Mode

Make direct API requests:

```bash
# Call an endpoint
dataforseo call --endpoint /v3/backlinks/backlinks --api-key YOUR_API_KEY --data '{"targets": ["example.com"]}'

# Get account information
dataforseo account --api-key YOUR_API_KEY

# List available endpoints
dataforseo endpoints

# Filter endpoints by category
dataforseo endpoints --category backlinks

# Interactive mode
dataforseo interactive
```

### Common Endpoints

- **Backlinks**: `/v3/backlinks/backlinks` - Get backlinks data
- **Organic Search**: `/v3/organic/organic` - Get organic search results
- **Keyword Data**: `/v3/keywords_data/keywords_data` - Get keyword metrics
- **Domain Data**: `/v3/domain_data/domain_data` - Get domain metrics
- **Account Info**: `/v3/rest/account` - Get account information

### Authentication

DataForSEO supports two authentication methods:

1. **API Key** (recommended):
   ```bash
   --api-key YOUR_API_KEY
   ```

2. **Username/Password**:
   ```bash
   --username YOUR_USERNAME --password YOUR_PASSWORD
   ```

## MCP Tools

When running as an MCP server, the following tools are available:

- `dataforseo_list_endpoints` - List all available endpoints
- `dataforseo_account_info` - Get account information
- `dataforseo_configure` - Configure authentication for the session
- `dataforseo_v3_backlinks_backlinks` - Get backlinks data
- `dataforseo_v3_organic_organic` - Get organic search results
- `dataforseo_v3_keywords_data_keywords_data` - Get keyword data
- And more for all DataForSEO endpoints

## Development

```bash
# Build
pnpm build

# Run server
pnpm start

# Type check
pnpm typecheck

# Lint and format
pnpm check
```

## License

MIT
