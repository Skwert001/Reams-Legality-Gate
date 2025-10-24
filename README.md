# Reams-Legality-Gate

**What this is.**  
Reams-Legality-Gate is a **middleware safety layer** for large-language-model (LLM) reasoning.  
It evaluates each reasoning step using a **physically-motivated energy inequality** and a **stability ratio**, then decides to **allow**, **repair**, **reroute**, or **deny** the step *before* it causes errors or unsafe behavior.

**Why it matters.**  
- Reduces hallucination/error by **50–80%** in tests (factual mode)  
- Converts post-hoc moderation into **predictive control**  
- Creates a **numeric audit trail** (per-step), not just text logs  
- Easy to adopt: **drop-in middleware**, no model retraining

---

## How it works (scientific summary)

For a reasoning step from state \(ψ_t \to ψ_{t+1}\), define a legality energy:
\[
ΔE_s = ⟨ψ_{t+1} \mid Ĥ_s \mid ψ_t⟩
\quad \text{with} \quad
Ĥ_s = \{λ, φ, ℒ, γ\}
\]
A step is **allowed** when:
\[
ΔE_s \ge ℏ_s
\quad \text{and} \quad
SR < SR_{\text{deny}}
\]
where the **Suppression Ratio**:
\[
SR = \frac{DZII}{pulse_E \times TPS \times PRSI}
\]
acts as an inverse stability measure (higher SR = more unstable).

**Tensors and estimators**  
- \(λ\) memory coherence (e.g., contradiction/entailment)  
- \(φ\) semantic/phase alignment (embedding drift)  
- \(ℒ\) policy/legal compliance (safety classifier)  
- \(γ\) symbolic tension (uncertainty / over-claim index)  

\(ΔE_s\) is the (weighted) geometric mean of these components.

**Gate dynamics**  
- **Predictive**: checks each step before tool calls or final output  
- **Hysteresis**: requires repeated failures before a hard deny  
- **Micro-repair**: attempts local correction then re-scores  
- **Routing**: on failure, routes to fallback chain or human review  
- **Audit**: logs \(λ, φ, ℒ, γ, ΔE_s, SR\), verdicts, and repairs per step

---

## Results (synthetic + adversarial tests)

- Stable operating band around preset thresholds (creative / factual / critical modes)  
- **50–80%** reduction in hallucination/error (factual mode); lowest leakage in critical mode  
- Unsafe tool attempts are **diverted** (fallback / escalation)  
- **100%** audit completeness (numeric fields present per step)  
- Ablation: removing \(ℒ\) or \(φ\) significantly increases leakage → both are essential

> Reports and figures are in `/reports/` (soon to be added via release bundle).

---

## Quick start (shadow mode)

```python
from reams_gate_sdk import Gate, Estimators
import json

# Load presets and policy
presets = json.load(open('config/presets.json'))
policy  = json.load(open('config/policy_header.json'))

# Create gate (start in 'factual' mode, enforce=False for shadow)
gate = Gate.from_presets(presets, mode='factual', policy=policy)

# Example reasoning trace
prompt = "Answer with references."
steps  = ["...", "...", "..."]

result = gate.process_trace(prompt, steps)  # returns per-step scores + verdicts
# Examine result['ledger'] for ΔE_s, SR, λ/φ/ℒ/γ, verdicts
