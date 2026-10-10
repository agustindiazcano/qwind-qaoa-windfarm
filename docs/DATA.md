# Data sources and licenses

There are two kinds of real data. **Primary: two real operating farms** (Penmanshiel, Kelmarsh) with their real turbine positions and a wind rose measured by their own turbines. **Extra: two ERA5 reanalysis roses** (Chubut, Bahia Blanca) applied to a *synthetic* grid of candidate cells (a real rose, not a real layout, and not a site assessment).

## Real farms (primary): Penmanshiel and Kelmarsh

| Item | Penmanshiel | Kelmarsh |
|---|---|---|
| Dataset key | `real_penmanshiel` | `real_kelmarsh` |
| Farm | 14 x Senvion MM82 (2.05 MW), Scotland | 6 x Senvion MM92 (2.05 MW), England |
| Rotor diameter / hub height | 82 m / 59 m | 92 m / 68.5 and 78.5 m |
| Source | Zenodo record 16807304, DOI 10.5281/zenodo.16807304 (version published 2025-08-13) | Zenodo record 16807551, DOI 10.5281/zenodo.16807551 (version published 2025-08-12) |
| Authors / publisher | Plumley, C. and Takeuchi, R.; released by Cubico Sustainable Investments Ltd | same |
| License | CC-BY-4.0 (read from the Zenodo API field `metadata.license.id` on 2026-10-10; the record text says "provided as is") | same |
| Access date | 2026-10-10 | 2026-10-10 |
| Turbine positions | Latitude/longitude of each turbine from `Penmanshiel_WT_static.csv` (14 turbines; WT03 does not exist) | 6 turbines from `Kelmarsh_WT_static.csv` |
| Wind rose | Measured: all turbines' nacelle `Wind speed (m/s)` and absolute `Wind direction (deg)` (nacelle position + vane; checked on the data: direction minus nacelle minus vane has mean -0.05 deg), 10-minute SCADA of the calendar year 2019 (year fixed before looking at the data), all turbines pooled, readings with a missing value dropped, no other filter. 728,900 readings | Same method, 314,942 readings |
| Sectors | 16 sectors of 22.5 deg centered on 0, 22.5, ...; frequency = readings in sector / valid readings; mean speed = mean wind speed of those readings | same |

**Attribution (CC BY 4.0, indicate changes):** "Penmanshiel / Kelmarsh wind farm data, Plumley and Takeuchi, Cubico Sustainable Investments Ltd, Zenodo, CC BY 4.0 (https://doi.org/10.5281/zenodo.16807304, https://doi.org/10.5281/zenodo.16807551). Adapted: only turbine positions and a 16-sector wind rose were derived from the data." CC BY 4.0 requires credit, a link to the license and an indication of changes (https://creativecommons.org/licenses/by/4.0/, legal code: https://creativecommons.org/licenses/by/4.0/legalcode.en).

How the instances are built (`qollab/data/farms.json`, `experiments/build_farms.py`):
1. Latitude/longitude of the turbines to meters with a local equirectangular projection around the farm centroid, then divided by the rotor diameter, so positions are in rotor diameters (x east, y north). Penmanshiel: nearest-neighbour spacing 4.2 D minimum and 4.5 D mean, extent 22 x 13.5 D. Kelmarsh: 2.9 D minimum and 3.4 D mean, extent 10 x 6 D.
2. **The candidate cells are the real turbine positions and the problem is to choose K of them to keep operating: a curtailment/selection problem, NOT layout design.** Penmanshiel: N = 14, K = 5, 7, 9. Kelmarsh: N = 6, K = 2, 3, 4. These K values (about 1/3, 1/2, 2/3 of N) were fixed before running.
3. Isolated power P0 is 1 for every cell (no invented heterogeneity; the synthetic grid sets use a seeded random P0 in [1, 1.2]).
4. A real farm has no grid: `grid_rows` = N and `grid_cols` = 1 in the results.

Limits of the farm data:
- The nacelle anemometer sits behind the rotor and sees wakes of upwind turbines, so measured speeds are biased low; directions are less affected. The wake model does not use mean speed yet.
- One year (2019) of one site each; the rose changes from year to year (not studied).
- The layout is the as-built one. Choosing which K of the existing turbines to keep operating is a curtailment/selection benchmark; nothing here designs or proposes a layout.
- No check against a met mast.

### Distances, sizes and the live-Run limits (hard constraints, fixed before any run)

| Farm | Turbines | Rotor diameter | Hub height | Pairwise distance in rotor diameters: min / median / max |
|---|---|---|---|---|
| Penmanshiel | 14 | 82 m | 59 m | 4.16 / 9.65 / 22.09 |
| Penmanshiel sub-instance (10 turbines) | 10 | 82 m | 59 m | 4.16 / 8.60 / 14.86 |
| Kelmarsh | 6 | 92 m | 68.5 and 78.5 m | 2.94 / 4.93 / 10.16 |

- **Live Qollab Run:** recommended up to 10 cells, hard limit 12, default N = 8. N = 14 took 42.8 s in the live Run (penalty QAOA, one run), over the 30 s budget. `main()` refuses `n_cells > 12`. These limits are not raised.
- **The 14-turbine Penmanshiel instance is OFFLINE ONLY** (`experiments/`, `results/`). The live Run never loads `farms.json` or `windrose.json` (`tests/test_live_run_isolation.py`).
- **Fixed sub-instance rule (written before looking at any result): `real_penmanshiel_sub10` = the 10 turbines closest to the centroid of the 14 positions (ties broken by turbine id order), original ids kept.** It keeps T05 to T14 and drops T01, T02, T04, T15. K = 3, 5, 7 (about 1/3, 1/2, 2/3 of 10). Same measured Penmanshiel rose. Not picked by outcome. Using it inside the live Run would be a possible future step and needs a human decision; today it is an offline dataset only.
- **Kelmarsh** (6 turbines, C(6,K) <= 20 subsets) is a **trivial contrast**: exact enumeration is instantaneous. It is reported on its own and never averaged with other datasets. Penmanshiel and the ERA5-on-synthetic-grid sets are never merged into one average either; results are reported per dataset.
- Wording: all real-farm datasets are a curtailment/selection problem (choose K of the existing turbine positions to keep operating), not layout design. The wake model is pairwise-additive Jensen and does not use mean speed yet. No quantum advantage is claimed.

### Offline cost of the real-farm datasets (estimate and rule)

Measured on the development machine (2026-10-10), one `run_qaoa` call at the FULL protocol settings (restarts 2, maxiter 60, shots 1000 = 120 objective evaluations), `real_penmanshiel` N = 14, K = 7, seed 1, directly via `run_qaoa` (no grid was launched):

| Variant | p = 1 | p = 2 | p = 3 |
|---|---|---|---|
| `penalty+x lam=10` | 7.7 s | 14.6 s | 20.3 s |
| `xy+dicke` | 30.7 s | 40.9 s | 36.2 s |

The cost of `xy+dicke` is dominated by a fixed part (exponential-size Dicke state preparation), so it is not linear in p; the measured values are used as they are (one run each, machine load not controlled, so the p = 3 value being below p = 2 is noise).

Extrapolation (the other variants are assumed to cost like their kind: three `penalty+x` variants like `lam=10`, `penalty+x ramp` like `lam=10`, `xy+dicke ramp` like `xy+dicke`; classical rows add about 5 s per N = 14 instance):

| Dataset | Instances | Estimate, serial | With `--jobs 3` |
|---|---|---|---|
| `real_penmanshiel` (N = 14) | 3 | 4 x 42.6 s + 2 x 107.8 s + 5 s = about 6.5 min per instance, about 20 min | about 7 min |
| `real_penmanshiel_sub10` (N = 10) | 3 | not measured; upper bound = the N = 14 figure, about 20 min (smaller state, expected much less) | about 7 min or less |
| `real_kelmarsh` (N = 6) | 3 | about 1-2 min (smoke run of 2 instances at quick settings took 7 s) | under 1 min |
| Whole new real-farm grid | 9 | at most about 45 min | about 15 min |

The ERA5 sets (8 instances each, N = 6 to 12) and the synthetic set (24 instances, about 1 h serial) are not re-estimated here.

Rule (fixed now): if a grid is expected to exceed about 2 h, reduce `restarts` or the maximum N, run it in the cloud or in the background (never in the test suite), and record exactly what was reduced here and in `summary.json`'s protocol. Today nothing is reduced: the estimate is well under 2 h, so the protocol `qwind-v1` is used unchanged. Caveats: single machine, single run per cell, sub-instance unmeasured.

## ERA5 reanalysis roses (extra): Chubut and Bahia Blanca

These are a secondary dataset: ERA5 is a reanalysis with a verified license, applied to the synthetic grid of candidate cells. They are not deficient; they simply answer a different question (a real rose, no real layout), and they are the fallback primary datasets if the Penmanshiel runs do not produce results by Sunday 2026-10-11 10:00 ART.

### Source (both ERA5 sites)

| Item | Value |
|---|---|
| Dataset | ERA5 hourly reanalysis, wind speed and wind direction at 100 m (`wind_speed_100m`, `wind_direction_100m`), 0.25 degree grid (about 25 km) |
| How it was accessed | Open-Meteo Historical Weather API (`https://archive-api.open-meteo.com/v1/archive`, `models=era5`, `wind_speed_unit=ms`), one request per site and year |
| Access date | 2026-10-10 |
| Period | 2015-01-01 to 2024-12-31 (10 years, fixed before looking at the data), 87,672 valid hours per site, no missing values |
| Hub height | 100 m (the ERA5 level used; not adapted to any turbine) |
| Raw files | Not committed (about 5 MB). Rebuilt by `experiments/build_windrose.py --raw <dir>` from the API JSON files |

### License and attribution (read from the sources on the access date)

| Layer | What the source says | Where |
|---|---|---|
| ERA5 (Copernicus Climate Change Service, C3S) | CDS dataset page lists the license as "CC-BY licence", DOI `10.24381/cds.adbb2d47`. The Licence to Use Copernicus Products (PDF from the ECMWF catalogue) allows use "for any purpose in so far as it is lawful" (clause 4.2) and requires: "Generated using Copernicus Climate Change Service information [Year]" (5.1.1), "Contains modified Copernicus Climate Change Service information [Year]" for adapted data (5.1.2), and a statement that "neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains" (5.1.3) | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview ; https://object-store.os-api.cci2.ecmwf.int/cci2-prod-catalogue/licences/licence-to-use-copernicus-products/licence-to-use-copernicus-products_b4b9451f54cffa16ecef5c912c9cebd6979925a956e3fa677976e0cf198c2c18.pdf |
| Open-Meteo API | "The data obtained through the API is provided under the terms of the CC-BY 4.0 licence." Free API only for non-commercial use ("You may only use the free API services for non-commercial purposes"); limits under 10,000 calls/day. Attribution: "You must give appropriate credit, provide a link to the licence, and indicate if changes were made". Suggested citation: Zippenfenig, P. (2023). Open-Meteo.com Weather API. Zenodo. https://doi.org/10.5281/ZENODO.7970649 | https://open-meteo.com/en/terms ; https://open-meteo.com/en/licence |

**Attribution to use in README, Qollab page and website:**
"Contains modified Copernicus Climate Change Service information 2026 (ERA5, via Open-Meteo, CC BY 4.0, https://creativecommons.org/licenses/by/4.0/). Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains." The data are modified here (reduced to a 16-sector rose). The license leaves `[Year]` open; we use 2026, the year this derived material was generated.

Not used: Global Wind Atlas (ERA5 and the measured farm data were enough). The free Open-Meteo API is for non-commercial use; this is an open-source research and hackathon project with no ads or subscriptions.

### Sites

| Site key | `dataset` | Requested point | ERA5 grid cell actually returned | Elevation of the cell | Sectors |
|---|---|---|---|---|---|
| `chubut` (primary, Comodoro Rivadavia area) | `real_chubut` | -45.87, -67.50 | -45.75, -67.50 | 43 m | 16 |
| `bahia_blanca` (contrast) | `real_bahia_blanca` | -38.72, -62.27 | -38.75, -62.25 | 25 m | 16 |

The requested coordinates are approximate points chosen for the area, not surveyed positions. The reanalysis value is the 0.25 degree grid cell, about 25 km wide.

### Derivation (`experiments/build_windrose.py`)

1. Hourly `wind_speed_100m` (m/s) and `wind_direction_100m` (degrees, meteorological: direction the wind comes FROM, 0 = north, clockwise) for 2015-2024.
2. 16 sectors of 22.5 degrees, centered on 0, 22.5, ..., 337.5 (sector k covers [k*22.5 - 11.25, k*22.5 + 11.25)).
3. `frequency` = hours in the sector / valid hours (so frequencies sum to 1). `mean_speed` = mean of `wind_speed_100m` over the hours in the sector.
4. Stored in `qollab/data/windrose.json` as `{"sites": {site: {"sectors": [{"direction_deg", "frequency", "mean_speed"}]}}}` plus metadata (period, grid cell, hours). `qwind.instances.load_wind_rose` reads only the sectors; at runtime there is no network access.
5. Tested in `tests/test_windrose_data.py` (the real file and the binning on a tiny known input).

### What the roses look like (computed from the file, no result claimed)

| Site | Dominant FROM direction | Largest sector frequency | Resultant length R (1 = one direction, 0 = uniform) | Entropy (max ln 16 = 2.773) | Top-3 sectors share | Overall mean speed |
|---|---|---|---|---|---|---|
| `chubut` | 270 (west) | 0.253 | 0.577 | 2.333 | 0.556 | 8.53 m/s |
| `bahia_blanca` | 337.5 (north-northwest) | 0.160 | 0.320 | 2.632 | 0.388 | 7.70 m/s |

| `penmanshiel` (measured) | 202.5 (SSW) | 0.152 | 0.346 | 2.625 | not computed | 7.05 m/s |
| `kelmarsh` (measured) | 247.5 (WSW) | 0.125 | 0.309 | 2.655 | not computed | 6.00 m/s |

The Chubut rose is the most concentrated (west and west-southwest). The three other roses are similar in dispersion (R 0.31 to 0.35) but point in different directions; the layouts of the two real farms differ too.

## Model limitations that apply to all of this data

- The wake model **does not use the mean speed yet**: only the sector frequencies (converted to "toward" angles) enter the model. `mean_speed` is stored for the future.
- Wake losses are **pairwise additive** (Jensen model); the sum of pairwise losses is an approximation.
- ERA5 datasets: the grid of candidate cells is **synthetic** (N/2 x 2 cells, spacing 5 D); the rose is real, the layout is not. Real-farm datasets: the layout is real.
- ERA5 is a 25 km reanalysis at 100 m, not a measurement and not a micro-siting study. No energy, cost or advantage claims follow from it.
