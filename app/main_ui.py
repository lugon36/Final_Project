# app/main_ui.py
import streamlit as st
import plotly.express as px
from app.queries import (
    fetch_relational_patient_data, fetch_lifestyle_master,
    fetch_pharmacology_protocols, fetch_advanced_cancer_stats, fetch_top_genotypes
)

def render_main_application():
    st.sidebar.success(f"👨‍⚕️ Dr. {st.session_state['current_user']} - Session Active")
    if st.sidebar.button("Secure Logout"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    st.title("🩺 ONCASIS: Integrative Oncology Care Assistant")
    st.warning("⚠️ **MEDICAL DISCLAIMER:** ONCASIS is an AI-powered clinical decision support tool. Recommendations must not substitute professional medical judgment.")
    st.markdown("---")

    # 1. Fetch ALL foundational data
    try:
        df_patients = fetch_relational_patient_data()
        lifestyle_db = fetch_lifestyle_master().to_dict(orient="records")
        pharma_db = fetch_pharmacology_protocols().to_dict(orient="records")
    except Exception as e:
        st.error(f"⚠️ Database Connection Error: {e}")
        st.stop()

    # 2. Dynamic UI Options
    # Usando dropna() nos aseguramos de que solo cargue los 15 cánceres oficiales de la BD
    unique_cancers = sorted(df_patients["cancer_type"].dropna().unique().tolist())
    unique_sex = sorted(df_patients["sex"].dropna().unique().tolist())
    
    smoking_options = ["Never Smoked", "Current Smoker", "Former Smoker"]
    activity_options = ["Sedentary", "Moderate Active", "Highly Athletic"]
    prior_options = [
        "None (Treatment-Naïve)", "None (Post-Resection Adjuvant)", 
        "Prior Anthracycline/Taxane Neoadjuvant Therapy", 
        "Prior Fluoropyrimidine (5-FU) Regimen", 
        "Prior Platinum-Based Chemotherapy Resistance", 
        "None or Post-Surgery Radiotherapy", "Others"
    ]
    
    # 3. Sidebar Form
    st.sidebar.header("📥 Patient Clinical Profile")
    with st.sidebar.form("patient_clinical_form"):
        age = st.slider("1. Patient Diagnosis Age:", min_value=18, max_value=100, value=55)
        sex = st.selectbox("2. Biological Sex:", options=unique_sex)
        smoking_status = st.selectbox("3. Tobacco Smoking History:", options=smoking_options)
        activity_level = st.selectbox("4. Current Physical Activity Baseline:", options=activity_options)
        selected_cancer = st.selectbox("5. Primary Tumor Location:", options=unique_cancers)
        
        cohort_data = df_patients[df_patients["cancer_type"] == selected_cancer]
        unique_stages = sorted(cohort_data["neoplasm_disease_stage_american_joint_committee_on_cancer_code"].dropna().unique().tolist())
        selected_stage = st.selectbox("6. Pathologic Stage Severity:", options=unique_stages if unique_stages else ["Any Stage"])
        selected_prior = st.selectbox("7. Longitudinal Therapeutic History:", options=prior_options)
        
        submit_button = st.form_submit_button(label="Generate Personalized Care Plan")

    if submit_button:
        safe_cancer_name = str(selected_cancer).strip().lower()
        safe_prior = str(selected_prior).strip().lower()

        # Match lifestyle & pharma
        matched_lifestyle = next((item for item in lifestyle_db if str(item.get("cancer_type", "")).strip().lower() == safe_cancer_name), None)
        pharma_options = [item for item in pharma_db if str(item.get("cancer_type", "")).strip().lower() == safe_cancer_name]
        matched_pharma = next((item for item in pharma_options if str(item.get("prior_treatment_status", "")).strip().lower() == safe_prior), None)
        
        if not matched_pharma and pharma_options:
            matched_pharma = pharma_options[0]

        # Tabs Layout
        tab_clinical, tab_pharma, tab_nutrition, tab_fitness, tab_stats = st.tabs([
            "📋 Overview", "💊 Pharmacology", "🍏 Nutrition", "🏋️ Fitness", "📊 SQL Analytics"
        ])
        
        with tab_clinical:
            st.markdown("### 📋 Patient Clinical Vector Summary")
            st.info(f"**Demographics:** {age} years old | {sex} | {smoking_status} | {activity_level}")
            st.error(f"**Primary Diagnosis:** {selected_cancer} (Stage: {selected_stage})")
            st.warning(f"**Therapeutic History:** {selected_prior}")
            
        with tab_pharma:
            st.markdown("### 💊 Evidence-Based Pharmacological Trajectories")
            if matched_pharma:
                st.success(f"**Recommended Drugs:** {matched_pharma.get('recommended_drugs', 'No data available.')}")
                st.caption(f"📚 *Scientific Source:* {matched_pharma.get('scientific_source', 'Internal Database')}")
            else:
                st.info("No specific pharmacology protocol found.")

        with tab_nutrition:
            if matched_lifestyle:
                col_rec, col_rest = st.columns(2)
                with col_rec:
                    st.markdown("### ✅ Therapeutic Nutritional Targets")
                    st.success(matched_lifestyle.get("recommended_foods", "Data missing."))
                with col_rest:
                    st.markdown("### ⛔ Absolute Dietary Restrictions")
                    st.error(matched_lifestyle.get("restricted_foods", "Data missing."))
                st.markdown("### 📅 Prescriptive 3-Day Nutrition Schema")
                st.markdown(matched_lifestyle.get("three_day_nutrition_plan", "No plan available."))
            else:
                st.warning("⚠️ Nutrition matrices missing for this cohort.")

        with tab_fitness:
            if matched_lifestyle:
                st.markdown("### 🏋️ Functional Exercise Protocols")
                st.markdown(matched_lifestyle.get("three_day_workout_routine", "Consult physical therapist."))
            else:
                st.warning("⚠️ Fitness matrices missing for this cohort.")

        # ==========================================
        # TAB 5: ADVANCED SQL VISUALIZATIONS (PLOTLY)
        # ==========================================
        with tab_stats:
            st.markdown(f"### 📈 Real-World Data Analytics for {selected_cancer}")
            df_age, df_risk = fetch_advanced_cancer_stats(selected_cancer)
            df_genotypes = fetch_top_genotypes(selected_cancer)
            
            col_sq1, col_sq2 = st.columns(2)
            
            with col_sq1:
                st.markdown("#### 👥 Gender Distribution")
                if not df_age.empty:
                    # Pie chart for sex distribution
                    fig_pie = px.pie(df_age, values='patient_count', names='sex', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.warning("No demographic data available.")
                    
            with col_sq2:
                st.markdown("#### 🚬 Smoking vs. Survival (Months)")
                if not df_risk.empty:
                    # Bar chart for survival vs smoking
                    fig_bar = px.bar(df_risk, x='smoking_status', y='avg_survival', color='smoking_status', text_auto=True)
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.warning("No risk factor data available.")
            
            st.markdown("---")
            st.markdown("#### 🧬 Top 5 Molecular Genotypes in Cohort")
            if not df_genotypes.empty:
                # Horizontal bar chart for mutations
                fig_geno = px.bar(df_genotypes, x='Patient Count', y='Molecular Subtype / Genotype', orientation='h', color='Patient Count', color_continuous_scale='Blues')
                fig_geno.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_geno, use_container_width=True)
            else:
                st.info("No specific molecular subtype data available.")
    else:
        st.info("💡 Configure the patient baseline in the sidebar and click 'Generate Personalized Care Plan'.")