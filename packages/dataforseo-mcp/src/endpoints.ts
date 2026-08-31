import type { DataForSEOEndpoint } from './types'

// DataForSEO API endpoints
// Reference: https://docs.dataforseo.com/v3/
export const DATAFORSEO_ENDPOINTS: DataForSEOEndpoint[] = [
  // SEO Data
  {
    path: '/v3/backlinks/backlinks',
    method: 'POST',
    description: 'Get backlinks data for a domain or URL',
    requiredAuth: true,
  },
  {
    path: '/v3/backlinks/domains_intersection',
    method: 'POST',
    description: 'Find domains that link to multiple specified targets',
    requiredAuth: true,
  },
  {
    path: '/v3/backlinks/live_backlinks',
    method: 'POST',
    description: 'Get live backlinks data',
    requiredAuth: true,
  },
  {
    path: '/v3/backlinks/new_lost_backlinks',
    method: 'POST',
    description: 'Get new and lost backlinks',
    requiredAuth: true,
  },
  {
    path: '/v3/backlinks/referring_domains',
    method: 'POST',
    description: 'Get referring domains data',
    requiredAuth: true,
  },
  {
    path: '/v3/backlinks/referring_ips',
    method: 'POST',
    description: 'Get referring IPs data',
    requiredAuth: true,
  },
  {
    path: '/v3/backlinks/anchors',
    method: 'POST',
    description: 'Get anchor text data',
    requiredAuth: true,
  },
  {
    path: '/v3/backlinks/texts',
    method: 'POST',
    description: 'Get link texts data',
    requiredAuth: true,
  },
  // Organic Search Data
  {
    path: '/v3/organic/organic',
    method: 'POST',
    description: 'Get organic search results',
    requiredAuth: true,
  },
  {
    path: '/v3/organic/organic_live',
    method: 'POST',
    description: 'Get live organic search results',
    requiredAuth: true,
  },
  {
    path: '/v3/organic/competitors',
    method: 'POST',
    description: 'Get organic competitors data',
    requiredAuth: true,
  },
  {
    path: '/v3/organic/historical',
    method: 'POST',
    description: 'Get historical organic search data',
    requiredAuth: true,
  },
  // Paid Search Data
  {
    path: '/v3/paid/paid',
    method: 'POST',
    description: 'Get paid search results',
    requiredAuth: true,
  },
  {
    path: '/v3/paid/paid_live',
    method: 'POST',
    description: 'Get live paid search results',
    requiredAuth: true,
  },
  {
    path: '/v3/paid/competitors',
    method: 'POST',
    description: 'Get paid competitors data',
    requiredAuth: true,
  },
  // Keyword Data
  {
    path: '/v3/keywords_data/keywords_data',
    method: 'POST',
    description: 'Get keyword data including search volume, CPC, competition',
    requiredAuth: true,
  },
  {
    path: '/v3/keywords_data/keywords_for_url',
    method: 'POST',
    description: 'Get keywords for a specific URL',
    requiredAuth: true,
  },
  {
    path: '/v3/keywords_data/keywords_group',
    method: 'POST',
    description: 'Get grouped keyword data',
    requiredAuth: true,
  },
  // Rank Tracking
  {
    path: '/v3/rank_tracker/rank_tracker',
    method: 'POST',
    description: 'Get rank tracking data',
    requiredAuth: true,
  },
  {
    path: '/v3/rank_tracker/rank_tracker_live',
    method: 'POST',
    description: 'Get live rank tracking data',
    requiredAuth: true,
  },
  // Domain Data
  {
    path: '/v3/domain_data/domain_data',
    method: 'POST',
    description: 'Get domain data including metrics and statistics',
    requiredAuth: true,
  },
  {
    path: '/v3/domain_data/domain_whosis',
    method: 'POST',
    description: 'Get domain WHOIS information',
    requiredAuth: true,
  },
  // Content Data
  {
    path: '/v3/content_data/content_data',
    method: 'POST',
    description: 'Get content data and analysis',
    requiredAuth: true,
  },
  {
    path: '/v3/content_data/content_duplicates',
    method: 'POST',
    description: 'Find duplicate content',
    requiredAuth: true,
  },
  // Technical SEO
  {
    path: '/v3/on_page/on_page',
    method: 'POST',
    description: 'Get on-page SEO analysis',
    requiredAuth: true,
  },
  {
    path: '/v3/on_page/on_page_issues',
    method: 'POST',
    description: 'Get on-page SEO issues',
    requiredAuth: true,
  },
  // Local SEO
  {
    path: '/v3/local_seo/local_seo',
    method: 'POST',
    description: 'Get local SEO data',
    requiredAuth: true,
  },
  {
    path: '/v3/local_seo/local_listings',
    method: 'POST',
    description: 'Get local business listings data',
    requiredAuth: true,
  },
  // Account information
  {
    path: '/v3/rest/account',
    method: 'GET',
    description: 'Get account information and API usage statistics',
    requiredAuth: true,
  },
]

// Get endpoint by path
export function getEndpoint(path: string): DataForSEOEndpoint | undefined {
  return DATAFORSEO_ENDPOINTS.find((endpoint) => endpoint.path === path)
}

// Get all endpoints
export function getAllEndpoints(): DataForSEOEndpoint[] {
  return [...DATAFORSEO_ENDPOINTS]
}

// Get endpoints by category
export function getEndpointsByCategory(category: string): DataForSEOEndpoint[] {
  const categoryEndpoints: Record<string, string[]> = {
    backlinks: [
      '/v3/backlinks/backlinks',
      '/v3/backlinks/domains_intersection',
      '/v3/backlinks/live_backlinks',
      '/v3/backlinks/new_lost_backlinks',
      '/v3/backlinks/referring_domains',
      '/v3/backlinks/referring_ips',
      '/v3/backlinks/anchors',
      '/v3/backlinks/texts',
    ],
    organic: [
      '/v3/organic/organic',
      '/v3/organic/organic_live',
      '/v3/organic/competitors',
      '/v3/organic/historical',
    ],
    paid: [
      '/v3/paid/paid',
      '/v3/paid/paid_live',
      '/v3/paid/competitors',
    ],
    keywords: [
      '/v3/keywords_data/keywords_data',
      '/v3/keywords_data/keywords_for_url',
      '/v3/keywords_data/keywords_group',
    ],
    rank_tracker: [
      '/v3/rank_tracker/rank_tracker',
      '/v3/rank_tracker/rank_tracker_live',
    ],
    domain_data: [
      '/v3/domain_data/domain_data',
      '/v3/domain_data/domain_whosis',
    ],
    content_data: [
      '/v3/content_data/content_data',
      '/v3/content_data/content_duplicates',
    ],
    on_page: [
      '/v3/on_page/on_page',
      '/v3/on_page/on_page_issues',
    ],
    local_seo: [
      '/v3/local_seo/local_seo',
      '/v3/local_seo/local_listings',
    ],
    account: ['/v3/rest/account'],
  }

  const paths = categoryEndpoints[category.toLowerCase()]
  if (!paths) return []

  return DATAFORSEO_ENDPOINTS.filter((endpoint) => paths.includes(endpoint.path))
}
