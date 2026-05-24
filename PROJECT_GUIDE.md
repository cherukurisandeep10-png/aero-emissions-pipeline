# AeroStream: Project Specification & Developer Documentation

This document serves as the formal technical specification and developer manual for the **AeroStream** platform. It provides system administrators, data engineers, and analytical developers with a comprehensive understanding of the pipeline's architecture, data flows, emissions modeling, and operational configurations.

---

## 📖 Table of Contents
1.  [System Architecture & Business Value](#1-system-architecture--business-value)
2.  [The Data Journey (Medallion Architecture)](#2-the-data-journey-medallion-architecture)
3.  [Scientific Emissions Modeling & Physics](#3-scientific-emissions-modeling--physics)
4.  [Technology Stack Rationale](#4-technology-stack-rationale)
5.  [Automated Pipeline Orchestration](#5-automated-pipeline-orchestration)
6.  [Operational Playbook (Local Execution)](#6-operational-playbook-local-execution)

---

## 1. System Architecture & Business Value

### Platform Core
AeroStream is an end-to-end telemetry and analytical data pipeline. It ingests global ADS-B transponder signals, runs real-time kinematic profile tracking, and calculates estimated carbon emissions ($CO_2$) based on aircraft class and multi-phase flight operations.

### Enterprise Value
In alignment with global environmental disclosures (such as ICAO and ESG climate frameworks), aviation operations require real-time visibility into emissions intensity.
*   **The Baseline Challenge:** Traditional emissions auditing is done retrospectively using fuel-receipt aggregation, which introduces data latency and prevents tactical routing interventions.
*   **AeroStream Utility:** It automates tracking using open-source, crowd-sourced transponder networks, enabling sustainability officers and flight coordinators to analyze fleet-wide carbon intensity on a second-by-second basis.

---

## 2. The Data Journey (Medallion Architecture)

The platform utilizes a structured Medallion Architecture to ingest, clean, and enrich incoming transponder state vectors:

```text
 [Live ADS-B Signals] ────> (REST API Connection)
                                  │
                                  ▼
┌────────────────────────────────────────────────────────┐
│ 1. BRONZE LAYER (data/bronze/flights/)                 │
│ Raw coordinate payloads partitioned by date and hour   │
│ into compressed Parquet files.                         │
└──────────────────────────┬─────────────────────────────┘
                           │ (DuckDB Copy/Schema Enforcement)
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. SILVER LAYER (data/lakehouse.db -> silver_flights)  │
│ Cleaned relational table with standardized data types  │
│ and cast timestamps.                                   │
└──────────────────────────┬─────────────────────────────┘
                           │ (dbt Transform & Assertions)
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. GOLD LAYER (data/lakehouse.db -> gold tables)       │
│ Materialized dimension and fact schemas optimized for  │
│ low-latency analytical queries and BI visuals.         │
└────────────────────────────────────────────────────────┘
```

### Layer Implementations:
1.  **Bronze (Raw Lake Landing):** Telemetry vectors are captured in structured Python payloads and committed directly to disk as **Parquet** partitioned files: `year_month_day=YYYY-MM-DD/hour=HH/`.
2.  **Silver (Structured Storage):** Raw files are aggregated and loaded into the local relational table `silver_flights` inside **DuckDB**, converting Unix timestamps into normalized SQL timestamps.
3.  **Gold (Semantic Layer):** **dbt Core** compiles modular SQL nodes to generate analytical marts:
    *   `stg_flights` (Staging Node): Employs SQL window functions (`ROW_NUMBER() OVER (...)`) to deduplicate active state vectors per aircraft per tracking window.
    *   `fct_flights_emissions` (Fact Node): Details granular metrics, calculating flight phases and spatial vectors.
    *   `dim_aircraft_types` (Dimension Node): Summarizes metrics (unique airframes, average groundspeed, cumulative $CO_2$ mass) grouped by aircraft class.

---

## 3. Scientific Emissions Modeling & Physics

To maintain scientific integrity, fuel burn is calculated dynamically based on real-time flight vectors:

1.  **Class Isolation:** The engine parses airspeed (groundspeed) and altitude levels to classify the transponder’s airframe:
    *   *Widebody Jet* (e.g., Boeing 777/787, Airbus A350)
    *   *Narrowbody Jet* (e.g., Boeing 737, Airbus A320)
    *   *Regional Jet* (e.g., Embraer E190, CRJ900)
    *   *Turboprop / Business Aviation*
    *   *Light General Aviation*
2.  **Flight Phase Profiling:** Using the aircraft’s vertical rate (velocity in meters-per-second converted to feet-per-minute), the system profiles the flight phase:
    *   `Climbing` ($>300$ ft/min)
    *   `Descending` ($<-300$ ft/min)
    *   `Cruising` (Level flight)
    *   `On Ground`
3.  **Dynamic Thrust Coefficients:**
    *   **Climbing:** Accounted for at **+35%** fuel burn to represent maximum takeoff/climb thrust.
    *   **Descending:** Accounted for at **-60%** fuel burn to represent idle descent profiles.
4.  **$CO_2$ Conversion:** Jet-A1 fuel consumption is translated to carbon mass using the standardized ICAO factor: **3.16 kg of $CO_2$ emitted per 1 kg of fuel consumed.**

---

## 4. Technology Stack Rationale

*   **DuckDB:** Chosen for its serverless, in-process analytical design. DuckDB provides optimized columnar operations, making it highly efficient for processing compressed Parquet files locally.
*   **dbt Core:** Enforces version-controlled, modular SQL transformations. By managing the semantic layer, dbt allows teams to run automated schema checks directly in the development lifecycle.
*   **Streamlit:** Serves as the presentation layer. Streamlit compiles Python scripts into a highly responsive analytical dashboard, allowing operational teams to visualize telemetry data.
*   **Parquet:** Chosen for the raw lake layer due to its columnar compression, reducing local storage footprints and boosting read performance for partitioned tables.
*   **Terraform:** Implements Infrastructure as Code (IaC) to define target cloud environments (Amazon S3 buckets, AWS Glue Data Catalogs, and Amazon Athena) as reproducible configurations.

---

## 5. Automated Pipeline Orchestration

The production environment is orchestrated automatically using **GitHub Actions**. Every 6 hours, the runner executes the following sequence:

1.  Instantiates a runner container and installs dependencies from `requirements.txt`.
2.  Triggers `src/ingest.py` to capture live airspace vectors from the OpenSky Network API.
3.  Changes directory into `dbt_project` to run transformations (`dbt run`) and execute data quality tests (`dbt test`).
4.  Performs a Git transaction to commit the updated analytical database (`lakehouse.db`) back to the repository.
5.  Streamlit Community Cloud instantly hot-reloads, serving the updated data payload.

---

## 6. Operational Playbook (Local Execution)

For local development and manual execution, run the following procedures inside your active terminal:

### 1. Initialize Virtual Environment
```bash
source venv/Scripts/activate
```

### 2. Execute Data Ingestion
```bash
PYTHONPATH=. python src/ingest.py
```

### 3. Run Semantic Modeling & Testing
```bash
cd dbt_project
dbt run --profiles-dir .
dbt test --profiles-dir .
cd ..
```

### 4. Boot Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```
