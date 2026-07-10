import pandas as pd
import streamlit as st
import plotly.express as px
from queries import (
    fetch_relational_patient_data, 
    fetch_lifestyle_master, 
    fetch_nhanes_lifestyle_stats,
    fetch_pharmacology_protocols, 
    fetch_advanced_cancer_stats, 
    fetch_top_genotypes, 
    fetch_nhanes_sedentary_stats, 
    fetch_survival_by_stage,
)

def render_main_application():
    st.sidebar.success(f"👨‍⚕️ Dr. {st.session_state['current_user']} - Session Active")
    if st.sidebar.button("Secure Logout"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    st.title("🩺 ONCASIS: Integrative Oncology Care Assistant")
    st.warning(
    "⚠️ **LEGAL NOTICE / CLINICAL DISCLAIMER:** This application is a digital support tool "
    "intended solely for informational purposes and to assist healthcare professionals. "
    "The data, lifestyle suggestions, and pharmacological schemas displayed do not replace "
    "professional clinical judgment. **The attending medical specialist always retains absolute responsibility "
    "and the final decision-making authority** regarding patient diagnosis and treatment protocols."
)
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
                    fig_pie = px.pie(df_age, values='patient_count', names='sex', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                    st.plotly_chart(fig_pie, use_container_width=True)
            with col_sq2:
                st.markdown("#### ⏳ Clinical Survival")
                df_kpi = fetch_survival_by_stage(selected_cancer, selected_stage)
                
                if not df_kpi.empty and df_kpi['avg_survival'][0] is not None:
                    avg_val = df_kpi['avg_survival'][0]
                    st.metric(label=f"Avg. Survival for {selected_stage}", value=f"{avg_val:.1f} months")
                    st.caption(f"Based on historical data for {selected_cancer}")
                else:
                    st.info("No sufficient data for this specific clinical combination.")
            
        
            st.markdown("---")
            st.markdown("### 🌍 Population-Level Lifestyle & Survival Insights (NHANES)")
            
      
            df_nhanes = fetch_nhanes_lifestyle_stats()
            if not df_nhanes.empty:
                fig_nhanes = px.bar(
                    df_nhanes, x='smoking_history', y='avg_survival', color='smoking_history',
                    title="Impact of Smoking History (100+ cigarettes) on Survival",
                    labels={'smoking_history': 'Smoking History', 'avg_survival': 'Avg. Survival (Months)'},
                    color_discrete_map={'Ever Smoked': '#EF553B', 'Never Smoked': '#00CC96'}
                )
                fig_nhanes.update_layout(showlegend=False)
                st.plotly_chart(fig_nhanes, use_container_width=True)
            
   
            st.markdown("### 🏃‍♂️ Impact of Sedentary Behavior")
            df_sed = fetch_nhanes_sedentary_stats()
            if not df_sed.empty:
                df_sed['survival_months'] = pd.to_numeric(df_sed['survival_months'], errors='coerce')
                df_sed['sedentary_minutes_day'] = pd.to_numeric(df_sed['sedentary_minutes_day'], errors='coerce')
                bins = [0, 300, 600, 1440]
                labels = ['Low (<300m)', 'Medium (300-600m)', 'High (>600m)']
                df_sed['sedentary_bins'] = pd.cut(df_sed['sedentary_minutes_day'], bins=bins, labels=labels)
                df_sed_grouped = df_sed.groupby('sedentary_bins', observed=True)['survival_months'].mean().reset_index()
                
                fig_sed = px.bar(
                    df_sed_grouped, x='sedentary_bins', y='survival_months',
                    title="Average Survival by Daily Sedentary Time",
                    color='sedentary_bins',
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig_sed, use_container_width=True)
            else:
                st.info("Sedentary data not currently available.")
    
            st.markdown("---")
            st.markdown("### 🌐 Evidence-Based International Oncology Guidelines")
            st.markdown("Direct clinical access paths to standard reference manuals:")

            col_guideline1, col_guideline2 = st.columns(2)
            with col_guideline1:
                st.markdown("#### 🇺🇸 US Frameworks")
                st.markdown("- [NCCN Guidelines](https://www.nccn.org/guidelines)")
                st.markdown("- [ASCO Portal](https://www.asco.org/practice-patients/guidelines)")
            with col_guideline2:
                st.markdown("#### 🇪🇺 EU & National Frameworks")
                st.markdown("- [ESMO Library](https://www.esmo.org/guidelines)")
                st.markdown("- [SEOM Portals](https://seom.org/guias-clinicas-seom)")

            st.markdown("### 🌐 General Comprehensive Oncology Registries")
            st.markdown("- [NCCN Global Index](https://www.nccn.org/guidelines) | [ESMO Clinical Index](https://www.esmo.org/guidelines) | [SEOM Clinical Index](https://seom.org/guias-clinicas-seom)")

    else:
        st.info("💡 Configure the patient baseline in the sidebar and click 'Generate Personalized Care Plan'.")


        