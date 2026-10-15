# XD CLAN — QAOA for Constrained Portfolio Optimization

**Event:** Qiskit Fall Fest 2026 × IIIT Delhi\
**Track:** Track 2 — Quantum Optimization\
**Project:** QAOA for Constrained Portfolio Optimization

## Team Details

| **Team Member**   | **Contact**                                                           |
| ----------------- | --------------------------------------------------------------------- |
| Vaibhav Shishodia | [contact@vaibhavshishodia.com](mailto:contact@vaibhavshishodia.com)   |
| Vidwan Kochhar    | [vidwankochhar99@gmail.com](mailto:vidwankochhar99@gmail.com)         |
| Samarth Kaushik   | [samarthkaushik39065@gmail.com](mailto:samarthkaushik39065@gmail.com) |

## Project Overview

XD CLAN explores how the **Quantum Approximate Optimization Algorithm (QAOA)** can be applied to constrained portfolio selection. The objective is to select a fixed number of assets while balancing expected return and risk, with diversification constraints introduced in the larger benchmark.

The project compares simulator-based quantum optimization experiments with classical optimization methods, including exhaustive enumeration and simulated annealing. It evaluates solution quality, feasibility, sampling behaviour, and how the computational problem changes as the number of candidate assets increases.

The experiments use reproducibly seeded synthetic data. They are algorithmic benchmarks, not financial advice or predictions about real-world stock performance.

XD CLAN Portfolio Optimizer : [https://qiskit-fall-fest-2026-iiitd-ajiq5qdibj2ujasptcycxm.streamlit.app/](https://qiskit-fall-fest-2026-iiitd-ajiq5qdibj2ujasptcycxm.streamlit.app/)

## Problem Statement

Portfolio selection is a combinatorial optimization problem. Given a collection of candidate assets, the objective is to choose a subset of a specified size while minimizing a risk/return cost and respecting constraints such as portfolio cardinality and sector exposure.

As the number of assets grows, the number of possible combinations increases rapidly. This project investigates QAOA as a heuristic for sampling candidate solutions and compares its output with classical reference methods.

## Objectives

- Formulate portfolio selection as a binary optimization problem.
- Encode the risk/return objective and cardinality constraints in a QAOA cost Hamiltonian.
- Compare QAOA sampling results with exact classical optimization.
- Evaluate multiple QAOA depths and cardinality-penalty settings.
- Compare an intermediate-size instance with a simulated-annealing baseline.
- Benchmark a larger sector-constrained instance using exact classical search.
- Keep simulator experiments, classical benchmarks, and hardware claims clearly distinguished.

## Mathematical Formulation

Each asset is represented by a binary decision variable:

`xᵢ ∈ {0, 1}`

Here, `xᵢ = 1` means asset `i` is selected, while `xᵢ = 0` means it is not selected.

The seeded risk/return objective is:

`C(x) = q xᵀΣx − μᵀx`

where:

- `x` is the binary asset-selection vector.
- `Σ = AAᵀ` is the covariance-like matrix used in the seeded instance.
- `μ` is the seeded return-weight vector.
- `q = 0.5` is the risk weighting used in the objective.

The cardinality constraint requires exactly `K` selected assets:

`Σᵢ xᵢ = K`

For QAOA, this constraint is encoded using a penalty term:

`λ(Σᵢ xᵢ − K)²`

Sector constraints are considered separately in the larger benchmark. The implementation distinguishes the optimization objective from the constraints used to determine whether a portfolio is feasible.

## Methodology

### 1. Reproducible problem generation

The notebook generates seeded problem instances so that results can be reproduced and compared consistently.

### 2. Beginner instance — 6 assets

- Assets: `n = 6`
- Required selections: `K = 3`
- Total bitstrings: 64
- Feasible portfolios: 20
- QAOA depth sweep: `p = 1…4`
- Additional experiments: Hamiltonian validation, approximation-ratio calculation, and cardinality-penalty sweep.

### 3. Intermediate instance — 12 assets

- Assets: `n = 12`
- Required selections: `K = 6`
- Feasible portfolios: 924
- Comparison methods: QAOA sampling, exact classical enumeration, and seeded simulated annealing.
- The classical exact result serves as the reference for evaluating sampled solutions.

### 4. Advanced classical benchmark — 20 assets

- Assets: `n = 20`
- Required selections: `K = 10`
- Total combinations: 184,756
- Combinations satisfying the configured sector cap: 80,000
- Method: exact classical enumeration over feasible portfolios.

**Important:** The 20-asset result is a classical benchmark, not a 20-qubit QAOA run.

### 5. Advanced quantum pilot — 8 qubits

The notebook also contains an 8-qubit pilot with explicit sector constraints, ideal QAOA simulation, noisy AerSimulator evaluation, and circuit-resource reporting. These are simulator experiments, not executions on a real IBM quantum processor.

## Key Results

### Beginner: 6 assets, selecting 3

- Exact classical optimum cost: `−0.5030146903`
- Optimal selected assets: `{2, 3, 6}`
- The recorded QAOA sampling runs at depths `p = 1…4` sampled a best feasible portfolio matching the exact optimum.
- The `p = 2` run recorded the highest feasible-shot rate in the depth-sweep results: **95.87%**.
- The `p = 2` run recorded a best-portfolio hit rate of **4.47%**.
- In a separate penalty-sweep experiment, `λ = 5` recorded the highest feasible-shot rate: **67.87%**.

The depth-sweep and penalty-sweep figures come from separate experiments and should not be combined into a single run.

### Intermediate: 12 assets, selecting 6

- Exact classical optimum cost: `−0.6872192458`
- Optimal selected assets: `{1, 4, 6, 8, 9, 12}`
- Feasible portfolios: **924**
- In the recorded `p = 1` QAOA sampling run, the exact optimum was sampled once in 4,096 shots.
- The independently reproduced, seeded 20,000-step simulated-annealing baseline also found the exact optimum.

Exact enumeration remains the reference result; a sampled match does not establish a quantum speedup.

### Advanced: 20 assets, selecting 10

- Total combinations: **184,756**
- Feasible combinations under the configured sector cap: **80,000**
- Exact classical optimum cost: `−1.4913972690`
- Optimal selected assets: `{1, 2, 5, 6, 7, 8, 12, 14, 15, 20}`
- Sector counts: `[3, 3, 3, 1]`

This is an exact classical result. No QAOA circuit was executed for this 20-asset case.

## Technology Stack

- Python
- Qiskit
- Qiskit Algorithms
- Qiskit Aer / AerSimulator
- NumPy
- pandas
- SciPy
- Matplotlib
- Jupyter Notebook
- Streamlit for the interactive portfolio-lab application

## Repository Contents

- `XD_CLAN_Portfolio_Optimization_Updated.ipynb` — main notebook containing the experiments and analysis.
- `XD_CLAN_Portfolio_Optimization_Presentation.pptx` — project presentation.
- `XD_CLAN_Portfolio_Optimization_Presentation.pdf` — PDF presentation.
- `XD_CLAN_XDCLAN_Fresh_Rebuilt_Verified_Package.zip` — bundled experiment result artifacts.
- `advanced_circuit_resources.csv` — advanced pilot circuit-resource results.
- `advanced_classical_results.csv` — advanced classical benchmark results.
- `advanced_quantum_pilot_results.csv` — advanced quantum pilot results.
- `advanced_verification_results.csv` — advanced verification outputs.
- `ibm_marrakesh_hardware_counts.csv` — saved counts from the recorded IBM Marrakesh run.
- `HARDWARE_EXPERIMENT_REPORT.md` — hardware job metadata, circuit resources, and interpretation.
- `intermediate_classical_comparison.csv` — intermediate classical comparison results.
- `intermediate_results.csv` — intermediate experiment results.
- `penalty_sweep_results.csv` — cardinality-penalty sweep results.
- `portfolio_summary.csv` — portfolio summary outputs.
- `qaoa_depth_results.csv` — QAOA depth experiment results.
- `qaoa_portfolio_results.csv` — QAOA portfolio sampling results.
- `streamlit_app/` — interactive portfolio-lab application source and requirements.

## Installation and Execution

### Notebook

Use Python with Jupyter Notebook or Google Colab. The notebook includes a package-installation cell for the core dependencies.

The core dependencies include:

```
python -m pip install "qiskit>=1.2,<3" "qiskit-algorithms>=0.3" scipy matplotlib pandas
```

Open `XD_CLAN_Portfolio_Optimization_Updated.ipynb` and run the cells in order to reproduce the notebook experiments.

The simulator experiments can be reproduced without IBM Quantum credentials. This package also includes a separate recorded IBM Quantum Runtime hardware run; reproducing that hardware execution requires suitable IBM Quantum access.

### Streamlit Application

From the `streamlit_app` directory:

```
python -m pip install -r requirements.txt
streamlit run app.py
```

The interactive application supports portfolio exploration, classical optimization, configurable asset counts, and downloadable result tables. Its editable demonstration dataset is synthetic and should not be interpreted as real market data.

## Reproducibility and Scientific Integrity

- Randomized problem instances use explicit seeds.
- Exact classical enumeration is used as the reference where feasible.
- Most QAOA depth/penalty results are based on simulator sampling.
- The package also documents a completed 6-qubit IBM Marrakesh hardware run and includes its saved measurement counts.
- The 20-asset result is classical-only.
- The 8-qubit pilot is a simulator experiment.
- The recorded hardware execution is not evidence of quantum speedup or quantum advantage.
- Finding the classical optimum in a QAOA sample does not demonstrate that QAOA is faster or superior to classical optimization.
- Synthetic demonstration data is not live stock-market data.

## Limitations

- The benchmark instances use seeded synthetic inputs rather than historical financial data.
- Simulator results do not establish performance on real quantum hardware.
- The exact classical reference is practical for the evaluated problem sizes but becomes more expensive as the search space grows.
- Feasible-shot rates and best-portfolio hit rates depend on the particular experiment, penalty setting, QAOA depth, and sampling run.
- The larger classical benchmark must not be presented as a completed large-scale quantum experiment.

## Attribution and Acknowledgements

The notebook is adapted from Benjamin Tirado’s BasQ Qiskit Fall Fest QAOA tutorial. Refer to the attribution and licence information included in the notebook.

Third-party libraries are used under their respective licences. Their use does not imply endorsement of this project by their maintainers.

## Submission Information

- **Team name:** XD CLAN
- **Project title:** QAOA for Constrained Portfolio Optimization
- **Event:** Qiskit Fall Fest 2026 × IIIT Delhi
- **Track:** Track 2 — Quantum Optimization
- **Primary deliverable:** `XD_CLAN_Portfolio_Optimization_Updated.ipynb`
- **Presentation:** `XD_CLAN_Portfolio_Optimization_Presentation.pptx` and `XD_CLAN_Portfolio_Optimization_Presentation.pdf`