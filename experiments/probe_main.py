"""
main.py of the SEPARATE Qollab test project used to probe a backend (see scripts/make_probe_project.py). Not the submission.

Select the backend in the Run dialog: the built-in simulator first (free), then an IonQ noise-model simulator (free), and a
quantum computer only if the price the runner quotes is acceptable (decline and nothing is charged). Qollab provides the
selected backend as the global `backend`; without it the probe uses Qiskit's noiseless basic simulator.
"""
import sys

from qwind.probe import format_report, run_probe


def main(n_cells=6, K=3, p=1, shots=1000):
    backend = globals().get("backend")
    print("Backend probe started", flush=True)
    print(f"Backend: {backend if backend is not None else 'none given, using the basic simulator'}", flush=True)
    try:
        result = run_probe(n_cells=n_cells, K=K, p=p, shots=shots, backend=backend)
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        raise
    print(format_report(result), flush=True)


if __name__ == "__main__":
    main()
