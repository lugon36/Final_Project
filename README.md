# Oncology Data Analysis & Clinical Recommendation Pipeline
## Project Overview
This project presents an end-to-end clinical data analysis pipeline focused on oncology. The objective is to translate raw healthcare data into actionable insights that can assist oncologists in risk stratification and patient management. By integrating clinical, lifestyle, and genomic data, this project aims to bridge the gap between complex datasets and clinical decision-making.

## Technical Stack
- **Database & ETL**: 
    - _Python_: Used for advanced data cleaning, feature engineering, and automating the ingestion of raw clinical data.
    - _PostgreSQL_: Utilized as the relational database engine to host the refined datasets.
    - _Neon Console_: Deployed as the serverless PostgreSQL cloud provider for scalable data management and secure access.
    - _SQL_: Used for complex querying, data structuring, and preparing the final datasets for visualization.

- **Data Visualization**: Tableau. I utilized advanced features including cross-source data relationships, filter actions for interactivity, and storytelling modules.

- **Data Processing**: SQL (PostgreSQL/BigQuery) for managing relational data models.

- **Web Application**: Streamlit (Python). The app provides an intuitive interface for clinicians to view data-driven recommendations in real time.

- **Methodology**: Data-driven survival analysis and risk classification.

## Tableau Storytelling & Methodology
The project uses a structured "Story" format in Tableau to guide stakeholders through the analytical process:

- **Introduction & Clinical Context**: An overview of the cohort, highlighting the disparity in cancer types to demonstrate why personalized oncology is essential.

- **Evidence-Based Insights**: Integration of clinical research papers to ground the analysis in established medical theory.

- **The Data Pipeline**: A clear, technical flowchart illustrating the data lifecycle: from source datasets (NHANES/TCGA) to SQL transformation and final application deployment.

- **Interactive Risk Dashboards**: A central hub where users can filter by cancer type, gender, or habits. This allows for dynamic exploration of survival outcomes and correlations between smoking, inactivity, and clinical risk.

- **Clinical Integration**: Seamless navigation to the Streamlit app, turning passive reports into an active clinical recommendation tool.

## Key Clinical Findings
- **Threshold of Inactivity**: Data analysis revealed a critical sedentary threshold of 8 hours per day. Beyond this point, there is a statistically significant decrease in disease-free survival times.

- **Multivariate Risk**: Patients categorized as "Highly Sedentary" and "Smokers" display the lowest overall survival rates, emphasizing the need for comprehensive lifestyle screening.

- **Biomarker Correlation**: Initial analysis shows that higher mutation burdens correlate with shorter disease-free periods, validating the importance of integrating molecular markers into prognostic models.

## Navigation Guide
- **Tableau Story**: [Insert Link to your Tableau Public Story]

- **Recommendation App**: onco-asis.streamlit.app

## Limitations & Future Development
- **Data Scope**: This analysis relies on the available cohort; future iterations should incorporate larger, prospective Real-World Data (RWD) to increase predictive accuracy.

- **Expert Validation**: While the model provides data-driven suggestions, it is designed as a decision-support tool and requires final clinical oversight by oncology specialists.

Developed by Lugon36 👩‍💻