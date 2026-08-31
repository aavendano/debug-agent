import { z } from 'zod'

// DataForSEO API response schema
export const DataForSEOResponseSchema = z.object({
  version: z.number(),
  status_code: z.number(),
  status_message: z.string(),
  time: z.string().optional(),
  cost: z.number().optional(),
  result_count: z.number().optional(),
  path: z.string().optional(),
  data: z.record(z.any()).optional(),
  results: z.array(z.record(z.any())).optional(),
})

export type DataForSEOResponse = z.infer<typeof DataForSEOResponseSchema>

// API endpoint configuration
export interface DataForSEOEndpoint {
  path: string
  method: 'GET' | 'POST'
  description: string
  parameters?: Record<string, string>
  requiredAuth: boolean
}

// Tool definition for MCP
export interface MCPTool {
  name: string
  description: string
  inputSchema: Record<string, any>
}

// CLI options
export interface CLIOptions {
  apiKey?: string
  endpoint?: string
  method?: string
  data?: Record<string, unknown>
  help?: boolean
  listEndpoints?: boolean
  version?: boolean
}

// Authentication configuration
export interface AuthConfig {
  apiKey: string
  username?: string
  password?: string
}

// API request configuration
export interface APIRequestConfig {
  endpoint: string
  method: 'GET' | 'POST'
  params?: Record<string, string | number | boolean>
  data?: Record<string, unknown>
  headers?: Record<string, string>
}
