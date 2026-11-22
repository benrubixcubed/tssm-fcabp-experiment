# TSSM-FCABP Multi-Modal Neuroimaging Acquisition Protocol (v2.0)

## 1. Anatomical Regions of Interest (MNI152 Coordinates)

| Region | Abbreviation | MNI (x, y, z) mm | Functional Role in TSSM |
| :--- | :--- | :--- | :--- |
| Left Dorsolateral Prefrontal Cortex | l-dlPFC | `-42, 26, 30` | Active neutrality / precision-weighted model maintenance |
| Right Dorsolateral Prefrontal Cortex | r-dlPFC | `44, 28, 32` | Conflict monitoring & suppression of premature phase collapse |
| Dorsal Anterior Cingulate Cortex | dACC | `0, 22, 36` | Expected free energy & opportunity-cost arbitration |
| Ventromedial Prefrontal Cortex | vmPFC | `0, 48, -10` | Low-resistance habitual belief valuation |
| Right Inferior Frontal Gyrus | rIFG / vlPFC | `48, 22, 8` | Active inhibition / explicit disbelief execution |

## 2. MRI / fMRS Sequence Targets (3T Scanner)
* **Structural T1w:** MPRAGE, 1.0 mm isotropic, TR = 2300 ms, TE = 2.98 ms, TI = 900 ms.
* **BOLD / pCASL Dual-Echo fMRI & Calibrated $\Delta\text{CMRO}_2$:**
  * **Acquisition:** Dual-echo pseudo-continuous Arterial Spin Labeling (pCASL), TR = 1500 ms (or 2000 ms for interleaved tag/control ASL), TE1/TE2 = 14/35 ms, 2.5 mm isotropic, multiband factor = 3.
  * **Timing & HRF Deconvolution:** Pseudo-randomized inter-trial jittering (`2.0–6.5 s` exponential distribution) paired with block-epoch modeling (`30–45 s` sustained ambiguity vs. low-ambiguity baseline epochs) to overcome slow ASL vascular transit delays (`TR ~ 3–4 s` effective tag-control pair) and isolate sub-second EEG microstate transitions via calibrated Davis model deconvolution.
* **Single-Voxel fMRS (Glx / Lactate Dynamics):**
  * **Sequence:** semi-LASER or MEGA-PRESS at 3T (or ultra-high-field 7T sLASER with `2-minute` sliding windows for high-SNR lactate/glutamate separation).
  * **Voxel Placement:** Centered on l-dlPFC (`-42, 26, 30`) or dACC (`0, 22, 36`) in dedicated counterbalanced runs, dimensions `20 × 20 × 20 mm³`.
  * **Parameters:** TR = 2000 ms, TE = 30 ms (semi-LASER), VAPOR water suppression, 32-step phase cycle blocks aligned to high-ambiguity vs. low-ambiguity epochs.

## 3. Simultaneous EEG Acquisition
* **Sampling Rate:** $\ge$ 1000 Hz (hardware-synchronized to MRI scanner 10 MHz clock).
* **Montage:** 64- or 128-channel MR-compatible cap (10-10 system) + 1 ECG channel for ballistocardiogram (BCG) and gradient artifact subtraction.

## 4. TTL Trigger Bitmask Reference (Matches `config.yaml` & `src/run_fcabp.py`)
* `10`: `FIXATION_ONSET` — Fixation cross baseline onset (jittered `2.0–6.5 s`)
* `20`: `PROPOSITION_ONSET` — Proposition text, pragmatic stake, and cue ratio onset
* `31`: `RESP_BELIEF` — Affirmative commitment (`BELIEF`)
* `32`: `RESP_DISBELIEF` — Active rejection (`DISBELIEF`)
* `33`: `RESP_SUSPEND` — Epistemic suspension of judgment (`SUSPEND`)
* `40`: `FEEDBACK_ONSET` — Asymmetric payoff outcome presentation
* 
