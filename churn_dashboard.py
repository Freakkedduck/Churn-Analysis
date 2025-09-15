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
# Custom CSS for Cards
# ------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #121212;
        color: #FFFFFF;
    }
    h1, h2, h3 {
        font-weight: 600;
        color: #1DB954;
    }
    .explanation {
        font-size: 0.9rem;
        color: #BBBBBB;
        margin-bottom: 15px;
    }
    .stExpander {
        background-color: #1E1E1E !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
        margin-bottom: 15px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
    }
    .stExpander summary {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
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
# Title + Dataset Info
# ------------------
st.title("Customer Churn Insights Dashboard")
st.markdown("Welcome! This dashboard helps you understand why customers leave and what to do about it.")

st.markdown(f"""
<div style="background-color:#1E1E1E; padding:15px; border-radius:10px; margin-bottom:20px; box-shadow:0 2px 6px rgba(0,0,0,0.3);">
<h4 style="color:#1DB954; margin-bottom:8px;">Dataset Used</h4>
<p><b>churn_analysis_results.csv</b> with telecom customer records.<br>
Includes plans, support calls, charges, churn status & risk scores.</p>
<p><b>Total Records:</b> {len(df)} customers | <b>Columns:</b> {len(df.columns)}</p>
</div>
""", unsafe_allow_html=True)

# ------------------
# Section 1: Quick Stats
# ------------------
with st.expander("Quick Stats (Pro View)", expanded=False):
    st.markdown('<p class="explanation">Expert-level overview of churn risks and patterns.</p>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Overall Churn Rate", f"{df['Churn'].mean()*100:.1f}%", f"{len(df)} customers")
    with col2:
        high_risk_count = len(df[df['Risk_Category'] == 'High Risk'])
        st.metric("High Risk Customers", high_risk_count, f"{high_risk_count/len(df)*100:.1f}% of total")
    with col3:
        intl_churn = df[df['International_plan'] == 1]['Churn'].mean() * 100
        st.metric("Intl Plan Churn", f"{intl_churn:.1f}%", "vs 12.4% overall")
    with col4:
        high_service_churn = df[df['Customer service calls'] >= 4]['Churn'].mean() * 100
        st.metric("High Support Calls Churn", f"{high_service_churn:.1f}%", "4+ calls")
    with col5:
        avg_risk_score = df['Churn_Risk_Score'].mean()
        st.metric("Avg Risk Score", f"{avg_risk_score:.3f}", "ML Prediction")

# ------------------
# Section 2: Overall Picture
# ------------------
with st.expander("Overall Picture (Easy View)", expanded=False):
    st.markdown('<p class="explanation">A beginner-friendly snapshot of churn: how many leave, who is high risk, and the average chance of leaving.</p>', unsafe_allow_html=True)

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
# Section 3: Why Are Customers Leaving?
# ------------------
with st.expander("Why Are Customers Leaving?", expanded=False):
    st.markdown('<p class="explanation">Charts highlight the main churn drivers: frequent support calls and unsuitable plan types.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        service_churn = df.groupby('Customer service calls')['Churn'].mean().reset_index()
        service_churn['Churn'] = service_churn['Churn'] * 100
        fig1 = px.bar(service_churn, x='Customer service calls', y='Churn',
                      color='Churn', color_continuous_scale='Greens',
                      labels={'Churn': 'Leaving (%)'},
                      title="More Calls → More Customers Leave",
                      template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
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
# Section 4: Who Should We Worry About?
# ------------------
with st.expander("Who Should We Worry About?", expanded=False):
    st.markdown('<p class="explanation">A quick look at the top 10 high-risk customers who should be contacted first.</p>', unsafe_allow_html=True)
    high_risk_df = df[df['Risk_Category'] == 'High Risk'][[
        'State', 'Account length', 'Customer service calls', 'Total_charge', 'Churn_Risk_Score'
    ]].copy()
    high_risk_df['Churn_Risk_Score'] = high_risk_df['Churn_Risk_Score'].round(2)
    st.dataframe(high_risk_df.head(10), use_container_width=True)

# ------------------
# Section 5: What Can We Do? (Action Plan)
# ------------------
with st.expander("What Can We Do? (Action Plan)", expanded=False):
    st.markdown('<p class="explanation">Actionable strategies to reduce churn and retain more customers.</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="spotify-card">
        <h4>Unhappy Callers</h4>
        Customers with 4+ calls → Reach out quickly.<br>
        <b>Potential churn reduction: ~20%</b>
    </div>
    <div class="spotify-card">
        <h4>International Plan Users</h4>
        Offer cheaper plans & usage alerts.<br>
        <b>Potential churn reduction: ~15%</b>
    </div>
    <div class="spotify-card">
        <h4>High Charges</h4>
        Suggest bill optimization for >$75 users.<br>
        <b>Potential churn reduction: ~10%</b>
    </div>
    """, unsafe_allow_html=True)

# ------------------
# Footer
# ------------------
st.markdown("---")
st.caption("Streamlit Dashboard | Built by Kunal")
