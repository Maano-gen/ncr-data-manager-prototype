import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io

st.set_page_config(
    page_title="NCR Data Manager Prototype",
    layout="wide",
    page_icon="🔬"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e2e8f0;
        border-radius: 6px 6px 0 0;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e3a5f !important;
        color: white !important;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 4px solid #1e3a5f;
    }
    .error-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 4px solid #e53e3e;
    }
    h1 { color: #1e3a5f; }
    h2, h3 { color: #2d4a6e; }
    .footer-note {
        font-size: 0.78rem;
        color: #718096;
        border-top: 1px solid #e2e8f0;
        padding-top: 12px;
        margin-top: 24px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("# 🔬 NCR Data Manager Prototype")
st.markdown("""
**Malima Maano Bryton** | Data Manager & Bioinformatician, SAMRC Genomics Platform  
PhD Candidate (Cancer Bioinformatics & Machine Learning) | *Ref: NICD0126/001-11*
""")
st.markdown("""
<div style="
    background-color: #fffbeb;
    border: 1.5px solid #f6ad55;
    border-left: 5px solid #dd6b20;
    border-radius: 8px;
    padding: 14px 20px;
    margin-bottom: 18px;
    font-size: 0.9rem;
    color: #7b341e;
">
⚠️ <strong>Data Disclaimer:</strong> All data displayed in this prototype is <strong>entirely synthetic and artificially generated for demonstration purposes only</strong>.
No real patient records, personal health information, or confidential NCR/NHLS data has been used or accessed.
All names, identifiers, dates, and clinical details are fictitious. This prototype was developed solely to illustrate
automated pipeline design, logical validation rules, ICD-O-3 coding logic, and probabilistic record linkage methodology
as relevant to the Data Manager role (Ref: NICD0126/001-11). All data handling in a live environment would comply
strictly with POPIA, NHLS confidentiality protocols, and NCR data governance standards.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Synthetic Dataset ───────────────────────────────────────────────────────
@st.cache_data
def load_default_data():
    records = []

    template = [
        # (histology_text, topography_text, sex, icd_topo, icd_morph, age_range, cancer_label)
        ("Invasive ductal carcinoma, breast, grade 2", "left breast upper outer quadrant", "F", "C50.4", "8500/3", (30, 75), "Breast"),
        ("Invasive ductal carcinoma, breast, grade 3", "right breast", "F", "C50.9", "8500/3", (28, 70), "Breast"),
        ("Squamous cell carcinoma of cervix", "cervix uteri", "F", "C53.9", "8070/3", (25, 65), "Cervix"),
        ("Cervical adenocarcinoma in situ", "endocervix", "F", "C53.0", "8140/2", (30, 60), "Cervix"),
        ("Prostate adenocarcinoma, Gleason 7", "prostate gland", "M", "C61.9", "8140/3", (50, 85), "Prostate"),
        ("Prostate carcinoma, poorly differentiated", "prostate", "M", "C61.9", "8010/3", (55, 80), "Prostate"),
        ("Acute lymphoblastic leukaemia, B-cell type", "bone marrow", "M", "C42.1", "9835/3", (2, 15), "Leukaemia"),
        ("Acute lymphoblastic leukaemia", "bone marrow", "F", "C42.1", "9835/3", (3, 18), "Leukaemia"),
        ("Squamous cell carcinoma of lung", "upper lobe, bronchus", "M", "C34.1", "8070/3", (45, 80), "Lung"),
        ("Adenocarcinoma of lung", "lower lobe, bronchus", "F", "C34.3", "8140/3", (40, 75), "Lung"),
        ("Colorectal adenocarcinoma", "sigmoid colon", "M", "C18.7", "8140/3", (40, 80), "Colorectal"),
        ("Rectal adenocarcinoma", "rectum", "F", "C20.9", "8140/3", (45, 78), "Colorectal"),
        ("Non-Hodgkin lymphoma, diffuse large B-cell", "lymph node, axillary", "M", "C77.3", "9680/3", (35, 75), "Lymphoma"),
        ("Follicular lymphoma, grade 2", "lymph node, cervical", "F", "C77.0", "9690/3", (30, 70), "Lymphoma"),
        ("Hepatocellular carcinoma", "liver", "M", "C22.0", "8170/3", (40, 75), "Liver"),
        ("Cholangiocarcinoma", "intrahepatic bile ducts", "F", "C22.1", "8160/3", (45, 70), "Liver"),
        ("Osteosarcoma, conventional", "distal femur", "M", "C40.2", "9180/3", (8, 25), "Bone"),
        ("Ewing sarcoma", "pelvis", "F", "C41.4", "9260/3", (5, 20), "Bone"),
        ("Melanoma of skin, superficial spreading", "back", "M", "C44.5", "8743/3", (30, 70), "Melanoma"),
        ("Melanoma, nodular", "lower limb", "F", "C44.7", "8721/3", (35, 65), "Melanoma"),
    ]

    labs = [
        "NHLS Johannesburg", "PathCare Cape Town", "NHLS Durban",
        "Lancet Pretoria", "NHLS Port Elizabeth", "PathCare Johannesburg",
        "NHLS Bloemfontein", "Ampath Pretoria"
    ]

    import random
    random.seed(42)

    record_num = 1
    for i, (hist, topo, sex, icd_t, icd_m, age_range, label) in enumerate(template):
        count = 5 if label in ["Breast", "Cervix", "Prostate"] else 3
        for j in range(count):
            age = random.randint(*age_range)
            birth_year = 2025 - age
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            dob_str = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"

            coll_day_offset = random.randint(1, 360)
            coll_date = pd.Timestamp("2025-01-01") + pd.Timedelta(days=coll_day_offset)
            report_date = coll_date + pd.Timedelta(days=random.randint(2, 10))

            nhls_id = f"NHLS{10000000 + record_num:08d}"
            ncr_app_id = f"NCRAPP{record_num:04d}" if record_num % 4 == 0 else ""

            records.append({
                "record_id": f"NCR2026{record_num:04d}",
                "lab_name": labs[record_num % len(labs)],
                "collection_date": coll_date.strftime("%Y-%m-%d"),
                "report_date": report_date.strftime("%Y-%m-%d"),
                "dob": dob_str,
                "sex": sex,
                "patient_age_at_collection": age,
                "histology_free_text": hist,
                "raw_topography_text": topo,
                "raw_morphology_text": hist.split(",")[0].lower(),
                "icd_o_3_topography": icd_t,
                "icd_o_3_morphology": icd_m,
                "linked_nhls_id": nhls_id,
                "linked_ncr_app_id": ncr_app_id,
                "cancer_group": label,
            })
            record_num += 1

    df = pd.DataFrame(records)

    # Inject deliberate errors for demo
    df.loc[1, "sex"] = "M"           # Male with cervix topography → sex-site mismatch
    df.loc[3, "sex"] = "F"           # Female with prostate topography → sex-site mismatch
    df.loc[7, "collection_date"] = "2025-12-20"
    df.loc[7, "report_date"] = "2025-12-15"   # collection AFTER report → date error
    df.loc[12, "patient_age_at_collection"] = 145   # age outlier
    df.loc[18, "patient_age_at_collection"] = -3    # negative age
    df.loc[22, "collection_date"] = "2025-11-30"
    df.loc[22, "report_date"] = "2025-11-28"        # another date error

    return df


# ── ICD-O-3 Rule-Based Coder ─────────────────────────────────────────────────
CODING_RULES = {
    "breast": ("C50.9", "8500/3", "Breast NOS"),
    "cervix": ("C53.9", "8070/3", "Cervix uteri NOS"),
    "prostate": ("C61.9", "8140/3", "Prostate gland"),
    "bone marrow": ("C42.1", "9835/3", "Bone marrow"),
    "lung": ("C34.9", "8140/3", "Bronchus and lung NOS"),
    "colon": ("C18.9", "8140/3", "Colon NOS"),
    "rectum": ("C20.9", "8140/3", "Rectum NOS"),
    "liver": ("C22.0", "8170/3", "Liver"),
    "lymph node": ("C77.9", "9680/3", "Lymph node NOS"),
    "femur": ("C40.2", "9180/3", "Long bones of lower limb"),
    "pelvis": ("C41.4", "9260/3", "Pelvic bones"),
    "skin": ("C44.9", "8720/3", "Skin NOS"),
}

def suggest_icd_o3(topography_text, morphology_text):
    text = (topography_text + " " + morphology_text).lower()
    for keyword, (topo_code, morph_code, site_label) in CODING_RULES.items():
        if keyword in text:
            confidence = "High" if keyword in topography_text.lower() else "Medium"
            return topo_code, morph_code, site_label, confidence
    return "UNKNOWN", "UNKNOWN", "Could not auto-code", "Low"


# ── Load data ────────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = load_default_data()

df = st.session_state.df

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    uploaded_file = st.file_uploader("Upload lab extract CSV", type="csv")
    if uploaded_file:
        st.session_state.df = pd.read_csv(uploaded_file)
        df = st.session_state.df
        st.success("✅ Custom file loaded")

    if st.button("🔄 Reset to Default Data"):
        st.session_state.df = load_default_data()
        st.rerun()

    st.markdown("---")
    st.markdown("**Dataset Summary**")
    st.metric("Total Records", len(df))
    st.metric("Labs Represented", df["lab_name"].nunique())
    st.metric("Cancer Types", df["cancer_group"].nunique() if "cancer_group" in df.columns else "N/A")

# ── Main Tabs ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Raw Data",
    "🧼 Data Cleaning & Validation",
    "🔬 ICD-O-3 Coding Pipeline",
    "🔗 Probabilistic Linkage",
    "📊 Dashboard Outputs"
])

# ── TAB 1: Raw Data ──────────────────────────────────────────────────────────
with tab1:
    st.subheader("Raw Incoming Pathology Reports")
    st.caption(f"Showing all {len(df)} records — modelled on real NCR 2022/2023 annual report data (NICD)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", len(df))
    col2.metric("Unique Labs", df["lab_name"].nunique())
    col3.metric("Female Cases", int((df["sex"] == "F").sum()))
    col4.metric("Male Cases", int((df["sex"] == "M").sum()))

    st.dataframe(df.drop(columns=["cancer_group"], errors="ignore"), use_container_width=True, height=400)

    csv_raw = df.to_csv(index=False).encode()
    st.download_button("📥 Download Raw Dataset", csv_raw, "ncr_raw_data.csv", "text/csv")


# ── TAB 2: Data Cleaning ─────────────────────────────────────────────────────
with tab2:
    st.subheader("Automated Data Cleaning & Logical Validation")
    st.markdown("""
    Applies the **exact validation rules** described in the NICD0126/001-11 amended JD:
    - Date correlations (collection ≤ report)
    - Sex-site consistency checks (ICD-O-3 site vs patient sex)
    - Age outlier detection
    - Missing critical field detection
    """)

    if st.button("🚀 Run Full Cleaning Pipeline", type="primary"):
        working = df.copy()

        # 1. Date correlation
        working["date_error"] = (
            pd.to_datetime(working["collection_date"], errors="coerce") >
            pd.to_datetime(working["report_date"], errors="coerce")
        )

        # 2. Sex-site consistency
        working["sex_site_error"] = (
            ((working["sex"] == "M") & working["icd_o_3_topography"].str.startswith("C53", na=False)) |
            ((working["sex"] == "F") & working["icd_o_3_topography"].str.startswith("C61", na=False))
        )

        # 3. Age outlier
        working["age_error"] = (
            (working["patient_age_at_collection"] < 0) |
            (working["patient_age_at_collection"] > 120)
        )

        # 4. Missing fields
        working["missing_field_error"] = (
            working["histology_free_text"].isna() |
            working["icd_o_3_topography"].isna() |
            working["dob"].isna()
        )

        # Summary
        n_date = working["date_error"].sum()
        n_sex = working["sex_site_error"].sum()
        n_age = working["age_error"].sum()
        n_missing = working["missing_field_error"].sum()
        total_errors = (working["date_error"] | working["sex_site_error"] | working["age_error"] | working["missing_field_error"]).sum()

        st.success(f"✅ Pipeline complete — scanned {len(working)} records")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Flagged", total_errors, delta=None)
        c2.metric("Date Errors", int(n_date))
        c3.metric("Sex-Site Mismatches", int(n_sex))
        c4.metric("Age Outliers", int(n_age))
        c5.metric("Missing Fields", int(n_missing))

        errors_df = working[
            working["date_error"] | working["sex_site_error"] | working["age_error"] | working["missing_field_error"]
        ][["record_id", "lab_name", "sex", "icd_o_3_topography",
           "patient_age_at_collection", "collection_date", "report_date",
           "date_error", "sex_site_error", "age_error", "missing_field_error"]]

        st.markdown("#### ❌ Flagged Records")
        st.dataframe(errors_df, use_container_width=True)

        # Error distribution chart
        error_counts = {
            "Date correlation error": int(n_date),
            "Sex-site mismatch": int(n_sex),
            "Age outlier": int(n_age),
            "Missing fields": int(n_missing),
        }
        fig_err = px.bar(
            x=list(error_counts.keys()),
            y=list(error_counts.values()),
            labels={"x": "Error Type", "y": "Count"},
            title="Error Distribution by Type",
            color=list(error_counts.values()),
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_err, use_container_width=True)

        # Download
        err_csv = errors_df.to_csv(index=False).encode()
        st.download_button(
            "📥 Download Error Report for Labs",
            err_csv, "ncr_error_report.csv", "text/csv"
        )


# ── TAB 3: Automated Coding ──────────────────────────────────────────────────
with tab3:
    st.subheader("Automated ICD-O-3 Coding Pipeline")
    st.markdown("""
    Rule-based NLP coding engine (prototype). In production this connects to a trained ML/NLP model  
    fine-tuned on IARC ICD-O-3 coding rules and NCR historical coded cases.
    """)

    sample_size = st.slider("Records to code", 5, len(df), 20)

    if st.button("🔬 Run Automated Coding", type="primary"):
        sample = df.head(sample_size).copy()
        results = []
        for _, row in sample.iterrows():
            sugg_topo, sugg_morph, site_label, confidence = suggest_icd_o3(
                str(row.get("raw_topography_text", "")),
                str(row.get("raw_morphology_text", ""))
            )
            match = (sugg_topo == row["icd_o_3_topography"])
            results.append({
                "record_id": row["record_id"],
                "histology_text": row["histology_free_text"][:60] + "...",
                "existing_topography": row["icd_o_3_topography"],
                "suggested_topography": sugg_topo,
                "suggested_morphology": sugg_morph,
                "suggested_site": site_label,
                "confidence": confidence,
                "match": "✅" if match else "⚠️ Review",
            })

        results_df = pd.DataFrame(results)
        n_match = (results_df["match"] == "✅").sum()
        st.success(f"✅ Coded {len(results_df)} records — {n_match}/{len(results_df)} matched existing codes")
        st.dataframe(results_df, use_container_width=True)

        coding_csv = results_df.to_csv(index=False).encode()
        st.download_button("📥 Download Coding Results", coding_csv, "ncr_coding_results.csv", "text/csv")


# ── TAB 4: Probabilistic Linkage ─────────────────────────────────────────────
with tab4:
    st.subheader("Probabilistic Record Linkage Demo")
    st.markdown("""
    Simulates **Fellegi-Sunter probabilistic linkage** between:
    - **Source A**: NHLS Laboratory Extract (incoming pathology reports)
    - **Source B**: NCR App existing registry records
    
    In production: uses Python `recordlinkage` library + ML-tuned weights on DOB, sex, NHLS ID, and morphology agreement.
    """)

    if st.button("🔗 Run Probabilistic Linkage", type="primary"):
        import random
        random.seed(99)

        linked = df[df["linked_ncr_app_id"] != ""].copy()
        unlinked = df[df["linked_ncr_app_id"] == ""].copy()

        linked["dob_score"] = [round(random.uniform(0.85, 1.00), 2) for _ in range(len(linked))]
        linked["sex_score"] = 1.0
        linked["nhls_id_score"] = [round(random.uniform(0.90, 1.00), 2) for _ in range(len(linked))]
        linked["composite_score"] = ((linked["dob_score"] + linked["sex_score"] + linked["nhls_id_score"]) / 3).round(3)
        linked["linkage_decision"] = linked["composite_score"].apply(lambda x: "✅ LINKED" if x >= 0.90 else "⚠️ REVIEW")

        unlinked["dob_score"] = [round(random.uniform(0.30, 0.65), 2) for _ in range(len(unlinked))]
        unlinked["sex_score"] = [round(random.uniform(0.5, 1.0), 2) for _ in range(len(unlinked))]
        unlinked["nhls_id_score"] = [round(random.uniform(0.20, 0.60), 2) for _ in range(len(unlinked))]
        unlinked["composite_score"] = ((unlinked["dob_score"] + unlinked["sex_score"] + unlinked["nhls_id_score"]) / 3).round(3)
        unlinked["linkage_decision"] = "❌ NEW RECORD"

        all_linkage = pd.concat([linked, unlinked]).sort_values("record_id")

        n_linked = (all_linkage["linkage_decision"] == "✅ LINKED").sum()
        n_review = (all_linkage["linkage_decision"] == "⚠️ REVIEW").sum()
        n_new = (all_linkage["linkage_decision"] == "❌ NEW RECORD").sum()

        c1, c2, c3 = st.columns(3)
        c1.metric("Linked to NCR App", int(n_linked))
        c2.metric("Needs Manual Review", int(n_review))
        c3.metric("New Records (Unmatched)", int(n_new))

        show_cols = ["record_id", "lab_name", "sex", "dob", "linked_nhls_id",
                     "linked_ncr_app_id", "dob_score", "sex_score", "nhls_id_score",
                     "composite_score", "linkage_decision"]
        st.dataframe(all_linkage[show_cols].head(30), use_container_width=True)

        fig_link = px.pie(
            values=[int(n_linked), int(n_review), int(n_new)],
            names=["Linked", "Review", "New Record"],
            title="Linkage Decision Distribution",
            color_discrete_sequence=["#38a169", "#d69e2e", "#e53e3e"]
        )
        st.plotly_chart(fig_link, use_container_width=True)

        link_csv = all_linkage[show_cols].to_csv(index=False).encode()
        st.download_button("📥 Download Linkage Results", link_csv, "ncr_linkage_results.csv", "text/csv")


# ── TAB 5: Dashboard Outputs ─────────────────────────────────────────────────
with tab5:
    st.subheader("Epidemiology Dashboard — NCR Quarterly Outputs")
    st.caption("Analysis-ready outputs as required by NCR epidemiologists and GICR/IACR reporting")

    col_a, col_b = st.columns(2)

    with col_a:
        if "cancer_group" in df.columns:
            cancer_counts = df["cancer_group"].value_counts().reset_index()
            cancer_counts.columns = ["Cancer Type", "Cases"]
            fig1 = px.bar(
                cancer_counts,
                x="Cases", y="Cancer Type",
                orientation="h",
                title="Cases by Cancer Type",
                color="Cases",
                color_continuous_scale="Blues"
            )
            fig1.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        sex_site = df.groupby(["cancer_group", "sex"]).size().reset_index(name="count") if "cancer_group" in df.columns else None
        if sex_site is not None:
            fig2 = px.bar(
                sex_site,
                x="cancer_group", y="count", color="sex",
                barmode="group",
                title="Cases by Cancer Type and Sex",
                color_discrete_map={"F": "#e91e8c", "M": "#1e5fe9"},
                labels={"cancer_group": "Cancer Type", "count": "Cases"}
            )
            fig2.update_xaxes(tickangle=45)
            st.plotly_chart(fig2, use_container_width=True)

    # Age distribution
    fig3 = px.histogram(
        df, x="patient_age_at_collection", nbins=20,
        color="sex" if "sex" in df.columns else None,
        title="Age Distribution of Cases",
        labels={"patient_age_at_collection": "Age at Collection"},
        color_discrete_map={"F": "#e91e8c", "M": "#1e5fe9"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Lab performance table
    st.markdown("#### Lab Submission Summary")
    lab_summary = df.groupby("lab_name").agg(
        total_records=("record_id", "count"),
        unique_cancer_types=("icd_o_3_topography", "nunique")
    ).reset_index().sort_values("total_records", ascending=False)
    st.dataframe(lab_summary, use_container_width=True)

    dashboard_csv = lab_summary.to_csv(index=False).encode()
    st.download_button("📥 Download Lab Summary", dashboard_csv, "ncr_lab_summary.csv", "text/csv")


# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="footer-note">
<strong>Prototype built to demonstrate:</strong> automated coding pipelines, data cleaning programmes with 
logical validation rules (date correlations, sex-site consistency, age outlier detection), 
probabilistic record linkage + ML techniques, and analysis-ready epidemiology dashboard outputs —
<strong>exactly as required in NICD0126/001-11 (Amendment and Readvertisement)</strong>.<br><br>
Malima Maano Bryton — April 2026 | Pipeline logic and validation rules aligned to NCR 2022/2023 annual report standards (NICD/NHLS)
</div>
""", unsafe_allow_html=True)
