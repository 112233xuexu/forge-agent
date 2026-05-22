from __future__ import annotations

from typing import Any, Optional


def build_memory_recovery_state(
    *,
    continuity_focus_path: str = '',
    current_focus_path: str = '',
    continuity_resume: Optional[dict[str, Any]] = None,
    memory_soak: Optional[dict[str, Any]] = None,
    target_focus_path: str = '',
    anchored_compare: Optional[dict[str, Any]] = None,
    anchored_soak: Optional[dict[str, Any]] = None,
    adopted_reanchor: bool = False,
) -> dict[str, Any]:
    resume = dict(continuity_resume or {})
    soak = dict(memory_soak or {})
    continuity_focus_path = str(continuity_focus_path or target_focus_path or resume.get('continuity_focus_path', '') or '').strip()
    current_focus_path = str(current_focus_path or resume.get('current_focus_path', '') or '').strip()
    target_focus_path = str(target_focus_path or continuity_focus_path or '').strip()
    soak_risk = str(soak.get('risk_level', '') or 'low')
    continuity_drift = bool(soak.get('continuity_drift', False))
    alignment_score = float(resume.get('alignment_score', 0.0) or 0.0)
    anchored = dict(anchored_compare or {})
    anchored_focus_path = str(anchored.get('current_focus_path', '') or '').strip()
    anchored_alignment_score = float(anchored.get('alignment_score', 0.0) or 0.0)
    anchored_risk = str((anchored_soak or {}).get('risk_level', '') or '')

    focus_mismatch = bool(target_focus_path and current_focus_path and current_focus_path != target_focus_path)
    trigger_reasons: list[str] = []
    if focus_mismatch:
        trigger_reasons.append('focus_mismatch')
    if continuity_drift:
        trigger_reasons.append('continuity_drift')
    if soak_risk in {'medium', 'high'}:
        trigger_reasons.append(f'soak_{soak_risk}')
    if target_focus_path and not current_focus_path:
        trigger_reasons.append('missing_focus')

    recommend_reanchor = bool(target_focus_path and trigger_reasons)
    if recommend_reanchor:
        mode = 'guarded_reanchor' if continuity_drift or soak_risk in {'medium', 'high'} else 'reanchor'
    elif soak_risk in {'medium', 'high'}:
        mode = 'stabilize'
    else:
        mode = 'steady'

    if adopted_reanchor and target_focus_path:
        mode = 'reanchored'

    recovery_score = 0
    if focus_mismatch:
        recovery_score += 2
    if continuity_drift:
        recovery_score += 2
    if soak_risk == 'medium':
        recovery_score += 1
    elif soak_risk == 'high':
        recovery_score += 2
    if adopted_reanchor:
        recovery_score = max(0, recovery_score - 2)

    return {
        'mode': mode,
        'continuity_focus_path': continuity_focus_path,
        'current_focus_path': current_focus_path,
        'target_focus_path': target_focus_path,
        'alignment_score': alignment_score,
        'soak_risk_level': soak_risk,
        'continuity_drift': continuity_drift,
        'trigger_reasons': trigger_reasons,
        'recommend_reanchor': recommend_reanchor,
        'anchored_focus_path': anchored_focus_path,
        'anchored_alignment_score': anchored_alignment_score,
        'anchored_risk_level': anchored_risk,
        'adopted_reanchor': bool(adopted_reanchor),
        'recovered_focus_path': target_focus_path if adopted_reanchor and target_focus_path else '',
        'recovery_score': recovery_score,
    }


def should_adopt_reanchor(
    current_state: Optional[dict[str, Any]],
    *,
    anchored_compare: Optional[dict[str, Any]] = None,
    anchored_soak: Optional[dict[str, Any]] = None,
) -> bool:
    state = dict(current_state or {})
    if not bool(state.get('recommend_reanchor', False)):
        return False
    target_focus_path = str(state.get('target_focus_path', '') or '').strip()
    if not target_focus_path:
        return False
    anchored = dict(anchored_compare or {})
    anchored_focus = str(anchored.get('current_focus_path', '') or '').strip()
    if anchored_focus != target_focus_path:
        return False
    anchored_alignment = float(anchored.get('alignment_score', 0.0) or 0.0)
    current_alignment = float(state.get('alignment_score', 0.0) or 0.0)
    risk = str(state.get('soak_risk_level', '') or 'low')
    continuity_drift = bool(state.get('continuity_drift', False))
    anchored_risk = str((anchored_soak or {}).get('risk_level', '') or 'low')
    minimum_alignment = current_alignment
    if continuity_drift or risk in {'medium', 'high'}:
        minimum_alignment = max(0.0, current_alignment - 0.15)
    if anchored_risk == 'high' and anchored_alignment < current_alignment:
        return False
    return anchored_alignment >= minimum_alignment


def update_memory_recovery_window(
    previous_window: Optional[dict[str, Any]],
    recovery_state: Optional[dict[str, Any]],
    *,
    max_history: int = 12,
) -> dict[str, Any]:
    prev = dict(previous_window or {})
    current = dict(recovery_state or {})
    mode = str(current.get('mode', '') or 'steady')
    adopted = bool(current.get('adopted_reanchor', False))
    stable_recovery_runs = int(prev.get('stable_recovery_runs', 0) or 0)
    if mode in {'steady', 'reanchored'} and not bool(current.get('continuity_drift', False)) and str(current.get('soak_risk_level', '') or 'low') == 'low':
        stable_recovery_runs += 1
    else:
        stable_recovery_runs = 0
    reanchor_count = int(prev.get('reanchor_count', 0) or 0) + (1 if adopted else 0)
    guarded_runs = int(prev.get('guarded_runs', 0) or 0) + (1 if mode == 'guarded_reanchor' else 0)
    history = [row for row in list(prev.get('history') or []) if isinstance(row, dict)]
    history.append({
        'mode': mode,
        'target_focus_path': str(current.get('target_focus_path', '') or ''),
        'current_focus_path': str(current.get('current_focus_path', '') or ''),
        'soak_risk_level': str(current.get('soak_risk_level', '') or ''),
        'adopted_reanchor': adopted,
    })
    history = history[-max(1, int(max_history)):]
    return {
        'last_mode': mode,
        'last_target_focus_path': str(current.get('target_focus_path', '') or ''),
        'last_current_focus_path': str(current.get('current_focus_path', '') or ''),
        'last_soak_risk_level': str(current.get('soak_risk_level', '') or ''),
        'stable_recovery_runs': stable_recovery_runs,
        'reanchor_count': reanchor_count,
        'guarded_runs': guarded_runs,
        'history': history,
    }


def summarize_memory_recovery_window(window: Optional[dict[str, Any]]) -> dict[str, Any]:
    payload = dict(window or {})
    history = [row for row in list(payload.get('history') or []) if isinstance(row, dict)]
    return {
        'last_mode': str(payload.get('last_mode', '') or ''),
        'stable_recovery_runs': int(payload.get('stable_recovery_runs', 0) or 0),
        'reanchor_count': int(payload.get('reanchor_count', 0) or 0),
        'guarded_runs': int(payload.get('guarded_runs', 0) or 0),
        'history_size': len(history),
    }
