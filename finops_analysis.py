import sqlite3
import pandas as pd

def run_finops_sql_engine():
    """
    Connects to the multi-cloud FinOps database, runs analytical SQL,
    and automatically exports the results into clean CSV files.
    """
    db_name = "multi_cloud_finops.db"
    print(f"Connecting to SQLite Database: '{db_name}'...")
    
    conn = sqlite3.connect(db_name)

    # -------------------------------------------------------------------------
    # QUERY 1: Cost Spike Anomaly Detection (Using LAG() Window Function)
    # -------------------------------------------------------------------------
    cost_spike_query = """
    WITH CostHistory AS (
        SELECT 
            Timestamp,
            Cloud_Provider,
            Cluster_ID,
            Pod_Name,
            Hourly_Cost_USD,
            LAG(Hourly_Cost_USD, 1) OVER (
                PARTITION BY Cloud_Provider, Cluster_ID, Pod_Name 
                ORDER BY Timestamp
            ) AS Prev_Hour_Cost
        FROM k8s_cluster_metrics
    )
    SELECT 
        Timestamp,
        Cloud_Provider,
        Pod_Name,
        Prev_Hour_Cost,
        Hourly_Cost_USD AS Current_Cost,
        ROUND(((Hourly_Cost_USD - Prev_Hour_Cost) / Prev_Hour_Cost) * 100, 2) AS Cost_Jump_Percent,
        CASE 
            WHEN ((Hourly_Cost_USD - Prev_Hour_Cost) / Prev_Hour_Cost) * 100 >= 100 THEN '🔴 CRITICAL SPIKE (Immediate Action!)'
            WHEN ((Hourly_Cost_USD - Prev_Hour_Cost) / Prev_Hour_Cost) * 100 >= 30 THEN '🟡 WARNING (Monitor Cost)'
            ELSE '🟢 NORMAL'
        END AS Alert_Status
    FROM CostHistory
    WHERE Prev_Hour_Cost IS NOT NULL
    ORDER BY Cost_Jump_Percent DESC;
    """

    # -------------------------------------------------------------------------
    # QUERY 2: Idle & Over-provisioned Pod Finder (Using Aggregate Functions & CTE)
    # -------------------------------------------------------------------------
    idle_resource_query = """
    WITH ResourceEfficiency AS (
        SELECT 
            Cloud_Provider,
            Cluster_ID,
            Pod_Name,
            ROUND(AVG(CPU_Usage_Cores), 2) AS Avg_CPU_Used,
            CPU_Limit_Cores AS CPU_Limit,
            ROUND(AVG(Hourly_Cost_USD), 2) AS Avg_Hourly_Cost
        FROM k8s_cluster_metrics
        GROUP BY Cloud_Provider, Cluster_ID, Pod_Name
    )
    SELECT 
        Cloud_Provider,
        Pod_Name,
        Avg_CPU_Used,
        CPU_Limit,
        ROUND((Avg_CPU_Used / CPU_Limit) * 100, 2) AS CPU_Utilization_Percent,
        Avg_Hourly_Cost,
        ROUND(Avg_Hourly_Cost * 24 * 30, 2) AS Projected_Monthly_Waste_USD,
        'HIGH WASTE: Recommend Instance Downsizing' AS Recommendation
    FROM ResourceEfficiency
    WHERE (Avg_CPU_Used / CPU_Limit) * 100 < 15.0
    ORDER BY Projected_Monthly_Waste_USD DESC;
    """

    # --- 1. EXECUTE & EXPORT QUERY 1 (Cost Spikes) ---
    print("\nExecuting Cost Spike Detection Pipeline...")
    df_spikes = pd.read_sql_query(cost_spike_query, conn)
    
    # Save to CSV (index=False means we don't save the row numbers)
    spike_csv_name = "finops_cost_spikes.csv"
    df_spikes.to_csv(spike_csv_name, index=False)
    print(f"Saved Cost Spike Report as: '{spike_csv_name}'")

    # --- 2. EXECUTE & EXPORT QUERY 2 (Idle Resources) ---
    print("\nExecuting Resource Efficiency Pipeline...")
    df_idle = pd.read_sql_query(idle_resource_query, conn)
    
    # Save to CSV
    idle_csv_name = "finops_idle_resources.csv"
    df_idle.to_csv(idle_csv_name, index=False)
    print(f"Saved Idle Resource Report as: '{idle_csv_name}'")

    conn.close()
    print("\n SQL Analysis & CSV Export completed successfully!")

if __name__ == "__main__":
    run_finops_sql_engine()
