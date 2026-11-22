from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np


@dataclass
class TSSMParameters:
    c_crit: float = 0.15
    effort_lambda: float = 1.0
    k_steepness: float = 15.0
    tau_min: float = 0.01
    alpha_0: float = 0.05
    alpha_max: float = 0.95
    beta_0: float = 0.85
    eta_biophys: float = 2.0e4
    phi_maint: float = 1.25


COHORT_PROFILES: Dict[str, TSSMParameters] = {
    "healthy_control": TSSMParameters(c_crit=0.15, effort_lambda=1.0, k_steepness=15.0),
    "clinical_burnout": TSSMParameters(c_crit=0.45, effort_lambda=3.5, k_steepness=18.0),
    "major_depressive_disorder": TSSMParameters(c_crit=0.75, effort_lambda=8.0, k_steepness=22.0),
}


def precision_multiplier_gamma(cost_load: np.ndarray | float, params: TSSMParameters) -> np.ndarray | float:
    exponent = np.clip(params.k_steepness * (cost_load - params.c_crit), -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(exponent))


def system_temperature_tau(cost_load: np.ndarray | float, params: TSSMParameters) -> np.ndarray | float:
    gamma = precision_multiplier_gamma(cost_load, params)
    return params.tau_min + (1.0 - params.tau_min) * gamma


def expected_free_energy(
    g_pragmatic: np.ndarray,
    g_epistemic: np.ndarray,
    cost_load: float,
    policy_cost: np.ndarray,
    params: TSSMParameters,
) -> np.ndarray:
    gamma = precision_multiplier_gamma(cost_load, params)
    return g_pragmatic - (gamma * g_epistemic) + (params.effort_lambda * policy_cost)


def action_probabilities(
    g_values: np.ndarray,
    cost_load: float,
    params: TSSMParameters,
) -> np.ndarray:
    tau = float(system_temperature_tau(cost_load, params))
    scaled = -g_values / max(tau, 1e-8)
    scaled -= np.max(scaled)
    exp_vals = np.exp(scaled)
    return exp_vals / np.sum(exp_vals)


def hmm_transition_rates(
    cost_load: np.ndarray | float,
    params: TSSMParameters,
) -> Tuple[np.ndarray | float, np.ndarray | float]:
    arg = np.clip(params.effort_lambda * (cost_load - params.c_crit), -60.0, 60.0)
    alpha_c = params.alpha_0 + (params.alpha_max - params.alpha_0) / (1.0 + np.exp(-arg))
    beta_c = params.beta_0 / (1.0 + np.exp(arg))
    return alpha_c, beta_c


def hmm_stationary_distribution(
    cost_load: np.ndarray | float,
    params: TSSMParameters,
) -> Tuple[np.ndarray | float, np.ndarray | float]:
    alpha_c, beta_c = hmm_transition_rates(cost_load, params)
    denom = alpha_c + beta_c
    return beta_c / denom, alpha_c / denom
  
