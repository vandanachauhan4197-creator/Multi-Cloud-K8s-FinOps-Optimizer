import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="FinOps Royal Executive Dashboard", layout="wide")

css_code = """
<style>
.stApp { background-color: #0A0E17; color: #F1F5F9; }
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
        border: 1px solid #374151;
            border-top: 3px solid #00F2FE;
                padding: 18px;
                    border-radius: 12px;
                        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
                        }
                        div[data-testid="stMetric"] label { color: #9CA3AF !important; font-size: 13px !important; font-weight: 600 !important; }
                        div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #F3F4F6 !important; font-weight: 700 !important; }
                        </style>
                        """
st.markdown(css_code, unsafe_allow_html=True)

st.title("📊 FinOps Multi-Cloud Cost & Waste Executive Dashboard")
st.caption(" Real-Time Analytics | AWS & Azure Telemetry")
st.divider()

idle_df = pd.read_csv('finops_idle_resources.csv')
spikes_df = pd.read_csv('finops_cost_spikes.csv')
st.sidebar.header("Interactive Filters")
st.sidebar.caption("Use these slicers to filter dashboard metrics")
selected_cloud = st.sidebar.selectbox("☁️ Filter Cloud Provider", ["All"] + list(idle_df.iloc[:, 0].unique()))
selected_pod = st.sidebar.selectbox("📦 Filter Specific Pod / Resource", ["All"] + list(idle_df.iloc[:, 1].unique()))
idle_df = idle_df if selected_pod == "All" else idle_df[idle_df.iloc[:, 1] == selected_pod]

idle_df = idle_df if selected_cloud == "All" else idle_df[idle_df.iloc[:, 0] == selected_cloud]

idle_df['Cost'] = pd.to_numeric(idle_df.iloc[:, -1], errors='coerce').fillna(150.0)
spikes_df['Spike_Cost'] = pd.to_numeric(spikes_df.iloc[:, -1], errors='coerce').fillna(320.0)

total_savings = idle_df['Cost'].sum()
idle_count = len(idle_df)
spike_count = len(spikes_df)
total_spike_cost = spikes_df['Spike_Cost'].sum()

m1, m2, m3, m4 = st.columns(4)
m1.metric(" Potential Monthly Savings", f"${total_savings:,.2f}")
m2.metric(" Unused Idle Resources", f"{idle_count} Items")
m3.metric(" Cost Anomaly Spikes", f"{spike_count} Alerts")
m4.metric(" Total Anomaly Impact", f"${total_spike_cost:,.2f}")

st.divider()

c1, c2 = st.columns(2)

fig_donut = px.pie(idle_df, names=idle_df.columns[0], values='Cost', hole=0.55, template="plotly_dark", color_discrete_sequence=['#3B82F6', '#E11D48', '#10B981', '#F59E0B'])
fig_donut.update_layout(dragmode=False, paper_bgcolor='#111827', plot_bgcolor='#111827', font_color='#F1F5F9')

c1.subheader("Cloud Waste Distribution")
c1.container(border=True).plotly_chart(fig_donut, use_container_width=True)

fig_bar = px.bar(spikes_df, x=spikes_df.columns[0], y='Spike_Cost', template="plotly_dark", color_discrete_sequence=['#00F2FE'])
fig_bar.update_layout(dragmode=False, paper_bgcolor='#111827', plot_bgcolor='#111827', font_color='#F1F5F9')


c2.subheader("Sudden Cost Anomaly Spikes")
c2.container(border=True).plotly_chart(fig_bar, use_container_width=True)

st.divider()

fig_cpu = px.bar(idle_df, x=idle_df.columns[1], y=idle_df.columns[4], color=idle_df.columns[0], title="CPU Usage % per Pod (Near Zero Indicates Idle Server)", template="plotly_dark", color_discrete_sequence=['#8B5CF6', '#EC4899'])
fig_cpu.update_layout(dragmode=False, paper_bgcolor='#111827', plot_bgcolor='#111827', font_color='#F1F5F9')


st.subheader("Low CPU Utilization Alert (< 5% Used = Waste)")
st.container(border=True).plotly_chart(fig_cpu, use_container_width=True)

st.divider()

st.subheader("📋 Resource Action Grid")
st.dataframe(idle_df, use_container_width=True)
st.divider()
st.download_button("📥 Download Filtered Waste Report", idle_df.to_csv(index=False), file_name="finops_waste_report.csv", mime="text/csv")



                        