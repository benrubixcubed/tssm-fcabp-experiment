# TSSM-FCABP: Forced-Choice Asymmetric Betting Paradigm

Turn-key behavioral, computational, and neuroimaging-ready experimental suite for **A Hierarchical Thermodynamic Taxonomy of Doxastic States: An Active Inference Model, Neuro-Computational Opportunity Cost Architecture, and EEG-fMRI Fusion Paradigm** by Ben Ruby (2026).

[![DOI](https://zenodo.org)](https://doi.org)

---

## Overview

The **Forced-Choice Asymmetric Betting Paradigm (FCABP)** operationalizes belief (`BELIEF`), active disbelief (`DISBELIEF`), and epistemic neutrality (`SUSPEND`) as metabolically constrained states governed by active inference and variational free energy minimization. 

* **Adaptive Difficulty:** Dynamically adjusts generative evidence ambiguity via `AdaptiveStaircase` to prevent ceiling/floor collapse and isolate the prefrontal metabolic threshold of suspended judgment.
* **Asymmetric Payoff Structure:** Rewards accurate commitment (`+stake`), penalizes false commitment (`-2 × stake`), and assigns a low-yield safe return (`+0.4 × stake`) to active suspension so neutrality must be metabolically justified against pragmatic opportunity cost.
* **Plug-and-Play Lab Architecture:** Separates site-specific MRI/EEG hardware triggers (`config.yaml`), outputs BIDS-compliant event logs and JSON data dictionaries (`src/bids_logger.py`), provides an end-to-end parameter recovery CLI (`src/simulate_recovery.py`), and specifies 3T fMRI/fMRS and simultaneous EEG acquisition targets (`protocol_specs.md`).

---

## Repository Structure

```text
tssm-fcabp-experiment/
├── config.yaml                 # Centralized MRI/EEG trigger modes, TTL bitmasks, and button-box mappings
├── protocol_specs.md           # MNI152 coordinates, 3T fMRI/fMRS pulse sequence targets, and EEG specs
├── pyproject.toml              # Pinned dependencies and CLI entry points
├── Dockerfile                  # Reproducible container environment for parameter recovery
├── CITATION.cff                # Machine-readable citation metadata
├── stimuli/
│   └── proposition_bank.csv    # Curated propositions with domains and pragmatic stakes
└── src/
    ├── run_fcabp.py            # Main experimental task runner with TTL trigger & BIDS hooks
    ├── adaptive_staircase.py   # Psychophysical ambiguity staircasing controller
    ├── hardware_interface.py   # Serial/TTL and emulated keyboard trigger abstraction layer
    ├── bids_logger.py          # BIDS *_events.tsv and *_events.json sidecar generator
    └── simulate_recovery.py    # Headless active-inference mock scanner & MLE parameter recovery
```

---

## Quick Start

### 1. Install
```bash
git clone https://github.com
cd tssm-fcabp-experiment
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e .
```

### 2. Run Mock Scanner & Parameter Recovery (Verification)
Verify BIDS output generation and maximum-likelihood recovery of system cognitive temperature ($\tau$) and metabolic suspension cost ($c_{\text{meta}}$) before running human participants:
```bash
tssm-simulate --trials 160 --tau 1.25 --c-meta 0.85
```
Or via Docker:
```bash
docker build -t tssm-fcabp:1.1.0 .
docker run --rm tssm-fcabp:1.1.0 --trials 160
```

### 3. Run a Behavioral or Scanner Session
```bash
# Behavioral / bench test
tssm-fcabp --subject sub-01 --session ses-01 --trials 60

# MRI / EEG scanner mode (pauses for scanner sync pulse defined in config.yaml)
tssm-fcabp --subject sub-01 --session ses-01 --trials 120 --wait-scanner
```

---

## Scanner & Hardware Configuration

Edit **`config.yaml`** to adapt the task to local imaging center hardware without modifying source code:

* **`trigger_mode`**: Set to `"keyboard"` for standard behavioral testing or emulated scanner triggers, or `"serial"` for USB/COM hardware TTL pulses (`serial_port`, `baud_rate`, `pulse_duration_ms`).
* **`response_pad`**: Map physical MRI-safe fiber-optic button-box keys (`1`, `2`, `3`, `q`) to `BELIEF`, `DISBELIEF`, `SUSPEND`, and `QUIT`.
* **`ttl_codes`**:
  * `10`: `FIXATION_ONSET`
  * `20`: `PROPOSITION_ONSET`
  * `31`: `RESP_BELIEF`
  * `32`: `RESP_DISBELIEF`
  * `33`: `RESP_SUSPEND`
  * `40`: `FEEDBACK_ONSET`

For anatomical regions of interest (l-dlPFC, r-dlPFC, dACC, vmPFC, rIFG), single-voxel fMRS placement, and simultaneous 64-channel EEG settings, see **`protocol_specs.md`**.

---

## BIDS Data Output

Each session automatically writes standardized files to `data/sub-<ID>/ses-<ID>/func/`:
* `sub-<ID>_ses-<ID>_task-FCABP_run-01_desc-<TIMESTAMP>_events.tsv`
* `sub-<ID>_ses-<ID>_task-FCABP_run-01_desc-<TIMESTAMP>_events.json`

---

## Citation

If you use this software, experimental paradigm, or acquisition specification in your research, please cite both the software release and the accompanying theoretical paper:

```bibtex
@software{ruby_2026_tssm_fcabp,
  author       = {Ruby, Ben},
  title        = {TSSM-FCABP: Forced-Choice Asymmetric Betting Paradigm and Thermodynamic State-Space Model},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {v1.1.0},
  doi          = {10.5281/zenodo.24433515},
  url          = {https://doi.org}
}
```

## License

Released under the [MIT License](LICENSE).
