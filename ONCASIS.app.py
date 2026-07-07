# ==============================================================================
# ONCASIS PRODUCTION APPLICATION ENGINE (app.py)
# ==============================================================================
import streamlit as st
import pandas as pd
from queries import (
    verify_user_login, 
    register_new_user, 
    fetch_relational_patient_data,  # <--- ¡AQUÍ ESTÁ LA QUE FALTABA!
    fetch_lifestyle_master,
    fetch_advanced_cancer_stats,
    fetch_pharmacology_protocols,
    fetch_top_genotypes,
    init_connection
)
from sqlalchemy import text

st.set_page_config(page_title="ONCASIS", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""

# ==============================================================================
# AUTHENTICATION UI GATEWAY
# ==============================================================================
def render_auth_gateway():
    st.title("🩺 ONCASIS: Clinical Access Portal")
    tab_login, tab_register = st.tabs(["🔐 System Login", "📝 Register New Clinician"])
    
    with tab_login:
        with st.form("login_form"):
            login_user = st.text_input("Username")
            login_pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Access ONCASIS"):
                if verify_user_login(login_user, login_pwd):
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = login_user
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
                    
    with tab_register:
        with st.form("register_form"):
            reg_user = st.text_input("New Username")
            reg_email = st.text_input("Institutional Email")
            reg_pwd = st.text_input("Secure Password", type="password")
            if st.form_submit_button("Register Account"):
                if register_new_user(reg_user, reg_email, reg_pwd):
                    st.success("Account created! You may now log in.")
                else:
                    st.error("Registration failed. Username may already be in use.")


# ==============================================================================
# MAIN APPLICATION ENGINE
# ==============================================================================
def render_main_application():
    st.sidebar.success(f"👨‍⚕️ Dr. {st.session_state['current_user']} - Session Active")
    if st.sidebar.button("Secure Logout"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    st.title("🩺 ONCASIS: Integrative Oncology Care Assistant")
    st.warning("⚠️ **MEDICAL DISCLAIMER:** ONCASIS is an AI-powered clinical decision support tool. The pharmacological, nutritional, and fitness trajectories generated are recommendations based on statistical guidelines and must not substitute professional medical judgment, direct clinical diagnosis, or multidisciplinary tumor board consensus.")
    st.markdown("---")

    # Fetch ALL foundational data from Cloud
    try:
        df_patients = fetch_relational_patient_data()
        lifestyle_db = fetch_lifestyle_master().to_dict(orient="records")
        pharma_db = fetch_pharmacology_protocols().to_dict(orient="records")
    except Exception as e:
        st.error(f"⚠️ Database Connection Error: {e}")
        st.stop()

    # Dynamic Extraction for Cancers & Sex
    unique_cancers = sorted(df_patients["cancer_type"].dropna().unique().tolist())
    unique_sex = sorted(df_patients["sex"].dropna().unique().tolist())
    
    # STATIC OPTIONS (Because the TCGA DB doesn't have real lifestyle data)
    smoking_options = ["Never Smoked", "Current Smoker", "Former Smoker"]
    activity_options = ["Sedentary", "Moderate Active", "Highly Athletic"]
    prior_options = [
        "None (Treatment-Naïve)", "None (Post-Resection Adjuvant)", 
        "Prior Anthracycline/Taxane Neoadjuvant Therapy", 
        "Prior Fluoropyrimidine (5-FU) Regimen", 
        "Prior Platinum-Based Chemotherapy Resistance", 
        "Prior or Post-Surgery Radiotherapy", "Others"
    ]
    
    st.sidebar.header("📥 Patient Clinical Profile")
    
    with st.sidebar.form("patient_clinical_form"):
        age = st.slider("1. Patient Diagnosis Age:", min_value=18, max_value=100, value=55)
        sex = st.selectbox("2. Biological Sex:", options=unique_sex)
        smoking_status = st.selectbox("3. Tobacco Smoking History:", options=smoking_options)
        activity_level = st.selectbox("4. Current Physical Activity Baseline:", options=activity_options)
        selected_cancer = st.selectbox("5. Primary Tumor Location:", options=unique_cancers)
        
        # Filter stages dynamically
        cohort_data = df_patients[df_patients["cancer_type"] == selected_cancer]
        unique_stages = sorted(cohort_data["neoplasm_disease_stage_american_joint_committee_on_cancer_code"].dropna().unique().tolist())
        selected_stage = st.selectbox("6. Pathologic Stage Severity:", options=unique_stages if unique_stages else ["Any Stage"])
        
        # Restored Prior Treatment Dropdown
        selected_prior = st.selectbox("7. Longitudinal Therapeutic History:", options=prior_options)
        
        submit_button = st.form_submit_button(label="Generate Personalized Care Plan")

    if submit_button:
        # 1. Clean inputs for robust string matching
        safe_cancer_name = str(selected_cancer).strip().lower()
        safe_prior = str(selected_prior).strip().lower()

        # 2. MATCH LIFESTYLE: Extract customized Nutrition & Fitness from the JSON Database
        matched_lifestyle = next(
            (item for item in lifestyle_db if str(item.get("cancer_type", "")).strip().lower() == safe_cancer_name), 
            None
        )

        # 3. MATCH PHARMACOLOGY: Dynamically query the Neon 'treatment_protocols' table
        # First, filter the protocols by the selected cancer type
        pharma_options_for_cancer = [
            item for item in pharma_db if str(item.get("cancer_type", "")).strip().lower() == safe_cancer_name
        ]
        
        # Second, filter by the precise longitudinal therapeutic history (Prior Treatment)
        matched_pharma = next(
            (item for item in pharma_options_for_cancer if str(item.get("prior_treatment_status", "")).strip().lower() == safe_prior), 
            None
        )
        
        # 4. SAFETY FALLBACK: If the CSV doesn't have an exact match for that specific prior treatment combination,
        # fallback to the first protocol available for that cancer cohort so the screen doesn't break.
        if not matched_pharma and pharma_options_for_cancer:
            matched_pharma = pharma_options_for_cancer[0]

        # Define tabs layout
      
        tab_clinical, tab_pharma, tab_nutrition, tab_fitness, tab_stats = st.tabs([
            "📋 Pathological Overview", "💊 Pharmacology", "🍏 Precision Nutrition", "🏋️ Functional Fitness", "📊 SQL Analytics"
        ])
        
        # TAB 1: Clinical
        with tab_clinical:
            st.markdown("### 📋 Patient Clinical Vector Summary")
            st.info(f"**Demographics:** {age} years old | {sex} | {smoking_status} | {activity_level}")
            st.error(f"**Primary Diagnosis:** {selected_cancer} (Stage: {selected_stage})")
            st.warning(f"**Therapeutic History:** {selected_prior}")
            
        # TAB 2: Pharmacology
        with tab_pharma:
            st.markdown("### 💊 Evidence-Based Pharmacological Trajectories")
            if matched_pharma:
                # Solo mostramos los fármacos y la fuente científica
                st.success(f"**Recommended Drugs:** {matched_pharma.get('recommended_drugs', 'No data available.')}")
                st.caption(f"📚 *Scientific Source:* {matched_pharma.get('scientific_source', 'Internal Database')}")
            else:
                st.info("No specific pharmacology protocol found for this cohort in the database.")

        # TAB 3: Nutrition (Restored 2-Column JSON Layout)
        with tab_nutrition:
            if matched_lifestyle:
                col_rec, col_rest = st.columns(2)
                with col_rec:
                    st.markdown("### ✅ Therapeutic Nutritional Targets")
                    st.success(matched_lifestyle.get("recommended_foods", "Data missing."))
                with col_rest:
                    st.markdown("### ⛔ Absolute Dietary Restrictions")
                    st.error(matched_lifestyle.get("restricted_foods", "Data missing."))
                
                st.markdown("---")
                st.markdown("### 📅 Prescriptive 3-Day Nutrition Schema")
                st.markdown(matched_lifestyle.get("three_day_nutrition_plan", "No detailed plan available."))
            else:
                st.warning("⚠️ Nutrition matrices missing for this specific cohort in the Lifestyle Database.")

        # TAB 4: Fitness (Restored JSON Layout)
        with tab_fitness:
            if matched_lifestyle:
                st.markdown("### 🏋️ Functional Exercise Protocols")
                st.markdown(matched_lifestyle.get("three_day_workout_routine", "Consult physical therapist."))
            else:
                st.warning("⚠️ Fitness matrices missing for this specific cohort in the Lifestyle Database.")

        # TAB 5: SQL Analytics & Clinical Guidelines (Todo agrupado)
        with tab_stats:
            st.markdown(f"### 📈 Real-World Data Analytics for {selected_cancer}")
            df_age, df_risk = fetch_advanced_cancer_stats(selected_cancer)
            df_genotypes = fetch_top_genotypes(selected_cancer)
            
            # --- SECCIÓN 1: Demografía y Riesgos ---
            col_sq1, col_sq2 = st.columns(2)
            with col_sq1:
                st.markdown("#### 👥 Average Age by Sex")
                if not df_age.empty:
                    st.dataframe(df_age, use_container_width=True, hide_index=True)
                else:
                    st.warning("No demographic data available.")
                    
            with col_sq2:
                st.markdown("#### 🚬 Smoking vs. Survival (Months)")
                if not df_risk.empty:
                    st.dataframe(df_risk, use_container_width=True, hide_index=True)
                else:
                    st.warning("No risk factor data. (TCGA Database lacks smoking metrics for this cohort).")
            
            st.markdown("---")
            
            # --- SECCIÓN 2: Genotipos Moleculares ---
            st.markdown("#### 🧬 Top 5 Molecular Genotypes / Subtypes in Cohort")
            if not df_genotypes.empty:
                st.dataframe(df_genotypes, use_container_width=True, hide_index=True)
            else:
                st.info("No specific molecular subtype data available for this cohort in the current database.")
                
            st.markdown("---")
            
            # --- SECCIÓN 3: Guías Clínicas Institucionales (Tu código original) ---
            st.markdown("### 📋 Institutional Clinical Guidelines")
            
            if selected_cancer != "Others":
                col_guideline1, col_guideline2 = st.columns(2)
                
                with col_guideline1:
                    st.markdown("#### 🇺🇸 United States Reference Frameworks")
                    st.markdown("- **NCCN Guidelines:** [National Comprehensive Cancer Network](https://www.nccn.org/guidelines)")
                    st.markdown("- **ASCO Portal:** [American Society of Clinical Oncology](https://www.asco.org/practice-patients/guidelines)")
                    
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
        st.info("💡 Welcome to ONCASIS. Configure the patient baseline in the sidebar and click 'Generate Personalized Care Plan'.")

# ==============================================================================
# ROUTING LOGIC
# ==============================================================================
if not st.session_state["logged_in"]:
    render_auth_gateway()
else:
    render_main_application()