# Backend probe, N = 6, K = 3, p = 1, 1000 shots (2026-10-11)

Computed from the two console outputs in this folder (no new run). The uniform baseline printed by the probe is over all 2^6 bitstrings; the fair one for a circuit that should stay in the valid subspace is the uniform distribution over the C(6,3) = 20 valid layouts, in which the 2 optimal layouts have probability 0.10.

| Backend | P(optimal) | P(feasible) | P(optimal), valid samples only | Uniform over valid layouts |
|---|---|---|---|---|
| Ideal (exact statevector) | 0.1784 | 1.0000 | 0.1784 | 0.1000 |
| Qiskit basic simulator (no noise) | 0.1600 | 1.0000 | 0.1600 | 0.1000 |
| IonQ simulator with noise model | 0.1010 | 0.6650 | 0.1519 (= 0.1010 / 0.6650) | 0.1000 |

Reading: the circuit works on Qollab's backend. With the IonQ noise model about a third of the samples leave the valid subspace; because the ansatz conserves K, those samples are detectable and can be discarded. The best sampled layout is the exact optimum in all three cases. At 1000 shots the sampling error on a probability of 0.1 is about 0.01.
