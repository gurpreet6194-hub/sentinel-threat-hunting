# Sentinel Threat-Hunting Query Pack

KQL hunting queries for Microsoft Sentinel, each documented with its purpose,
detection logic, tuning guidance, and investigation steps. Built for the
tables a Sentinel trial workspace provides (`SigninLogs`, `AuditLogs`,
`DeviceNetworkEvents`).

## Skills demonstrated

- KQL: aggregations (`summarize`, `dcount`, `make_set`, `arg_max`),
  time windows (`ago`, `bin`, `between`), anti-joins for dormancy checks
- Threat hunting methodology: hypothesis → query → pivot → investigate
- MITRE ATT&CK mapping for each query
- Detection-as-code discipline: every query ships with tuning notes and
  next steps, not just the query text

## Query catalog

| File | Purpose | Primary table | MITRE |
|---|---|---|---|
| `queries/brute_force_campaign.kql` | Flag IPs with abnormal failed-sign-in volumes, including low-and-slow password spraying via distinct-user counts | `SigninLogs` | T1110.001, T1110.003 |
| `queries/anomalous_data_egress.kql` | Catch devices sending far above their 7-day baseline (possible exfiltration) | `DeviceNetworkEvents` | T1041, T1048 |
| `queries/admin_consent_grants.kql` | Detect new admin consent / app role grants — rogue OAuth-app persistence | `AuditLogs` | T1550.001, T1136 |
| `queries/dormant_account_reactivation.kql` | Find accounts signing in after 90+ days of silence (possible takeover) | `SigninLogs` | T1078 |

## Usage

1. **Ad hoc**: Sentinel → Logs → paste a query → Run. Shrink the `ago(...)`
   windows while testing on small trial datasets.
2. **Saved hunts**: Threat management → Hunting → Queries → New query.
3. **Analytics rules**: Configuration → Analytics → Scheduled query rule.
   Map entities (`IPAddress`, `UserPrincipalName`) so incidents get proper
   entity graphs.

## Validation

KQL can only be fully validated against a live workspace. Until then,
`validate_kql.py` runs the checks that *are* possible offline:

```bash
python3 validate_kql.py
# [ OK ] admin_consent_grants.kql
# [ OK ] anomalous_data_egress.kql
# [ OK ] brute_force_campaign.kql
# [ OK ] dormant_account_reactivation.kql
# 4 passed, 0 failed (structural check only — ...)
```

It verifies balanced delimiters, the documentation header, and pipeline
structure — and was itself tested against a deliberately broken query.

## Lab setup

See [`docs/lab-setup.md`](docs/lab-setup.md) for building the free/trial
environment these queries run against: Microsoft 365 E5 trial, Azure free
account, 31-day Sentinel trial, Defender for Endpoint P2 trial, and which
data connectors to enable.
