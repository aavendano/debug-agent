import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js'
import {
  MCP_SERVER_NAME,
  MCP_SERVER_VERSION,
} from './constants'
import { getAllEndpoints, getEndpointsByCategory } from './endpoints'
import { client, createClient, DataForSEOClient } from './api-client'
import type { AuthConfig } from './types'

interface MCPToolDefinition {
  name: string
  description: string
  inputSchema: {
    type: string
    properties: Record<string, any>
    required?: string[]
  }
}

interface MCPToolResult {
  content: Array<{
    type: string
    text?: string
    uri?: string
  }>
  isError?: boolean
  error?: string
}

export class DataForSEOMCPServer {
  private server: Server
  private transport: StdioServerTransport
  private dfClient: DataForSEOClient
  private authConfig?: AuthConfig

  constructor() {
    this.server = new Server(
      {
        name: MCP_SERVER_NAME,
        version: MCP_SERVER_VERSION,
      },
      {
        capabilities: {
          tools: {},
        },
      }
    )
    this.transport = new StdioServerTransport()
    this.dfClient = client
    this.setupHandlers()
  }

  private setupHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      const tools = this.getAvailableTools()
      return { tools }
    })

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params
      return this.handleToolCall(name, args)
    })
  }

  private getAvailableTools(): MCPToolDefinition[] {
    const endpoints = getAllEndpoints()
    const tools: MCPToolDefinition[] = []

    // Add endpoint-specific tools
    for (const endpoint of endpoints) {
      const endpointName = endpoint.path.replace(/\/v3\//g, '').replace(/\//g, '_')
      tools.push({
        name: `dataforseo_${endpointName}`,
        description: endpoint.description,
        inputSchema: {
          type: 'object',
          properties: {
            data: {
              type: 'object',
              description: 'Request data for the API endpoint',
            },
            apiKey: {
              type: 'string',
              description: 'DataForSEO API key (optional if already configured)',
            },
          },
          required: ['data'],
        },
      })
    }

    // Add utility tools
    tools.push(
      {
        name: 'dataforseo_list_endpoints',
        description: 'List all available DataForSEO API endpoints',
        inputSchema: {
          type: 'object',
          properties: {
            category: {
              type: 'string',
              description: 'Filter endpoints by category (backlinks, organic, paid, keywords, etc.)',
            },
          },
        },
      },
      {
        name: 'dataforseo_account_info',
        description: 'Get DataForSEO account information and API usage statistics',
        inputSchema: {
          type: 'object',
          properties: {
            apiKey: {
              type: 'string',
              description: 'DataForSEO API key',
            },
          },
          required: ['apiKey'],
        },
      },
      {
        name: 'dataforseo_configure',
        description: 'Configure DataForSEO authentication for the session',
        inputSchema: {
          type: 'object',
          properties: {
            apiKey: {
              type: 'string',
              description: 'DataForSEO API key',
            },
            username: {
              type: 'string',
              description: 'DataForSEO username (alternative to API key)',
            },
            password: {
              type: 'string',
              description: 'DataForSEO password (alternative to API key)',
            },
          },
          required: [],
        },
      }
    )

    return tools
  }

  private async handleToolCall(
    name: string,
    args: Record<string, unknown>
  ): Promise<MCPToolResult> {
    try {
      // Handle configuration
      if (name === 'dataforseo_configure') {
        const apiKey = args.apiKey as string | undefined
        const username = args.username as string | undefined
        const password = args.password as string | undefined

        this.authConfig = {
          apiKey,
          username,
          password,
        }
        this.dfClient = createClient(this.authConfig)

        return {
          content: [
            {
              type: 'text',
              text: '✅ DataForSEO authentication configured successfully',
            },
          ],
        }
      }

      // Handle list endpoints
      if (name === 'dataforseo_list_endpoints') {
        const category = args.category as string | undefined
        const endpoints = category
          ? getEndpointsByCategory(category)
          : getAllEndpoints()

        const endpointList = endpoints
          .map((e) => `- **${e.path}** (${e.method}): ${e.description}`)
          .join('\n')

        return {
          content: [
            {
              type: 'text',
              text: `Available DataForSEO endpoints:\n\n${endpointList}`,
            },
          ],
        }
      }

      // Handle account info
      if (name === 'dataforseo_account_info') {
        const apiKey = args.apiKey as string | undefined
        const authConfig = apiKey ? { apiKey } : this.authConfig

        if (!authConfig?.apiKey && !authConfig?.username) {
          throw new Error('API key or username/password required')
        }

        const client = createClient(authConfig)
        const accountInfo = await client.getAccountInfo()

        return {
          content: [
            {
              type: 'text',
              text: `Account Information:\n\n${JSON.stringify(accountInfo, null, 2)}`,
            },
          ],
        }
      }

      // Handle endpoint calls
      if (name.startsWith('dataforseo_')) {
        const endpointPath = `/v3/${name.replace('dataforseo_', '').replace(/_/g, '/')}`
        const data = args.data as unknown
        const apiKey = args.apiKey as string | undefined

        const authConfig = apiKey ? { apiKey } : this.authConfig

        if (!authConfig?.apiKey && !authConfig?.username) {
          throw new Error('API key or username/password required')
        }

        const client = createClient(authConfig)
        const response = await client.call(endpointPath, data)

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(response, null, 2),
            },
          ],
        }
      }

      throw new Error(`Unknown tool: ${name}`)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error)
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error: ${errorMessage}`,
          },
        ],
        isError: true,
        error: errorMessage,
      }
    }
  }

  async start(): Promise<void> {
    await this.server.connect(this.transport)
    console.log(`🚀 ${MCP_SERVER_NAME} v${MCP_SERVER_VERSION} started on stdio`)
  }

  async stop(): Promise<void> {
    await this.transport.close()
    await this.server.close()
  }
}

// Singleton server instance
export const server = new DataForSEOMCPServer()

export function createMCPServer(): DataForSEOMCPServer {
  return new DataForSEOMCPServer()
}
