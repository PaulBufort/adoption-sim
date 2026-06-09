"""Scenario configs (TOML) and versioned results (CSV + JSON metadata sidecar).

Engineering note (see docs/journal.md): TOML via stdlib ``tomllib`` instead of the
spec's YAML wording, to honor the hard dependency policy (NetworkX + NumPy +
Streamlit only). Unknown keys fail loudly with a suggestion — a typo in a scenario
file must never silently fall back to a default.

Stack policy: numpy + stdlib only.
"""

from __future__ import annotations

import csv
import datetime
import difflib
import json
import pathlib
import platform
import subprocess
import tomllib

import numpy as np

from core import defaults
from core.dynamics import SimParams
from core.seeding import STRATEGIES

_ORG_EXTRA = {"weights", "sister_close"}
_SECTIONS = {
    "meta": {"name", "description"},
    "org": set(defaults.ORG) | _ORG_EXTRA,
    "agents": set(defaults.AGENTS),
    "dynamics": set(defaults.DYNAMICS) | {"w_comms"},
    "seeding": set(defaults.SEEDING) | {"strategy"},
    "run": {"replicates", "master_seed", "share_graph"},
}


def default_scenario() -> dict:
    """Full scenario with every default filled in (single source: core/defaults.py)."""
    return {
        "meta": {"name": "unnamed", "description": ""},
        "org": dict(defaults.ORG),
        "agents": dict(defaults.AGENTS),
        "dynamics": dict(defaults.DYNAMICS),
        "seeding": {"strategy": "cluster", **defaults.SEEDING},
        "run": {
            "replicates": defaults.ANALYSIS["replicates"],
            "master_seed": 0,
            "share_graph": False,
        },
    }


def load_scenario(path: str | pathlib.Path) -> dict:
    """Load a TOML scenario, validate keys, merge over defaults."""
    with open(path, "rb") as fh:
        user = tomllib.load(fh)
    sc = default_scenario()
    for section, values in user.items():
        if section not in _SECTIONS:
            raise ValueError(_unknown(section, _SECTIONS, f"section [{section}]"))
        if not isinstance(values, dict):
            raise ValueError(f"[{section}] must be a table of key = value pairs")
        for key, val in values.items():
            if key not in _SECTIONS[section]:
                raise ValueError(_unknown(key, _SECTIONS[section], f"key {section}.{key}"))
            sc[section][key] = val
    strategy = sc["seeding"]["strategy"]
    if strategy not in STRATEGIES:
        raise ValueError(_unknown(strategy, STRATEGIES, f"seeding.strategy {strategy!r}"))
    return sc


def _unknown(value: str, known, label: str) -> str:
    hint = difflib.get_close_matches(str(value), [str(k) for k in known], n=1)
    suggestion = f" — did you mean {hint[0]!r}?" if hint else ""
    return f"unknown {label}{suggestion} (valid: {', '.join(sorted(map(str, known)))})"


def build_sim_params(sc: dict) -> SimParams:
    a, d = sc["agents"], sc["dynamics"]
    able = a["able_rate_default"]
    able_rates = a.get("able_rates", able)
    if isinstance(able_rates, dict):  # TOML keys are strings; depts are ints
        able_rates = {int(k): float(v) for k, v in able_rates.items()}
    return SimParams(
        theta_mean=a["theta_mean"],
        theta_concentration=a["theta_concentration"],
        theta_role_offsets=tuple(a["theta_role_offsets"]),
        p_innovator=a["p_innovator"],
        p_willing=tuple(a["p_willing"]),
        able_rates=able_rates,
        w_comms=d.get("w_comms", defaults.WEIGHTS["comms"]),
        broadcast_steps=d["broadcast_steps"],
        retention_factor=d["retention_factor"],
        relapse_prob=d["relapse_prob"],
        max_steps=d["max_steps"],
    )


def org_kwargs(sc: dict) -> dict:
    return dict(sc["org"])


def set_path(sc: dict, dotted: str, value) -> dict:
    """Return a deep-copied scenario with e.g. 'agents.theta_mean' set to value."""
    out = json.loads(json.dumps(sc))  # cheap deep copy of a plain dict tree
    section, key = dotted.split(".", 1)
    if section not in _SECTIONS or key not in _SECTIONS[section]:
        raise ValueError(_unknown(dotted, [f"{s}.{k}" for s, ks in _SECTIONS.items() for k in ks], dotted))
    out[section][key] = value
    return out


# --- Versioned results ---------------------------------------------------------

def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
            cwd=pathlib.Path(__file__).parent,
        ).stdout.strip()
    except Exception:
        return "unknown"


def save_results(rows: list[dict], csv_path: str | pathlib.Path, scenario: dict | None = None,
                 extra_meta: dict | None = None) -> pathlib.Path:
    """Write rows to CSV plus a JSON sidecar with everything needed to reproduce:
    scenario, library versions, git commit, timestamp. Returns the CSV path."""
    if not rows:
        raise ValueError("no rows to save")
    csv_path = pathlib.Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with open(csv_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    import core
    import networkx
    meta = {
        "scenario": scenario,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "networkx": networkx.__version__,
            "adoption_sim": core.__version__,
        },
        "git_commit": _git_commit(),
        "data_is_synthetic": True,
        **(extra_meta or {}),
    }
    sidecar = csv_path.with_suffix(".meta.json")
    sidecar.write_text(json.dumps(meta, indent=2))
    return csv_path
