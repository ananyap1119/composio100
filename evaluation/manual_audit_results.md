# First-pass manual audit results

Sampled apps: 10
Completed audited claims: 50 of 50

| Metric | Result |
|---|---:|
| Supported | 23 |
| Incorrect | 3 |
| Missed evidence | 23 |
| Correctly uncertain | 1 |
| Incomplete | 0 |
| Concrete-claim precision | 88.5% |
| Evidence coverage | 98.0% |
| Overall audit correctness | 48.0% |
| Verdict accuracy | 40.0% |

## Accuracy by app
- Salesforce: 5/5 (100.0%)
- HubSpot: 4/5 (80.0%)
- Apify: 5/5 (100.0%)
- Close: 1/5 (20.0%)
- Jira: 1/5 (20.0%)
- Otter AI: 2/5 (40.0%)
- Linear: 0/5 (0.0%)
- Front: 1/5 (20.0%)
- Shopify: 4/5 (80.0%)
- Zoho CRM: 1/5 (20.0%)

## Accuracy by field
- api_breadth: {'claims': 12, 'supported': 5, 'incorrect': 0, 'missed_evidence': 7, 'correctly_uncertain': 0}
- authentication: {'claims': 9, 'supported': 3, 'incorrect': 1, 'missed_evidence': 5, 'correctly_uncertain': 0}
- buildability_verdict: {'claims': 10, 'supported': 4, 'incorrect': 0, 'missed_evidence': 5, 'correctly_uncertain': 1}
- documented_api: {'claims': 4, 'supported': 3, 'incorrect': 0, 'missed_evidence': 1, 'correctly_uncertain': 0}
- existing_customer_admin_access: {'claims': 5, 'supported': 2, 'incorrect': 1, 'missed_evidence': 2, 'correctly_uncertain': 0}
- independent_developer_access: {'claims': 7, 'supported': 3, 'incorrect': 1, 'missed_evidence': 3, 'correctly_uncertain': 0}
- mcp_status: {'claims': 2, 'supported': 2, 'incorrect': 0, 'missed_evidence': 0, 'correctly_uncertain': 0}
- multi_tenant_partner_access: {'claims': 1, 'supported': 1, 'incorrect': 0, 'missed_evidence': 0, 'correctly_uncertain': 0}

## Failure taxonomy
- incorrect terminology: 1
- insufficient source retrieval: 9
- credential-path confusion: 2
- custom-app versus public-distribution confusion: 11
- developer versus customer access confusion: 3

## Systemic fixes
- Prioritize credential-creation and developer-console documentation.
- Separate developer app creation from customer workspace/site authorization.
- Distinguish private/custom apps from public marketplace distribution and review.
- Normalize OAuth, private-app token, API-key and bearer-token terminology per provider.
- Expand GraphQL and API-reference retrieval queries for public API/read/write evidence.
- Classify official MCP servers separately from community or unknown MCP mentions.