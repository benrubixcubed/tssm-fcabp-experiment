import argparse
import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize

try:
    from src.adaptive_staircase import AdaptiveStaircase
    from src.bids_logger import BIDSLogger
    from src.run_fcabp import TRIGGERS, generate_trial_evidence, score_asymmetric_bet
except ImportError:
    from adaptive_staircase import AdaptiveStaircase
    from bids_logger import BIDSLogger
    from run_fcabp import TRIGGERS, generate_trial_evidence, score_asymmetric_bet


def softmax_thermo(free_energies: np.ndarray, tau: float) -> np.ndarray:
    scaled = -free_energies / max(tau, 1e-4)
    shifted = scaled - np.max(scaled)
    exp_v = np.exp(shifted)
    return exp_v / np.sum(exp_v)


def simulate_active_inference_session(
    n_trials: int,
    true_tau: float,
    true_c_meta: float,
    out_dir: str = "data",
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    stim_path = os.path.join(os.path.dirname(__file__), "..", "stimuli", "proposition_bank.csv")
    stim_df = pd.read_csv(stim_path)

    staircase = AdaptiveStaircase(initial_ambiguity=0.45)
    logger = BIDSLogger(out_dir=out_dir, subject="sub-sim01", session="ses-01")
    current_onset = 0.0

    for t_idx in range(1, n_trials + 1):
        row = stim_df.sample(n=1, random_state=int(rng.integers(0, 1_000_000))).iloc[0]
        ambiguity = staircase.current_ambiguity
        stake = int(row["pragmatic_stake"])
        ev = generate_trial_evidence(ambiguity, row["ground_truth_label"], rng)

        p_belief = ev["supporting_cues"] / 10.0
        p_disbelief = ev["contradicting_cues"] / 10.0

        # Expected variational free energy under your asymmetric payoff matrix (+stake vs -2*stake)
        fe_belief = (1.0 - p_belief) * (2.0 * stake) - p_belief * stake
        fe_disbelief = (1.0 - p_disbelief) * (2.0 * stake) - p_disbelief * stake
        # Epistemic suspension earns +0.4*stake safely but incurs metabolic ATP cost c_meta
        fe_suspend = -0.4 * stake + (true_c_meta * stake)

        probs = softmax_thermo(np.array([fe_belief, fe_disbelief, fe_suspend]), tau=true_tau)
        choices = ["BELIEF", "DISBELIEF", "SUSPEND"]
        choice = str(rng.choice(choices, p=probs))

        is_correct, payoff = score_asymmetric_bet(choice, row["ground_truth_label"], stake)
        next_amb = staircase.update(is_correct)
        rt_sec = float(np.clip(rng.normal(1.2 + (0.45 if choice == "SUSPEND" else 0.0), 0.25), 0.35, 5.0))

        logger.log_trial({
            "onset": round(current_onset, 4),
            "duration": round(rt_sec, 4),
            "trial_type": choice,
            "trial_number": t_idx,
            "stim_id": row["stim_id"],
            "domain": row["domain"],
            "ground_truth": row["ground_truth_label"],
            "choice": choice,
            "response_time_ms": round(rt_sec * 1000.0, 2),
            "is_correct": int(is_correct),
            "payoff": payoff,
            "ambiguity_level": round(ambiguity, 4),
            "next_ambiguity_level": round(next_amb, 4),
            "supporting_cues": ev["supporting_cues"],
            "stake": stake,
            "trigger_codes": f"{TRIGGERS['FIXATION_ONSET']},{TRIGGERS['PROPOSITION_ONSET']},{TRIGGERS[f'RESP_{choice}']},{TRIGGERS['FEEDBACK_ONSET']}",
        })
        current_onset += rt_sec + float(rng.uniform(1.5, 2.5))

    tsv_path = logger.flush()
    return pd.read_csv(tsv_path, sep="\t")


def recover_tssm_parameters(df: pd.DataFrame) -> tuple[float, float]:
    choice_map = {"BELIEF": 0, "DISBELIEF": 1, "SUSPEND": 2}
    y = df["choice"].map(choice_map).to_numpy()
    p_b = df["supporting_cues"].to_numpy() / 10.0
    p_d = 1.0 - p_b
    stakes = df["stake"].to_numpy().astype(float)

    def nll(params: np.ndarray) -> float:
        tau, c_meta = params
        if tau <= 0.05 or c_meta <= 0.0:
            return 1e9
        loss = 0.0
        for idx, pb, pd_val, s in zip(y, p_b, p_d, stakes):
            fe = np.array([
                (1.0 - pb) * (2.0 * s) - pb * s,
                (1.0 - pd_val) * (2.0 * s) - pd_val * s,
                -0.4 * s + (c_meta * s),
            ])
            probs = softmax_thermo(fe, tau)
            loss -= np.log(np.clip(probs[idx], 1e-12, 1.0))
        return float(loss)

    res = minimize(nll, x0=np.array([1.5, 0.8]), method="Nelder-Mead")
    return float(res.x), float(res.x)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock Scanner & TSSM Parameter Recovery")
    parser.add_argument("--trials", type=int, default=160)
    parser.add_argument("--tau", type=float, default=1.25)
    parser.add_argument("--c-meta", type=float, default=0.85)
    parser.add_argument("--out-dir", type=str, default="data")
    args = parser.parse_args()

    df = simulate_active_inference_session(args.trials, args.tau, args.c_meta, args.out_dir)
    est_tau, est_c_meta = recover_tssm_parameters(df)

    print("=" * 60)
    print(f"TSSM-FCABP MOCK SCANNER & PARAMETER RECOVERY ({args.trials} trials)")
    print(f"  System Temperature (tau)   : True = {args.tau:.3f} | Recovered = {est_tau:.3f}")
    print(f"  Metabolic Cost (c_meta)    : True = {args.c_meta:.3f} | Recovered = {est_c_meta:.3f}")
    print("  Doxastic State Distribution:")
    print(df["choice"].value_counts(normalize=True).round(3).to_string())
    print("=" * 60)


if __name__ == "__main__":
    main()
  
