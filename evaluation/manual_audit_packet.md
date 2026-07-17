# Manual audit packet

This packet is intentionally uncompleted.

## Salesforce (`salesforce`)
- Category: CRM
- Verdict: build_now
- Confidence: high
- Decisive claims: none recorded
- Evidence:
  - [https://salesforce.com/](https://salesforce.com/) — Salesforce is the#1 AI CRM(customer relationship management) platform.
  - [https://salesforce.com/](https://salesforce.com/) — Salesforce is the#1 AI CRM(customer relationship management) platform. We bring companies and customers together by providing a unified set of applications, powered by agentic AI and data. This enables every department to work as one, including sales, service, marketing, commerce, and IT.
  - [https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_oauth_and_connected_apps.htm](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_oauth_and_connected_apps.htm) — To implement this authorization, use either an external client app or a connected app and an OAuth 2.0 authorization flow.
  - [https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_concepts_security.htm](https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_concepts_security.htm) — If the permission isn’t set, users must add their security token to the end of their password to log in.
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 

## HubSpot (`hubspot`)
- Category: HubSpot Customer Platform
- Verdict: build_now
- Confidence: medium
- Decisive claims: Normalization: supplementary extraction degraded safely: ModelQuotaExhausted, existing_customer_access: unresolved, multi_tenant_integration_access: unresolved, graphql: unresolved, bulk_operations: unresolved, webhooks_events: unresolved, websocket: unresolved, sdk_available: unresolved, mcp_status: unresolved
- Evidence:
  - [https://www.hubspot.com/products/customer-platform](https://www.hubspot.com/products/customer-platform) — HubSpot Customer Platform
  - [https://legal.hubspot.com/hubspot-product-and-services-catalog](https://legal.hubspot.com/hubspot-product-and-services-catalog) — HubSpot is a customer platform consisting of several premium products — Marketing Hub, Sales Hub, Service Hub, Content Hub, Data Hub, Revenue Hub, as well as Smart CRM, a system of record that unifies customer data across your teams.
  - [https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview) — If you plan to distribute your app to multiple accounts (either through listing on the HubSpot Marketplace or by managing specific authorized accounts), your app must be built using OAuth authentication.
  - [https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys](https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/account-service-keys) — you can use service keys to query HubSpot's REST APIs directly without having to use the CLI or other platform developer tools first.
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 

## Pipedrive (`pipedrive`)
- Category: CRM
- Verdict: build_now
- Confidence: medium
- Decisive claims: Normalization: rest: concrete value invalidated because evidence was missing, existing_customer_access: unresolved, multi_tenant_integration_access: unresolved, rest: unresolved, graphql: unresolved, bulk_operations: unresolved, websocket: unresolved, sdk_available: unresolved, mcp_status: unresolved
- Evidence:
  - [https://www.pipedrive.com/en/what-is-pipedrive-crm](https://www.pipedrive.com/en/what-is-pipedrive-crm) — Pipedrive is an easy-to-use, effective CRM platform
  - [https://www.pipedrive.com/en/what-is-pipedrive-crm](https://www.pipedrive.com/en/what-is-pipedrive-crm) — Pipedrive is an easy-to-use, effective CRM platform designed to help grow your business from day one.
  - [https://developers.pipedrive.com/tutorials/adding-leads-to-pipedrive](https://developers.pipedrive.com/tutorials/adding-leads-to-pipedrive) — You can use either an API token (see the code snippet below) or OAuth.
  - [https://developers.pipedrive.com/docs/api/v1/Oauth](https://developers.pipedrive.com/docs/api/v1/Oauth) — Using OAuth 2.0 is necessary for developing apps that are available in the Pipedrive Marketplace.
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 

## Podio (`podio`)
- Category: CRM
- Verdict: unknown
- Confidence: low
- Decisive claims: category: unresolved, authentication_methods: unresolved, existing_customer_access: unresolved, multi_tenant_integration_access: unresolved, rest: unresolved, read_operations: unresolved, write_operations: unresolved, api_breadth: unresolved, graphql: unresolved, bulk_operations: unresolved, websocket: unresolved, sdk_available: unresolved, mcp_status: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved
- Evidence:
  - [https://company.podio.com/resources/getstarted.pdf](https://company.podio.com/resources/getstarted.pdf) — In Podio you work in workspaces that belong to an organization.
  - [https://podio.com/signup?force_locale=en_US](https://podio.com/signup?force_locale=en_US) — Create your free account and join over 500,000 teams getting their work done on Podio.
  - [https://workflow-automation.podio.com/help/use-of-the-hook-checkbox.php](https://workflow-automation.podio.com/help/use-of-the-hook-checkbox.php) — A WebHook is an HTTP callback: this is the notification between Podio and Workflow Automations to inform the other, that an action or update has occurred.
  - [https://workflow-automation.podio.com/help/use-of-the-hook-checkbox.php](https://workflow-automation.podio.com/help/use-of-the-hook-checkbox.php) — By default, any update made in Podio generates a Hook Event
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 

## Zoho CRM (`zoho-crm`)
- Category: Customer Relationship Management (CRM) Software
- Verdict: unknown
- Confidence: low
- Decisive claims: existing_customer_access: unresolved, multi_tenant_integration_access: unresolved, api_breadth: unresolved, websocket: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved
- Evidence:
  - [https://www.zoho.com/crm/crm-software.html](https://www.zoho.com/crm/crm-software.html) — Complete Overview of Customer Relationship Management (CRM) Software - Zoho CRM
  - [https://www.zoho.com/crm/what-is-zoho-crm.html](https://www.zoho.com/crm/what-is-zoho-crm.html) — Zoho CRM acts as a single repository to bring your sales, marketing, and customer support activities together, and streamline your process, policy, and people in one platform.
  - [https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html](https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html) — The Zoho CRM API uses the OAuth 2.0 protocol for authentication.
  - [https://www.zoho.com/crm/developer/](https://www.zoho.com/crm/developer/) — Sign Up For Free
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 

## Attio (`attio`)
- Category: CRM
- Verdict: build_now
- Confidence: medium
- Decisive claims: Normalization: description: concrete value invalidated because evidence was missing, description: unresolved, existing_customer_access: unresolved, multi_tenant_integration_access: unresolved, graphql: unresolved, bulk_operations: unresolved, websocket: unresolved
- Evidence:
  - [https://attio.com/](https://attio.com/) — Attio: The CRM for agentic revenue
  - [https://docs.attio.com/rest-api/guides/authentication](https://docs.attio.com/rest-api/guides/authentication) — By implementing an OAuth 2.0 flow
  - [https://docs.attio.com/sdk/guides/creating-an-app](https://docs.attio.com/sdk/guides/creating-an-app) — Head over to our Developer dashboard and sign in with your Attio account.
  - [https://docs.attio.com/docs/overview](https://docs.attio.com/docs/overview) — This allows developers to build apps that read and write information to and from Attio workspaces.
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 

## Twenty (`twenty`)
- Category: CRM
- Verdict: build_with_customer_credentials
- Confidence: medium
- Decisive claims: independent_developer_access: unresolved, multi_tenant_integration_access: unresolved, graphql: unresolved, websocket: unresolved, mcp_status: unresolved
- Evidence:
  - [https://docs.twenty.com/user-guide/getting-started/capabilities/what-is-twenty](https://docs.twenty.com/user-guide/getting-started/capabilities/what-is-twenty) — Twenty is an open-source CRM
  - [https://docs.twenty.com/user-guide/getting-started/capabilities/what-is-twenty](https://docs.twenty.com/user-guide/getting-started/capabilities/what-is-twenty) — Twenty is an open-source CRM that gives you the building blocks to create exactly what your business needs.
  - [https://docs.twenty.com/developers/extend/oauth](https://docs.twenty.com/developers/extend/oauth) — Internal scripts, automation | API Key
  - [https://docs.twenty.com/developers/extend/api](https://docs.twenty.com/developers/extend/api) — Create an API key in Settings → API & Webhooks → + Create key.
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 

## Close (`close`)
- Category: CRM
- Verdict: unknown
- Confidence: low
- Decisive claims: category: unresolved, independent_developer_access: unresolved, existing_customer_access: unresolved, multi_tenant_integration_access: unresolved, graphql: unresolved, bulk_operations: unresolved, websocket: unresolved, sdk_available: unresolved, mcp_status: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved
- Evidence:
  - [https://close.com/?referrer=wordpress.com](https://close.com/?referrer=wordpress.com) — It combines calling, email, SMS, pipeline management, reporting, and an AI sales agent named Chloe into a single platform.
  - [https://developer.close.com/api/overview](https://developer.close.com/api/overview) — - API Keys — Best for scripts, internal tools, and server-side integrations.
Use HTTP Basic Auth with your API key as the username and an empty password.
  - [https://developer.close.com/api/overview](https://developer.close.com/api/overview) — We publish an OpenAPI spec at:
  - [https://developer.close.com/api/overview](https://developer.close.com/api/overview) — Close uses industry-standard REST conventions
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 

## Copper (`copper`)
- Category: Enterprise CRM
- Verdict: unknown
- Confidence: low
- Decisive claims: independent_developer_access: unresolved, existing_customer_access: unresolved, multi_tenant_integration_access: unresolved, graphql: unresolved, websocket: unresolved, mcp_status: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved
- Evidence:
  - [https://www.copper.com/enterprise-crm](https://www.copper.com/enterprise-crm) — Best Enterprise CRM Software
  - [https://www.copper.com/enterprise-crm](https://www.copper.com/enterprise-crm) — Meet the first CRM that drives productivity across the entire organization.
  - [https://developer.copper.com/introduction/authentication.html](https://developer.copper.com/introduction/authentication.html) — There are two ways to access the Copper Developer API: API keys and OAuth2.0.
  - [https://developer.copper.com/](https://developer.copper.com/) — The Copper Web API allows you to access and build your own applications
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 

## DealCloud (`dealcloud`)
- Category: CRM
- Verdict: unknown
- Confidence: low
- Decisive claims: Normalization: existing_customer_access: concrete value invalidated because evidence was missing, category: unresolved, description: unresolved, independent_developer_access: unresolved, existing_customer_access: unresolved, multi_tenant_integration_access: unresolved, graphql: unresolved, bulk_operations: unresolved, webhooks_events: unresolved, websocket: unresolved, Buildability remains unresolved from available evidence, buildability verdict remains unresolved
- Evidence:
  - [https://api.docs.dealcloud.com/docs/apikeys](https://api.docs.dealcloud.com/docs/apikeys) — Copy API Key to Clipboard to copy your API key for use in integrations or API requests.
  - [https://api.docs.dealcloud.com/docs/token](https://api.docs.dealcloud.com/docs/token) — DealCloud uses the OAuth2 Client Credentials flow to generate a bearer token
  - [https://api.docs.dealcloud.com/docs](https://api.docs.dealcloud.com/docs) — This site provides a comprehensive overview of our REST APIs, their capabilities, and available endpoints.
  - [https://api.docs.dealcloud.com/docs](https://api.docs.dealcloud.com/docs) — REST APIs
- Audit: [ ] supported  [ ] unsupported  [ ] unclear
- Correction: 
