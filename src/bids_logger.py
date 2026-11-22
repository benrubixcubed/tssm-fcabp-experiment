import json
import os
from typing import Any, Dict, List
import pandas as pd


class BIDSLogger:
    """Writes BIDS-compliant events.tsv and accompanying events.json sidecar dictionaries."""

    def __init__(self, out_dir: str, subject: str, session: str, task: str = "fcabp"):
        self.out_dir = out_dir
        self.subject = subject if subject.startswith("sub-") else f"sub-{subject}"
        self.session = session if session.startswith("ses-") else f"ses-{session}"
        self.task = task
        self.records: List[Dict[str, Any]] = []

    def log_trial(self, trial_data: Dict[str, Any]) -> None:
        self.records.append(dict(trial_data))

    def flush(self) -> str | None:
        if not self.records:
            return None

        beh_dir = os.path.join(self.out_dir, self.subject, self.session, "beh")
        os.makedirs(beh_dir, exist_ok=True)

        base_name = f"{self.subject}_{self.session}_task-{self.task}_events"
        tsv_path = os.path.join(beh_dir, f"{base_name}.tsv")
        json_path = os.path.join(beh_dir, f"{base_name}.json")

        df = pd.DataFrame(self.records)
        df.to_csv(tsv_path, sep="\t", index=False)

        sidecar = {
            "TaskName": "Forced-Choice Asymmetric Betting Paradigm (FCABP)",
            "onset": {"Description": "Proposition stimulus onset relative to run start", "Units": "s"},
            "duration": {"Description": "Decision response time window", "Units": "s"},
            "trial_type": {
                "Description": "Recorded doxastic state choice",
                "Levels": {
                    "BELIEF": "Affirmative commitment (+stake / -2*stake)",
                    "DISBELIEF": "Active rejection (+stake / -2*stake)",
                    "SUSPEND": "Epistemic suspension of judgment (+0.4*stake)",
                },
            },
            "trial_number": {"Description": "Sequential trial index (1-based)"},
            "stim_id": {"Description": "Proposition stimulus identifier from proposition_bank.csv"},
            "domain": {"Description": "Epistemic domain category of proposition"},
            "ground_truth": {"Description": "Underlying generative state label"},
            "choice": {"Description": "Participant selected action"},
            "response_time_ms": {"Description": "Decision latency", "Units": "ms"},
            "is_correct": {"Description": "Accuracy flag (1=correct, 0=incorrect)"},
            "payoff": {"Description": "Asymmetric payoff points awarded", "Units": "points"},
            "ambiguity_level": {"Description": "Current adaptive staircase ambiguity parameter [0, 1]"},
            "next_ambiguity_level": {"Description": "Updated staircase ambiguity for subsequent trial"},
            "fixation_jitter_s": {"Description": "Pre-stimulus exponential fixation jitter duration", "Units": "s"},
            "trigger_codes": {"Description": "Comma-separated MRI/EEG TTL trigger codes sent during trial"},
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(sidecar, f, indent=2)

        return tsv_path
