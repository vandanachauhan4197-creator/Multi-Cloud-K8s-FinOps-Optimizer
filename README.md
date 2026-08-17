# ☁️ Multi-Cloud K8s FinOps Optimizer

An end-to-end data analytics project built to identify hidden infrastructure costs and detect sudden compute cost spikes across AWS and Azure Kubernetes clusters.

---

## 🎯 Features
* **Multi-Cloud Data Pipeline:** Processes operational metrics from AWS & Azure Kubernetes clusters.
* **Cost Spike Alerts:** Uses SQL `LAG()` window functions to automatically flag sudden cost jumps (>100% spikes).
* **Idle Resource Detection:** Identifies under-utilized pods (<15% CPU usage) and projects monthly financial waste.
* **Data Governance:** Ingests data with compliance audit metadata (`Ingestion_Timestamp`, `Encryption_Status`).
* **Visual Dashboards:** Interactive reports built with Streamlit and Looker studio.

---

## 🛠️ Tech Stack
* **Language:** Python (`pandas`, `sqlite3`, `datetime`)
* **Database & SQL:** SQLite (CTEs, Window Functions, Case Statements)
* **BI Tools:** Power BI, Tableau

---

## 📁 Repository Structure...
(text)
├── data/
│   ├── finops_cost_spikes.csv
│   └── finops_idle_resources.csv
├── scripts/
│   ├── finops_ingestion.py
│   └── finops_analysis.py
├── dashboards/
│   ├── finops dashboard.py(streamlit)
│   └── Finops cost anomaly dashboard(looker studio)
└── README.md

⚙️How to run
1. Build database and ingest data
(python scripts/finops_ingestion.py)
2. Run SQL engine and export repots
(python scripts/finops_analysis.py)
3. View Dashboards(streamlit/looker studio)

