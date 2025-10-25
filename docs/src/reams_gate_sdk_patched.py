
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
import math, re, json, numpy as np

BANNED = {"exploit","bypass","harm","malware","weapon","illegal","jailbreak","private data","ssn"}
CERTAINTY = {"always","never","guarantee","prove","impossible","certain","must","undeniably"}
EVIDENCE = {"because","according","study","paper","data","source","citation","ref","evidence","figure","table","appendix","[","]"}

def _tok(t): return re.findall(r"[a-zA-Z0-9]+", (t or "").lower())
def _bow(t):
    from collections import Counter
    return Counter(_tok(t))
def _cos(a,b):
    if not a or not b: return 0.0
    keys=set(a)|set(b)
    dot=sum(a.get(k,0)*b.get(k,0) for k in keys)
    na=(sum(v*v for v in a.values()))**0.5
    nb=(sum(v*v for v in b.values()))**0.5
    if na==0 or nb==0: return 0.0
    return dot/(na*nb)

def _λ(history, step): return _cos(_bow(history), _bow(step))
def _φ(prompt, step):  return _cos(_bow(prompt), _bow(step))
def _ℒ(step):
    t=(step or "").lower()
    hits=sum(1 for w in BANNED if w in t)
    return max(0.0, 1.0-0.25*hits)
def _γ(step):
    t=(step or "").lower()
    hits=sum(1 for w in CERTAINTY if w in t)
    return max(0.0, 1.0-0.15*hits)

def _evidence_density(step):
    t=(step or ""); toks=_tok(t)
    if not toks: return 0.0
    hits=sum(1 for w in EVIDENCE if w in t.lower())
    nums=len(re.findall(r"\d+(\.\d+)?", t))
    return min(1.0, (hits + 0.5*nums) / (len(toks)/20 + 1e-9))

def _retrieval_dispersion(step):
    toks=_tok(step); 
    if not toks: return 0.0
    return len(set(toks))/len(toks)
def _tokens_per_step(step): return min(1.0, len(_tok(step))/100.0)
def _prsi_integrity(step):
    cites=len(re.findall(r"\[[^\]]+\]", step or ""))
    quotes=len(re.findall(r"\"[^\"]+\"", step or ""))
    proper=len(re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b", step or ""))
    raw=cites*0.5 + quotes*0.3 + min(1, proper/10)
    return max(0.0, min(1.0, raw))
def SR(step):
    DZII=_retrieval_dispersion(step)+1e-6
    pulse=_evidence_density(step)+1e-6
    TPS=_tokens_per_step(step)+1e-6
    PRSI=_prsi_integrity(step)+1e-6
    return DZII/(pulse*TPS*PRSI+1e-9), PRSI

def delta_Es(lam, phi, L, gamma, weights):
    eps=1e-9
    return math.exp(
        weights["λ"]*math.log(lam+eps) +
        weights["φ"]*math.log(phi+eps) +
        weights["ℒ"]*math.log(L+eps) +
        weights["γ"]*math.log(gamma+eps)
    )

@dataclass
class GateConfig:
    hbar_s: float
    sr_deny: float
    hysteresis: int
    p_repair: float
    repair_gain: float
    weights: Dict[str,float]

class Gate:
    def __init__(self, config: GateConfig, policy: Dict[str,Any]):
        self.cfg = config
        self.policy = policy
        self.history = ""
        self.fail_streak = 0
        self.hibernating = False
        self.alert_buf = []

    def _alert_check(self, des, sr) -> bool:
        self.alert_buf.append((des, sr))
        if len(self.alert_buf) < 3: return False
        mdes = sum(d for d,_ in self.alert_buf[-3:]) / 3.0
        msr  = sum(s for _,s in self.alert_buf[-3:]) / 3.0
        return (mdes < 0.5*self.cfg.hbar_s) or (msr > 0.8*self.cfg.sr_deny)

    def score_step(self, prompt: str, step: str) -> Dict[str,Any]:
        if self.hibernating:
            return {"verdict":"hibernate","reason":"killswitch engaged"}

        lam = _λ(self.history, step); phi = _φ(prompt, step)
        L  = _ℒ(step); gamma = _γ(step)
        des = delta_Es(lam, phi, L, gamma, self.cfg.weights)
        sr, prsi = SR(step)

        prsi_pass = True if not self.policy.get("enforce", False) else (prsi >= self.policy.get("prsi_min", 0.75))
        allow = (des >= self.cfg.hbar_s and sr < self.cfg.sr_deny and prsi_pass)
        verdict = "allow" if allow else "deny"

        if not allow:
            self.fail_streak += 1
            if self.cfg.hysteresis and self.fail_streak < self.cfg.hysteresis:
                verdict = "allow"
        else:
            self.fail_streak = 0

        repair=False
        if verdict=="deny" and np.random.rand() < self.cfg.p_repair:
            repair=True
            step = step + " [clarified with evidence]"
            lam = min(1.0, lam + self.cfg.repair_gain*0.1)
            phi = min(1.0, phi + self.cfg.repair_gain*0.1)
            des = delta_Es(lam, phi, L, gamma, self.cfg.weights)
            sr, prsi = SR(step)
            prsi_pass = True if not self.policy.get("enforce", False) else (prsi >= self.policy.get("prsi_min", 0.75))
            if des >= self.cfg.hbar_s and sr < self.cfg.sr_deny and prsi_pass:
                verdict="allow"

        if verdict=="allow":
            self.history += " " + step

        # alerts + killswitch (simplified)
        if self.policy.get("enforce", False):
            is_alert = self._alert_check(des, sr)
            if not hasattr(self, "_ks"): self._ks = {"alerts":0,"steps":0,"mleak":0}
            self._ks["steps"] += 1
            if is_alert: self._ks["alerts"] += 1
            # malicious leak heuristic: L very low and banned keyword while allowed
            mal_kw = any(k in (step or "").lower() for k in ["exploit","jailbreak","ssn"])
            if verdict=="allow" and (L < self.policy["killswitch"]["L_floor_burst"]) and mal_kw:
                self._ks["mleak"] += 1
            if (self._ks["alerts"] >= self.policy["killswitch"]["alerts_in_window"]["k"] and
                self._ks["steps"] <= self.policy["killswitch"]["alerts_in_window"]["window_steps"]):
                self.hibernating = True; verdict="hibernate"
            if self._ks["mleak"] > self.policy["killswitch"]["malicious_leak_limit"]:
                self.hibernating = True; verdict="hibernate"

        return {"verdict":verdict, "λ":lam, "φ":phi, "ℒ":L, "γ":gamma, "ΔE_s":des, "SR":sr, "PRSI":prsi, "repair":repair}
