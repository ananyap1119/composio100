Audit result

The original 3 finalized / 7 review-required split is too conservative. Official documentation supports moving six of the seven review-required apps to concrete verdicts.

Revised status: 9 finalized, 1 partly review-required.

Build now: Salesforce, HubSpot, Apify, Linear, Zoho CRM
Build now, with customer-admin authorization: Jira
Build after vendor/public-app approval: Close, Front
Build after Shopify App Store review: Shopify
Enterprise-customer build; public distribution remains uncertain: Otter AI

I treated each app as five grouped audit claims, for 50 claims total.

Salesforce
Claim 1

Agent value: OAuth 2.0 authentication
Audit result: Supported
Correct value: Salesforce REST integrations support OAuth 2.0 through connected or external client apps.
Official URL: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_oauth_and_connected_apps.htm
One-sentence explanation: Salesforceâ€™s REST documentation explicitly requires an OAuth-enabled connected or external client app for OAuth flows.

Claim 2

Agent value: Self-serve developer access and credential creation
Audit result: Supported
Correct value: A developer can register a free Developer Edition org and create an app that generates client credentials.
Official URL: https://developer.salesforce.com/docs/platform/mobile-sdk/guide/connected-apps-howto.html
One-sentence explanation: Salesforce documents both self-service Developer Edition registration and app creation through Setup and App Manager.

Claim 3

Agent value: Broad REST read and write coverage
Audit result: Supported
Correct value: The REST API supports retrieving, creating, updating and deleting Salesforce records, alongside composite and other advanced resources.
Official URL: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_list.htm
One-sentence explanation: Official REST resources document record retrieval, updates, deletion and broader composite operations.

Claim 4

Agent value: Official Salesforce MCP
Audit result: Supported
Correct value: Salesforce publishes and hosts official MCP servers with OAuth and Salesforce object operations.
Official URL: https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/hosted-mcp-servers-overview.html
One-sentence explanation: Salesforceâ€™s developer site identifies them as Salesforce Hosted MCP Servers and documents read, create, update and delete tools.

Claim 5

Agent value: Build now
Audit result: Supported
Correct value: Build now, but customer organizations may require an administrator to pre-authorize the app or assigned users.
Official URL: https://help.salesforce.com/s/articleView?id=sf.connected_app_manage_oauth.htm&type=5
One-sentence explanation: Developer-side app creation is self-serve, while customer-side OAuth access remains subject to each organizationâ€™s connected-app policies.

Final verdict: Build now â€” customer-admin policy caveat.

HubSpot
Claim 1

Agent value: OAuth 2.0
Audit result: Supported
Correct value: OAuth is required when an app is installed across multiple HubSpot accounts.
Official URL: https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview
One-sentence explanation: HubSpot explicitly requires OAuth for multi-account app distribution and issues bearer access tokens after installation.

Claim 2

Agent value: OAuth/API-key authentication paths
Audit result: Incorrect
Correct value: The relevant current terms are OAuth access token and static or private-app access token, not API key.
Official URL: https://developers.hubspot.com/docs/apps/legacy-apps/private-apps/overview
One-sentence explanation: HubSpot calls the single-account credential a private-app access token, while â€œdeveloper API keysâ€ are a separate developer-tooling concept rather than CRM API authentication.

Claim 3

Agent value: Self-serve developer account, app creation and multi-customer installation
Audit result: Supported
Correct value: Developers can create apps and test accounts themselves, with OAuth used for installations across customer accounts.
Official URL: https://developers.hubspot.com/docs/apps/developer-platform/build-apps/create-an-app
One-sentence explanation: HubSpot documents app creation, developer test accounts, OAuth credentials and multi-account distribution without requiring vendor contact.

Claim 4

Agent value: Broad CRM read and write API
Audit result: Supported
Correct value: HubSpotâ€™s REST APIs are accessible through private-app access tokens or public-app OAuth tokens, subject to selected scopes.
Official URL: https://developers.hubspot.com/docs/apps/developer-platform/overview
One-sentence explanation: HubSpot states that all REST APIs are available through the supported private and public authentication paths.

Claim 5

Agent value: Build now
Audit result: Supported
Correct value: Build now with OAuth for multiple customers or a private/static access token for a single account.
Official URL: https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview
One-sentence explanation: Both single-account and multi-account build paths are officially documented and self-service.

Final verdict: Build now â€” replace â€œAPI keyâ€ with â€œprivate-app/static access token.â€

Apify
Claim 1

Agent value: API-token authentication
Audit result: Supported
Correct value: Apify authenticates API requests with an API token supplied as a bearer token or URL parameter.
Official URL: https://docs.apify.com/api/v2
One-sentence explanation: The API reference directly documents tokens from the Apify Console and bearer-token authentication.

Claim 2

Agent value: Free or trial self-serve credential creation
Audit result: Supported
Correct value: Developers can create a free account without a credit card and immediately obtain an API token.
Official URL: https://docs.apify.com/platform/integrations/agent-onboarding
One-sentence explanation: Apifyâ€™s onboarding documentation says the free plan needs no credit card and directs users to the self-service token page.

Claim 3

Agent value: REST API availability
Audit result: Supported
Correct value: Apify provides a versioned public REST API.
Official URL: https://docs.apify.com/api/v2
One-sentence explanation: The official V2 reference documents HTTP endpoints, authentication, request bodies and resource responses.

Claim 4

Agent value: Read/write coverage across Actors, runs, datasets and storage
Audit result: Supported
Correct value: The API can start Actors, inspect runs, retrieve datasets and programmatically access or modify storage resources.
Official URL: https://docs.apify.com/api/v2
One-sentence explanation: Apify documents POST-based Actor execution and programmatic access to datasets, key-value stores and other storage.

Claim 5

Agent value: Build now
Audit result: Supported
Correct value: Build now using a self-generated API token.
Official URL: https://docs.apify.com/platform/integrations/agent-onboarding
One-sentence explanation: Account creation, token generation and usable API endpoints are all publicly documented without an approval process.

Final verdict: Build now.

Close
Claim 1

Agent value: Authentication methods unresolved
Audit result: Missed evidence
Correct value: Close supports API-key authentication and OAuth 2.0.
Official URL: https://developer.close.com/api/overview/oauth-authentication
One-sentence explanation: Close has separate official documentation for user-generated API keys and OAuth client credentials.

Claim 2

Agent value: Credential access unresolved
Audit result: Missed evidence
Correct value: Existing Close users can self-create API keys and OAuth apps; non-users can request a free development organization from Close.
Official URL: https://developer.close.com/integrations
One-sentence explanation: The integration guide explicitly describes both self-service credentials for users and the support-request path for non-user development organizations.

Claim 3

Agent value: Broad read/write API evidence
Audit result: Supported
Correct value: Close exposes a broad REST API covering CRM records, activities, users, organizations and related resources with read and write operations.
Official URL: https://developer.close.com/api/overview
One-sentence explanation: The official API reference and integration guide describe broad programmatic read and write access.

Claim 4

Agent value: Multi-customer credential distribution unresolved
Audit result: Missed evidence
Correct value: OAuth apps start private, and Close must make the app public before unrelated Close customers can authorize it.
Official URL: https://developer.close.com/integrations/create-an-oauth-app
One-sentence explanation: Close explicitly instructs developers to request public status when they want other customers to authorize an OAuth app.

Claim 5

Agent value: Review-required verdict
Audit result: Missed evidence
Correct value: Build now for a specific customer using its API key; build after Close public-app approval for multi-customer OAuth distribution.
Official URL: https://developer.close.com/integrations/create-an-oauth-app
One-sentence explanation: The official documentation resolves both the private customer-specific path and the approval-dependent public distribution path.

Final verdict: Build after Close approval for public multi-customer OAuth; customer-specific builds can start now.

Jira
Claim 1

Agent value: Authentication evidence reduced to a workspace-admin credential requirement
Audit result: Missed evidence
Correct value: Jira Cloud supports OAuth 2.0 3LO and user-generated API tokens; Forge and Connect provide additional app authentication models.
Official URL: https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/
One-sentence explanation: Atlassian documents API-token basic authentication for scripts and OAuth 2.0 3LO for distributed integrations.

Claim 2

Agent value: A workspace administrator must create the integration credentials
Audit result: Incorrect
Correct value: Developers independently create an OAuth app, client ID and secret in Atlassianâ€™s developer console.
Official URL: https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/
One-sentence explanation: App creation and sharing are handled by the developer, not by an administrator in every customer workspace.

Claim 3

Agent value: Customer workspace-admin approval is required
Audit result: Supported
Correct value: A Jira site administrator must authorize a third-party or OAuth app before it can access that siteâ€™s user data.
Official URL: https://support.atlassian.com/atlassian-cloud/kb/your-site-admin-must-authorize-this-app-error-in-atlassian-cloud-apps/
One-sentence explanation: Atlassian distinguishes developer-side app creation from site-admin authorization inside the customerâ€™s cloud site.

Claim 4

Agent value: REST read/write breadth unresolved
Audit result: Missed evidence
Correct value: Jiraâ€™s REST APIs and OAuth scopes cover reading, creating, editing and administering Jira data.
Official URL: https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/
One-sentence explanation: The OAuth documentation enumerates read, write and manage scopes intended for Jira REST endpoints.

Claim 5

Agent value: Review-required toolkit verdict
Audit result: Missed evidence
Correct value: Build now with a distributable OAuth 3LO app, while expecting customer site-admin authorization and an unreviewed-app warning until Atlassian review.
Official URL: https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/
One-sentence explanation: Developers can enable sharing and distribute an authorization URL before Marketplace listing, although customer authorization and review warnings remain.

Final verdict: Build now â€” customer site-admin authorization required.

Otter AI
Claim 1

Agent value: Public API and authentication evidence unresolved
Audit result: Missed evidence
Correct value: Otter publishes a documented API authenticated with user-created bearer API keys.
Official URL: https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API
One-sentence explanation: Otterâ€™s April 23, 2026 documentation describes API-key creation, bearer authentication, rate limits and endpoint definitions.

Claim 2

Agent value: Contact-vendor/Enterprise-gated access
Audit result: Supported
Correct value: The API is available to Enterprise workspaces, and customers are told to contact their account manager when it is not enabled.
Official URL: https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API
One-sentence explanation: Otter directly identifies Enterprise workspace access and the account-manager enablement path.

Claim 3

Agent value: Workspace-admin access is required for the integration generally
Audit result: Incorrect
Correct value: Ordinary Enterprise users can create personal API keys, while Super Admin status is required only for the separate administration endpoints.
Official URL: https://help.otter.ai/hc/en-us/articles/39661865499799-Super-Admin-specific-APIs
One-sentence explanation: Otter separates authenticated user API access from endpoints specifically reserved for workspace Super Admins.

Claim 4

Agent value: Read and write capability unresolved
Audit result: Missed evidence
Correct value: The API provides broad retrieval of conversations, transcripts, audio and related data, plus a limited write endpoint for creating a conversation from a file.
Official URL: https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API
One-sentence explanation: Official endpoint documentation lists extensive GET operations and POST /conversations, but no broad update/delete CRM-style surface.

Claim 5

Agent value: Gated buildability verdict
Audit result: Correctly uncertain
Correct value: Build with an Enterprise customerâ€™s API key is justified, but official public documentation does not explain a general third-party, multi-customer OAuth or app-distribution process.
Official URL: https://help.otter.ai/hc/en-us/articles/36130822688279-Otter-ai-Public-API
One-sentence explanation: The documented API resolves Enterprise customer access but does not establish an independently distributable public integration credential path.

Final verdict: Build for Enterprise customers with customer credentials; retain review for public multi-customer distribution.

Linear
Claim 1

Agent value: OAuth support incomplete
Audit result: Missed evidence
Correct value: Linear supports OAuth 2.0 and allows developers to create OAuth applications.
Official URL: https://linear.app/developers/oauth-2-0-authentication
One-sentence explanation: Linearâ€™s OAuth guide documents application creation, authorization-code flow and access scopes.

Claim 2

Agent value: Personal API-token support incomplete
Audit result: Missed evidence
Correct value: Linear supports self-generated personal API keys.
Official URL: https://linear.app/developers/graphql
One-sentence explanation: Linearâ€™s GraphQL documentation directly describes creating and using personal API keys.

Claim 3

Agent value: Public API evidence incomplete
Audit result: Missed evidence
Correct value: Linear exposes a public GraphQL API.
Official URL: https://linear.app/developers/graphql
One-sentence explanation: The official developer site identifies GraphQL as Linearâ€™s public API and documents its endpoint and schema.

Claim 4

Agent value: Read and write operations unresolved
Audit result: Missed evidence
Correct value: GraphQL queries read data and mutations create or modify Linear entities.
Official URL: https://linear.app/developers/graphql
One-sentence explanation: Linear explicitly documents queries and mutations, while its API overview says the API can mutate supported entities.

Claim 5

Agent value: Review-required verdict
Audit result: Missed evidence
Correct value: Build now; personal keys support customer-specific use, while OAuth supports distributable integrations.
Official URL: https://linear.app/docs/api-and-webhooks
One-sentence explanation: Authentication, app creation, read/write operations and API breadth are all publicly resolved, with workspace permissions applying to key and app management.

Final verdict: Build now.

Front
Claim 1

Agent value: Authentication methods unresolved
Audit result: Missed evidence
Correct value: Front supports OAuth 2.0 and company-level API tokens; public integrations normally require OAuth.
Official URL: https://dev.frontapp.com/docs/authentication
One-sentence explanation: Frontâ€™s authentication documentation explicitly lists bearer access through OAuth and API tokens.

Claim 2

Agent value: Public developer API with partial read evidence
Audit result: Supported
Correct value: Front exposes a public Core API covering conversations, messages, contacts, inboxes and other company resources.
Official URL: https://dev.frontapp.com/reference/introduction
One-sentence explanation: Front describes the Core API as a comprehensive public interface and documents OAuth and API-token access.

Claim 3

Agent value: Write/create/update operations unresolved
Audit result: Missed evidence
Correct value: Front supports write, delete and send permissions, including creating messages and creating or updating contacts and conversations.
Official URL: https://dev.frontapp.com/docs/create-and-revoke-api-tokens
One-sentence explanation: Official token documentation defines write as creating and updating resources and send as creating or replying to messages.

Claim 4

Agent value: Credential and administrator requirements unresolved
Audit result: Missed evidence
Correct value: A company admin must create apps and API tokens, and an admin must authorize both private and public OAuth apps.
Official URL: https://dev.frontapp.com/docs/create-and-manage-apps
One-sentence explanation: Front explicitly limits app creation, token management and OAuth authorization to company administrators.

Claim 5

Agent value: Review-required buildability verdict
Audit result: Missed evidence
Correct value: Build now for one Front customer with admin-created credentials; public distribution requires OAuth and coordination with Front to publish in its App Store.
Official URL: https://dev.frontapp.com/docs/create-and-manage-apps
One-sentence explanation: Private apps work inside the creating instance immediately, while publishing to all customers requires notifying and working with Front.

Final verdict: Build after Front publishing approval for public distribution; customer-specific builds can start now.

Shopify
Claim 1

Agent value: OAuth authentication
Audit result: Supported
Correct value: Public Shopify apps must authenticate merchants through OAuth immediately after installation.
Official URL: https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements
One-sentence explanation: Shopifyâ€™s App Store requirements explicitly mandate OAuth during installation and reinstallation.

Claim 2

Agent value: Partner/developer path and distinction between custom and public apps
Audit result: Supported
Correct value: Public distribution supports many merchants, while custom distribution is limited to one store or stores in the same Shopify Plus organization.
Official URL: https://shopify.dev/docs/apps/launch/distribution/select-distribution-method
One-sentence explanation: Shopify separately documents public and custom distribution and warns that the selected method cannot later be changed.

Claim 3

Agent value: Marketplace/app-review requirement
Audit result: Supported
Correct value: A publicly distributed App Store app must be submitted to and approved by Shopifyâ€™s review team.
Official URL: https://shopify.dev/docs/apps/launch/app-store-review/pass-app-review
One-sentence explanation: Shopify requires a production-ready app to pass its formal approval process before App Store distribution.

Claim 4

Agent value: Current REST versus GraphQL positioning unresolved
Audit result: Missed evidence
Correct value: REST Admin API is legacy, and all new public apps have been required to use the GraphQL Admin API since April 1, 2025.
Official URL: https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements
One-sentence explanation: Shopify states both the REST legacy date and the GraphQL-only requirement for new public apps.

Claim 5

Agent value: Marketplace-review and multi-tenant build verdict
Audit result: Supported
Correct value: Build after app review for broad public distribution; use custom distribution or own-store credentials only for the limited merchant-specific path.
Official URL: https://shopify.dev/docs/apps/launch/distribution/select-distribution-method
One-sentence explanation: Public multi-merchant and custom merchant-specific paths have different installation and review requirements and must not be combined.

Final verdict: Build after Shopify App Store review for public distribution.

Zoho CRM
Claim 1

Agent value: OAuth evidence unresolved
Audit result: Missed evidence
Correct value: Zoho CRM V8 APIs use OAuth 2.0 with client IDs, client secrets, authorization codes, access tokens and refresh tokens.
Official URL: https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html
One-sentence explanation: Zohoâ€™s official OAuth overview directly documents delegated access and the complete token model.

Claim 2

Agent value: Developer-console and client-creation access unresolved
Audit result: Missed evidence
Correct value: A developer with a Zoho CRM account can register a client through the Zoho API Console and generate organization-specific authorization.
Official URL: https://www.zoho.com/crm/developer/docs/api/v8/api-collection.html
One-sentence explanation: Zoho identifies a CRM account and registered self-client or web client as the prerequisites for API use.

Claim 3

Agent value: Read/write operations and API breadth unresolved
Audit result: Missed evidence
Correct value: Zoho CRM exposes RESTful CRUD, metadata, composite, bulk, notification and query APIs.
Official URL: https://www.zoho.com/crm/developer/docs/api/v8/
One-sentence explanation: The official V8 index explicitly lists CRUD and several broad supporting API families.

Claim 4

Agent value: Official Zoho MCP
Audit result: Supported
Correct value: Zoho publishes and operates pre-built Zoho CRM MCP servers with read, CRUD, customization and workflow tools.
Official URL: https://www.zoho.com/crm/developer/docs/mcp/overview.html
One-sentence explanation: The source is hosted and maintained on Zohoâ€™s own developer domain and states that Zoho provides the servers without requiring users to host them.

Claim 5

Agent value: Review-required buildability verdict
Audit result: Missed evidence
Correct value: Build now using OAuth and the API Console; customer operations remain limited by the authorizing userâ€™s CRM permissions and subscription API quota.
Official URL: https://www.zoho.com/crm/developer/docs/mcp/overview.html
One-sentence explanation: Both the REST and MCP paths are documented, and authorization is explicitly scoped to the authenticating userâ€™s permissions rather than a blanket administrator requirement.

Final verdict: Build now.

Metrics
Outcome	Claims
Supported	23
Incorrect	3
Missed evidence	23
Correctly uncertain	1
Total	50
Concrete-claim precision

23 supported / 26 concrete claims = 88.5%

The agentâ€™s concrete statements were usually accurate; the main concrete errors were HubSpotâ€™s â€œAPI keyâ€ terminology, Jiraâ€™s characterization of who creates credentials, and Otterâ€™s blanket workspace-admin requirement.

Evidence coverage

49 resolved / 50 checked = 98.0%

Only Otterâ€™s general public multi-customer distribution path remains genuinely unresolved in official public documentation.

Overall audit correctness

(23 supported + 1 correctly uncertain) / 50 = 48.0%

The low overall score is primarily caused by 23 missed-evidence claims, not by large numbers of false concrete claims.
