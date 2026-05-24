# AeroStream: Resilient Aviation Operations & Emissions Data Lakehouse

A modern, end-to-end data lakehouse pipeline designed to ingest real-time global aviation telemetry, model flight states, and estimate carbon emissions (CO₂) utilizing the Medallion Architecture.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Data Sources
        API[OpenSky Network API]
        MOCK[Automated Mock Fallback Engine]
    end

    subgraph Data Lakehouse (Medallion Architecture)
        subgraph Bronze Layer
            parquet[Partitioned Parquet Lake Storage]
        end

        subgraph Silver Layer
            raw_db[(DuckDB: silver_flights)]
        end

        subgraph Gold Layer (dbt Marts)
            stg[stg_flights View] --> dim[dim_aircraft_types Table]
            stg --> fct[fct_flights_emissions Table]
        end
    end

    subgraph BI & Analytics
        dashboard[Streamlit Analytics App]
        dbt_test[dbt Core Test Suite]
    end

    API -->|Ingest Core| parquet
    MOCK -->|Auto-Recovery fallback| parquet
    parquet -->|Schema Enforcement Loader| raw_db
    raw_db -->|dbt compile & run| stg
    dim -->|Aggregated Metrics| dashboard
    fct -->|Spatiotemporal Visuals| dashboard
```

---

## 🚀 Technical Architecture & Implementations

### 1. Medallion Data Pipeline
*   **Bronze Zone:** Telemetry payloads are captured from OpenSky transponders, parsed into Pandas, and stored as compressed, partitioned Parquet files partitioned by date and hour: `year_month_day=YYYY-MM-DD/hour=HH/`.
*   **Silver Zone:** Raw snapshots are structured and merged into a local DuckDB analytical database executing consistent data schemas.
*   **Gold Zone:** Analytical schemas are transformed and compiled via **dbt Core** into relational dimension and fact models ready for downstream operational analysis.

### 2. Resilient Ingestion & Automated Fallback
To mitigate external server latency, rate limits, and connection drops associated with public crowd-sourced radio networks, the ingestion module features an automated state fallback. If the external API request fails or times out, the pipeline dynamically instantiates a high-fidelity synthetic transponder simulator to ensure continuous operation.

### 3. Flight Phase & Climate Modeling
The pipeline runs a custom aerodynamic physics model that translates spatial indicators into instantaneous fuel consumption and environmental metrics:
*   **Phase Profiling:** Maps climb and descent rates (feet per minute) to categorize operational states (`Climbing`, `Cruising`, `Descending`, `On Ground`).
*   **Emissions Algorithm:** Integrates fuel-burn coefficients by aircraft category, factoring in the increased thrust required during climbs (+35%) and reduced fuel rates during idle descents (-60%).

---

## 🛠️ Project Structure

```
├── README.md                      # Technical documentation
├── requirements.txt               # Unified project dependencies
├── Makefile                       # Developer automation utilities
├── data/                          # Local Lakehouse Storage
│   ├── bronze/                    # Partitioned raw Parquet landing
│   └── lakehouse.db               # DuckDB Database (Silver + Gold tables)
├── src/                           # Core Operational Code
│   ├── __init__.py
│   ├── ingest.py                  # API Ingestion & Failover execution engine
│   └── emissions_calculator.py    # Aerodynamic emissions profiling module
├── dbt_project/                   # dbt Semantic Layer
│   ├── dbt_project.yml            # dbt configuration
│   ├── profiles.yml               # DuckDB connection profile
│   └── models/
│       ├── schema.yml             # Data quality testing constraints
│       ├── staging/
│       │   └── stg_flights.sql    # Casts types, standardizes, & deduplicates
│       └── marts/
│           ├── dim_aircraft_types.sql  # Summarizes metrics per aircraft class
│           └── fct_flights_emissions.sql # Granular flight-phase and carbon metrics
├── dashboard/                     # Analytical Interface
│   └── app.py                     # Streamlit application
└── terraform/                     # Cloud Infrastructure-as-Code
    ├── main.tf                    # S3, IAM, and AWS Glue Catalog templates
    ├── variables.tf
    └── outputs.tf
```

---

## ⚡ Setup & Execution

### 1. Environment Configurations
Verify Python 3.9+ is installed. Clone the repository and install the unified dependencies:

```bash
# Clone the repository
git clone https://github.com/cherukurisandeep10-png/aero-emissions-pipeline.git
cd aero-emissions-pipeline

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Execute Data Ingestion (Bronze & Silver)
Run the pipeline launcher to capture live transponder updates:
```bash
PYTHONPATH=. python src/ingest.py
```

### 3. Run dbt Compilations & Schema Checks (Gold)
Navigate to the `dbt_project` directory to materialize semantic models and execute data quality assertions:
```bash
cd dbt_project

# Compile semantic schemas
dbt run --profiles-dir .

# Run data quality test constraints
dbt test --profiles-dir .
```

### 4. Launch Analytics Dashboard
Return to the root directory and boot up the interactive Streamlit service:
```bash
cd ..
streamlit run dashboard/app.py
```

---

## 🛡️ Infrastructure as Code (IaC) Deployment
To deploy this project to production on AWS, refer to the Terraform configurations inside the `terraform/` directory. Applying the configuration provisions:
*   An **S3 Bucket** acting as the cloud storage backing the Medallion lakehouse.
*   An **AWS Glue Catalog Database** representing the semantic schema definitions.
*   An **AWS Glue Crawler** automated to crawl parquet partitions and update database schemas dynamically.
