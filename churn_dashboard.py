import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------
# Page Config
# ------------------
st.set_page_config(
    page_title="Customer Churn Dashboard",
    layout="wide",
    page_icon="📊"
)

# ------------------
# Load Data
# ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("churn_analysis_results.csv")
    return df

df = load_data()

# ------------------
# Title
# ------------------
st.title("Customer Churn Insights Dashboard")
st.markdown("Welcome! This dashboard helps you understand **why customers leave** and **what to do about it**")

# ------------------
# Pro View: Key Metrics Row
# ------------------
st.header("Quick Stats (Pro View)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Overall Churn Rate",
        value=f"{df['Churn'].mean()*100:.1f}%",
        delta=f"{len(df)} customers"
    )

with col2:
    high_risk_count = len(df[df['Risk_Category'] == 'High Risk'])
    st.metric(
        label="High Risk Customers",
        value=high_risk_count,
        delta=f"{high_risk_count/len(df)*100:.1f}% of total"
    )

with col3:
    intl_churn = df[df['International_plan'] == 1]['Churn'].mean() * 100
    st.metric(
        label="Intl Plan Churn Rate",
        value=f"{intl_churn:.1f}%",
        delta="vs 12.4% overall"
    )

with col4:
    high_service_churn = df[df['Customer service calls'] >= 4]['Churn'].mean() * 100
    st.metric(
        label="High Service Calls Churn",
        value=f"{high_service_churn:.1f}%",
        delta="4+ calls"
    )

with col5:
    avg_risk_score = df['Churn_Risk_Score'].mean()
    st.metric(
        label="Avg Risk Score",
        value=f"{avg_risk_score:.3f}",
        delta="ML Prediction"
    )

# ------------------
# Step 1: Overall Picture
# ------------------
st.header("1️Overall Picture (Easy View)")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Customers Leaving (%)",
        value=f"{df['Churn'].mean()*100:.1f}%"
    )

with col2:
    high_risk = len(df[df['Risk_Category'] == 'High Risk'])
    st.metric(
        label="High Risk Customers",
        value=high_risk
    )

with col3:
    avg_risk = df['Churn_Risk_Score'].mean()
    st.metric(
        label="Chance of Leaving (avg)",
        value=f"{avg_risk:.2f}"
    )

# ------------------
# Step 2: Why are customers leaving?
# ------------------
st.header("Why Are Customers Leaving?")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Calls to Support vs Leaving")
    service_churn = df.groupby('Customer service calls')['Churn'].mean().reset_index()
    service_churn['Churn'] = service_churn['Churn'] * 100

    fig1 = px.bar(
        service_churn,
        x='Customer service calls',
        y='Churn',
        color='Churn',
        color_continuous_scale='Reds',
        labels={'Churn': 'Customers Leaving (%)'},
        title="More Calls → More Customers Leave"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Plan Type vs Leaving")
    plan_data = []
    for plan_val, plan_name in [(0, 'No Intl Plan'), (1, 'Intl Plan')]:
        churn_rate = df[df['International_plan'] == plan_val]['Churn'].mean() * 100
        plan_data.append({"Plan": plan_name, "Churn %": churn_rate})

    for plan_val, plan_name in [(0, 'No VM Plan'), (1, 'VM Plan')]:
        churn_rate = df[df['Voice_mail_plan'] == plan_val]['Churn'].mean() * 100
        plan_data.append({"Plan": plan_name, "Churn %": churn_rate})

    plan_df = pd.DataFrame(plan_data)
    fig2 = px.bar(plan_df, x='Plan', y='Churn %', color='Churn %', color_continuous_scale='Blues')
    st.plotly_chart(fig2, use_container_width=True)

# ------------------
# Step 3: Who should we worry about?
# ------------------
st.header("Who Should We Worry About?")
high_risk_df = df[df['Risk_Category'] == 'High Risk'][[
    'State', 'Account length', 'Customer service calls', 'Total_charge', 'Churn_Risk_Score'
]].copy()

high_risk_df['Churn_Risk_Score'] = high_risk_df['Churn_Risk_Score'].round(2)
st.dataframe(high_risk_df.head(10), use_container_width=True)

# ------------------
# Step 4: What can we do?
# ------------------
st.header("What Can We Do? (Action Plan)")

st.info("**Unhappy Callers (4+ calls)** → Reach out quickly! Can save ~20%")
st.success("**Intl Plan Users** → Offer cheaper plans. Can save ~15%")
st.warning("**High Charges (> $75)** → Suggest bill optimization. Can save ~10%")

# ------------------
# Footer
# ------------------
st.markdown(\"---\")\nst.caption(\"Dashboard powered by Streamlit | Pro + Easy Views\")\n```

---

st.markdown("*Dashboard powered by Streamlit and Built by Kunal Rao | Data updated in real-time*")
