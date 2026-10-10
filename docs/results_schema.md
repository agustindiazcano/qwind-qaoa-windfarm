# Results Schema

Everything shown in the README, the Qollab page and the website must come from the files in `results/`.
The website reads **only** `results/summary.json` (copied by `scripts/sync_results_to_web.py`).
`tests/test_results_schema.py` is the executable version of this document: it validates the generated files.

Files written by `experiments/run_all.py`:

| File | Content |
|---|---|
| `results/<dataset>/summary.json`, `results/<dataset>/per_instance.csv` | One run of one dataset (`synthetic`, `real_chubut`, `real_bahia_blanca`). A run only writes its own folder, so datasets never overwrite each other. |
| `results/summary.json` | Merged file the website reads: protocol, environment, list of datasets, instances and aggregated results (mean, std, 95% interval over instances). Built by `python experiments/run_all.py --merge`. |
| `results/per_instance.csv` | One row per instance x method x variant x depth, all datasets concatenated. Source of every aggregate. |

`--merge` only reads sub-folders named after a dataset and refuses to merge runs made with different protocols. A single-dataset folder follows the same schema (a `datasets` list with one entry).

## `dataset` values
`dataset` identifies where the wind rose comes from. Allowed values: `synthetic` or `real_<site>` (lowercase letters, digits and underscores, for example `real_chubut`). Synthetic and real results are stored side by side and never mixed in an aggregate.

Real datasets (`docs/DATA.md`) are of two kinds:
- `real_chubut`, `real_bahia_blanca`: a real ERA5 wind rose on the synthetic grid of candidate cells. They reuse only the (N, K) pairs and seeds of the synthetic A-rose instances (8 instances per site: N = 6, 8, 10, 12 with two K each), so `n_instances` = 8 (synthetic: 24).
- `real_penmanshiel`, `real_penmanshiel_sub10`, `real_kelmarsh`: the real turbine positions of an operating farm are the candidate cells and a measured wind rose is used; one instance per K, so `n_instances` = 3 each (Penmanshiel N = 14, K = 5, 7, 9; `real_penmanshiel_sub10` N = 10, K = 3, 5, 7, the 10 turbines closest to the farm centroid; Kelmarsh N = 6, K = 2, 3, 4). A farm has no grid: `grid_rows` = N and `grid_cols` = 1. These are **curtailment/selection problems** (choose K of the existing turbine positions to keep operating), not layout design. `real_kelmarsh` is a trivial contrast (C(6,K) <= 20 subsets). Datasets are always reported separately; an aggregate row never mixes datasets.

## `results/summary.json`

| Key | Type | Meaning |
|---|---|---|
| `schema_version` | string | `"1.0"`. |
| `status` | string | `"final"` for the full protocol, `"smoke"` for a tiny test run. A `smoke` file is not a result and must not be quoted. In a merged file it is `"final"` only if every dataset is `"final"`, otherwise `"smoke"`. |
| `protocol` | object | Everything fixed BEFORE running: id, datasets, depths, restarts, maxiter, shots, lam multipliers, ramp total time, variants. Never retuned after seeing results. |
| `environment` | object | Python, Qiskit, NumPy and SciPy versions. |
| `datasets` | list | One object per dataset in the file: `dataset`, `status` (`final` \| `smoke`), `n_instances`. Each dataset appears once; every `instances` and `results` entry refers to a listed dataset. Sorted by name in a merged file. |
| `instances` | list | One object per instance: `dataset`, `instance_id`, `wind_rose`, `N`, `K`, `grid_rows`, `grid_cols`, `seed`. |
| `results` | list | Aggregated rows, see below. |
| `caveats` | list of strings | Model limitations (pairwise additive wake losses, small instances, simulator only, no advantage claimed). Must not be empty. |

### Each element of `results`

| Key | Type | Meaning |
|---|---|---|
| `dataset` | string | See above. |
| `method` | string | `exact`, `sa`, `greedy` or `qaoa`. |
| `variant` | string | For example `exact`, `sa`, `greedy`, `penalty+x lam=3`, `penalty+x lam=10 ramp`, `xy+dicke`, `xy+dicke ramp`. |
| `p` | integer or null | QAOA depth. `null` for classical methods. |
| `n_instances` | integer | Instances aggregated. |
| `metrics` | object | Metric name to `{mean, std, ci95_low, ci95_high}`. The interval is a normal approximation, `mean +/- 1.96 std / sqrt(n_instances)`. |
| `baselines` | object (qaoa only) | Mean over the same instances of `uniform_feasible_p_optimal`, `uniform_feasible_ratio` and `random_p_hit`. |
| `frac_beating_uniform_ratio` | number (qaoa only) | Fraction of instances where `approx_ratio_feasible` beats the uniform-over-feasible ratio. |
| `frac_beating_uniform_p_optimal` | number (qaoa only) | Same for `p_optimal`. |

Metrics for `qaoa`: `p_optimal`, `p_feasible`, `approx_ratio_feasible`, `n_evals`, `time_s`.
Metrics for classical methods: `energy_gap`, `time_s`.

## `results/per_instance.csv`

Columns, in this exact order:

`dataset, instance_id, wind_rose, N, K, grid_rows, grid_cols, seed, method, variant, p, lam_mult, energy_best, energy_gap, p_optimal, p_feasible, approx_ratio_feasible, uniform_feasible_p_optimal, uniform_feasible_ratio, random_p_hit, n_evals, shots, time_s`

| Column | Meaning |
|---|---|
| `dataset`, `instance_id`, `wind_rose`, `N`, `K`, `grid_rows`, `grid_cols`, `seed` | Instance description. |
| `method`, `variant` | As in `summary.json`. |
| `p` | QAOA depth (empty for classical methods). |
| `lam_mult` | Penalty weight of the circuit cost as a multiple of `max|h|` (0 when the ansatz enforces the constraint). Empty for classical methods. |
| `energy_best` | Best QUBO energy found (for QAOA: best sampled bitstring). |
| `energy_gap` | `energy_best` minus the exact optimum of the reference QUBO. |
| `p_optimal` | Probability mass of the optimal bitstring(s) in the exact output distribution (qaoa only). |
| `p_feasible` | Probability mass on states with exactly K turbines (qaoa only). |
| `approx_ratio_feasible` | Approximation ratio computed over feasible states only (qaoa only). |
| `uniform_feasible_p_optimal`, `uniform_feasible_ratio` | The same two metrics for the uniform distribution over the C(N, K) feasible states (qaoa only). |
| `random_p_hit` | Probability that `shots` random feasible subsets contain an optimum (qaoa only). |
| `n_evals` | Objective evaluations: optimizer evaluations for QAOA, energy evaluations for the classical methods when known. |
| `shots` | Samples drawn (qaoa only). |
| `time_s` | Wall-clock seconds. The only non-deterministic column. |

Empty cells mean "not applicable" (for example quantum-only columns on classical rows).
