"""Kumaradi and Chaitanyadi Avastha (RULES KUMARADI_001, CHAITANYADI_001).

Only these two Avastha systems are implemented, as specified for V1.
"""
from __future__ import annotations

from .chart_calculator import ChartContext
from .rules import avastha_rules as ar
from .rules import planetary_rules as pr


def _avastha(bands_odd, bands_even, degree: float, sign: int,
             rule_id: str, name: str) -> dict:
    parity = pr.sign_parity(sign)          # RULE FUNC_007
    bands = bands_odd if parity == "Odd" else bands_even
    start, end, result = ar.resolve_band(bands, degree)

    return {
        "name": name,
        "result": result,
        "signType": parity,
        "sign": sign,
        "signName": pr.sign_name(sign),
        "degree": round(degree, 6),
        "degreeDms": pr.to_dms(degree),
        "rangeUsed": f"{start:g}°–{end:g}°",
        "bands": [
            {"range": f"{s:g}°–{e:g}°", "value": v, "active": (s, e, v) == (start, end, result)}
            for s, e, v in bands
        ],
        "ruleApplied": (
            f"{parity} sign. Degree {pr.to_dms(degree)} falls in the "
            f"{start:g}°–{end:g}° band, giving {result}."
        ),
        "evidence": (
            f"Sign = {pr.sign_name(sign)} ({parity}); "
            f"Degree = {pr.to_dms(degree)}; "
            f"Range = {start:g}°–{end:g}°; "
            f"Result = {result}"
        ),
        "sources": {"source": "Custom Rule Engine", "rule": rule_id,
                    "methodology": "Supplied rule material"},
    }


def kumaradi_avastha(ctx: ChartContext, planet: int) -> dict:
    pos = ctx.positions[planet]
    out = _avastha(ar.KUMARADI_ODD, ar.KUMARADI_EVEN,
                   pos.degree_in_sign, pos.sign,
                   "KUMARADI_001", "Kumaradi Avastha")
    if planet in pr.NODES:
        out["applicabilityNote"] = ar.NODE_APPLICABILITY_NOTE
    return out


def chaitanyadi_avastha(ctx: ChartContext, planet: int) -> dict:
    pos = ctx.positions[planet]
    out = _avastha(ar.CHAITANYADI_ODD, ar.CHAITANYADI_EVEN,
                   pos.degree_in_sign, pos.sign,
                   "CHAITANYADI_001", "Chaitanyadi Avastha")
    if planet in pr.NODES:
        out["applicabilityNote"] = ar.NODE_APPLICABILITY_NOTE
    return out


def avasthas(ctx: ChartContext, planet: int) -> dict:
    """SECTION I."""
    return {
        "kumaradi": kumaradi_avastha(ctx, planet),
        "chaitanyadi": chaitanyadi_avastha(ctx, planet),
    }
