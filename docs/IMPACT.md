# What the choice of turbines could be worth (illustrative estimate)

This note estimates the **scale** of the energy and value at stake in the decision QWind addresses: which K of a farm's turbines to keep running when the farm has to run fewer. It is an illustration built from a model and from measured production data, **not a forecast and not a measured saving**.

<!-- IMPACT:START -->
**Illustrative estimate for Penmanshiel.** Assumptions: each kept turbine produces its measured 2019 average (637 kW, a capacity factor of 31.1%); the farm runs with only K of its 14 turbines for 1,000 hours; the wake losses are the modelled ones, for the best choice against an average random choice of the same K turbines; the prices are round numbers for illustration.

| Turbines kept (K of 14) | Modelled power lost to wakes: best vs average random choice | More energy from the same K turbines | Extra energy per 1,000 hours | Value at £50/MWh | Value at £75/MWh | Value at £100/MWh |
|---|---|---|---|---|---|---|
| 5 | 1.0% vs 5.3% | +4.5% | 136 MWh | £6.8k | £10.2k | £13.6k |
| 7 | 4.0% vs 8.0% | +4.3% | 176 MWh | £8.8k | £13.2k | £17.6k |
| 9 | 7.0% vs 10.6% | +4.0% | 207 MWh | £10.3k | £15.5k | £20.7k |

This is an illustrative estimate of scale, not a forecast. It comes from a model, it compares with an average random choice (not with what an operator does today), it assumes 1,000 hours in that configuration (a year has 8,760; how many hours a farm is curtailed is not in our data), and it counts neither costs nor the structure of any contract. Details and sources: [docs/IMPACT.md](https://github.com/agustindiazcano/qwind-qaoa-windfarm/blob/main/docs/IMPACT.md).
<!-- IMPACT:END -->

## Assumptions

| Item | Value | Where it comes from |
|---|---|---|
| Production of one kept turbine | Its measured average power in 2019 (see the table above), taken as the same for every turbine | Penmanshiel SCADA, 10-minute `Power (kW)`, 14 turbines, Zenodo [10.5281/zenodo.16807304](https://doi.org/10.5281/zenodo.16807304), CC BY 4.0. The measured average already includes real wakes and downtime, so it understates an isolated turbine and the estimate is on the cautious side |
| Wake losses | Share of the K kept turbines' potential power lost to wakes, for the best choice and for the average of all choices | The QWind model (Jensen wake, pairwise-additive losses, equal turbines) with the measured Penmanshiel 2019 wind rose, by exact enumeration of every way of choosing K of the 14 turbines (`experiments/make_illustrations.py`) |
| Comparison | The best choice against the **average random choice** of the same K turbines | Chosen because we have no data on how operators choose today |
| Hours | 1,000 hours with only K turbines running | A round number for scale. A year has 8,760 hours; the number of hours a farm is curtailed is not in our data |
| Price of energy | £50, £75 and £100 per MWh | Round numbers for illustration. A reference point: the UK government's administrative strike price for onshore wind (more than 5 MW) in Contracts for Difference Allocation Round 6 is **£64/MWh in 2012 prices** ([CfD AR6 budget notice](https://assets.publishing.service.gov.uk/media/65e867c162ff48001a87b252/cfd-ar6-budget-notice.pdf), Table 2). The value scales linearly: use your own price |

## How to read it

- "More energy from the same K turbines" compares the energy delivered after wakes by the best choice and by an average random choice of the same number of turbines.
- "Extra energy" is that difference over 1,000 hours, using the measured average power per turbine.
- "Value" is the extra energy times a price. It is revenue-equivalent energy value, not profit.

## Limits

- It comes from a model. The Jensen wake model with pairwise-additive losses is a simplification, and real wake losses depend on turbulence, atmospheric stability and the control of the farm.
- The comparison is against a random choice. An operator may already choose well (for example with a priority list), in which case the gain is smaller. We do not have data on current practice.
- The hours of curtailment are an assumption for scale. The estimate says nothing about how often a farm has to run fewer turbines.
- Costs, contract structure (for example a Contract for Difference or a power purchase agreement), grid constraints and the effect on turbine wear are not included.
- One farm (Penmanshiel), one year of wind and of production, one wind rose.
- Nothing here has been measured in a real operation of the algorithm: the quantum circuit is evaluated on whether it finds these choices, and at this size exact search finds them too.

## How to regenerate

`python experiments/estimate_impact.py --scada <directory with the extracted Penmanshiel Turbine_Data_*.csv>` measures the inputs again; without `--scada` it only updates the table in this note and in the README from `results/impact_inputs.json`.
