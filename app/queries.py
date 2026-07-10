# app/queries.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import hashlib

# 1. Secure connection retrieval from Streamlit Secrets
DATABASE_URL = st.secrets["DATABASE_URL"]

@st.cache_resource
def init_connection():
    return create_engine(DATABASE_URL)

def hash_password(password):
    """Encrypts passwords using SHA-256 for secure database storage."""
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# SECTION A: USER AUTHENTICATION & MANAGEMENT
# ==========================================
def create_users_table_if_not_exists():
    engine = init_connection()
    query = """
    CREATE TABLE IF NOT EXISTS application_users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(64) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with engine.connect() as connection:
        connection.execute(text(query))
        connection.commit()

def register_new_user(username, email, password):
    engine = init_connection()
    create_users_table_if_not_exists()
    pwd_hash = hash_password(password)
    query = """
        INSERT INTO application_users (username, email, password_hash)
        VALUES (:username, :email, :password_hash);
    """
    try:
        with engine.connect() as connection:
            connection.execute(text(query), {"username": username, "email": email, "password_hash": pwd_hash})
            connection.commit()
        return True
    except Exception:
        return False

def verify_user_login(username, password):
    engine = init_connection()
    create_users_table_if_not_exists()
    pwd_hash = hash_password(password)
    query = """
        SELECT user_id FROM application_users 
        WHERE username = :username AND password_hash = :password_hash;
    """
    with engine.connect() as connection:
        result = connection.execute(text(query), {"username": username, "password_hash": pwd_hash}).fetchone()
        return result is not None

# ==========================================
# SECTION B: CLINICAL DATA INTAKE & STATS
# ==========================================
@st.cache_data
def fetch_relational_patient_data():
    """Retrieves all clinical data from the master 'patients' table."""
    engine = init_connection()
    query = """
        SELECT 
            diagnosis_age AS age,
            sex,
            cancer_type,
            neoplasm_disease_stage_american_joint_committee_on_cancer_code,
            overall_survival_months,
            subtype
        FROM patients;
    """
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)

@st.cache_data
def fetch_advanced_cancer_stats(selected_cancer):
    """Computes clinical aggregation metrics."""
    engine = init_connection()
    # Ajustado a tus nombres de columnas reales
    age_query = """
        SELECT sex, ROUND(AVG(diagnosis_age)::numeric, 1) AS avg_age, COUNT(*) as patient_count
        FROM patients
        WHERE cancer_type = :cancer_type
        GROUP BY sex;
    """

    with engine.connect() as connection:
        df_age = pd.read_sql(text(age_query), connection, params={"cancer_type": selected_cancer})
        
    return df_age, pd.DataFrame() # Devolvemos un DF vacío para riesgo ya que no tienes esos datos

@st.cache_data
def fetch_top_genotypes(selected_cancer):
    """Fetches top 5 subtypes."""
    engine = init_connection()
    query = """
        SELECT subtype AS "Molecular Subtype / Genotype", COUNT(*) as "Patient Count"
        FROM patients
        WHERE cancer_type = :cancer_type 
          AND subtype != 'Not applicable / Unknown'
        GROUP BY subtype
        ORDER BY "Patient Count" DESC
        LIMIT 5;
    """
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection, params={"cancer_type": selected_cancer})

@st.cache_data
def fetch_lifestyle_master():
    engine = init_connection()
    query = "SELECT * FROM lifestyle_master;"
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)

@st.cache_data
def fetch_pharmacology_protocols():
    engine = init_connection()
    query = "SELECT * FROM treatment_protocols;"
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)

@st.cache_data
def fetch_advanced_cancer_stats(selected_cancer):
    """Computes clinical aggregation metrics from the master 'patients' table."""
    engine = init_connection()
    
 
    query = """
        SELECT 
            sex, 
            ROUND(AVG(diagnosis_age)::numeric, 1) AS avg_age, 
            COUNT(*) as patient_count
        FROM patients
        WHERE cancer_type = :cancer_type
        GROUP BY sex;
    """
    
    with engine.connect() as connection:
        df_age = pd.read_sql(text(query), connection, params={"cancer_type": selected_cancer})
        
    return df_age, pd.DataFrame()

@st.cache_data
def fetch_top_genotypes(selected_cancer):
    engine = init_connection()
    query = """
        SELECT subtype AS "Molecular Subtype / Genotype", COUNT(*) as "Patient Count"
        FROM patients
        WHERE cancer_type = :cancer_type AND subtype != 'Not applicable / Unknown'
        GROUP BY subtype
        ORDER BY "Patient Count" DESC
        LIMIT 5;
    """
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection, params={"cancer_type": selected_cancer})
    
@st.cache_data
def fetch_nhanes_lifestyle_stats():
    """Retrieves life-long smoking history and mortality data."""
    engine = init_connection()
    
    # Hemos añadido ::FLOAT para convertir survival_months a número
    query = """
        SELECT 
            CASE 
                WHEN smoked_100_cigs = 1 THEN 'Ever Smoked'
                WHEN smoked_100_cigs = 2 THEN 'Never Smoked'
                ELSE 'Unknown'
            END AS smoking_history,
            AVG(survival_months::FLOAT) AS avg_survival
        FROM nhanes_analytics_data
        WHERE smoked_100_cigs IN (1, 2)
        GROUP BY smoking_history
        ORDER BY avg_survival DESC;
    """
    
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)
    
@st.cache_data
def fetch_nhanes_sedentary_stats():
    engine = init_connection()
    query = """
        SELECT sedentary_minutes_day, survival_months
        FROM nhanes_analytics_data
        WHERE sedentary_minutes_day IS NOT NULL 
          AND survival_months IS NOT NULL;
    """
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)
    
@st.cache_data
def fetch_survival_by_stage(cancer_type, stage):
    engine = init_connection()
    
    query = """
        SELECT ROUND(AVG(CAST(overall_survival_months AS NUMERIC)), 2) as avg_survival
        FROM patients
        WHERE cancer_type = :cancer 
          AND neoplasm_disease_stage_american_joint_committee_on_cancer_code = :stage;
    """
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection, params={"cancer": cancer_type, "stage": stage})