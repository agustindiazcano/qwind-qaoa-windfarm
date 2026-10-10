# QWind QAOA Benchmark

QWind is a Qiskit QAOA benchmark for wind-farm layout optimization (wake-loss QUBO with cardinality constraint), compared against exact enumeration, simulated annealing and greedy search.

*This effort is supported by Qollab & IonQ.*

## How to upload `qollab/`
To deploy this project to the Qollab platform:
1. Select the **"Upload your own files"** project shape.
2. Upload the entire `qollab/` folder contents.
3. The entry point must be `main.py` at the top level.
4. Run the project with the built-in simulator.

## Disclosure
- **AI tools**: Anthropics Claude and Google Gemini models were used for code generation and project scaffolding.
- **Libraries**: Qiskit, NumPy, SciPy (for platform execution), plus Qiskit Aer and Matplotlib for offline experiments.
- **Data sources**: Built-in synthetic wind rose / datasets (TBD).
