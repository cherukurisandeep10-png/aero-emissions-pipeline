# AeroStream: Resilient Aviation Operations & Emissions Data Lakehouse

[![dbt Core](https://img.shields.io/badge/dbt-Core%20v1.11-FF694B?logo=dbt&logoColor=white)](https://github.com/dbt-labs/dbt-core)
[![DuckDB](https://img.shields.io/badge/DuckDB-v1.5-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-v1.57-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-844FBA?logo=terraform&logoColor=white)](https://www.terraform.io/)

A modern, production-grade end-to-end data engineering project designed to ingest global aviation telemetry, model operational flight profiles, and estimate real-time carbon emissions (CO₂).

This project showcases **best-in-class data engineering patterns** ideal for high-scale, cost-effective lakehouse implementations. It is a stellar addition to my professional portfolio, highlighting my ability to merge domain expertise in aviation with the Modern Data Stack.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Data Sources
        API[OpenSky Network API]
        MOCK[Resilient Fallback Mock Generator]
    end

    subgraph Data Lakehouse (Medallion Architecture)
        subgraph Bronze Layer
            parquet[Partitioned Parquet Files on Local Disk / S3]
        end

        subgraph Silver Layer
            raw_db[(DuckDB: silver_flights)]
        end

        subgraph Gold Layer (dbt Marts)
            stg[stg_flights View] --> dim[dim_aircraft_types Table]
            stg --> fct[fct_flights_emissions Table]
        end
    end

    subgraph Analytics & Presentation
        dashboard[Streamlit BI Dashboard]
        dbt_test[dbt Tests / Data Quality Audit]
    end

    API -->|Ingest Script| parquet
    MOCK -->|Auto-Fallback| parquet
    parquet -->|Direct Copy / Schema Enforcement| raw_db
    raw_db -->|dbt run| stg
    dim -->|Interactive Queries| dashboard
    fct -->|Operational Logs & Map| dashboard
```

---

## 🚀 Key Technical Features Demonstrated

1. **Medallion Data Architecture:** 
   - **Bronze:** Raw JSON/CSV telemetry converted into compressed, partitioned Parquet files (`year_month_day=YYYY-MM-DD/hour=HH/`).
   - **Silver:** Cleaned, structured DuckDB relational schema with standardized data types.
   - **Gold:** Normalized Dimensional & Fact schemas tailored for optimal downstream reporting.
2. **Resilient Data Ingestion Design:** Employs an automated **Mock Generator Fallback** pattern. If the external live OpenSky REST API is down, throttled, or rate-limited, the system automatically triggers a realistic transponder simulation to guarantee 100% pipeline uptime and flawless local testing.
3. **Advanced dbt Core modeling:**
   - SQL Window functions (`ROW_NUMBER() OVER (...)`) to deduplicate redundant aircraft states within the same window.
   - Strictly defined data-quality schema validation tests (`not_null`, `unique`, and `accepted_values` for operational flight phases like Climbing/Cruising/Descending/On Ground).
4. **Domain-Specific Calculations (Climate Engineering):** Integrates an aerodynamic emissions algorithm mimicking standard ICAO metrics, translating airspeeds, altitude thresholds, and vertical rates into instantaneous jet-fuel consumption and metric-tonnes of CO₂ emitted.
5. **Interactive Single-Node BI Delivery:** Streamlit-powered dashboard visualizing real-time air traffic density, geospatial trajectory charts (Plotly), flight phase breakdowns, and category carbon-intensity distributions.

---

## 🛠️ Project Directory Structure

```
├── README.md                      # Professional project documentation
├── requirements.txt               # Unified Python dependencies
├── data/                          # Simulated Cloud Data Lake
│   ├── bronze/                    # Raw partitioned Parquet data lakehouse landing
│   └── lakehouse.db               # Local DuckDB warehouse (Silver + Gold tables)
├── src/                           # Core operational engine
│   ├── __init__.py
│   ├── ingest.py                  # API connector, mock fallback, & ingestion executor
│   └── emissions_calculator.py    # Aerodynamic flight & CO2 modeling algorithms
├── dbt_project/                   # dbt transformation models
│   ├── dbt_project.yml            # dbt configs
│   ├── profiles.yml               # DuckDB connection profile
│   └── models/
│       ├── schema.yml             # Data quality checks & column definitions
│       ├── staging/
│       │   └── stg_flights.sql    # Casts types, standardizes, & deduplicates telemetry
│       └── marts/
│           ├── dim_aircraft_types.sql  # Summarizes average flight levels & emissions per class
│           └── fct_flights_emissions.sql # Granular fact table labeling flight phases & tracking metrics
├── dashboard/                     # BI Interface
│   └── app.py                     # Rich Streamlit metrics and maps
└── terraform/                     # IaC Blueprint for Production AWS Cloud Scale
    ├── main.tf                    # S3, Athena, & IAM Cloud configuration
    ├── variables.tf
    └── outputs.tf
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites & Environment Setup
Ensure you have Python 3.9+ installed. Clone this repository, set up a virtual environment, and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/your-username/aero-emissions-pipeline.git
cd aero-emissions-pipeline

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install core packages (Pandas, Requests, DuckDB, dbt-duckdb, Streamlit, Plotly)
pip install -r requirements.txt
```

### 2. Run the Data Ingestion Pipeline
Execute the Python ingestion script to harvest real-time flight transponder telemetry or trigger the local fallback engine:

```bash
# Set PYTHONPATH to root and run
PYTHONPATH=. python src/ingest.py
```
*Expected output:* You will see raw Parquet snapshots compiled in `data/bronze/` and populated tables within `data/lakehouse.db`.

### 3. Run dbt Transformations & Data Quality Tests
Navigate to the `dbt_project` directory and compile the staging and analytical tables:

```bash
cd dbt_project

# Run models (compiles silver schema into gold marts)
dbt run --profiles-dir .

# Run automated tests (ensures data integrity, tests for nulls/phase validations)
dbt test --profiles-dir .
```

### 4. Launch the Streamlit Dashboard
Run the BI platform to explore interactive charts, geospatial scatter plots, and aircraft emissions breakdowns:

```bash
# Return to the root directory
cd ..

# Launch Streamlit dashboard
streamlit run dashboard/app.py
```
The dashboard will launch automatically in your browser at `http://localhost:8501`.

---

## 🛡️ Cloud Scale Deployment Blueprint (Infrastructure as Code)
For professional deployments, a complete **Terraform IaC blueprint** is provided inside the `terraform/` directory. This script defines the production-ready target architecture on AWS:
- **AWS S3 Bucket** to serve as the cloud Bronze and Silver data lake storage.
- **AWS Glue Crawler & Data Catalog** to define the relational schema over parquet snapshots.
- **Amazon Athena** or **Snowflake Integration** to query historical aviation metrics seamlessly at scale.

To provision the cloud resources:
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## 🎯 Resume Bullet Points (How to Highlight This!)
Add this project to your resume under a **"Key Projects"** section:

> **AeroStream: Real-Time Aviation Telemetry & Carbon Emissions Data Lakehouse (dbt, DuckDB, Python, Parquet, Terraform)**
> - Engineered an end-to-end Medallion-architecture data pipeline ingesting global transponder signals from the OpenSky REST API, writing structured, partitioned Parquet datasets to a localized data lake.
> - Implemented an automated fallback transponder generator, ensuring 100% pipeline execution uptime under heavy API rate limits or connection timeouts.
> - Developed SQL transformations in **dbt Core** and **DuckDB**, implementing window functions to deduplicate incoming streaming signals and writing 6 standard data-quality checks (`not_null`, `unique`, `accepted_values`) to guarantee data integrity.
> - Designed a custom aerodynamic math module translating flight indicators (airspeed, altitude, vertical rate) into standard fuel burn metrics, presenting carbon footprint insights via an interactive **Streamlit** dashboard.

---

## 📈 LinkedIn Profile Showcasing Post
*(Copy, modify, and post this to LinkedIn to drive recruiters to your GitHub!)*

```text
🚀 I just launched my latest project: "AeroStream" — an end-to-end global aviation operations & carbon emissions data lakehouse! ✈️💨

Having spent 2 years working in data systems at Boeing, I wanted to combine my passion for aviation domain engineering with the Modern Data Stack to showcase how we can track operational flight profiles and report climate impact in real-time.

Here is what I built:
1️⃣ Ingestion Engine: A robust Python pipeline pulling real-time transponder data from the OpenSky Network API. Built with a resilient fallback simulation to maintain 100% processing uptime.
2️⃣ Data Lake (Bronze): Compiling raw states into hourly, partitioned Parquet files to optimize storage and downstream execution speeds.
3️⃣ Lakehouse (Silver): Sourcing clean, structured schemas into a relational database.
4️⃣ Analytical Transformations (Gold): Modeled dimensions and facts inside dbt (Data Build Tool) on DuckDB, leveraging SQL window functions to deduplicate aircraft telemetry and defining data-quality test suites.
5️⃣ BI Delivery: Designed an interactive Streamlit application charting active flights geospatially, profiling aircraft phases (climbing, cruising, descending), and aggregating real-time carbon intensity.

Developing this gave me a fantastic opportunity to deep-dive into:
- Modular, resilient software engineering in Python
- Modern analytical databases (DuckDB) and semantic modeling (dbt)
- Cloud provisioning via Terraform IaC blueprints

Check out the full repository here and feel free to share your thoughts! 👇
🔗 [Insert Your Github Link Here]

#DataEngineering #ModernDataStack #Aviation #DuckDB #dbt #Streamlit #ClimateTech #Aerospace #Boeing
```
