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
# Custom CSS for Spotify Theme
# ------------------
st.markdown("""
    <style>
    /* Import Poppins font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        background-color: #191414;
        color: #FFFFFF;
    }
    h1, h2, h3, h4 {
        font-weight: 600;
        color: #1DB954;
    }
    .stMetric {
        background: #282828;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: #FFFFFF;
    }
    .stMetric label {
        color: #AAAAAA;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    /* Custom cards for Action Plan */
    .spotify-card {
        background-color: #282828;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        color: #FFFFFF;
    }
    .spotify-card h4 {
        color: #1DB954;
        margin-bottom: 10px;
    }
    .explanation {
        font-size: 0.9rem;
        color: #BBBBBB;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

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
st.header("Quick Stats")
st.markdown('<p class="explanation">These are the raw numbers that give an expert-level overview of churn risk in your customer base.</p>', unsafe_allow_html=True)

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
st.header("1. Overall Picture (Easy View)")
st.markdown('<p class="explanation">Here we simplify things: how many customers are leaving, how many are high risk, and what the average chance of leaving looks like.</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Customers Leaving (%)", f"{df['Churn'].mean()*100:.1f}%")

with col2:
    high_risk = len(df[df['Risk_Category'] == 'High Risk'])
    st.metric("High Risk Customers", high_risk)

with col3:
    avg_risk = df['Churn_Risk_Score'].mean()
    st.metric("Chance of Leaving (avg)", f"{avg_risk:.2f}")

# ------------------
# Step 2: Why are customers leaving?
# ------------------
st.header("2. Why Are Customers Leaving?")
st.markdown('<p class="explanation">These charts show the biggest reasons customers leave: too many support calls and plan choices that don’t fit their needs.</p>', unsafe_allow_html=True)

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
        color_continuous_scale='Greens',
        labels={'Churn': 'Customers Leaving (%)'},
        title="More Calls → More Customers Leave",
        template="plotly_dark"
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
    fig2 = px.bar(plan_df, x='Plan', y='Churn %', color='Churn %',
                  color_continuous_scale='Greens', template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# ------------------
# Step 3: Who should we worry about?
# ------------------
st.header("3. Who Should We Worry About?")
st.markdown('<p class="explanation">Here are the top high-risk customers who are most likely to leave soon. These are your priority for retention.</p>', unsafe_allow_html=True)

high_risk_df = df[df['Risk_Category'] == 'High Risk'][[
    'State', 'Account length', 'Customer service calls', 'Total_charge', 'Churn_Risk_Score'
]].copy()
high_risk_df['Churn_Risk_Score'] = high_risk_df['Churn_Risk_Score'].round(2)
st.dataframe(high_risk_df.head(10), use_container_width=True)

# ------------------
# Step 4: What can we do?
# ------------------
st.header("4. What Can We Do? (Action Plan)")
st.markdown('<p class="explanation">Finally, here are simple, actionable strategies you can apply to reduce churn and keep more customers happy.</p>', unsafe_allow_html=True)

st.markdown("""
<div class="spotify-card">
    <h4>Unhappy Callers</h4>
    Customers with 4+ calls → Reach out quickly! <br>
    <b>Can save ~20%</b>
</div>
<div class="spotify-card">
    <h4>Intl Plan Users</h4>
    Offer cheaper plans & usage alerts. <br>
    <b>Can save ~15%</b>
</div>
<div class="spotify-card">
    <h4>High Charges</h4>
    Suggest bill optimization for >$75 users. <br>
    <b>Can save ~10%</b>
</div>
""", unsafe_allow_html=True)

# ------------------
# Footer
# ------------------
st.markdown("---")
st.caption("Built by Kunal Rao | Powered by Streamlit")
