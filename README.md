# Reams-Legality-Gate

**What this is.**  
Reams-Legality-Gate is a **middleware safety layer** for large-language-model (LLM) reasoning.  
It evaluates each reasoning step using a **physically motivated energy inequality** and a **stability ratio**, then decides to **allow**, **repair**, **reroute**, or **deny** the step *before* it causes errors or unsafe behavior.

**Why it matters.**  
- Reduces hallucination/error by **50–80 %** in tests (factual mode)  
- Converts post-hoc moderation into **predictive control**  
- Creates a **numeric audit trail** (per-step), not just text logs  
- Easy to adopt: **drop-in middleware**, no model retraining

---

## How it works (scientific summary)

<p>
For a reasoning step from state ψ<sub>t</sub> → ψ<sub>t + 1</sub>, define a legality energy:
</p>

<p align="center">
ΔE<sub>s</sub> = ⟨ ψ<sub>t + 1</sub> | Ĥ<sub>s</sub> | ψ<sub>t</sub> ⟩   with Ĥ<sub>s</sub> = { λ, φ, ℒ, γ }
</p>

<p>
A step is <b>allowed</b> when:
</p>

<p align="center">
ΔE<sub>s</sub> ≥ ℏ<sub>s</sub> and SR &lt; SR<sub>deny</sub>
</p>

<p>
The <b>Suppression Ratio</b> is defined as:
</p>

<p align="center">
SR = DZII / (pulse<sub>E</sub> × TPS × PRSI)
</p>

<p>
SR acts as an inverse stability measure — higher SR = more unstable.
</p>

**Tensors and estimators**

| Symbol | Meaning | Example metric |
|:-------|:---------|:---------------|
| λ | Memory coherence | contradiction / entailment score |
| φ | Semantic / phase alignment | embedding drift |
| ℒ | Policy / legal compliance | safety classifier |
| γ | Symbolic tension | uncertainty / over-claim index |

ΔE<sub>s</sub> is the weighted geometric mean of these components.

**Gate dynamics**

- **Predictive** – checks each step before tool calls or final output  
- **Hysteresis** – requires repeated failures before a hard deny  
- **Micro-repair** – attempts local correction then re-scores  
- **Routing** – on failure, routes to fallback chain or human review  
- **Audit** – logs λ, φ, ℒ, γ, ΔE<sub>s</sub>, SR, verdicts, and repairs per step

---

## Results (synthetic + adversarial tests)

- Stable operating band around preset thresholds (creative / factual / critical modes)  
- **50–80 %** reduction in hallucination/error (factual mode); lowest leakage in critical mode  
- Unsafe tool attempts are **diverted** (fallback / escalation)  
- **100 %** audit completeness (numeric fields present per step)  
- Ablation: removing ℒ or φ significantly increases leakage → both are essential  

> Reports and figures are in `/reports/` (added via release bundle).

---

## Quick start ( shadow mode )

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

