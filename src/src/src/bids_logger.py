import json
import os
from datetime import datetime
from typing import Any, Dict, List
import pandas as pd


SIDECAR_METADATA = {
    "onset": {"LongName": "Trial onset", "Description": "Stimulus onset relative to session start", "Units": "s"},
    "duration": {"LongName": "Deliberation duration", "Description": "Response time from proposition onset to button press", "Units": "s"},
    "trial_type": {"LongName": "Doxastic stance", "Description": "Selected epistemic stance (BELIEF, DISBELIEF, or SUSPEND)"},
    "trial_number": {"LongName": "Trial index", "Description": "1-based sequential trial number"},
    "stim_id": {"LongName": "Stimulus identifier", "Description": "Unique ID from proposition_bank.csv"},
    "domain": {"LongName": "Epistemic domain", "Description": "Conceptual category of proposition"},
    "ground_truth": {"LongName": "Ground-truth stance", "Description": "Normative target classification for adaptive staircasing"},
    "choice": {"LongName": "Participant choice", "Description": "Recorded behavioral choice (BELIEF, DISBELIEF, SUSPEND)"},
    "response_time_ms": {"LongName": "Response time (ms)", "Description": "Deliberation latency in milliseconds", "Units": "ms"},
    "is_correct": {"LongName": "Accuracy flag", "Description": "1 if choice matched ground_truth, 0 otherwise"},
    "payoff": {"LongName": "Asymmetric payoff", "Description": "Points awarded (+stake, -2*stake, or +0.4*stake for SUSPEND)"},
    "ambiguity_level": {"LongName": "Current ambiguity", "Description": "Staircase ambiguity parameter on current trial"},
    "next_ambiguity_level": {"LongName": "Updated ambiguity", "Description": "Staircase ambiguity parameter for subsequent trial"},
    "trigger_codes": {"LongName": "TTL event sequence", "Description": "Comma-separated EEG/fMRI trigger markers emitted on trial"},
}


class BIDSLogger:
    """Writes BIDS-compliant *_events.tsv and *_events.json sidecar files."""

    def __init__(self, out_dir: str, subject: str, session: str):
        sub_clean = subject if subject.startswith("sub-") else f"sub-{subject}"
        ses_clean = session if session.startswith("ses-") else f"ses-{session}"
        self.func_dir = os.path.join(out_dir, sub_clean, ses_clean, "func")
        os.makedirs(self.func_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"{sub_clean}_{ses_clean}_task-FCABP_run-01_desc-{timestamp}"
        self.tsv_path = os.path.join(self.func_dir, f"{base}_events.tsv")
        self.json_path = os.path.join(self.func_dir, f"{base}_events.json")
        self.records: List[Dict[str, Any]] = []

    def log_trial(self, record: Dict[str, Any]) -> None:
        self.records.append(record)

    def flush(self) -> str | None:
        if not self.records:
            return None
        df = pd.DataFrame(self.records)
        # Ensure BIDS-standard leading columns while retaining all custom metrics
        lead_cols = ["onset", "duration", "trial_type"]
        other_cols = [c for c in df.columns if c not in lead_cols]
        df = df[lead_cols + other_cols]
        df.to_csv(self.tsv_path, sep="\t", index=False)

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(SIDECAR_METADATA, f, indent=2)
        return self.tsv_path
      
