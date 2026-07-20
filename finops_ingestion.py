import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_multi_cloud_logs():
    """
    Generates mock Multi-Cloud (AWS & Azure) Kubernetes cluster metrics
    including resource limits, actual usage, and hourly costs.
    """
    print(" Generating synthetic Multi-Cloud Kubernetes metrics...")
    
    providers = ['AWS', 'Azure']
    pods = ['web-frontend', 'payment-gateway', 'auth-service', 'analytics-db']
    data = []
    
    # Generate data for the last 5 hours to analyze trends and spikes
    current_time = datetime.now()
    
    for hour in range(5, 0, -1):
        timestamp = (current_time - timedelta(hours=hour)).strftime('%Y-%m-%d %H:00:00')
        
        for provider in providers:
            cluster_id = f"{provider.lower()}-prod-cluster-01"
            
            for pod in pods:
                # Setting up baseline resource allocations
                cpu_limit = 4.0  # Cores
                mem_limit = 16.0  # GB
                
                # Default under-utilization scenario (FinOps Leakage Target)
                if pod == 'analytics-db':
                    cpu_usage = round(random.uniform(0.1, 0.2), 2)  # Critical Idle State (~5% usage)
                    mem_usage = round(random.uniform(0.5, 1.0), 2)
                    hourly_cost = 4.50  # Highly over-priced for 5% utilization!
                
                # Normal operational scenario
                elif pod == 'web-frontend':
                    cpu_usage = round(random.uniform(2.0, 3.2), 2)
                    mem_usage = round(random.uniform(8.0, 12.0), 2)
                    hourly_cost = 1.20
                    
                # Sudden Cost Spike Scenario (Anomaly Target)
                elif pod == 'payment-gateway':
                    cpu_usage = round(random.uniform(1.5, 2.5), 2)
                    mem_usage = round(random.uniform(6.0, 10.0), 2)
                    # Artificially spike cost in the 3rd hour
                    if hour == 2:  # 2 hours ago
                        hourly_cost = 8.80  # Huge sudden cost spike!
                    else:
                        hourly_cost = 2.10
                
                else:  # auth-service
                    cpu_usage = round(random.uniform(0.8, 1.5), 2)
                    mem_usage = round(random.uniform(3.0, 5.0), 2)
                    hourly_cost = 0.95

                # Data Lineage & Governance Columns:-
                ingestion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data_owner = "Vandana_Chauhan"
                encryption_status = "AES-256-Active"

                data.append([
                    timestamp, provider, cluster_id, pod, 
                    cpu_limit, cpu_usage, mem_limit, mem_usage, hourly_cost,
                    ingestion_time, data_owner, encryption_status
                ])
                
    columns = [
        'Timestamp', 'Cloud_Provider', 'Cluster_ID', 'Pod_Name',
        'CPU_Limit_Cores', 'CPU_Usage_Cores', 'Memory_Limit_GB', 'Memory_Usage_GB', 'Hourly_Cost_USD',
        'Ingestion_Timestamp', 'Data_Owner', 'Encryption_Status'
    ]
    return pd.DataFrame(data, columns=columns)

def ingest_to_sqlite():
    """
    Establishes connection to SQLite, builds the enterprise schemas,
    and ingests clean multi-cloud metric data.
    """
    db_name = "multi_cloud_finops.db"
    table_name = "k8s_cluster_metrics"
    
    # Generating mock log dataset:-
    df_logs = generate_multi_cloud_logs()
    
    print(f"Connecting to SQLite database: '{db_name}'...")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create Table Schema with Data Governance standards:-
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Timestamp TEXT,
            Cloud_Provider TEXT,
            Cluster_ID TEXT,
            Pod_Name TEXT,
            CPU_Limit_Cores REAL,
            CPU_Usage_Cores REAL,
            Memory_Limit_GB REAL,
            Memory_Usage_GB REAL,
            Hourly_Cost_USD REAL,
            Ingestion_Timestamp TEXT,
            Data_Owner TEXT,
            Encryption_Status TEXT
        )
    """)
    conn.commit()
    
    # Ingesting data into the Database:-
    print(f"Loading dataset into '{table_name}' table...")
    df_logs.to_sql(table_name, conn, if_exists='replace', index=False)
    
    # Verifying the Ingestion:-
    print("Ingestion complete! Verifying database contents...")
    db_preview = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
    print("\n--- SQL DATABASE PREVIEW ---")
    print(db_preview[['Timestamp', 'Cloud_Provider', 'Pod_Name', 'Hourly_Cost_USD', 'Data_Owner']])
    
    conn.close()
    print(f"\nDatabase saved successfully as '{db_name}'")

if __name__ == "__main__":
    ingest_to_sqlite()
