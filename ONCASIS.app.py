# ==============================================================================
# ONCASIS PRODUCTION APPLICATION ENGINE (app.py)
# ==============================================================================
import streamlit as st
import pandas as pd
from queries import (
    verify_user_login, 
    register_new_user, 
    fetch_relational_patient_data, 
    fetch_lifestyle_master,
    fetch_advanced_cancer_stats
)

# 1. Configuration of the Page Layout
st.set_page_config(
    page_title="ONCASIS - Clinical Care Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Session State Initialization (The Security Gate)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""

# ==============================================================================
# 3. AUTHENTICATION UI GATEWAY
# ==============================================================================
def render_auth_gateway():
    """Renders the login and registration screens."""
    st.title("🩺 ONCASIS: Clinical Access Portal")
    st.markdown("Please log in with your clinician credentials to access the analytics engine.")
    
    tab_login, tab_register = st.tabs(["🔐 System Login", "📝 Register New Clinician"])
    
    with tab_login:
        with st.form("login_form"):
            login_user = st.text_input("Clinician Username")
            login_pwd = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Access ONCASIS")
            
            if submit_login:
                if verify_user_login(login_user, login_pwd):
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = login_user
                    st.success("Authentication successful! Loading clinical environment...")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please verify your username and password.")
                    
    with tab_register:
        with st.form("register_form"):
            reg_user = st.text_input("New Username")
            reg_email = st.text_input("Institutional Email")
            reg_pwd = st.text_input("Secure Password", type="password")
            submit_reg = st.form_submit_button("Register Account")
            
            if submit_reg:
                if register_new_user(reg_user, reg_email, reg_pwd):
                    st.success("Account created successfully! You may now log in via the Login tab.")
                else:
                    st.error("Registration failed. Username or email may already be in use.")

# ==============================================================================
# 4. MAIN APPLICATION ENGINE (PROTECTED ROUTE)
# ==============================================================================
def render_main_application():
    """Renders the core clinical assistant with all oncology modules."""
    
    # Active Session Indicator & Logout Button
    st.sidebar.success(f"👨‍⚕️ Dr. {st.session_state['current_user']} - Session Active")
    if st.sidebar.button("Secure Logout"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.rerun()
        
    st.sidebar.markdown("---")

    # CLINICAL DISCLAIMER & WARNING
    st.warning(
        "⚠️ **LEGAL NOTICE / CLINICAL DISCLAIMER:** This application is a digital support tool "
        "intended solely for informational purposes and to assist healthcare professionals. "
        "The data, lifestyle suggestions, and pharmacological schemas displayed do not replace "
        "professional clinical judgment. **The attending medical specialist always retains absolute responsibility.**"
    )

    st.title("🩺 ONCASIS: Integrative Oncology Care Assistant")
    st.subheader("Precision Pharmacotherapy, Prescriptive Nutrition, and Strength Training Protocol Mapping")
    st.markdown("---")

    # Fetch foundational data from the cloud
    try:
        df_patients = fetch_relational_patient_data()
        lifestyle_db = fetch_lifestyle_master().to_dict(orient="records")
    except Exception as e:
        st.error(f"⚠️ Database Connection Error: {e}")
        st.stop()

    # ==============================================================================
    # SIDEBAR INPUT INTERFACE FORM WITH CUSTOM BUTTON STYLING
    # ==============================================================================
    st.sidebar.header("📥 Patient Clinical Profile")

    st.markdown(
        """
        <style>
        div[data-testid="stSidebar"] button[data-testid="stFormSubmitButton"] {
            background-color: #00768H;
            color: white !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            border: 1px solid #005F73 !important;
            width: 100% !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.3s ease in-out;
        }
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
        age = st.slider("1. Patient Diagnosis Age:", min_value=18, max_value=100, value=55)
        sex = st.selectbox("2. Biological Sex:", options=["Female", "Male"])
        smoking_status = st.radio("3. Tobacco Smoking History:", options=["Never Smoked", "Current Smoker", "Former Smoker"])
        activity_level = st.selectbox("4. Current Physical Activity Baseline:", options=["Sedentary", "Moderate Active", "Highly Athletic"])
        
        raw_cancers = sorted(df_patients["cancer_type"].dropna().unique()) if not df_patients.empty else []
        unique_cancers = raw_cancers + ["Others"]
        selected_cancer = st.selectbox("5. Primary Tumor Location (Cancer Type):", options=unique_cancers)
        
        if selected_cancer != "Others" and not df_patients.empty:
            cohort_data = df_patients[df_patients["cancer_type"] == selected_cancer]
            unique_stages = sorted(cohort_data["neoplasm_disease_stage_american_joint_committee_on_cancer_code"].dropna().unique())
        else:
            unique_stages = ["Any Stage"]
        
        selected_stage = st.selectbox("6. Pathologic Stage Severity:", options=unique_stages)
        
        base_prior_options = [
            "None (Treatment-Naïve)", "None (Post-Resection Adjuvant)", "Prior Anthracycline/Taxane Neoadjuvant Therapy", 
            "Prior Fluoropyrimidine (5-FU) Regimen", "Prior Platinum-Based Chemotherapy Resistance", "Prior or Post-Surgery Radiotherapy"
        ]
        prior_options_with_other = base_prior_options + ["Others"]
        selected_prior = st.selectbox("7. Longitudinal Therapeutic History:", options=prior_options_with_other)
        
        submit_button = st.form_submit_button(label="Generate Personalized Care Plan")

    # ==============================================================================
    # MAIN DISPLAY ENGINE
    # ==============================================================================
    if submit_button:
        # Core Clinical Logic Matcher
        matched_protocol = next(
            (item for item in lifestyle_db if item.get("cancer_type") == selected_cancer), 
            None
        )
        
        if not matched_protocol and selected_cancer != "Others" and len(lifestyle_db) > 0:
            matched_protocol = lifestyle_db[0]
            
        tab_clinical, tab_nutrition, tab_fitness, tab_stats = st.tabs([
            "📋 Pathological Overview", "🍏 Precision Nutrition", "🏋️ Functional Fitness", "📊 Advanced Analytics & Guidelines"
        ])
        
        # TAB 1: Clinical Summary
        with tab_clinical:
            st.markdown("### 📋 Patient Clinical Vector Summary")
            st.info(f"**Demographics:** {age} years old | {sex} | {smoking_status} | {activity_level}")
            st.error(f"**Primary Diagnosis:** {selected_cancer} (Stage: {selected_stage})")
            st.warning(f"**Therapeutic History:** {selected_prior}")
            
            st.markdown("---")
            if matched_protocol:
                st.markdown("### 💊 Evidence-Based Pharmacological Trajectories")
                st.success(f"**Standard Protocols:** {matched_protocol.get('recommended_drugs', 'Requires personalized assessment.')}")
                st.caption(f"📚 *Literature Source:* {matched_protocol.get('scientific_source', 'Internal Medical Database')}")
            else:
                st.info("Please consult international guidelines for 'Others' category.")

        # TAB 2: Nutrition
        with tab_nutrition:
            if matched_protocol:
                col_rec, col_rest = st.columns(2)
                with col_rec:
                    st.markdown("### ✅ Therapeutic Nutritional Targets")
                    st.success(matched_protocol.get("recommended_foods", "General balanced diet recommended."))
                with col_rest:
                    st.markdown("### ⛔ Absolute Dietary Restrictions")
                    st.error(matched_protocol.get("restricted_foods", "Limit processed foods and alcohol."))
                st.markdown("---")
                st.markdown(matched_protocol.get("three_day_nutrition_plan", "No specific plan available."))
            else:
                st.warning("No specific nutritional matrices exist for this rare selection.")

        # TAB 3: Fitness
        with tab_fitness:
            if matched_protocol:
                st.markdown(matched_protocol.get("three_day_workout_routine", "Consult with a physical therapist."))
            else:
                st.warning("No specific strength protocols exist for this rare selection.")

        # TAB 4: SQL Analytics & International Guidelines
        with tab_stats:
            st.markdown(f"### 📈 Real-World Data Analytics for {selected_cancer}")
            st.markdown("Metrics calculated in real-time from our integrated PostgreSQL cloud architecture.")
            
            if selected_cancer != "Others":
                # Fetch SQL advanced metrics
                df_age, df_risk = fetch_advanced_cancer_stats(selected_cancer)
                
                col_sq1, col_sq2 = st.columns(2)
                with col_sq1:
                    st.markdown("#### 👥 Demographics: Average Age by Sex")
                    if not df_age.empty:
                        st.dataframe(df_age, use_container_width=True, hide_index=True)
                    else:
                        st.warning("Insufficient demographic data for this cohort.")
                        
                with col_sq2:
                    st.markdown("#### 🚬 Risk Factors: Smoking vs. Survival (Months)")
                    if not df_risk.empty:
                        st.dataframe(df_risk, use_container_width=True, hide_index=True)
                    else:
                        st.warning("Insufficient risk factor data for this cohort.")
                
                st.markdown("---")
                
                # Guidelines Directory
                st.markdown("### 🌐 Evidence-Based International Oncology Guidelines")
                col_guideline1, col_guideline2 = st.columns(2)
                
                with col_guideline1:
                    st.markdown("#### 🇺🇸 United States Frameworks")
                    st.markdown("- **NCCN Guidelines:** [National Comprehensive Cancer Network](https://www.nccn.org/guidelines)")
                    st.markdown("- **ASCO Portal:** [American Society of Clinical Oncology](https://www.asco.org/practice-patients/guidelines)")
                        
                with col_guideline2:
                    st.markdown("#### 🇪🇺 European Frameworks")
                    st.markdown("- **ESMO Library:** [European Society for Medical Oncology](https://www.esmo.org/guidelines)")
                    st.markdown("- **SEOM Portals:** [Sociedad Española de Oncología Médica](https://seom.org/guias-clinicas-seom)")
            else:
                st.info("No TCGA population baseline records are available for the clinical selection 'Others'.")

    else:
        st.info("💡 Welcome to the ONCASIS secure portal. Please configure the patient baseline in the sidebar and click 'Generate'.")

# ==============================================================================
# 5. ROUTING LOGIC (THE SWITCH)
# ==============================================================================
if not st.session_state["logged_in"]:
    render_auth_gateway()
else:
    render_main_application()