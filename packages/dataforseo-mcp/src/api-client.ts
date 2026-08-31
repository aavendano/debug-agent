import {
  DATAFORSEO_API_URL,
  DEFAULT_TIMEOUT_MS,
  AUTH_HEADER_NAME,
  CONTENT_TYPE_JSON,
  USER_AGENT,
} from './constants'
import type { APIRequestConfig, AuthConfig, DataForSEOResponse } from './types'
import { DataForSEOResponseSchema } from './types'
import { getEndpoint } from './endpoints'

export class DataForSEOClient {
  private apiKey?: string
  private username?: string
  private password?: string
  private timeout: number

  constructor(auth?: AuthConfig, timeout: number = DEFAULT_TIMEOUT_MS) {
    this.apiKey = auth?.apiKey
    this.username = auth?.username
    this.password = auth?.password
    this.timeout = timeout
  }

  setAuth(auth: AuthConfig): void {
    this.apiKey = auth.apiKey
    this.username = auth.username
    this.password = auth.password
  }

  private async fetchWithTimeout(
    url: string,
    options: RequestInit,
    timeout: number = this.timeout
  ): Promise<Response> {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      })
      return response
    } finally {
      clearTimeout(timeoutId)
    }
  }

  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {}

    if (this.apiKey) {
      headers[AUTH_HEADER_NAME] = `Basic ${Buffer.from(`${this.apiKey}:`).toString('base64')}`
    } else if (this.username && this.password) {
      headers[AUTH_HEADER_NAME] = `Basic ${Buffer.from(`${this.username}:${this.password}`).toString('base64')}`
    }

    return headers
  }

  async request<T = DataForSEOResponse>(
    config: APIRequestConfig
  ): Promise<T> {
    const endpoint = getEndpoint(config.endpoint)
    if (!endpoint) {
      throw new Error(`Unknown endpoint: ${config.endpoint}`)
    }

    const url = new URL(config.endpoint, DATAFORSEO_API_URL)

    // Add query parameters for GET requests
    if (config.method === 'GET' && config.params) {
      Object.entries(config.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value))
        }
      })
    }

    const headers: HeadersInit = {
      [CONTENT_TYPE_JSON]: CONTENT_TYPE_JSON,
      [USER_AGENT]: USER_AGENT,
      ...this.getAuthHeaders(),
      ...config.headers,
    }

    const fetchOptions: RequestInit = {
      method: config.method,
      headers,
    }

    // Add body for POST requests
    if (config.method === 'POST' && config.data) {
      fetchOptions.body = JSON.stringify(config.data)
    }

    const response = await this.fetchWithTimeout(url.toString(), fetchOptions)

    if (!response.ok) {
      const errorText = await response.text().catch(() => '')
      throw new Error(
        `API request failed with status ${response.status}: ${errorText}`
      )
    }

    const result = await response.json()

    // Validate response schema
    const validated = DataForSEOResponseSchema.safeParse(result)
    if (validated.success) {
      return validated.data as unknown as T
    }

    return result as T
  }

  async getAccountInfo(): Promise<DataForSEOResponse> {
    return this.request({ endpoint: '/v3/rest/account', method: 'GET' })
  }

  async getBacklinks(data: unknown): Promise<DataForSEOResponse> {
    return this.request({
      endpoint: '/v3/backlinks/backlinks',
      method: 'POST',
      data: Array.isArray(data) ? data : [data],
    })
  }

  async getOrganicSearch(data: unknown): Promise<DataForSEOResponse> {
    return this.request({
      endpoint: '/v3/organic/organic',
      method: 'POST',
      data: Array.isArray(data) ? data : [data],
    })
  }

  async getKeywordData(data: unknown): Promise<DataForSEOResponse> {
    return this.request({
      endpoint: '/v3/keywords_data/keywords_data',
      method: 'POST',
      data: Array.isArray(data) ? data : [data],
    })
  }

  async getDomainData(data: unknown): Promise<DataForSEOResponse> {
    return this.request({
      endpoint: '/v3/domain_data/domain_data',
      method: 'POST',
      data: Array.isArray(data) ? data : [data],
    })
  }

  async getOnPageAnalysis(data: unknown): Promise<DataForSEOResponse> {
    return this.request({
      endpoint: '/v3/on_page/on_page',
      method: 'POST',
      data: Array.isArray(data) ? data : [data],
    })
  }

  // Generic method for any endpoint
  async call(endpoint: string, data?: unknown): Promise<DataForSEOResponse> {
    const endpointInfo = getEndpoint(endpoint)
    if (!endpointInfo) {
      throw new Error(`Unknown endpoint: ${endpoint}`)
    }

    return this.request({
      endpoint,
      method: endpointInfo.method,
      data: data ? (Array.isArray(data) ? data : [data]) : undefined,
    })
  }
}

// Singleton client instance
export const client = new DataForSEOClient()

export function createClient(auth?: AuthConfig, timeout?: number): DataForSEOClient {
  return new DataForSEOClient(auth, timeout)
}
