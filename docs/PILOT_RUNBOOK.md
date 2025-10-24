# Pilot Runbook: Shadow → Enforce Deployment

**Purpose**  
This runbook defines the 10-day procedure for testing and enabling the Reams-Legality-Gate SDK
within an existing reasoning or retrieval-augmented generation (RAG) system.

**Objective**  
Verify that legality gating reduces error and hallucination rates without harming latency or throughput,
and demonstrate a measurable return on safety and auditability.

---

## 0.  Prerequisites

- Python 3.10 + environment  
- LLM or agent framework (LangChain, crewAI, or equivalent)  
- Access to logs or output traces for error tracking  
- `Reams-Legality-Gate` repository cloned locally  
- Preset and policy files from `/config` in place

---

## 1.  Configuration

| Parameter | Default | Description |
|------------|----------|-------------|
| `mode` | `factual` | Balanced preset for production validation |
| `enforce` | `false` | Start in **shadow** mode (log only) |
| `retention_days` | `30` | Audit log retention period |
| `cloak` | `true` | Mask thresholds in public logs |
| `prsi_min` | `0.75` | Evidence/reference integrity floor |

---

## 2.  Day-by-Day Checklist

| Day | Phase | Action |
|-----|--------|--------|
| **1** | Initialization | Install SDK, confirm imports, and run the included demo trace. |
| **2** | Integration | Wrap the gate around one reasoning chain (e.g., RAG query path).  Start collecting per-step ΔEₛ and SR logs. |
| **3** | Baseline logging | Keep enforcement off; record 100–200 steps of normal output for comparison. |
| **4** | Validation | Review audit logs: confirm ΔEₛ ≥ ℏₛ events align with coherent outputs; SR peaks correspond to instability. |
| **5** | Threshold tuning | Adjust `hbar_s` ± 5 %, `sr_deny` ± 5 % to minimize false denials. |
| **6** | Partial enforcement | Set `enforce=true` for *factual* contexts only. Keep creative routes in shadow. |
| **7** | Routing test | Force several failure scenarios; verify fallback / escalate paths execute correctly. |
| **8** | Performance audit | Measure latency overhead (target < 20 % per step). |
| **9** | Metrics review | Compare hallucination and error rates vs. baseline; compute percentage savings. |
| **10** | Report & seal | Append SHA-256 seal to `/seals/SEAL_LEDGER.jsonl` and export summary metrics to `/reports/`. |

---

## 3.  Success Criteria

| Metric | Target |
|---------|--------|
| Hallucination/error reduction | ≥ 50 % |
| Reviewer labor reduction | ≥ 40 % |
| Average latency overhead | ≤ 20 % |
| Audit completeness | 100 % (ΔEₛ and SR per step) |
| PRSI compliance | ≥ 95 % of lawful steps above floor |

---

## 4.  Data to Collect

- `shadow_ledger.jsonl` — raw per-step metrics  
- `summary.csv` — daily aggregate metrics  
- `before_after_examples.md` — short qualitative samples  
- `performance.json` — latency and throughput stats

---

## 5.  Reporting Template

```text
Pilot: Reams-Legality-Gate  Ω.84
System: [Agent / RAG / Pipeline name]
Duration: [Dates]
Total steps: [N]
Mode: factual
Enforce: true (from Day 6)
ΔEₛ threshold: [value]
SR deny: [value]

Results:
  • Hallucination reduction: [ % ]
  • Review time saved: [ % ]
  • Latency overhead: [ ms  or % ]
  • Audit completeness: [ % ]

SHA-256 seal: [ hash ]
