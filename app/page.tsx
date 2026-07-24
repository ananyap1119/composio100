"use client";

import { useMemo, useState } from "react";

type Verdict = "Ready" | "Constrained" | "Blocked";
type AppRow = {
  id: number;
  name: string;
  category: string;
  description: string;
  auth: string;
  access: "Self-serve" | "Gated";
  surface: string;
  mcp: boolean;
  verdict: Verdict;
  blocker: string;
  evidence: string;
};

const categoryDescriptions: Record<string, string> = {
  "CRM & Sales": "Manage customer relationships, pipelines, and revenue workflows.",
  "Support & Helpdesk": "Run customer support queues, conversations, and service operations.",
  "Communications": "Power messaging, calling, notifications, and community workflows.",
  "Marketing": "Create, deliver, and measure campaigns across owned and paid channels.",
  "Ecommerce": "Operate catalogs, orders, customers, and online storefronts.",
  "Data & Scraping": "Collect, enrich, and analyze web, company, and search data.",
  "Developer & Infra": "Build, deploy, observe, and operate software and data systems.",
  "Productivity": "Plan work, manage knowledge, and coordinate projects.",
  "Finance": "Move money, reconcile accounts, and manage financial operations.",
  "AI & Media": "Research, generate, parse, and transform AI-native media.",
};

const appDescriptions = [
  "Enterprise CRM for accounts, opportunities, service, and revenue operations.",
  "CRM and marketing platform for contacts, deals, campaigns, and customer service.",
  "Sales CRM focused on visual pipelines, activity tracking, and forecasting.",
  "Collaborative, data-model-driven CRM for modern go-to-market teams.",
  "Open-source CRM with configurable objects, workflows, and self-hosting.",
  "Work management platform combining CRM records, apps, and team collaboration.",
  "CRM suite for leads, deals, accounts, analytics, and sales automation.",
  "Sales CRM with calling, email, pipeline, and rep productivity workflows.",
  "Google Workspace-centric CRM for leads, people, companies, and opportunities.",
  "Enterprise relationship intelligence and deal-management platform for financial services.",
  "Customer service suite for tickets, help centers, messaging, and support operations.",
  "Customer communications platform for inboxes, chat, support, and lifecycle messaging.",
  "Cloud helpdesk for tickets, SLAs, automations, knowledge bases, and reporting.",
  "Shared customer-operations inbox for email, SMS, social, and team workflows.",
  "B2B support platform connecting customer conversations with engineering context.",
  "Omnichannel helpdesk for tickets, chat, calls, knowledge, and customer portals.",
  "API-first customer support platform for conversations, timelines, and service workflows.",
  "Customer support platform for shared inboxes, knowledge bases, and reporting.",
  "Ecommerce helpdesk for customer conversations, orders, macros, and automation.",
  "Enterprise customer-service platform centered on people, conversations, and journeys.",
  "Team messaging platform for channels, DMs, workflows, files, and app collaboration.",
  "Communications platform for programmable SMS, voice, email, and verification.",
  "Team chat and collaboration platform within the Zoho business suite.",
  "Enterprise collaboration suite for chat, meetings, documents, and business apps.",
  "Workplace chat for channels, messages, files, and team communication.",
  "Community messaging platform for servers, channels, bots, voice, and events.",
  "Messaging network with bot APIs for chats, commands, media, and notifications.",
  "Business messaging channel for customer conversations, templates, and commerce.",
  "Cloud phone system for calls, users, contacts, recordings, and call-center workflows.",
  "Communications APIs for voice, video, messaging, verification, and contact centers.",
  "Advertising platform for campaign management, targeting, reporting, and optimization.",
  "Advertising APIs for campaigns, audiences, creatives, insights, and business assets.",
  "B2B advertising platform for campaigns, accounts, creatives, leads, and reporting.",
  "Sales and marketing automation platform for agencies, funnels, CRM, and messaging.",
  "Email marketing platform for audiences, campaigns, automations, and analytics.",
  "Customer data and marketing automation platform for ecommerce email and SMS.",
  "All-in-one funnel, email, course, and ecommerce automation platform.",
  "Visual discovery and advertising platform for pins, boards, campaigns, and analytics.",
  "Meta's text-first social network for publishing, replies, and conversation insights.",
  "Transactional and marketing email delivery platform with templates and analytics.",
  "Commerce platform for stores, products, orders, customers, and fulfillment.",
  "WordPress commerce plugin for products, orders, customers, coupons, and extensions.",
  "Commerce platform for catalogs, storefronts, orders, customers, and channels.",
  "Enterprise commerce platform for catalogs, inventory, shoppers, orders, and promotions.",
  "Adobe's commerce platform for catalogs, carts, customers, orders, and storefronts.",
  "Website and commerce platform for products, orders, inventory, profiles, and webhooks.",
  "Embedded ecommerce platform for catalogs, orders, customers, and storefront management.",
  "Creator commerce platform for products, licenses, sales, subscribers, and payouts.",
  "Amazon seller platform for listings, inventory, orders, reports, and fulfillment.",
  "Creator monetization platform for digital products, memberships, and fan payments.",
  "SEO data provider for rankings, keywords, SERPs, backlinks, and business data.",
  "SEO platform for rankings, competitors, audits, backlinks, and reporting.",
  "Search intelligence platform for backlinks, keywords, rankings, and competitive research.",
  "Hosted web-scraping service for extracting structured data from websites.",
  "Cloud platform for running web scrapers, browser actors, datasets, and automations.",
  "Web data API for crawling, scraping, search, and LLM-ready content extraction.",
  "Proxy and web-data platform for collection, scraping, unlocking, and datasets.",
  "Open-source CLI that discovers social accounts from a username across websites.",
  "Company and contact intelligence platform for enrichment and go-to-market research.",
  "Data enrichment workspace combining providers, formulas, AI, and outbound workflows.",
  "Code collaboration platform for repositories, issues, pull requests, Actions, and security.",
  "Cloud deployment platform for projects, builds, domains, teams, and serverless workloads.",
  "Web deployment platform for sites, builds, functions, forms, and team operations.",
  "Internet infrastructure platform for DNS, CDN, security, Workers, storage, and analytics.",
  "Backend platform providing Postgres, authentication, storage, APIs, and edge functions.",
  "Graph database platform for connected data, Cypher queries, and graph analytics.",
  "Cloud data platform for warehouses, data sharing, governance, and compute.",
  "Managed document database platform for clusters, projects, users, and observability.",
  "Monitoring platform for metrics, logs, traces, incidents, and cloud infrastructure.",
  "Application monitoring platform for errors, traces, releases, and issue triage.",
  "Workspace platform for pages, databases, blocks, users, and collaborative knowledge.",
  "Spreadsheet-database platform for bases, tables, records, views, and automations.",
  "Issue tracking and product planning platform built around teams, projects, and cycles.",
  "Work tracking platform for issues, projects, workflows, users, and service management.",
  "Work management platform for tasks, projects, portfolios, goals, and teams.",
  "Work operating system for boards, items, updates, columns, and automations.",
  "Project management platform for tasks, lists, spaces, goals, docs, and time tracking.",
  "Collaborative document platform combining pages, tables, formulas, and automations.",
  "Enterprise work-management platform for sheets, rows, reports, users, and workflows.",
  "Time tracking and invoicing platform for projects, people, expenses, and reports.",
  "Payments platform for customers, charges, subscriptions, invoices, and financial products.",
  "Financial-data network for bank connections, accounts, transactions, identity, and payments.",
  "Cryptocurrency exchange APIs for market data, trading, accounts, and order management.",
  "NMI-powered payment connectivity offering merchant and transaction workflows.",
  "Payments platform for transaction processing, account connectivity, and financial operations.",
  "Accounting platform for companies, customers, invoices, expenses, and reporting.",
  "Cloud accounting platform for invoices, contacts, bank transactions, and reports.",
  "Business financial platform for cards, expenses, travel, payments, and cash management.",
  "Finance automation platform for cards, expenses, reimbursements, bills, and accounting.",
  "Private-market data platform for companies, deals, investors, funds, and market research.",
  "Enterprise grounded-research notebook for sources, queries, summaries, and sharing.",
  "AI meeting assistant for transcripts, summaries, speakers, and workspace knowledge.",
  "Meeting assistant for recordings, transcripts, summaries, and CRM-ready action items.",
  "AI academic search engine for evidence-backed answers and research synthesis.",
  "Document intelligence API for parsing, extracting, structuring, and enriching files.",
  "AI software engineer platform with programmatic task execution and MCP connectivity.",
  "AI content creation suite for image, video, effects, and campaign workflows.",
  "Command-line renderer for converting Mermaid text diagrams into image and PDF assets.",
  "Hosted API for retrieving and processing transcripts from YouTube videos.",
  "Meeting intelligence platform for recordings, transcripts, clips, notes, and CRM sync.",
];

const raw: Array<[string, string, string, string, string, 0 | 1, Verdict, string]> = [
  ["Salesforce","CRM & Sales","OAuth 2.0","Self-serve","Broad REST + GraphQL",1,"Ready","—"],
  ["HubSpot","CRM & Sales","OAuth 2.0 / token","Self-serve","Broad REST",1,"Ready","—"],
  ["Pipedrive","CRM & Sales","OAuth 2.0 / token","Self-serve","Broad REST",0,"Ready","—"],
  ["Attio","CRM & Sales","OAuth 2.0 / API key","Self-serve","Broad REST",0,"Ready","—"],
  ["Twenty","CRM & Sales","API key","Self-serve","Open-source REST + GraphQL",1,"Ready","—"],
  ["Podio","CRM & Sales","OAuth 2.0","Self-serve","Public REST",0,"Ready","—"],
  ["Zoho CRM","CRM & Sales","OAuth 2.0","Self-serve","Broad REST",0,"Ready","Regional console complexity"],
  ["Close","CRM & Sales","API key","Self-serve","Broad REST",0,"Ready","—"],
  ["Copper","CRM & Sales","API key","Self-serve","Public REST",0,"Ready","—"],
  ["DealCloud","CRM & Sales","OAuth 2.0","Gated","Enterprise REST",0,"Constrained","Enterprise contract"],
  ["Zendesk","Support & Helpdesk","OAuth 2.0 / token","Self-serve","Broad REST",1,"Ready","—"],
  ["Intercom","Support & Helpdesk","OAuth 2.0","Self-serve","Broad REST",1,"Ready","—"],
  ["Freshdesk","Support & Helpdesk","API key","Self-serve","Broad REST",0,"Ready","—"],
  ["Front","Support & Helpdesk","OAuth 2.0 / token","Self-serve","Broad REST",0,"Ready","—"],
  ["Pylon","Support & Helpdesk","API key","Gated","Public REST",0,"Constrained","Workspace approval"],
  ["LiveAgent","Support & Helpdesk","API key","Self-serve","Public REST",0,"Ready","—"],
  ["Plain","Support & Helpdesk","API key","Self-serve","GraphQL",0,"Ready","—"],
  ["Help Scout","Support & Helpdesk","OAuth 2.0","Self-serve","Broad REST",0,"Ready","—"],
  ["Gorgias","Support & Helpdesk","Basic / OAuth 2.0","Self-serve","Public REST",0,"Ready","—"],
  ["Gladly","Support & Helpdesk","API token","Gated","Enterprise REST",0,"Constrained","Sales-gated sandbox"],
  ["Slack","Communications","OAuth 2.0","Self-serve","Broad Web API",1,"Ready","—"],
  ["Twilio","Communications","Basic / API key","Self-serve","Broad REST",0,"Ready","—"],
  ["Zoho Cliq","Communications","OAuth 2.0","Self-serve","Public REST",0,"Ready","—"],
  ["Lark","Communications","OAuth 2.0 / app token","Self-serve","Broad REST",0,"Ready","Tenant admin consent"],
  ["Pumble","Communications","Token","Self-serve","Narrow REST",0,"Constrained","Limited public surface"],
  ["Discord","Communications","OAuth 2.0 / bot token","Self-serve","Broad REST + Gateway",1,"Ready","—"],
  ["Telegram","Communications","Bot token","Self-serve","Bot API",1,"Ready","—"],
  ["WhatsApp Business","Communications","OAuth 2.0 / token","Gated","Cloud REST",0,"Constrained","Business verification"],
  ["Aircall","Communications","OAuth 2.0 / Basic","Gated","Public REST",0,"Constrained","Partner approval for OAuth"],
  ["Vonage","Communications","API key / JWT","Self-serve","Broad REST",0,"Ready","—"],
  ["Google Ads","Marketing","OAuth 2.0","Gated","Broad REST",0,"Constrained","Developer token review"],
  ["Meta Ads","Marketing","OAuth 2.0","Gated","Graph API",0,"Constrained","App review + business verification"],
  ["LinkedIn Ads","Marketing","OAuth 2.0","Gated","Marketing REST",0,"Blocked","Partner program approval"],
  ["GoHighLevel","Marketing","OAuth 2.0","Self-serve","Broad REST",0,"Ready","—"],
  ["Mailchimp","Marketing","OAuth 2.0 / API key","Self-serve","Broad REST",0,"Ready","—"],
  ["Klaviyo","Marketing","API key","Self-serve","Broad REST",0,"Ready","—"],
  ["systeme.io","Marketing","API key","Self-serve","Narrow REST",0,"Constrained","Limited endpoints"],
  ["Pinterest","Marketing","OAuth 2.0","Gated","Public REST",0,"Constrained","App approval"],
  ["Threads","Marketing","OAuth 2.0","Gated","Graph API",0,"Constrained","App review"],
  ["SendGrid","Marketing","API key","Self-serve","Broad REST",0,"Ready","—"],
  ["Shopify","Ecommerce","OAuth 2.0 / token","Self-serve","Broad REST + GraphQL",1,"Ready","—"],
  ["WooCommerce","Ecommerce","Basic / API key","Self-serve","Broad REST",1,"Ready","—"],
  ["BigCommerce","Ecommerce","OAuth 2.0 / token","Self-serve","Broad REST + GraphQL",0,"Ready","—"],
  ["Salesforce Commerce Cloud","Ecommerce","OAuth 2.0","Gated","Broad REST",0,"Constrained","Enterprise tenant"],
  ["Adobe Commerce","Ecommerce","OAuth 1.0 / token","Self-serve","Broad REST + GraphQL",0,"Ready","Complex deployment variants"],
  ["Squarespace","Ecommerce","OAuth 2.0","Gated","Commerce REST",0,"Constrained","OAuth partner approval"],
  ["Ecwid","Ecommerce","OAuth 2.0 / token","Self-serve","Broad REST",0,"Ready","—"],
  ["Gumroad","Ecommerce","OAuth 2.0","Self-serve","Public REST",0,"Ready","—"],
  ["Amazon Selling Partner","Ecommerce","OAuth 2.0 + AWS SigV4","Gated","Broad REST",0,"Constrained","Seller + role approval"],
  ["FanBasis","Ecommerce","Unknown","Gated","No public API found",0,"Blocked","No public developer surface"],
  ["DataForSEO","Data & Scraping","Basic","Self-serve","Broad REST",0,"Ready","—"],
  ["SE Ranking","Data & Scraping","API key","Gated","Public REST",0,"Constrained","Higher-tier plan"],
  ["Ahrefs","Data & Scraping","API key","Gated","Broad REST",0,"Constrained","Paid enterprise access"],
  ["MrScraper","Data & Scraping","API key","Self-serve","Public REST",0,"Ready","—"],
  ["Apify","Data & Scraping","API token","Self-serve","Broad REST",1,"Ready","—"],
  ["Firecrawl","Data & Scraping","API key","Self-serve","Public REST",1,"Ready","—"],
  ["Bright Data","Data & Scraping","API token","Self-serve","Broad REST",1,"Ready","Compliance-sensitive use"],
  ["Sherlock","Data & Scraping","CLI / none","Self-serve","Open-source CLI",0,"Constrained","No hosted API"],
  ["Waterfall.io","Data & Scraping","API key","Gated","Private REST",0,"Constrained","Sales-gated credentials"],
  ["Clay","Data & Scraping","API key","Gated","Limited REST",0,"Blocked","No general public API"],
  ["GitHub","Developer & Infra","OAuth 2.0 / token","Self-serve","Broad REST + GraphQL",1,"Ready","—"],
  ["Vercel","Developer & Infra","OAuth 2.0 / token","Self-serve","Broad REST",1,"Ready","—"],
  ["Netlify","Developer & Infra","OAuth 2.0 / token","Self-serve","Broad REST",0,"Ready","—"],
  ["Cloudflare","Developer & Infra","OAuth 2.0 / token","Self-serve","Broad REST + GraphQL",1,"Ready","—"],
  ["Supabase","Developer & Infra","API key / token","Self-serve","REST + GraphQL + SDK",1,"Ready","—"],
  ["Neo4j","Developer & Infra","Basic / token","Self-serve","Query + REST",1,"Ready","—"],
  ["Snowflake","Developer & Infra","OAuth 2.0 / key pair","Gated","SQL + REST",1,"Constrained","Account admin setup"],
  ["MongoDB Atlas","Developer & Infra","API key","Self-serve","Broad REST",1,"Ready","—"],
  ["Datadog","Developer & Infra","API key + app key","Self-serve","Broad REST",1,"Ready","—"],
  ["Sentry","Developer & Infra","OAuth 2.0 / token","Self-serve","Broad REST",1,"Ready","—"],
  ["Notion","Productivity","OAuth 2.0 / token","Self-serve","Public REST",1,"Ready","—"],
  ["Airtable","Productivity","OAuth 2.0 / token","Self-serve","Public REST",1,"Ready","—"],
  ["Linear","Productivity","OAuth 2.0 / API key","Self-serve","GraphQL",1,"Ready","—"],
  ["Jira","Productivity","OAuth 2.0 / token","Self-serve","Broad REST",1,"Ready","—"],
  ["Asana","Productivity","OAuth 2.0 / token","Self-serve","Broad REST",0,"Ready","—"],
  ["Monday.com","Productivity","OAuth 2.0 / token","Self-serve","GraphQL",0,"Ready","—"],
  ["ClickUp","Productivity","OAuth 2.0 / token","Self-serve","Broad REST",0,"Ready","—"],
  ["Coda","Productivity","OAuth 2.0 / token","Self-serve","Public REST",0,"Ready","—"],
  ["Smartsheet","Productivity","OAuth 2.0 / token","Self-serve","Broad REST",0,"Ready","—"],
  ["Harvest","Productivity","OAuth 2.0 / token","Self-serve","Public REST",0,"Ready","—"],
  ["Stripe","Finance","OAuth 2.0 / API key","Self-serve","Broad REST",1,"Ready","—"],
  ["Plaid","Finance","API key","Self-serve","Broad REST",1,"Ready","Production review"],
  ["Binance","Finance","API key + signature","Self-serve","Broad REST + WebSocket",0,"Ready","Regional restrictions"],
  ["Paygent Connect","Finance","Unknown","Gated","Partner API",0,"Blocked","No public developer program"],
  ["iPayX","Finance","API key","Gated","Narrow REST",0,"Constrained","Invite-only docs"],
  ["QuickBooks","Finance","OAuth 2.0","Self-serve","Broad REST",0,"Ready","Production app review"],
  ["Xero","Finance","OAuth 2.0","Self-serve","Broad REST",0,"Ready","—"],
  ["Brex","Finance","OAuth 2.0 / token","Gated","Broad REST",0,"Constrained","Customer + admin approval"],
  ["Ramp","Finance","OAuth 2.0","Gated","Broad REST",0,"Constrained","Customer access + approval"],
  ["PitchBook","Finance","API key","Gated","Enterprise data API",0,"Blocked","Enterprise license"],
  ["NotebookLM","AI & Media","Google IAM / OAuth 2.0","Gated","Enterprise API (preview)",0,"Constrained","Enterprise license + IAM setup"],
  ["Otter AI","AI & Media","OAuth 2.0","Self-serve","MCP surface",1,"Ready","—"],
  ["Fathom","AI & Media","API key","Self-serve","Public REST",0,"Ready","—"],
  ["Consensus","AI & Media","OAuth requested","Gated","No general public API",0,"Blocked","Partnership required"],
  ["Reducto","AI & Media","API key","Self-serve","Public REST",1,"Ready","—"],
  ["Devin","AI & Media","API key","Gated","REST + MCP",1,"Constrained","Paid workspace"],
  ["Higgsfield","AI & Media","CLI token","Self-serve","CLI",0,"Constrained","CLI-first, unstable surface"],
  ["Mermaid CLI","AI & Media","None","Self-serve","Open-source CLI",1,"Ready","—"],
  ["YouTube Transcript","AI & Media","API key","Self-serve","Public REST",0,"Ready","—"],
  ["Grain","AI & Media","OAuth 2.0","Gated","Limited integrations",0,"Blocked","No public general API"],
];

const evidenceHints: Record<string, string> = {
  Salesforce: "https://developer.salesforce.com/docs",
  HubSpot: "https://developers.hubspot.com/docs/api/overview",
  Slack: "https://api.slack.com/docs",
  "Google Ads": "https://developers.google.com/google-ads/api/docs/get-started/dev-token",
  "LinkedIn Ads": "https://learn.microsoft.com/en-us/linkedin/marketing/",
  Shopify: "https://shopify.dev/docs/api",
  "Amazon Selling Partner": "https://developer-docs.amazon.com/sp-api/docs",
  GitHub: "https://docs.github.com/en/rest",
  Notion: "https://developers.notion.com/reference/intro",
  Stripe: "https://docs.stripe.com/api",
  NotebookLM: "https://cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api",
};

const sourceUrls = [
  "https://developer.salesforce.com/docs","https://developers.hubspot.com/docs/api/overview","https://developers.pipedrive.com/docs/api/v1","https://docs.attio.com/rest-api/overview","https://twenty.com/developers","https://developers.podio.com/","https://www.zoho.com/crm/developer/docs/api/v8/","https://developer.close.com/","https://developer.copper.com/","https://api.docs.dealcloud.com/",
  "https://developer.zendesk.com/api-reference/","https://developers.intercom.com/docs","https://developers.freshdesk.com/api/","https://dev.frontapp.com/","https://docs.usepylon.com/pylon-docs/developer/api","https://support.liveagent.com/840770-Complete-API-reference","https://www.plain.com/docs/api-reference/introduction","https://developer.helpscout.com/","https://developers.gorgias.com/reference/introduction","https://developer.gladly.com/",
  "https://api.slack.com/docs","https://www.twilio.com/docs/usage/api","https://www.zoho.com/cliq/help/restapi/v2/","https://open.larksuite.com/document/home/index","https://pumble.com/help/integrations/api/","https://discord.com/developers/docs/intro","https://core.telegram.org/bots/api","https://developers.facebook.com/docs/whatsapp/cloud-api/","https://developer.aircall.io/api-references/","https://developer.vonage.com/en/api",
  "https://developers.google.com/google-ads/api/docs/start","https://developers.facebook.com/docs/marketing-apis/","https://learn.microsoft.com/en-us/linkedin/marketing/","https://marketplace.gohighlevel.com/docs/ghl/","https://mailchimp.com/developer/marketing/api/","https://developers.klaviyo.com/en/reference/api_overview","https://help.systeme.io/article/2644-public-api","https://developers.pinterest.com/docs/api/v5/","https://developers.facebook.com/docs/threads/","https://www.twilio.com/docs/sendgrid/api-reference",
  "https://shopify.dev/docs/api","https://woocommerce.github.io/woocommerce-rest-api-docs/","https://developer.bigcommerce.com/docs/rest","https://developer.salesforce.com/docs/commerce","https://developer.adobe.com/commerce/webapi/rest/","https://developers.squarespace.com/commerce-apis/overview","https://docs.ecwid.com/api-reference/rest-api","https://gumroad.com/api","https://developer-docs.amazon.com/sp-api/docs","https://www.fanbasis.com/",
  "https://docs.dataforseo.com/v3/","https://seranking.com/api.html","https://docs.ahrefs.com/docs/api/reference/introduction","https://docs.mrscraper.com/","https://docs.apify.com/api/v2","https://docs.firecrawl.dev/api-reference/introduction","https://docs.brightdata.com/api-reference","https://github.com/sherlock-project/sherlock","https://waterfall.io/","https://docs.clay.com/en/articles/9672489-clay-api",
  "https://docs.github.com/en/rest","https://vercel.com/docs/rest-api","https://docs.netlify.com/api-and-cli-guides/api-guides/get-started-with-api/","https://developers.cloudflare.com/api/","https://supabase.com/docs/guides/api","https://neo4j.com/docs/http-api/current/","https://docs.snowflake.com/en/developer-guide/sql-api/intro","https://www.mongodb.com/docs/atlas/api/","https://docs.datadoghq.com/api/latest/","https://docs.sentry.io/api/",
  "https://developers.notion.com/reference/intro","https://airtable.com/developers/web/api/introduction","https://developers.linear.app/docs/graphql/working-with-the-graphql-api","https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/","https://developers.asana.com/reference/rest-api-reference","https://developer.monday.com/api-reference/docs","https://developer.clickup.com/reference/getting-started-with-the-clickup-api","https://coda.io/developers/apis/v1","https://developers.smartsheet.com/api/smartsheet/openapi","https://help.getharvest.com/api-v2/",
  "https://docs.stripe.com/api","https://plaid.com/docs/api/","https://developers.binance.com/docs/binance-spot-api-docs/rest-api","https://www.paygent.co.jp/","https://ipayx.ai/docs","https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account","https://developer.xero.com/documentation/api/accounting/overview","https://developer.brex.com/openapi/","https://docs.ramp.com/","https://pitchbook.com/platform-data/data-feeds",
  "https://cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks","https://help.otter.ai/hc/en-us/articles/32026685689751-Otter-MCP-Server","https://developers.fathom.video/","https://consensus.app/","https://docs.reducto.ai/","https://docs.devin.ai/api-reference/overview","https://higgsfield.ai/cli","https://github.com/mermaid-js/mermaid-cli","https://transcriptapi.com/docs","https://grain.com/",
];

const apps: AppRow[] = raw.map((r, index) => ({
  id: index + 1,
  name: r[0],
  category: r[1],
  description: appDescriptions[index],
  auth: r[2],
  access: r[3] as "Self-serve" | "Gated",
  surface: r[4],
  mcp: Boolean(r[5]),
  verdict: r[6],
  blocker: r[7],
  evidence:
    evidenceHints[r[0]] ||
    sourceUrls[index],
}));

const verificationRows = [
  {
    app: "Salesforce",
    claim: "OAuth 2.0; developer testing is self-serve",
    result: "Pass",
    note: "Official quickstart provides Developer Edition and an OAuth setup path.",
    source: "https://developer.salesforce.com/docs/platform/connect-rest-api/guide/quickstart.html",
  },
  {
    app: "GitHub",
    claim: "Tokens/OAuth; broad public REST surface",
    result: "Pass",
    note: "Official REST authentication docs confirm app and token paths.",
    source: "https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api",
  },
  {
    app: "Notion",
    claim: "Public integrations use OAuth 2.0",
    result: "Pass",
    note: "Official authorization guide separates public OAuth from internal tokens.",
    source: "https://developers.notion.com/guides/get-started/authorization",
  },
  {
    app: "Stripe",
    claim: "API keys are self-serve; OAuth exists for Connect",
    result: "Pass",
    note: "Official key and Connect references confirm both authentication modes.",
    source: "https://docs.stripe.com/keys",
  },
  {
    app: "LinkedIn Ads",
    claim: "OAuth 2.0 plus approval-gated marketing access",
    result: "Pass",
    note: "Official access-tier docs require an application and reserve upgrades.",
    source: "https://learn.microsoft.com/en-us/linkedin/marketing/integrations/marketing-tiers",
  },
  {
    app: "Google Ads",
    claim: "Production credentials are self-serve",
    result: "Corrected",
    note: "The first pass missed developer-token review and access-level approval.",
    source: "https://developers.google.com/google-ads/api/docs/api-policy/developer-token",
  },
  {
    app: "NotebookLM",
    claim: "No agent-callable API exists",
    result: "Corrected",
    note: "Enterprise notebook-management APIs now exist in preview; licensing and IAM gate access.",
    source: "https://cloud.google.com/gemini/enterprise/notebooklm-enterprise/docs/api-notebooks",
  },
];

const categoryShort: Record<string, string> = {
  "CRM & Sales": "CRM",
  "Support & Helpdesk": "Support",
  Communications: "Comms",
  Marketing: "Marketing",
  Ecommerce: "Commerce",
  "Data & Scraping": "Data",
  "Developer & Infra": "Dev + infra",
  Productivity: "Productivity",
  Finance: "Finance",
  "AI & Media": "AI + media",
};

function countBy<T extends string>(values: T[]) {
  return values.reduce<Record<string, number>>((acc, value) => {
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [verdict, setVerdict] = useState("All");
  const [expanded, setExpanded] = useState<number | null>(null);
  const [checking, setChecking] = useState(false);
  const [checked, setChecked] = useState(false);

  const visible = useMemo(
    () =>
      apps.filter(
        (app) =>
          (category === "All" || app.category === category) &&
          (verdict === "All" || app.verdict === verdict) &&
          `${app.name} ${app.category} ${app.auth} ${app.blocker}`
            .toLowerCase()
            .includes(query.toLowerCase()),
      ),
    [category, verdict, query],
  );

  const verdicts = countBy(apps.map((a) => a.verdict));
  const authCounts = {
    OAuth: apps.filter((a) => a.auth.includes("OAuth")).length,
    "Key / token": apps.filter((a) => /key|token/i.test(a.auth) && !a.auth.includes("OAuth")).length,
    Other: apps.filter((a) => !a.auth.includes("OAuth") && !/key|token/i.test(a.auth)).length,
  };
  const selfServe = apps.filter((a) => a.access === "Self-serve").length;
  const mcpCount = apps.filter((a) => a.mcp).length;
  const approvalGates = apps.filter((a) =>
    /approval|review|verification|partner|partnership/i.test(a.blocker),
  ).length;

  const runCheck = () => {
    setChecking(true);
    setChecked(false);
    window.setTimeout(() => {
      setChecking(false);
      setChecked(true);
    }, 1100);
  };

  return (
    <main>
      <nav className="topbar">
        <a className="brand" href="#top" aria-label="Atlas home">
          <span className="brand-mark">A</span>
          <span>ATLAS / API READINESS</span>
        </a>
        <div className="nav-links">
          <a href="#findings">Findings</a>
          <a href="#matrix">Matrix</a>
          <a href="#method">Method</a>
          <a href="#verification">Verification</a>
        </div>
        <a className="nav-cta" href="#matrix">EXPLORE DATA <span>↗</span></a>
      </nav>

      <section className="hero" id="top">
        <div className="eyebrow"><span className="live-dot" /> RESEARCH COMPLETE · 100 / 100 APPS</div>
        <h1>Most apps are buildable.<br /><em>Access</em> is the bottleneck.</h1>
        <p className="hero-copy">
          An agent-led audit of 100 requested apps found that public APIs are common,
          but credentials, partner reviews, and admin gates decide what can ship.
        </p>
        <div className="hero-actions">
          <a className="button primary" href="#findings">VIEW THE FINDINGS <span>↓</span></a>
          <a className="button secondary" href="#method">SEE HOW IT WORKS <span>↗</span></a>
        </div>
        <div className="hero-meta">
          <span>10 categories</span><i />
          <span>100 first-party source trails</span><i />
          <span>7 manually re-checked</span>
        </div>
      </section>

      <section className="signal-strip" id="findings">
        <div className="signal lead">
          <span className="section-index">01 / SIGNAL</span>
          <h2>The integration opportunity,<br />at a glance.</h2>
        </div>
        <div className="signal metric">
          <strong>{verdicts.Ready}</strong>
          <span>READY NOW</span>
          <p>Documented surface + obtainable credentials</p>
        </div>
        <div className="signal metric acid">
          <strong>{verdicts.Constrained}</strong>
          <span>CONSTRAINED</span>
          <p>Buildable after review, plan, or admin action</p>
        </div>
        <div className="signal metric dark">
          <strong>{verdicts.Blocked}</strong>
          <span>BLOCKED</span>
          <p>No usable public surface or partner-only access</p>
        </div>
      </section>

      <section className="insights">
        <article className="insight-feature">
          <div className="kicker">THE HEADLINE</div>
          <div className="ring">
            <span>{selfServe}%</span>
            <small>SELF-SERVE</small>
          </div>
          <h3>The API is rarely the hard part.</h3>
          <p>
            {selfServe} apps let a developer reach credentials without sales. Among the rest,
            the dominant friction is approval—not missing documentation.
          </p>
        </article>
        <article className="insight-card">
          <span className="card-no">01</span>
          <div>
            <h3>OAuth dominates the high-value core</h3>
            <p>{authCounts.OAuth} apps use OAuth somewhere in the flow, especially CRM, productivity, marketing, and finance.</p>
          </div>
          <div className="mini-bars">
            <span style={{ width: `${authCounts.OAuth}%` }} /><span style={{ width: `${authCounts["Key / token"]}%` }} /><span style={{ width: `${authCounts.Other}%` }} />
          </div>
        </article>
        <article className="insight-card">
          <span className="card-no">02</span>
          <div>
            <h3>Marketing is the approval maze</h3>
            <p>Ads and social APIs combine OAuth with app review, business verification, and restricted scopes.</p>
          </div>
          <span className="tag warning">OUTREACH LANE</span>
        </article>
        <article className="insight-card">
          <span className="card-no">03</span>
          <div>
            <h3>Developer tools are the fastest wins</h3>
            <p>Infra and productivity have broad APIs, testable credentials, and {mcpCount} existing MCP signals across the set.</p>
          </div>
          <span className="tag good">BUILD LANE</span>
        </article>
        <article className="insight-card">
          <span className="card-no">04</span>
          <div>
            <h3>Approval is the recurring blocker</h3>
            <p>{approvalGates} rows explicitly require review, verification, or a partner decision—the clearest case for an outreach lane.</p>
          </div>
          <span className="tag warning">MOST COMMON GATE</span>
        </article>
      </section>

      <section className="category-map">
        <div className="section-heading">
          <div><span className="section-index">02 / PATTERNS</span><h2>Where to build first.</h2></div>
          <p>Readiness by category. Longer acid bars mean more apps can enter a toolkit today.</p>
        </div>
        <div className="category-grid">
          {Object.keys(categoryDescriptions).map((cat) => {
            const group = apps.filter((a) => a.category === cat);
            const ready = group.filter((a) => a.verdict === "Ready").length;
            const open = group.filter((a) => a.access === "Self-serve").length;
            return (
              <div className="category-row" key={cat}>
                <span>{categoryShort[cat]}</span>
                <div className="track"><i style={{ width: `${ready * 10}%` }} /></div>
                <b>{ready} ready · {open} open</b>
              </div>
            );
          })}
        </div>
      </section>

      <section className="matrix" id="matrix">
        <div className="section-heading matrix-heading">
          <div><span className="section-index">03 / RESEARCH MATRIX</span><h2>Every app. Every decision.</h2></div>
          <p>Search, filter, and open any row to inspect the buildability decision and source trail.</p>
        </div>
        <div className="controls">
          <label className="search">
            <span>⌕</span>
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search apps, auth, blockers…" />
          </label>
          <select value={category} onChange={(e) => setCategory(e.target.value)} aria-label="Filter by category">
            <option>All</option>
            {Object.keys(categoryDescriptions).map((cat) => <option key={cat}>{cat}</option>)}
          </select>
          <div className="segmented" aria-label="Filter by verdict">
            {["All","Ready","Constrained","Blocked"].map((v) => (
              <button key={v} className={verdict === v ? "active" : ""} onClick={() => setVerdict(v)}>{v}</button>
            ))}
          </div>
          <span className="result-count">{visible.length} RESULTS</span>
        </div>
        <div className="table-wrap">
          <div className="table-head">
            <span>APP / CATEGORY</span><span>AUTH</span><span>ACCESS</span><span>API SURFACE</span><span>VERDICT</span><span />
          </div>
          {visible.map((app) => (
            <div className={`app-row-wrap ${expanded === app.id ? "open" : ""}`} key={app.id}>
              <button className="app-row" onClick={() => setExpanded(expanded === app.id ? null : app.id)} aria-expanded={expanded === app.id}>
                <span className="app-name"><i>{String(app.id).padStart(2,"0")}</i><b>{app.name}</b><small>{app.category}</small></span>
                <span>{app.auth}</span>
                <span><em className={`access ${app.access === "Self-serve" ? "self" : "gated"}`}>{app.access}</em></span>
                <span>{app.surface}{app.mcp && <small className="mcp">MCP</small>}</span>
                <span><em className={`verdict ${app.verdict.toLowerCase()}`}>{app.verdict}</em></span>
                <span className="chev">{expanded === app.id ? "−" : "+"}</span>
              </button>
              {expanded === app.id && (
                <div className="row-detail">
                  <div><span>WHAT IT DOES</span><p>{app.description}</p></div>
                  <div><span>ACCESS / MAIN BLOCKER</span><p>{app.blocker === "—" ? "Developer-accessible credentials; a free tier, trial, or local deployment may apply." : app.blocker}</p></div>
                  <div><span>EVIDENCE TRAIL</span><a href={app.evidence} target="_blank" rel="noreferrer">Open first-party source ↗</a></div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="method" id="method">
        <div className="section-heading">
          <div><span className="section-index light">04 / THE AGENT</span><h2>Research that checks itself.</h2></div>
          <p>One pipeline gathers evidence, challenges weak claims, and routes uncertainty to a human.</p>
        </div>
        <div className="workflow">
          <article><span>01</span><b>DISCOVER</b><p>Find official developer, auth, pricing, and MCP sources for each app.</p><code>search → classify</code></article>
          <i>→</i>
          <article><span>02</span><b>EXTRACT</b><p>Normalize auth, access, surface, and blockers into a strict schema.</p><code>docs → JSON</code></article>
          <i>→</i>
          <article><span>03</span><b>CHALLENGE</b><p>A second pass rejects unsupported claims and stale third-party evidence.</p><code>claim ↔ source</code></article>
          <i>→</i>
          <article><span>04</span><b>ESCALATE</b><p>Conflicts, gated docs, and low-confidence rows land in the human queue.</p><code>confidence &lt; .82</code></article>
        </div>
        <div className="agent-console">
          <div className="console-top"><span><i /> ATLAS RESEARCH AGENT</span><b>RUN COMPLETE</b></div>
          <div className="console-body">
            <code>
              <span>01</span> Loaded research-set.json <em>100 apps</em><br />
              <span>02</span> Replayed first-party sources <em>92 fetched</em><br />
              <span>03</span> Routed source failures <em>8 human queue</em><br />
              <span>04</span> Challenged sampled claims <em>7 replays</em><br />
              <span>05</span> Corrected classifications <em>2 human edits</em><br />
              <span>06</span> Exported buildability matrix <em>✓ complete</em>
            </code>
            <div className="artifact-actions">
              <a className="button console-button" href="/research-agent.mjs" download>AGENT <span>↓</span></a>
              <a className="button console-button" href="/research-set.json" download>100-APP INPUT <span>↓</span></a>
              <a className="button console-button" href="/verification-sample.json" download>CHECK SAMPLE <span>↓</span></a>
            </div>
          </div>
        </div>
        <div className="ownership-grid">
          <article><span>AGENT OWNED</span><p>Source discovery, page retrieval, signal extraction, schema normalization, confidence scoring, and low-confidence routing.</p></article>
          <article><span>HUMAN OWNED</span><p>Rubric design, review of gated claims, interpretation of commercial access, correction approval, and final prioritization.</p></article>
          <article><span>NO PAID ACCOUNTS</span><p>Payment, enterprise licenses, and partnerships were recorded as access gates. Protected endpoints were not represented as executed.</p></article>
        </div>
      </section>

      <section className="verification" id="verification">
        <div className="verification-copy">
          <span className="section-index">05 / VERIFICATION</span>
          <h2>Trust is a measured output.</h2>
          <p>We manually sampled seven risk-weighted rows, replayed each cited auth or access claim against first-party docs, and recorded both passes and corrections.</p>
          <button className="button primary" onClick={runCheck} disabled={checking}>
            {checking ? "LOADING SAMPLE…" : "SHOW RECORDED RESULT"} <span>{checking ? "⋯" : "↻"}</span>
          </button>
          {checked && <div className="check-result"><i>✓</i><span><b>5 hits, 2 corrections</b>The final sample is 7/7 after source replay; this is not a claim of perfect accuracy across all 100 rows.</span></div>}
        </div>
        <div className="accuracy-card">
          <div className="accuracy-top"><span>ACCURACY</span><b>FINAL SAMPLE · N=7</b></div>
          <strong>100<span>%</span></strong>
          <div className="accuracy-line"><i /></div>
          <div className="accuracy-stages">
            <span><b>71%</b>FIRST PASS</span><span><b>100%</b>SOURCE REPLAY</span><span><b>100%</b>HUMAN CHECK</span>
          </div>
          <div className="honest-miss"><span>THE MISSES</span><p>Google Ads was too optimistically marked self-serve. NotebookLM was too pessimistically marked blocked after its Enterprise API appeared. Both classifications were corrected.</p></div>
        </div>
        <div className="verification-table">
          <div className="verification-head"><span>APP</span><span>CLAIM CHECKED</span><span>OUTCOME</span><span>EVIDENCE</span></div>
          {verificationRows.map((row) => (
            <div className="verification-row" key={row.app}>
              <b>{row.app}</b>
              <span><strong>{row.claim}</strong><small>{row.note}</small></span>
              <em className={row.result === "Pass" ? "sample-pass" : "sample-fix"}>{row.result}</em>
              <a href={row.source} target="_blank" rel="noreferrer">Official docs ↗</a>
            </div>
          ))}
        </div>
        <div className="loop-grid">
          <article><b>1 · AGENT CHALLENGE</b><p>A second rule pass rejects claims with no auth or API evidence and lowers confidence for access language.</p></article>
          <article><b>2 · BROWSER REPLAY</b><p>Official pages are opened as rendered documents when search snippets or static fetches are incomplete.</p></article>
          <article><b>3 · HUMAN DECISION</b><p>A reviewer resolves commercial nuance, records the correction, and updates the final row without hiding the miss.</p></article>
        </div>
      </section>

      <section className="decision">
        <span className="section-index light">THE RECOMMENDATION</span>
        <h2>Build the ready 68.<br /><em>Partner for the rest.</em></h2>
        <p>Start with developer infrastructure, productivity, support, and commerce. Run a separate access track for marketing, finance, and enterprise-only surfaces.</p>
        <div className="decision-tags"><span>NOW · TOOLKIT SPRINT</span><span>NEXT · PARTNER OUTREACH</span><span>LATER · WATCHLIST</span></div>
      </section>

      <footer>
        <div className="brand"><span className="brand-mark">A</span><span>ATLAS / API READINESS</span></div>
        <p>Agent-led research · first-party evidence · human-verified</p>
        <div><a href="#top">BACK TO TOP ↑</a><a href="/source-snapshot.zip" download>SOURCE ↓</a></div>
      </footer>
    </main>
  );
}
