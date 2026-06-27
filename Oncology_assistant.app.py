# ==============================================================================
# ONCO PRODUCTION APPLICATION ENGINE (app.py) - EXTENDED NUTRITION SYSTEM
# ==============================================================================
import json
import pandas as pd
import streamlit as st

# 1. Configuration of the Page Layout
st.set_page_config(
    page_title="ONCASIS - Clinical Care Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Optimized Resource Intake Cache Layer
#@st.cache_data
def load_application_resources():
    df_patients = pd.read_csv("data/onco_patients_clean.csv")
    with open("data/onco_lifestyle_master.json", "r") as file:
        lifestyle_db = json.load(file)
    return df_patients, lifestyle_db

try:
    df_patients, lifestyle_db = load_application_resources()
except Exception as e:
    st.error(f"⚠️ Storage Error: Could not load files from the 'data/' folder. Details: {e}")
    st.stop()

# 3. CLINICAL DISCLAIMER & WARNING (⚠️ MEDICO-LEGAL BOUNDARY)
st.warning(
    "⚠️ **LEGAL NOTICE / CLINICAL DISCLAIMER:** This application is a digital support tool "
    "intended solely for informational purposes and to assist healthcare professionals. "
    "The data, lifestyle suggestions, and pharmacological schemas displayed do not replace "
    "professional clinical judgment. **The attending medical specialist always retains absolute responsibility "
    "and the final decision-making authority** regarding patient diagnosis and treatment protocols."
)


# 4. Main Interface Header Banner
st.title("🩺 ONCASIS: Integrative Oncology Care Assistant")
st.subheader("Precision Pharmacotherapy, Prescriptive Nutrition, and Strength Training Protocol Mapping")
st.markdown("---")

# 5. SIDEBAR INPUT INTERFACE FORM (Clinician Entry Points)
st.sidebar.header("📥 Patient Clinical Profile")

# Injected CSS to target and differentiate the form submit button visually
st.markdown(
    """
    <style>
    /* Targeting the specific Streamlit form submit button inside the sidebar */
    div[data-testid="stSidebar"] button[data-testid="stFormSubmitButton"] {
        background-color: #00768H; /* Custom Clinical Teal/Blue background */
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: 1px solid #005F73 !important;
        width: 100% !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease in-out;
    }
    /* Hover effect to make it interactive when the clinician moves the cursor over it */
    div[data-testid="stSidebar"] button[data-testid="stFormSubmitButton"]:hover {
        background-color: #005F73 !important;
        border-color: #001219 !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar.form("patient_clinical_form"):
    # Demographics and Baseline Lifestyle
    age = st.slider("1. Patient Diagnosis Age:", min_value=18, max_value=100, value=55)
    sex = st.selectbox("2. Biological Sex:", options=["Female", "Male"])
    smoking_status = st.radio("3. Tobacco Smoking History:", options=["Never Smoked", "Current Smoker", "Former Smoker"])
    activity_level = st.selectbox("4. Current Physical Activity Baseline:", options=["Sedentary", "Moderate Active", "Highly Athletic"])
    
    # Primary Tumor Location Custom Intake Layer + "Others" Boundary
    raw_cancers = sorted(df_patients["cancer_type"].unique()) if "cancer_type" in df_patients.columns else []
    unique_cancers = raw_cancers + ["Others"]
    selected_cancer = st.selectbox("5. Primary Tumor Location (Cancer Type):", options=unique_cancers)
    
    # Dynamic Filtering for Pathologic Stage based on selected cancer type
    if selected_cancer != "Others" and "cancer_type" in df_patients.columns:
        cohort_data = df_patients[df_patients["cancer_type"] == selected_cancer]
        unique_stages = sorted(cohort_data["neoplasm_disease_stage_american_joint_committee_on_cancer_code"].unique()) if "neoplasm_disease_stage_american_joint_committee_on_cancer_code" in df_patients.columns else []
    else:
        unique_stages = ["Any Stage"]
    
    selected_stage = st.selectbox("6. Pathologic Stage Severity:", options=unique_stages)
    
    # Therapeutic History Array Custom Intake Layer + "Others" Boundary
    base_prior_options = [
        "None (Treatment-Naïve)", "None (Post-Resection Adjuvant)", "None (Treatment-Naïve / EGFR+)", "None (Primary Active Surveillance or ADT)", "None (Post-Surgical Baseline Resection)",
        "Prior Anthracycline/Taxane Neoadjuvant Therapy", "Prior Fluoropyrimidine (5-FU) Regimen", "Prior Platinum-Based Chemotherapy Resistance", "Prior Platinum-Based Chemotherapy Failure",
        "Prior Docetaxel Chemotherapy Failure", "Prior Immune Checkpoint Inhibitor Anti-PD1 Failure", "Prior or Post-Surgery Radiotherapy", "Prior Platinum-Based Chemotherapy (Platinum-Sensitive)",
        "Prior Platinum-Based Gemcitabine Chemotherapy", "Prior Fluoropyrimidine/Platinum First-Line Therapy", "Prior Sorafenib First-Line Systemic Therapy"
    ]
    prior_options_with_other = base_prior_options + ["Others"]
    selected_prior = st.selectbox("7. Longitudinal Therapeutic History:", options=prior_options_with_other)
    
    # Differentiated Submission Gatekeeper Button
    submit_button = st.form_submit_button(label="Generate Personalized Care Plan")

# 6. REACTIVE SYSTEM PROCESSING CORE & DATA RETRIEVAL
if submit_button:
    st.success(f"🚀 Care Plan generated successfully for a {age}-year-old {sex} patient.")
    
    matched_entry = None
    if selected_cancer != "Others":
        for entry in lifestyle_db:
            if entry["cancer_type"] == selected_cancer:
                matched_entry = entry
                break
                
    # 7. APP OUTPUT LAYER: TABBED SEGREGATED DASHBOARD LAYOUT
    tab_drugs, tab_diet, tab_gym, tab_stats = st.tabs([
        "💊 Medical Pharmacotherapy", 
        "🥦 Prescriptive Nutrition Guide", 
        "🏋️ Physical Rehabilitation Plan", 
        "📊 Historical Cohort Metrics"
    ])
    
    # TAB 1: Clinical Pharmacology Recommendation Cards
    with tab_drugs:
        st.markdown("### 🧬 Targeted Pharmacotherapy & Clinical Protocol")
        if selected_cancer == "Others" or selected_prior == "Others":
            st.warning("⚠️ **Notice:** Selecting clinical profiles categorized as 'Others' prevents the system from mapping an automated targeted drug line. Please refer to international standards such as ASCO / ESMO guidelines for atypical staging profiles.")
        elif matched_entry:
            st.info(f"**Recommended Treatment Lines:** {matched_entry['recommended_drugs']}")
            st.caption(f"**Evidence Guidelines Source:** *{matched_entry['scientific_source']}*")
        else:
            st.warning("⚠️ No matching targeted pharmacological protocol found for this configuration of staging and therapeutic history.")
        
    # TAB 2: Automated 3-Day Nutritionist Menu WITH HIGH-DENSITY FOOD TAXONOMY
    with tab_diet:
        st.subheader("📋 Patient Educational Guideline (Printable Nutritional Sheet)")
        st.success("💡 *Specialist Recommendation:* Maintaining an active lifestyle and well-balanced metabolic intake is key during therapy. Patients are highly advised to walk a minimum of 30 minutes daily at a moderate pace to combat cancer-related fatigue (CRF).")
        st.markdown("---")
        
        st.markdown("### 🥗 Precision Oncology Dietary Management")
        st.markdown("The following matrix classifies dietary groups based on clinical evidence to support cell repair and reduce systemic inflammation during active therapeutic cycles.")
        
        # Creating a dual column layout to show recommended vs restricted indexes side by side
        col_rec, col_rest = st.columns(2)
        
        if selected_cancer == "Others":
            with col_rec:
                st.info("#### 🟢 Highly Recommended Food Indexes")
                st.markdown("- **Recommended Foods:** High-fiber leafy vegetables, thoroughly cooked legumes, lean proteins, cold-water fish rich in Omega-3 fatty acids, and optimal hydration using water and herbal infusions.")
            with col_rest:
                st.error("#### 🔴 Restricted / Avoidance Food Indexes")
                st.markdown("- **Foods to Restrict:** Ultra-processed products, refined sugars, processed or undercooked red meats, and alcoholic beverages.")
        elif matched_entry:
            with col_rec:
                st.info("#### 🟢 Highly Recommended Food Indexes")
                st.markdown(matched_entry.get("recommended_foods", "General recommendations available in clinical summary."))
            with col_rest:
                st.error("#### 🔴 Restricted / Avoidance Food Indexes")
                st.markdown(matched_entry.get("restricted_foods", "General restrictions available in clinical summary."))
                
        st.markdown("---")
        st.markdown("### 🍽️ Sample 3-Day Menu Structure")
        if matched_entry and selected_cancer != "Others":
            st.markdown(matched_entry['three_day_nutrition_plan'])
        else:
            st.info("Please consult general oncology dietitian protocols for profiles flagged under atypical 'Others' parameters.")
        
    # TAB 3: Automated 3-Day Gym Workout Routine Split
    with tab_gym:
        st.subheader("📋 Patient Exercise & Rehabilitation Plan (Printable Sheet)")
        st.success("💡 *Specialist Recommendation:* Tailored resistance exercise protects lean skeletal muscle mass (combating sarcopenia) and enhances immune function response. Perform all movements controlling your breathing markers and rest as needed.")
        st.markdown("---")
        
        if selected_cancer == "Others":
            st.markdown("### 🏋️ General Physical Activity Parameters")
            st.markdown("- Lightweight cardiovascular training (such as walking or light stationary cycling) calibrated to daily patient energy limits.")
            st.markdown("- Active joint mobility movements and gentle stretching drills to preserve structural range of motion.")
            st.markdown("- Avoid tracking maximum loads or performing exhaustive workouts that could disrupt immune baselines.")
        elif matched_entry:
            st.markdown(matched_entry['three_day_workout_routine'])
            
# TAB 4: Cohort Big Data Metrics & International Guidelines Directory
    with tab_stats:
        st.markdown("### 📊 Historical Real-World Patient Insights")
        st.markdown("This section analyzes historical outcomes for patients with identical matching criteria inside our integrated dataset.")
        
        if selected_cancer != "Others" and "cancer_type" in df_patients.columns:
            cohort_subset = df_patients[df_patients["cancer_type"] == selected_cancer]
            
            # Dynamically apply sub-filtering based on the clinician's selected stage
            if selected_stage in cohort_subset["neoplasm_disease_stage_american_joint_committee_on_cancer_code"].values:
                cohort_subset = cohort_subset[cohort_subset["neoplasm_disease_stage_american_joint_committee_on_cancer_code"] == selected_stage]
            
            st.markdown("---")
            # Rendering the high-density analytical summary metrics cards
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Total Co-occurring Cohort Cases Tracked ($N$):", 
                    value=f"{len(cohort_subset):,}"
                )
            with col2:
                if "overall_survival_months" in cohort_subset.columns and len(cohort_subset) > 0:
                    avg_survival = cohort_subset["overall_survival_months"].mean()
                    st.metric(
                        label="Historical Average Survival Time:", 
                        value=f"{avg_survival:.1f} months"
                    )
                else:
                    st.metric(
                        label="Historical Average Survival Time:", 
                        value="N/A"
                    )
            st.markdown("---")
            st.caption("ℹ️ *Data Source Registry:* Metrics extracted from the indexed TCGA PanCancer Clinical Data Cluster.")
            
            # ==============================================================================
            # NEW: INTERNATIONAL CLINICAL GUIDELINES DIRECTORY FOR ONCOLOGISTS
            # ==============================================================================
            st.markdown("### 🌐 Evidence-Based International Oncology Guidelines")
            st.markdown(f"Direct clinical access paths to standard reference manuals corresponding to **{selected_cancer}** profiles:")
            
            # Dynamic link generator based on clinical sub-categories
            col_guideline1, col_guideline2 = st.columns(2)
            
            with col_guideline1:
                st.markdown("#### 🇺🇸 United States Reference Frameworks")
                st.markdown("- **NCCN Guidelines:** [National Comprehensive Cancer Network](https://www.nccn.org/guidelines)")
                st.markdown("- **ASCO Portal:** [American Society of Clinical Oncology](https://www.asco.org/practice-patients/guidelines)")
                
                # Dynamic targeted recommendation help cards
                if selected_cancer == "Breast Cancer":
                    st.info("💡 *Quick Link:* Check the latest ASCO/NCCN Breast Cancer Biomarker Updates.")
                elif selected_cancer in ["Colorectal Cancer", "Stomach Cancer", "Pancreatic Cancer"]:
                    st.info("💡 *Quick Link:* Access NCCN Guidelines for Gastrointestinal Carcinomas.")
                    
            with col_guideline2:
                st.markdown("#### 🇪🇺 European & National Reference Frameworks")
                st.markdown("- **ESMO Library:** [European Society for Medical Oncology](https://www.esmo.org/guidelines)")
                st.markdown("- **SEOM Portals:** [Sociedad Española de Oncología Médica](https://seom.org/guias-clinicas-seom)")
                
                if selected_cancer in ["Lung Adenocarcinoma", "Lung Squamous Cell Carcinoma"]:
                    st.info("💡 *Quick Link:* Open ESMO Consensus Principles on Thoracic Malignancies.")
                    
        else:
            st.info("No TCGA population baseline records are available for the clinical selection 'Others'.")
            
            st.markdown("---")
            st.markdown("### 🌐 General Comprehensive Oncology Registries")
            st.markdown("For atypical or rare pathology patterns flagged under 'Others', please consult the global indices directly:")
            st.markdown("- **NCCN Guidelines Global Index:** [NCCN Official Access](https://www.nccn.org/guidelines)")
            st.markdown("- **ESMO Clinical Guidelines Index:** [ESMO Official Portal](https://www.esmo.org/guidelines)")
            st.markdown("- **SEOM Clinical Guidelines Index:** [SEOM Clinical Guidelines](https://seom.org/guias-clinicas-seom)")


else:
    # Baseline welcoming card before calculation triggers
    st.info("💡 Welcome to ONCASIS. Please configure the patient baseline variables inside the left sidebar panel and click 'Generate Personalized Care Plan' to fetch the multi-line medical protocols.")