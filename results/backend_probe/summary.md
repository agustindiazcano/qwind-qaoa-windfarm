# Backend probe, N = 6, K = 3, p = 1 (2026-10-11)

Computed from the console outputs in this folder (no new run). 1000 shots on the simulators, 997 on the quantum computer. The uniform baseline printed by the probe is over all 2^6 bitstrings; the fair one for a circuit that should stay in the valid subspace is the uniform distribution over the C(6,3) = 20 valid layouts, in which the 2 optimal layouts have probability 0.10.

| Backend | P(optimal) | P(feasible) | P(optimal), valid samples only | Uniform over valid layouts |
|---|---|---|---|---|
| Ideal (exact statevector) | 0.1784 | 1.0000 | 0.1784 | 0.1000 |
| Qiskit basic simulator (no noise) | 0.1600 | 1.0000 | 0.1600 | 0.1000 |
| IonQ simulator with noise model | 0.1010 | 0.6650 | 0.1519 (= 0.1010 / 0.6650) | 0.1000 |
| **IonQ Forte 1, real quantum computer** | 0.1304 | 0.7834 | 0.1665 (= 0.1304 / 0.7834) | 0.1000 |

Reading: the circuit works on Qollab's backend. With the IonQ noise model about a third of the samples leave the valid subspace; because the ansatz conserves K, those samples are detectable and can be discarded. The best sampled layout is the exact optimum in all three cases. At 1000 shots the sampling error on a probability of 0.1 is about 0.01.

## The quantum computer run

- One run, 997 shots, N = 6: the sampling error on the valid-only probability (about 780 valid samples) is about 0.013, so 0.1665 is within one error of the ideal 0.1784 and about five errors above the 0.1000 of a random valid choice.
- The measured P(feasible) of 0.7834 is higher than the 0.6650 of the noise-model simulator: IonQ says its noise models are simplified approximations of the hardware and should not be expected to match it quantitatively.
- Cost (reported by the owner from the runner): the console shows 168.20 credits and a balance of 0.00 afterwards, from a balance of 100. The circuit execution took 200.9 s against a predicted 98.9 s. The shot count was above the threshold at which IonQ's debiasing is on by default (500), which Qollab's documentation says can raise the price; the quoted price before approval was not recorded.

The original console export of the quantum computer run, as downloaded from Qollab, is kept next to the text version: `agustindiazcano-qwind-output-completed-2026-10-11T03-37-01.138Z.html`.
