import streamlit as st
import pandas as pd
import os


from data_sources import pubmed_recent_authors, nih_reporter_grants
from scoring import score_row





DEFAULT_FILE = "Load default.csv"

@st.cache_data
def load_default_data():
    if os.path.exists(DEFAULT_FILE):
        if DEFAULT_FILE.endswith(".csv"):
            return pd.read_csv(DEFAULT_FILE)
        elif DEFAULT_FILE.endswith(".xlsx"):
            return pd.read_excel(DEFAULT_FILE)
    return pd.DataFrame()




# ---------------- Page config & theme ----------------
st.set_page_config(
    page_title="3D In‑Vitro Lead Generation",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#0E7C86"   # biotech‑friendly teal
GREEN = "#22A65A"
AMBER = "#F0A500"
GREY = "#808080"

st.markdown(f"""
<style>
.main {{ background-color: #f7fafc; }}
.block-container {{ padding-top: 1.2rem; }}
h1, h2, h3 {{ color: {PRIMARY}; }}
.stDataFrame {{ background: white; border-radius: 10px; }}
.card {{ background: white; border-radius: 12px; padding: 14px 16px; border: 1px solid #e7e7e7; }}
.badge {{ display:inline-block; padding:6px 10px; border-radius:999px; font-size:0.85rem; font-weight:600; }}
.badge-green {{ background: {GREEN}22; color: {GREEN}; border: 1px solid {GREEN}55; }}
.badge-amber {{ background: {AMBER}22; color: {AMBER}; border: 1px solid {AMBER}55; }}
.badge-grey {{ background: {GREY}22; color: {GREY}; border: 1px solid {GREY}55; }}
</style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown("# 🧪 3D In‑Vitro Lead Generation Dashboard")
st.write("Identify, enrich, and rank leads for therapies using 3D in‑vitro models. Real PubMed authors, NIH grants, upload CSV from Apollo/Clay, dynamic filters, scoring, and export.")

# Load default Excel file once 
df_raw = load_default_data() 
# ---------------- Sidebar: data source ---------------- 
st.sidebar.header("🔌 Data source") 
source = st.sidebar.radio( 
    "Choose source",
    ["Default file","Upload CSV (Apollo/Clay)", "PubMed authors (query)", "NIH grants (keyword)", "Use seed demo (100 rows)"], 
    index=0
) 
if source == "Default file": 
    df_raw = load_default_data()
elif source == "Upload CSV (Apollo/Clay)": 
    st.sidebar.caption("Export real leads from Apollo.io or Clay with LinkedIn URLs and business emails, then upload here.") 
    file = st.sidebar.file_uploader("Upload leads CSV or Excel", type=["csv", "xlsx"]) 
    if file is not None: 
        ext = os.path.splitext(file.name)[1].lower() 
        if ext == ".csv": 
            df_raw = pd.read_csv(file) 
        elif ext == ".xlsx": 
            df_raw = pd.read_excel(file) 
        else: 
            st.error("Unsupported file format. Please upload a CSV or XLSX file.")

elif source == "PubMed authors (query)":
    st.sidebar.caption("Real authors fetching via PubMed. Example: Drug‑Induced Liver Injury[Title] AND 3D cell culture")
    query = st.sidebar.text_input("PubMed query", value="Drug-Induced Liver Injury[Title] AND 3D cell culture")
    if st.sidebar.button("Fetch authors"):
        df_raw = pubmed_recent_authors(query, max_results=50)

elif source == "NIH grants (keyword)":
    st.sidebar.caption("Fetch NIH grants with keyword to identify funded academics.")
    keyword = st.sidebar.text_input("Grant keyword", value="liver toxicity")
    if st.sidebar.button("Fetch grants"):
        df_raw = nih_reporter_grants(keyword, max_results=50)

elif source == "Use seed demo (100 rows)":
    st.sidebar.caption("Use the generated 100‑row dataset (run generate_seed_csv.py first).")
    try:
        df_raw = pd.read_csv("seed_leads_100.csv")
    except Exception:
        st.sidebar.error("seed_leads_100.csv not found. Run: python generate_seed_csv.py")

# ---------------- Normalize columns ----------------
essential_cols = ["Name","Title","Company","Person location","Company HQ","Email","LinkedIn","Last paper title","Last paper year","Conference","Funding round","NAMs signal","Notes","Action"]
if df_raw.empty:
    # minimal placeholder to avoid errors when nothing is loaded
    df_raw = pd.DataFrame(columns=essential_cols)

for c in essential_cols:
    if c not in df_raw.columns:
        df_raw[c] = ""

# ---------------- Scoring ----------------
df = df_raw.copy()
df["Score"] = df.apply(score_row, axis=1)
df["Probability"] = df["Score"]
df = df.sort_values(by="Score", ascending=False)
df["Rank"] = range(1, len(df) + 1)

# ---------------- Sidebar: filters ----------------
st.sidebar.header("🔍 Filters")
keyword = st.sidebar.text_input("Keyword search (e.g., Boston, Toxicology, Liver)")
min_score = st.sidebar.slider("Minimum score", 0, 100, 20, step=5)
title_filters = st.sidebar.multiselect(
    "Title contains",
    ["Director", "Head", "VP", "Safety", "Toxicology", "Scientist", "Hepatic", "3D"],
    default=[]
)
hub_filters = st.sidebar.multiselect(
    "Location hubs",
    ["Boston/Cambridge", "Bay Area", "Basel", "UK Golden Triangle"],
    default=[]
)

def infer_hub(loc_str):
    s = str(loc_str).lower()
    if "boston" in s or "cambridge" in s: return "Boston/Cambridge"
    if "bay area" in s or "san francisco" in s: return "Bay Area"
    if "basel" in s: return "Basel"
    if "oxford" in s or "cambridge uk" in s or "golden triangle" in s: return "UK Golden Triangle"
    return None

filtered = df[df["Score"] >= min_score].copy()

if keyword:
    k = keyword.lower()
    filtered = filtered[filtered.apply(lambda r: k in str(r.values).lower(), axis=1)]

if title_filters:
    patt = "|".join([t.lower() for t in title_filters])
    filtered = filtered[filtered["Title"].str.lower().str.contains(patt, na=False)]

if hub_filters:
    filtered["Hub"] = filtered.apply(
        lambda r: infer_hub(str(r.get("Person location","")) + " " + str(r.get("Company HQ",""))), axis=1
    )
    filtered = filtered[filtered["Hub"].isin(hub_filters)]

# ---------------- Summary cards ----------------
col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.markdown(f'<div class="card"><b>Total leads</b><br>{len(df)}</div>', unsafe_allow_html=True)
with col_b:
    st.markdown(f'<div class="card"><b>Filtered leads</b><br>{len(filtered)}</div>', unsafe_allow_html=True)
with col_c:
    top_score = int(filtered["Score"].max()) if not filtered.empty else 0
    st.markdown(f'<div class="card"><b>Top score</b><br><span class="badge badge-green">{top_score}</span></div>', unsafe_allow_html=True)
with col_d:
    st.markdown('<div class="card"><b>Export</b><br>Use the button below to download CSV.</div>', unsafe_allow_html=True)

# ---------------- Table ----------------
st.markdown("## 📊 Ranked leads")
column_config = {
    "LinkedIn": st.column_config.LinkColumn("LinkedIn"),
    "Email": st.column_config.Column("Email"),
    "Score": st.column_config.ProgressColumn("Score", format="%d", min_value=0, max_value=100),
    "Probability": st.column_config.ProgressColumn("Probability", format="%d", min_value=0, max_value=100),
}
display_cols = [
    "Rank","Score","Probability","Name","Title","Company","Person location","Company HQ",
    "Email","LinkedIn","Last paper title","Last paper year","Conference","Funding round","NAMs signal","Action"
]
display_cols = [c for c in display_cols if c in filtered.columns]

st.dataframe(
    filtered[display_cols],
    use_container_width=True,
    column_config=column_config,
    hide_index=True
)

# ---------------- Download ----------------
st.download_button(
    label="⬇️ Download filtered leads (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="lead_generation_filtered.csv",
    mime="text/csv",
    type="primary"
)

# ---------------- Scoring logic panel ----------------
with st.expander("🧮 Scoring logic"):
    st.write("""
- Role fit: Title contains Toxicology, Safety, Hepatic, or 3D → +30
- Company intent: Series A/B funding → +20
- Technographic: Uses in‑vitro/NAMs → +15; methods mentioned → +10
- Location hub: Boston/Cambridge, Bay Area, Basel, UK Golden Triangle → +10
- Scientific intent: DILI paper in the last 2 years → +40
- Score capped at 100; Probability mirrors Score for demo clarity.
""")
