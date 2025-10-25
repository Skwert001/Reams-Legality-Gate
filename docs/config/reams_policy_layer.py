
import json, hashlib, time, math, random
from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class CloakResult:
    hbar_private: float
    sr_deny_private: float
    hbar_public_band: Tuple[float, float]
    sr_public_band: Tuple[float, float]

def cloak_thresholds(hbar_s: float, sr_deny: float, pct_hbar: float, pct_sr: float) -> CloakResult:
    def jitter(val, pct):
        delta = val * pct
        return val + random.uniform(-delta, delta)
    h_priv = jitter(hbar_s, pct_hbar)
    s_priv = jitter(sr_deny, pct_sr)
    h_lo, h_hi = round(hbar_s*(1-pct_hbar),3), round(hbar_s*(1+pct_hbar),3)
    s_lo, s_hi = round(sr_deny*(1-pct_sr),3), round(sr_deny*(1+pct_sr),3)
    return CloakResult(h_priv, s_priv, (h_lo,h_hi), (s_lo,s_hi))

def prsi_hard_check(prsi: float, floor: float=0.75) -> bool:
    return prsi >= floor

def redact_text(s: str) -> str:
    import re
    s = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b','[redacted-email]', s)
    s = re.sub(r'\b\d{3}-\d{2}-\d{4}\b','[redacted-ssn]', s)
    s = re.sub(r'\b\d{9,}\b','[redacted-num]', s)
    return s

@dataclass
class KillState:
    alerts: int = 0
    steps: int = 0
    L_bursts: int = 0
    malicious_leaks: int = 0
    hibernating: bool = False

def update_killswitch(state: KillState, is_alert: bool, L_value: float, is_malicious_leak: bool, policy: Dict[str,Any]) -> KillState:
    state.steps += 1
    if is_alert:
        state.alerts += 1
    if L_value < policy["killswitch"]["L_floor_burst"]:
        state.L_bursts += 1
    if is_malicious_leak:
        state.malicious_leaks += 1
    if state.alerts >= policy["killswitch"]["alerts_in_window"]["k"] and state.steps <= policy["killswitch"]["alerts_in_window"]["window_steps"]:
        state.hibernating = True
    if state.malicious_leaks > policy["killswitch"]["malicious_leak_limit"]:
        state.hibernating = True
    return state

def seal_append(ledger_path: str, meta: Dict[str,Any], seal_log: str):
    import json, hashlib, os, time
    if os.path.exists(ledger_path):
        with open(ledger_path, 'rb') as f:
            blob = f.read()
        digest = hashlib.sha256(blob).hexdigest()
    else:
        digest = hashlib.sha256(json.dumps(meta, sort_keys=True).encode()).hexdigest()
    record = {"ts": int(time.time()), "ledger": ledger_path, "sha256": digest, "meta": meta}
    with open(seal_log, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record
