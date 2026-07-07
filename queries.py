
# DATABASE CONNECTION & QUERY MODULE
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import hashlib

# 1. Fetch the secure database string directly from the TOML vault
DATABASE_URL = st.secrets["DATABASE_URL"]

# 2. Initialize the cloud engine securely
@st.cache_resource
def init_connection():
    """Initializes and caches the Neon PostgreSQL engine."""
    return create_engine(DATABASE_URL)

def fetch_relational_patient_data():
    """Retrieves the core demographic and primary tumor clinical mappings."""
    engine = init_connection()
    query = """
        SELECT 
            p.age,
            p.sex,
            p.smoking_status,
            p.activity_level,
            d.cancer_type,
            d.neoplasm_disease_stage_american_joint_committee_on_cancer_code,
            d.overall_survival_months
        FROM patients p
        INNER JOIN diagnostics d ON p.patient_id = d.patient_id;
    """
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)

def fetch_lifestyle_master():
    """Retrieves the oncology lifestyle parameters from Neon."""
    engine = init_connection()
    query = "SELECT * FROM lifestyle_master;"
    try:
        with engine.connect() as connection:
            df_result = pd.read_sql(text(query), connection)
            return df_result
    except Exception as e:
        st.error(f"Lifestyle Query Failed: {e}")
        return pd.DataFrame()

def fetch_pharmacology_protocols():
    """Extracts the oncological treatment guidelines from Neon."""
    engine = init_connection()
    query = "SELECT * FROM treatment_protocols;"
    try:
        with engine.connect() as connection:
            return pd.read_sql(text(query), connection)
    except Exception as e:
        st.error(f"❌ Pharmacology Query Failed: {e}")
        return pd.DataFrame()


    # ==============================================================================
# ADVANCED DATABASE CORE & AUTHENTICATION MODULE (queries.py)
# ==============================================================================
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import hashlib

# 1. Secure connection retrieval from Streamlit Secrets
DATABASE_URL = st.secrets["DATABASE_URL"]

@st.cache_resource
def init_connection():
    """Initializes and caches the SQLAlchemy database engine connection."""
    return create_engine(DATABASE_URL)

def hash_password(password):
    """Encrypts passwords using SHA-256 for secure database storage."""
    return hashlib.sha256(password.encode()).hexdigest()


# SECTION A: USER AUTHENTICATION & MANAGEMENT (NEON DRIVEN)
def create_users_table_if_not_exists():
    """Ensures the application user credential directory is ready."""
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
    """Inserts a new clinician account into the secure cloud database."""
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
    except Exception as e:
        # Handles UNIQUE constraint violations safely (e.g., user already exists)
        return False

def verify_user_login(username, password):
    """Validates login attempts against stored encrypted credentials."""
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


# SECTION B: CLINICAL DATA INTAKE & ADVANCED ONCOLOGY STATS
def fetch_relational_patient_data():
    """Retrieves the core demographic and primary tumor clinical mappings."""
    engine = init_connection()
    query = """
        SELECT 
            p.age,
            p.sex,
            p.smoking_status,  
            p.activity_level,
            d.cancer_type,
            d.neoplasm_disease_stage_american_joint_committee_on_cancer_code,
            d.overall_survival_months
        FROM patients p
        INNER JOIN diagnostics d ON p.patient_id = d.patient_id;
    """
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)

def fetch_lifestyle_master():
    """Extracts the multi-line text mapping catalog for treatment plans."""
    engine = init_connection()
    query = "SELECT * FROM lifestyle_master;"
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection)

def fetch_advanced_cancer_stats(selected_cancer):
    """Computes high-value clinical aggregation metrics for the oncologist tab."""
    engine = init_connection()
    
    # Query A: Demographics distribution (Average age of diagnosis per sex)
    age_query = """
        SELECT 
            p.sex,
            ROUND(AVG(p.age)::numeric, 1) AS avg_age,
            COUNT(*) as patient_count
        FROM patients p
        INNER JOIN diagnostics d ON p.patient_id = d.patient_id
        WHERE d.cancer_type = :cancer_type
        GROUP BY p.sex;
    """
    
    # Query B: Risk factor cross-tabulation (Smoking correlation with survival)
    risk_query = """
        SELECT 
            p.smoking_status,
            ROUND(AVG(d.overall_survival_months)::numeric, 1) AS avg_survival
        FROM patients p
        INNER JOIN diagnostics d ON p.patient_id = d.patient_id
        WHERE d.cancer_type = :cancer_type AND p.smoking_status NOT IN ('Unknown', 'N/A')
        GROUP BY p.smoking_status
        ORDER BY avg_survival DESC;
    """
    
    with engine.connect() as connection:
        df_age = pd.read_sql(text(age_query), connection, params={"cancer_type": selected_cancer})
        df_risk = pd.read_sql(text(risk_query), connection, params={"cancer_type": selected_cancer})
        
    return df_age, df_risk

def fetch_top_genotypes(selected_cancer):
    """Fetches the top 5 most frequent molecular subtypes/genotypes for the selected cancer."""
    engine = init_connection()
    query = """
        SELECT 
            subtype AS "Molecular Subtype / Genotype",
            COUNT(*) as "Patient Count"
        FROM diagnostics
        WHERE cancer_type = :cancer_type 
          AND subtype IS NOT NULL 
          AND subtype NOT IN ('Unknown', 'N/A', '')
        GROUP BY subtype
        ORDER BY "Patient Count" DESC
        LIMIT 5;
    """
    with engine.connect() as connection:
        return pd.read_sql(text(query), connection, params={"cancer_type": selected_cancer})