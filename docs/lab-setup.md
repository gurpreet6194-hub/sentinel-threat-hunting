# Microsoft Sentinel Lab Setup Guide

Everything below uses free or trial tiers — no paid licenses required to run
the queries in `../queries/`.

## 1. Accounts and trials

| Component | How to get it free | What it unlocks |
|---|---|---|
| Microsoft 365 E5 trial | Microsoft 365 admin center → Billing → Purchase services → "Microsoft 365 E5" 30-day trial (new tenants) | Entra ID P2: `SigninLogs`, `AuditLogs`, Identity Protection |
| Azure free account | azure.microsoft.com/free — 12 months of free services + credit | Log Analytics workspace to host Sentinel |
| Microsoft Sentinel | In the Azure portal, on your Log Analytics workspace → "Add Microsoft Sentinel" — first 31 days of ingestion are free | The SIEM itself: Logs, Hunting, Analytics rules |
| Defender for Endpoint P2 trial | Microsoft Defender portal → Trials — 90-day Defender for Endpoint P2 trial, onboard 1–2 VMs | `DeviceNetworkEvents`, `DeviceProcessEvents`, `DeviceFileEvents` |

## 2. Wiring data in (order matters)

1. **Create the Log Analytics workspace** (Azure portal → Log Analytics
   workspaces), then enable **Microsoft Sentinel** on it.
2. **Content hub → install data connectors**: "Microsoft Entra ID",
   "Microsoft Defender for Endpoint", "Office 365", "Azure Activity".
3. **Open each connector page and connect**: for Entra ID, tick
   *Sign-in logs*, *Audit logs*, *Non-interactive sign-in logs* and let it
   stream into the workspace.
4. **Defender for Endpoint**: onboard a trial VM (or your own test VM) so
   `DeviceNetworkEvents` starts flowing — this powers the data-egress query.
5. Wait 15–60 minutes for first data, then open **Sentinel → Logs** and run
   `SigninLogs | take 10` to confirm ingestion.

## 3. Running the query pack

- **Ad hoc**: Sentinel → Logs → paste any file from `../queries/` → Run.
  Adjust the `ago(...)` windows down (e.g. `ago(1h)`) while testing so you
  get fast results on small trial datasets.
- **Saved hunts**: Sentinel → Threat management → Hunting → Queries → "New
  query" → paste the KQL, set the data source tables, save. Re-run on a
  schedule during the trial to build a hunting habit.
- **Analytics rules** (detection-as-code): Sentinel → Configuration →
  Analytics → Create → Scheduled query rule → paste the query, set the
  entity mappings (IP → `IPAddress`, Account → `UserPrincipalName`), and
  start with the brute-force query — it is the least noisy.

## 4. Generating your own test data

Trials rarely have attacks in them. Safe ways to produce signal:

- Run a **controlled password spray** against your own trial tenant from a
  lab VM (document the source IP first so you can find it in the results).
- Use the **Microsoft 365 attack simulator** (Defender portal → Attack
  simulation training) for consent-grant scenarios.
- Simulate egress with a large file copy to external storage from the
  onboarded VM, then tune `sensitivityMultiplier` in the egress query.

Never run these against production tenants or accounts you do not own.
