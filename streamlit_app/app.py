from __future__ import annotations

import itertools
import math
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Civic? XD CLAN | Quantum Portfolio Lab", page_icon="⚛️", layout="wide")

MAX_CLASSICAL_EXACT = 20
MAX_QAOA_SIMULATOR = 8

st.markdown("""
<style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1450px;}
    .hero {padding: 1.35rem 1.5rem; border-radius: 18px; border: 1px solid rgba(130,120,190,.3);
           background: linear-gradient(120deg, rgba(85,70,160,.15), rgba(40,130,150,.10)); margin-bottom: 1rem;}
    .hero h1 {margin: 0 0 .25rem 0; font-size: 2rem;}
    .muted {opacity: .75; font-size: .92rem;}
    div[data-testid="stMetric"] {border: 1px solid rgba(130,120,190,.22); border-radius: 14px; padding: .8rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>⚛️ XD CLAN · Quantum Portfolio Lab</h1>
<div class="muted">Scalable portfolio experiments · exact classical baselines · QAOA simulation where tractable</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Problem setup")
    n_assets = st.slider("Number of assets", min_value=4, max_value=MAX_CLASSICAL_EXACT, value=6, step=1,
                         help="Exact classical enumeration is enabled through 20 assets. The number of candidate portfolios grows exponentially.")
    k_assets = st.slider("Assets to select (K)", min_value=1, max_value=n_assets, value=min(3, n_assets), step=1)
    risk_weight = st.slider("Risk weight", min_value=0.0, max_value=2.0, value=0.5, step=0.05)
    sector_cap_on = st.checkbox("Enable sector diversification cap", value=False)
    sector_cap = st.number_input("Maximum assets per sector", min_value=1, max_value=n_assets, value=min(2, n_assets), step=1,
                                 disabled=not sector_cap_on)
    seed = st.number_input("Data seed", min_value=0, max_value=999999, value=2026, step=1)
    st.divider()
    st.caption("Official benchmark settings remain separate from this interactive sandbox.")

st.subheader("Asset data")
st.write("Use the reproducible demo dataset or upload your own CSV. For uploaded data, include `asset`, `expected_return`, `risk`, and optionally `sector`.")

uploaded = st.file_uploader("Upload asset data (CSV)", type=["csv"])
def make_demo_data(n: int, seed_value: int) -> pd.DataFrame:
    rng = np.random.default_rng(int(seed_value))
    # Stable deterministic demo values, not financial advice or real market forecasts.
    returns = rng.uniform(0.025, 0.18, n)
    risk = rng.uniform(0.04, 0.28, n)
    sectors = np.array([f"Sector {(i % max(2, min(5, math.ceil(n / 4)))) + 1}" for i in range(n)])
    return pd.DataFrame({
        "asset": [f"Asset {i+1:02d}" for i in range(n)],
        "expected_return": np.round(returns, 5),
        "risk": np.round(risk, 5),
        "sector": sectors
    })

if uploaded is not None:
    try:
        raw = pd.read_csv(uploaded)
        raw.columns = [str(c).strip().lower() for c in raw.columns]
        required = {"asset", "expected_return", "risk"}
        if not required.issubset(raw.columns):
            st.error("CSV must contain columns: asset, expected_return, risk. Optional: sector.")
            st.stop()
        raw = raw.copy()
        raw["asset"] = raw["asset"].astype(str)
        raw["expected_return"] = pd.to_numeric(raw["expected_return"], errors="coerce")
        raw["risk"] = pd.to_numeric(raw["risk"], errors="coerce")
        if raw[["expected_return", "risk"]].isna().any().any() or len(raw) < 2:
            st.error("Uploaded CSV needs at least two rows and numeric expected_return/risk values.")
            st.stop()
        if "sector" not in raw:
            raw["sector"] = "Unassigned"
        raw["sector"] = raw["sector"].fillna("Unassigned").astype(str)
        if len(raw) < n_assets:
            st.warning(f"Your CSV has {len(raw)} assets, so the asset count was adjusted from {n_assets} to {len(raw)}.")
            n_assets = len(raw)
            k_assets = min(k_assets, n_assets)
        data = raw.head(n_assets).reset_index(drop=True)
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
        st.stop()
else:
    data = make_demo_data(n_assets, seed)

data = data.head(n_assets).reset_index(drop=True)
if k_assets > len(data):
    k_assets = len(data)

edited = st.data_editor(data, use_container_width=True, num_rows="fixed", key="asset_editor",
                        column_config={
                            "expected_return": st.column_config.NumberColumn("Expected return", format="%.5f"),
                            "risk": st.column_config.NumberColumn("Risk", format="%.5f"),
                            "sector": st.column_config.TextColumn("Sector")
                        })
if len(edited) != n_assets:
    st.info("The asset table has a different number of rows than the slider. Use the asset-count slider to set the problem size.")

def portfolio_score(indices: tuple[int, ...], df: pd.DataFrame, risk_w: float) -> float:
    r = df.loc[list(indices), "expected_return"].to_numpy(dtype=float)
    v = df.loc[list(indices), "risk"].to_numpy(dtype=float)
    # A simple illustrative objective: reward expected return and penalize aggregate risk.
    return float(-np.sum(r) + risk_w * np.sum(v * v))

def is_sector_feasible(indices: tuple[int, ...], df: pd.DataFrame, enabled: bool, cap: int) -> bool:
    if not enabled:
        return True
    counts = df.loc[list(indices), "sector"].value_counts()
    return bool((counts <= cap).all())

def exact_optimize(df: pd.DataFrame, k: int, risk_w: float, sector_enabled: bool, cap: int):
    n = len(df)
    candidate_count = math.comb(n, k)
    best = None
    feasible = 0
    rows = []
    for inds in itertools.combinations(range(n), k):
        if not is_sector_feasible(inds, df, sector_enabled, cap):
            continue
        feasible += 1
        score = portfolio_score(inds, df, risk_w)
        rows.append((score, inds))
        if best is None or score < best[0]:
            best = (score, inds)
    return best, feasible, candidate_count, rows

if sector_cap_on:
    sector_counts = edited["sector"].value_counts()
    max_possible = sum(min(int(sector_cap), int(v)) for v in sector_counts.values)
    if max_possible < k_assets:
        st.error(f"These sector caps permit at most {max_possible} selected assets, but K={k_assets}. Add sectors, raise the cap, or lower K.")
        st.stop()

candidate_count = math.comb(len(edited), k_assets)
st.subheader("Optimization")
left, right = st.columns([1, 1])
with left:
    st.metric("Candidate portfolios", f"{candidate_count:,}")
    st.caption("This is C(N, K), before sector constraints.")
with right:
    st.metric("State space for N qubits", f"{2 ** len(edited):,}")
    st.caption("Statevector memory and simulation cost grow exponentially with qubit count.")

if len(edited) > MAX_CLASSICAL_EXACT:
    st.error("This app is configured for at most 20 assets. Larger cases need a heuristic or specialized optimizer.")
    st.stop()

if st.button("Run exact classical optimization", type="primary", use_container_width=True):
    with st.spinner("Enumerating feasible portfolios…"):
        result, feasible_count, total_count, all_rows = exact_optimize(
            edited, k_assets, risk_weight, sector_cap_on, int(sector_cap)
        )
    if result is None:
        st.error("No feasible portfolio exists for the current K and sector constraints.")
    else:
        score, inds = result
        selected = edited.iloc[list(inds)].copy()
        st.session_state["last_result"] = {
            "score": score,
            "indices": list(inds),
            "selected": selected.to_dict(orient="records"),
            "feasible": feasible_count,
            "total": total_count,
            "all_rows": [(float(s), list(i)) for s, i in all_rows],
            "n": len(edited),
            "k": k_assets
        }

if "last_result" in st.session_state:
    saved = st.session_state["last_result"]
    if saved["n"] == len(edited) and saved["k"] == k_assets:
        st.success("Exact classical search completed.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Best objective", f"{saved['score']:.6f}")
        m2.metric("Feasible portfolios", f"{saved['feasible']:,}")
        m3.metric("Feasible rate", f"{100*saved['feasible']/max(1,saved['total']):.2f}%")
        m4.metric("Selected assets", str(len(saved["indices"])))
        chosen = pd.DataFrame(saved["selected"])
        st.markdown("#### Best portfolio")
        st.dataframe(chosen, use_container_width=True, hide_index=True)
        st.download_button("Download best portfolio CSV", chosen.to_csv(index=False).encode("utf-8"),
                           file_name="xd_clan_best_portfolio.csv", mime="text/csv")
        st.download_button("Download all feasible candidates CSV",
                           pd.DataFrame([{"objective": s, "asset_indices_1_based": ",".join(str(i+1) for i in inds)}
                                         for s, inds in saved["all_rows"]]).to_csv(index=False).encode("utf-8"),
                           file_name="xd_clan_feasible_candidates.csv", mime="text/csv")
        plot_data = edited.copy()
        plot_data["selected"] = ["Selected" if i in saved["indices"] else "Not selected" for i in range(len(plot_data))]
        fig = px.scatter(plot_data, x="risk", y="expected_return", color="selected", hover_name="asset",
                         symbol="selected", title="Expected return vs. risk (illustrative input values)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Inputs changed since the previous run. Run the optimizer again to refresh results.")

st.divider()
st.subheader("Quantum simulation readiness")
if len(edited) <= MAX_QAOA_SIMULATOR:
    st.success(f"{len(edited)} assets fit within this app's small-circuit QAOA simulation guardrail ({MAX_QAOA_SIMULATOR} qubits).")
    st.write("This page does not silently claim a QAOA result: use the notebook's QAOA workflow for a reproducible quantum simulation and save its actual outputs separately.")
else:
    st.warning(f"{len(edited)} assets exceed the current {MAX_QAOA_SIMULATOR}-qubit QAOA pilot guardrail. The exact classical optimizer still works up to {MAX_CLASSICAL_EXACT} assets, but this app will not pretend that a larger QAOA circuit has been executed.")
st.caption("Demo data are synthetic and for algorithm demonstration only. They are not investment advice. Exact classical search is an objective baseline, not evidence of quantum advantage.")
