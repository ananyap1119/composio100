# Manual audit selection

| App | Category | Verdict | Confidence | Main audit focus | Why selected |
|---|---|---|---|---|---|
| Salesforce | CRM | build_now | high | validated decisive claims | Evidence-finalized CRM baseline with OAuth and official MCP. |
| HubSpot | HubSpot Customer Platform | build_now | medium | validated decisive claims | Evidence-finalized self-serve CRM-platform case with OAuth and API-key paths. |
| Apify | Data, SEO and Scraping | build_now | medium | validated decisive claims | Evidence-finalized API-key data-platform case, contrasting with SaaS CRMs. |
| Close | CRM | unknown | low | Buildability remains unresolved from available evidence, buildability verdict remains unresolved | Credential-path uncertainty with several authentication options and otherwise broad API evidence. |
| Jira | Productivity and Project Management | unknown | low | write_operations: unresolved, api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved | Workspace-admin credential requirement tests existing-customer access and admin gating. |
| Otter AI | AI, Research and Media-native | unknown | low | api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved | Contact-vendor and workspace-admin path tests a gated, unusual integration. |
| Linear | Productivity and Project Management | unknown | low | authentication_methods: unresolved, documented_api: unresolved, read_operations: unresolved, write_operations: unresolved, api_breadth: unresolved, buildability verdict remains unresolved | API evidence is fundamentally incomplete: authentication, API, read and write are all unresolved. |
| Front | customer_service_platform | unknown | low | Normalization: write_operations: concrete value invalidated because evidence was missing, write_operations: unresolved, api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved | API evidence is partial: read is present but write and breadth remain unverified. |
| Shopify | Ecommerce | unknown | low | write_operations: unresolved, api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved | Marketplace-review path tests multi-tenant distribution and ecommerce access. |
| Zoho CRM | Customer Relationship Management (CRM) Software | unknown | low | api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved | Official MCP edge case with OAuth and API evidence but unresolved breadth/access dimensions. |

## Salesforce

Current verdict: build_now
Confidence: high
Selection reason: Evidence-finalized CRM baseline with OAuth and official MCP.
Primary audit focus: validated decisive claims

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- Salesforce: The #1 Agentic AI CRM | Salesforce AU — https://salesforce.com/
- Salesforce: The #1 Agentic AI CRM | Salesforce AU — https://salesforce.com/
- Authorization Through External Client Apps or Connected Apps and OAuth 2.0 | REST API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_oauth_and_connected_apps.htm
- Security and the API | SOAP API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_concepts_security.htm
- Security and the API | SOAP API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_concepts_security.htm
- Using the Client Credentials Flow for Easier API Authentication | Salesforce Developers Blog — https://developer.salesforce.com/blogs/2023/03/using-the-client-credentials-flow-for-easier-api-authentication
- Authorization Through External Client Apps or Connected Apps and OAuth 2.0 | REST API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_oauth_and_connected_apps.htm
- Authorization | Salesforce DX Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth.htm
- Security and the API | SOAP API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_concepts_security.htm
- The Salesforce Platform - Transformed for Tomorrow | Get Started with Fundamentals | Fundamentals | Salesforce Developers — https://architect.salesforce.com/docs/architect/fundamentals/guide/platform-transformation
- The Salesforce Platform - Transformed for Tomorrow | Get Started with Fundamentals | Fundamentals | Salesforce Developers — https://architect.salesforce.com/docs/architect/fundamentals/guide/platform-transformation
- Developer Documentation | Salesforce Developers — https://developer.salesforce.com/docs
- Introduction to REST API | REST API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm
- GraphQL API | Salesforce Developers — https://developer.salesforce.com/docs/platform/graphql/references/graphql?meta=Summary
- Introduction to REST API | REST API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm
- What is GraphQL API? | Get Started | GraphQL API | Salesforce Developers — https://developer.salesforce.com/docs/platform/graphql/guide/intro-graphql-api.html
- Create a Connected App | Getting Started With Mobile SDK for iOS and Android | Mobile SDK Development Guide | Salesforce Developers — https://developer.salesforce.com/docs/platform/mobile-sdk/guide/connected-apps-howto.html
- Create a Connected App | Getting Started With Mobile SDK for iOS and Android | Mobile SDK Development Guide | Salesforce Developers — https://developer.salesforce.com/docs/platform/mobile-sdk/guide/connected-apps-howto.html
- Introduction to REST API | REST API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm
- GraphQL API | Salesforce Developers — https://developer.salesforce.com/docs/platform/graphql/references/graphql?meta=Summary
- Developer Documentation | Salesforce Developers — https://developer.salesforce.com/docs
- Introduction to REST API | REST API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm
- About the API Families | API Reference | Connect REST API Developer Guide (New UI) | Salesforce Developers — https://developer.salesforce.com/docs/platform/connect-rest-api/references
- Introduction to REST API | REST API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm
- What is GraphQL API? | Get Started | GraphQL API | Salesforce Developers — https://developer.salesforce.com/docs/platform/graphql/guide/intro-graphql-api.html
- Authorization Through External Client Apps or Connected Apps and OAuth 2.0 | SOAP API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_oauth_and_connected_apps.htm
- Security and the API | SOAP API Developer Guide | Salesforce Developers — https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_concepts_security.htm
- What is GraphQL API? | Get Started | GraphQL API | Salesforce Developers — https://developer.salesforce.com/docs/platform/graphql/guide/intro-graphql-api.html

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes


## HubSpot

Current verdict: build_now
Confidence: medium
Selection reason: Evidence-finalized self-serve CRM-platform case with OAuth and API-key paths.
Primary audit focus: validated decisive claims

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- Grow Your Business on HubSpot's Customer Platform | HubSpot — https://www.hubspot.com/products/customer-platform
- HubSpot Product & Services Catalog — https://legal.hubspot.com/hubspot-product-and-services-catalog
- Authentication overview - HubSpot docs — https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview
- Make API requests using a service key (BETA) - HubSpot docs — https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys
- Developer Platform Basics & Onboarding — https://developers.hubspot.com/developer-platform-basics
- 2026-03 API reference - HubSpot docs — https://developers.hubspot.com/docs/api-reference/latest/overview
- 2026-03 API reference - HubSpot docs — https://developers.hubspot.com/docs/api-reference/latest/overview
- Using Object APIs - HubSpot docs — https://developers.hubspot.com/docs/guides/crm/using-object-apis
- Using Object APIs - HubSpot docs — https://developers.hubspot.com/docs/guides/crm/using-object-apis
- 2026-03 API reference - HubSpot docs — https://developers.hubspot.com/docs/api-reference/latest/overview

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes


## Apify

Current verdict: build_now
Confidence: medium
Selection reason: Evidence-finalized API-key data-platform case, contrasting with SaaS CRMs.
Primary audit focus: validated decisive claims

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- docs.apify.com — https://docs.apify.com/?fpr=dxxgr
- API integration | Platform | Apify Documentation — https://docs.apify.com/platform/integrations/api
- Apify API | Apify Documentation — https://docs.apify.com/api/v2
- Getting started | Academy | Apify Documentation — https://docs.apify.com/academy/getting-started
- API integration | Platform | Apify Documentation — https://docs.apify.com/platform/integrations/api
- API integration | Platform | Apify Documentation — https://docs.apify.com/platform/integrations/api
- Apify API | Apify Documentation — https://docs.apify.com/api/v2
- API integration | Platform | Apify Documentation — https://docs.apify.com/platform/integrations/api
- Apify API | Apify Documentation — https://docs.apify.com/api/v2
- API integration | Platform | Apify Documentation — https://docs.apify.com/platform/integrations/api
- Apify API | Apify Documentation — https://docs.apify.com/api/v2
- API integration | Platform | Apify Documentation — https://docs.apify.com/platform/integrations/api
- Apify API | Apify Documentation — https://docs.apify.com/api/v2
- API integration | Platform | Apify Documentation — https://docs.apify.com/platform/integrations/api
- Apify API | Apify Documentation — https://docs.apify.com/api/v2
- API integration | Platform | Apify Documentation — https://docs.apify.com/platform/integrations/api
- Apify API | Apify Documentation — https://docs.apify.com/api/v2

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes


## Close

Current verdict: unknown
Confidence: low
Selection reason: Credential-path uncertainty with several authentication options and otherwise broad API evidence.
Primary audit focus: Buildability remains unresolved from available evidence, buildability verdict remains unresolved

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- Close CRM | Sales CRM with Built-In AI Sales Agent — https://close.com/?referrer=wordpress.com
- API Overview | Close | Developer API Documentation — https://developer.close.com/api/overview
- API Overview | Close | Developer API Documentation — https://developer.close.com/api/overview
- API Overview | Close | Developer API Documentation — https://developer.close.com/api/overview
- API Overview | Close | Developer API Documentation — https://developer.close.com/api/overview
- API Overview | Close | Developer API Documentation — https://developer.close.com/api/overview
- API Overview | Close | Developer API Documentation — https://developer.close.com/api/overview
- API Overview | Close | Developer API Documentation — https://developer.close.com/api/overview
- Webhook Subscriptions - Close API Documentation — https://developer.close.com/resources/webhook-subscriptions

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes


## Jira

Current verdict: unknown
Confidence: low
Selection reason: Workspace-admin credential requirement tests existing-customer access and admin gating.
Primary audit focus: write_operations: unresolved, api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- Security for other integrations — https://developer.atlassian.com/cloud/jira/platform/security-for-other-integrations/
- OAuth 2.0 (3LO) apps — https://developer.atlassian.com/cloud/jira/software/oauth-2-3lo-apps/
- Security overview — https://developer.atlassian.com/cloud/jira/software/security-overview/
- Cloud and Data Center for developers — https://developer.atlassian.com/developer-guide/cloud-and-data-center-for-developers/
- The Jira Service Management Cloud REST API — https://developer.atlassian.com/cloud/jira/service-desk/rest/api-group-customer/
- The Jira Software Cloud REST API — https://developer.atlassian.com/cloud/jira/software/rest/intro/
- The Jira Software Cloud REST API — https://developer.atlassian.com/cloud/jira/software/rest/intro/
- The Jira Software Cloud REST API — https://developer.atlassian.com/cloud/jira/software/rest/intro/
- developer.atlassian.com — https://developer.atlassian.com/server/jira/platform/rest/v11002/intro

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes


## Otter AI

Current verdict: unknown
Confidence: low
Selection reason: Contact-vendor and workspace-admin path tests a gated, unusual integration.
Primary audit focus: api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- What is Otter? – Help Center — https://help.otter.ai/hc/en-us/articles/360035266494-What-is-Otter
- Otter.ai Public API – Help Center — https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API
- Connect Microsoft SharePoint to Otter.ai – Help Center — https://help.otter.ai/hc/en-us/articles/38533740881175-Microsoft-SharePoint-Otter-ai-Integration-Overview
- Outlook Extension | Manage Microsoft Teams Recording Permissions – Help Center — https://help.otter.ai/hc/en-us/articles/35561754307479-Manage-Microsoft-Teams-Recording-Permissions
- Directory Sync | SCIM – Help Center — https://help.otter.ai/hc/en-us/articles/39080325978391-Directory-Sync-SCIM
- Otter.ai Public API – Help Center — https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API
- Otter.ai Public API – Help Center — https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API
- Otter.ai Public API – Help Center — https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API
- Otter.ai Public API – Help Center — https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes


## Linear

Current verdict: unknown
Confidence: low
Selection reason: API evidence is fundamentally incomplete: authentication, API, read and write are all unresolved.
Primary audit focus: authentication_methods: unresolved, documented_api: unresolved, read_operations: unresolved, write_operations: unresolved, api_breadth: unresolved, buildability verdict remains unresolved

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- No official evidence URL retained.

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes


## Front

Current verdict: unknown
Confidence: low
Selection reason: API evidence is partial: read is present but write and breadth remain unverified.
Primary audit focus: Normalization: write_operations: concrete value invalidated because evidence was missing, write_operations: unresolved, api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- What is Front? Overview and How it Works — https://front.com/product
- Front | Customer service platform — powered by AI, designed for humans — https://front.com/
- AI Powered Customer Service Platform | Front — https://front.com/customer-service
- Omnichannel Customer Support in One Workspace | Front — https://front.com/product/omnichannel-support-inbox
- AI-Powered Customer Service for Modern Support Teams | Front — https://front.com/product/ai
- What is Front? Overview and How it Works — https://front.com/product
- About Page | Front — https://front.com/about
- Omnichannel Customer Support in One Workspace | Front — https://front.com/product/omnichannel-support-inbox
- How to create and revoke API tokens — https://help.front.com/en/articles/2331
- Developer resources for building API integrations — https://help.front.com/en/articles/2309
- How to create and revoke API tokens — https://help.front.com/en/articles/2331
- Developer resources for building API integrations — https://help.front.com/en/articles/2309
- Keeping a log of messages sent and received via Front — https://help.front.com/en/articles/2273
- Keeping a log of messages sent and received via Front — https://help.front.com/en/articles/2273
- Developer resources for building API integrations — https://help.front.com/en/articles/2309
- Get started with Front's MCP server [beta] — https://help.front.com/en/articles/4883136

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes


## Shopify

Current verdict: unknown
Confidence: low
Selection reason: Marketplace-review path tests multi-tenant distribution and ecommerce access.
Primary audit focus: write_operations: unresolved, api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- Authentication and authorization — https://shopify.dev/docs/apps/build/authentication-authorization
- Create an app — https://shopify.dev/docs/api/shop/guides/creating-a-client
- About client credentials — https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets
- Create an app — https://shopify.dev/docs/api/shop/guides/creating-a-client
- Generate access tokens for custom apps in the Shopify admin — https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/generate-app-access-tokens-admin
- App Store requirements — https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements
- Authentication and authorization — https://shopify.dev/docs/apps/build/authentication-authorization
- Create an app — https://shopify.dev/docs/api/shop/guides/creating-a-client
- Generate access tokens for custom apps in the Shopify admin — https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/generate-app-access-tokens-admin
- About client credentials — https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets
- About token acquisition — https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens
- Generate access tokens for custom apps in the Shopify admin — https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/generate-app-access-tokens-admin
- Generate access tokens for custom apps in the Shopify admin — https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/generate-app-access-tokens-admin
- About client credentials — https://shopify.dev/docs/apps/build/authentication-authorization/client-secrets
- Create an app — https://shopify.dev/docs/api/shop/guides/creating-a-client

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes


## Zoho CRM

Current verdict: unknown
Confidence: low
Selection reason: Official MCP edge case with OAuth and API evidence but unresolved breadth/access dimensions.
Primary audit focus: api_breadth: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved

### Claims to verify

- [ ] Category and one-line description
- [ ] Documented public API
- [ ] Authentication methods
- [ ] Read operations
- [ ] Write operations
- [ ] API breadth
- [ ] Independent developer credential access
- [ ] Existing-customer/admin access
- [ ] Multi-tenant or partner access
- [ ] MCP status
- [ ] Final buildability verdict

### Existing evidence

- What is Customer Relationship Management (CRM) software? | Complete Overview of Customer Relationship Management (CRM) Software - Zoho CRM — https://www.zoho.com/crm/crm-software.html
- What is Zoho CRM ? | Overview of Zoho CRM Software — https://www.zoho.com/crm/what-is-zoho-crm.html
- OAuth 2.0 Authentication | Zoho CRM API | V8 — https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html
- Zoho CRM | Developer Tools and API — https://www.zoho.com/crm/developer/
- Developer Resources | Zoho CRM — https://www.zoho.com/crm/developer/docs/
- Developer Resources | Zoho CRM — https://www.zoho.com/crm/developer/docs/
- Developer Resources | Zoho CRM — https://www.zoho.com/crm/developer/docs/
- Developer Resources | Zoho CRM — https://www.zoho.com/crm/developer/docs/
- Zoho CRM | Developer Tools and API — https://www.zoho.com/crm/developer/
- Bulk Write API - Overview | Zoho CRM API | V8 — https://www.zoho.com/crm/developer/docs/api/v8/bulk-write/overview.html
- Create Webhook API | Zoho CRM API | V8 — https://www.zoho.com/crm/developer/docs/api/v8/create-webhook.html
- Developer Resources | Zoho CRM — https://www.zoho.com/crm/developer/docs/
- Zoho CRM MCP - An Overview | Developer Tools — https://www.zoho.com/crm/developer/docs/mcp/overview.html

### Manual findings

Correct:
Incorrect:
Unclear:
Missing evidence:

### Corrections required

### Notes
