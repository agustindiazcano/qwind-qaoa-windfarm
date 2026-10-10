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

**Attribution (CC BY 4.0, indicate changes):** "Penmanshiel / Kelmarsh wind farm data, Plumley and Takeuchi, Cubico Sustainable Investments Ltd, Zenodo, CC BY 4.0 (https://doi.org/10.5281/zenodo.16807304, https://doi.org/10.5281/zenodo.16807551). Adapted: only turbine positions and a 16-sector wind rose were derived from the data." A link to the CC BY 4.0 legal text next to the attribution is *to verify*: the Zenodo API names the license id, but I did not read the license legal text itself.

How the instances are built (`qollab/data/farms.json`, `experiments/build_farms.py`):
1. Latitude/longitude of the turbines to meters with a local equirectangular projection around the farm centroid, then divided by the rotor diameter, so positions are in rotor diameters (x east, y north). Penmanshiel: nearest-neighbour spacing 4.2 D minimum and 4.5 D mean, extent 22 x 13.5 D. Kelmarsh: 2.9 D minimum and 3.4 D mean, extent 10 x 6 D.
2. **The candidate cells are the real turbine positions and the problem is to choose K of them to keep.** Penmanshiel: N = 14, K = 5, 7, 9. Kelmarsh: N = 6, K = 2, 3, 4. These K values (about 1/3, 1/2, 2/3 of N) were fixed before running.
3. Isolated power P0 is 1 for every cell (no invented heterogeneity; the synthetic grid sets use a seeded random P0 in [1, 1.2]).
4. A real farm has no grid: `grid_rows` = N and `grid_cols` = 1 in the results.

Limits of the farm data:
- The nacelle anemometer sits behind the rotor and sees wakes of upwind turbines, so measured speeds are biased low; directions are less affected. The wake model does not use mean speed yet.
- One year (2019) of one site each; the rose changes from year to year (not studied).
- The layout is the as-built one; the farms were not designed with this objective, so "which turbines to keep" is a benchmark question, not a redesign proposal.
- No check against a met mast.

## ERA5 reanalysis roses (extra): Chubut and Bahia Blanca

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
"Contains modified Copernicus Climate Change Service information 2025 (ERA5, via Open-Meteo, CC BY 4.0). Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains." The data are modified here (reduced to a 16-sector rose). The `[Year]` in the notice is not defined by the license text we read: 2025 is a placeholder, *to verify* before publishing.

Not verified / not used:
- Global Wind Atlas was **not used**: its pages are a JavaScript application whose license text could not be read from the fetched content. Its license is therefore *unverified* here.
- The classic ERA5 citation (Hersbach et al. 2020/2023) was not read from a source in this session: *to verify*. Only the DOI above, shown on the CDS page, is verified.
- Whether the non-commercial limit of the free Open-Meteo API fits the hackathon use is judged non-commercial (research demo), but is a human decision: *to verify*.

### Sites

| Site key | `dataset` | Requested point | ERA5 grid cell actually returned | Elevation of the cell | Sectors |
|---|---|---|---|---|---|
| `chubut` (primary, Comodoro Rivadavia area) | `real_chubut` | -45.87, -67.50 | -45.75, -67.50 | 43 m | 16 |
| `bahia_blanca` (contrast) | `real_bahia_blanca` | -38.72, -62.27 | -38.75, -62.25 | 25 m | 16 |

The requested coordinates are approximate points chosen for the area, not surveyed positions (*to verify* if a precise location matters). The reanalysis value is the 0.25 degree grid cell, about 25 km wide.

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
