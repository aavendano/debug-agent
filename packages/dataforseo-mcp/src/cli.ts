#!/usr/bin/env node

import { Command } from 'commander'
import pc from 'picocolors'
import prompts from 'prompts'
import {
  MCP_SERVER_NAME,
  MCP_SERVER_VERSION,
} from './constants'
import { getAllEndpoints, getEndpointsByCategory } from './endpoints'
import { createClient, DataForSEOClient } from './api-client'
import type { AuthConfig, CLIOptions } from './types'
import { DataForSEOMCPServer } from './mcp-server'

async function main(): Promise<void> {
  const program = new Command()

  program
    .name('dataforseo')
    .alias('dataforseo-mcp')
    .description('DataForSEO MCP server and CLI')
    .version(MCP_SERVER_VERSION)

  // MCP Server mode (default)
  program
    .command('server')
    .alias('start')
    .description('Start DataForSEO MCP server on stdio')
    .option('--api-key <key>', 'DataForSEO API key')
    .option('--username <username>', 'DataForSEO username')
    .option('--password <password>', 'DataForSEO password')
    .action(async (options) => {
      const authConfig: AuthConfig = {
        apiKey: options.apiKey,
        username: options.username,
        password: options.password,
      }

      const server = new DataForSEOMCPServer()
      
      // Configure client with auth if provided
      if (authConfig.apiKey || authConfig.username) {
        const client = createClient(authConfig)
        // Store auth in server instance
        ;(server as any).authConfig = authConfig
        ;(server as any).dfClient = client
      }

      console.log(pc.green(`🚀 Starting ${MCP_SERVER_NAME} v${MCP_SERVER_VERSION}`))
      console.log(pc.gray('MCP server running on stdio...'))

      await server.start()
    })

  // CLI mode for direct API requests
  program
    .command('call')
    .description('Make a direct DataForSEO API request')
    .requiredOption('--endpoint <endpoint>', 'API endpoint path (e.g., /v3/backlinks/backlinks)')
    .option('--method <method>', 'HTTP method (GET or POST)', 'POST')
    .option('--api-key <key>', 'DataForSEO API key')
    .option('--username <username>', 'DataForSEO username')
    .option('--password <password>', 'DataForSEO password')
    .option('--data <data>', 'JSON string for request data', '')
    .action(async (options) => {
      const authConfig: AuthConfig = {
        apiKey: options.apiKey,
        username: options.username,
        password: options.password,
      }

      if (!authConfig.apiKey && !authConfig.username) {
        console.error(pc.red('❌ Error: API key or username/password required'))
        console.error(pc.gray('Use --api-key, --username, or --password'))
        process.exit(1)
      }

      const client = createClient(authConfig)

      try {
        let data = undefined
        if (options.data) {
          try {
            data = JSON.parse(options.data)
          } catch {
            console.error(pc.red('❌ Error: Invalid JSON data'))
            process.exit(1)
          }
        }

        const response = await client.call(
          options.endpoint,
          data
        )

        console.log(pc.green('✅ API request successful'))
        console.log(pc.gray('Response:'))
        console.log(JSON.stringify(response, null, 2))
      } catch (error) {
        console.error(pc.red(`❌ Error: ${error instanceof Error ? error.message : String(error)}`))
        process.exit(1)
      }
    })

  // List endpoints
  program
    .command('endpoints')
    .alias('list')
    .description('List available DataForSEO API endpoints')
    .option('--category <category>', 'Filter by category (backlinks, organic, paid, etc.)')
    .action(async (options) => {
      const endpoints = options.category
        ? getEndpointsByCategory(options.category)
        : getAllEndpoints()

      if (endpoints.length === 0) {
        console.log(pc.yellow(`No endpoints found for category: ${options.category}`))
        return
      }

      console.log(pc.blue(`Available DataForSEO endpoints${options.category ? ` (${options.category})` : ''}:`))
      console.log(pc.gray('='.repeat(80)))

      for (const endpoint of endpoints) {
        console.log(pc.green(`📍 ${endpoint.path}`))
        console.log(pc.gray(`   Method: ${endpoint.method}`))
        console.log(pc.gray(`   Description: ${endpoint.description}`))
        console.log('')
      }

      console.log(pc.gray(`Total: ${endpoints.length} endpoint${endpoints.length !== 1 ? 's' : ''}`))
    })

  // Interactive mode
  program
    .command('interactive')
    .alias('i')
    .description('Interactive DataForSEO API explorer')
    .option('--api-key <key>', 'DataForSEO API key')
    .option('--username <username>', 'DataForSEO username')
    .option('--password <password>', 'DataForSEO password')
    .action(async (options) => {
      const authConfig: AuthConfig = {
        apiKey: options.apiKey,
        username: options.username,
        password: options.password,
      }

      if (!authConfig.apiKey && !authConfig.username) {
        console.log(pc.yellow('🔑 No authentication provided, will prompt for API key'))
      }

      console.log(pc.blue('🎯 DataForSEO Interactive Explorer'))
      console.log(pc.gray('='.repeat(50)))

      // Get or prompt for API key
      let apiKey = authConfig.apiKey
      if (!apiKey && !authConfig.username) {
        const response = await prompts({
          type: 'password',
          name: 'apiKey',
          message: 'Enter your DataForSEO API key:',
        })

        if (prompts.isCancel(response)) {
          console.log(pc.gray('Cancelled'))
          process.exit(0)
        }

        apiKey = response.apiKey
        authConfig.apiKey = apiKey
      }

      const client = createClient(authConfig)

      // List categories
      const categories = [
        'backlinks',
        'organic',
        'paid',
        'keywords',
        'rank_tracker',
        'domain_data',
        'content_data',
        'on_page',
        'local_seo',
        'account',
      ]

      const categoryResponse = await prompts({
        type: 'select',
        name: 'category',
        message: 'Select a category:',
        choices: [
          ...categories.map((c) => ({ title: c, value: c })),
          { title: 'All endpoints', value: 'all' },
        ],
      })

      if (prompts.isCancel(categoryResponse)) {
        console.log(pc.gray('Cancelled'))
        process.exit(0)
      }

      const endpoints = categoryResponse.category === 'all'
        ? getAllEndpoints()
        : getEndpointsByCategory(categoryResponse.category)

      const endpointResponse = await prompts({
        type: 'select',
        name: 'endpoint',
        message: 'Select an endpoint:',
        choices: endpoints.map((e) => ({
          title: `${e.method} ${e.path} - ${e.description}`,
          value: e.path,
        })),
      })

      if (prompts.isCancel(endpointResponse)) {
        console.log(pc.gray('Cancelled'))
        process.exit(0)
      }

      const endpoint = endpointResponse.endpoint
      const endpointInfo = getAllEndpoints().find((e) => e.path === endpoint)

      if (!endpointInfo) {
        console.error(pc.red('❌ Endpoint not found'))
        process.exit(1)
      }

      console.log(pc.blue(`\n📝 Endpoint: ${endpoint}`))
      console.log(pc.gray(`Method: ${endpointInfo.method}`))
      console.log(pc.gray(`Description: ${endpointInfo.description}`))

      // Get request data
      const dataResponse = await prompts({
        type: 'text',
        name: 'data',
        message: 'Enter request data (JSON format, leave empty for none):',
      })

      if (prompts.isCancel(dataResponse)) {
        console.log(pc.gray('Cancelled'))
        process.exit(0)
      }

      try {
        const data = dataResponse.data ? JSON.parse(dataResponse.data) : undefined
        const response = await client.call(endpoint, data)

        console.log(pc.green('\n✅ API request successful'))
        console.log(pc.gray('Response:'))
        console.log(JSON.stringify(response, null, 2))
      } catch (error) {
        console.error(pc.red(`\n❌ Error: ${error instanceof Error ? error.message : String(error)}`))
        process.exit(1)
      }
    })

  // Account info
  program
    .command('account')
    .description('Get DataForSEO account information')
    .requiredOption('--api-key <key>', 'DataForSEO API key')
    .action(async (options) => {
      const client = createClient({ apiKey: options.apiKey })

      try {
        const accountInfo = await client.getAccountInfo()
        console.log(pc.green('✅ Account information retrieved'))
        console.log(JSON.stringify(accountInfo, null, 2))
      } catch (error) {
        console.error(pc.red(`❌ Error: ${error instanceof Error ? error.message : String(error)}`))
        process.exit(1)
      }
    })

  // Parse arguments
  const args = process.argv.slice(2)

  // If no arguments, start MCP server by default
  if (args.length === 0) {
    await program.parseAsync(['server'])
    return
  }

  await program.parseAsync(process.argv)
}

main().catch((error) => {
  console.error(pc.red(`Fatal error: ${error instanceof Error ? error.message : String(error)}`))
  process.exit(1)
})
