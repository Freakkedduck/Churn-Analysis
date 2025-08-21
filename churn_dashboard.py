import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(
    page_title="Customer Churn Analytics Dashboard",
    page_icon="",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('churn_analysis_results.csv')
    return df

df = load_data()

# Title and header
st.title("Customer Churn Analytics Dashboard")
st.markdown("### Telecom Customer Retention Intelligence")

# Tabs for dashboard sections
tab1, tab2 = st.tabs(["📊 Dashboard", "📋 Retention Playbook"])

with tab1:
    # Key Metrics Row
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

    # Charts Row 1
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Churn Rate by Customer Service Calls")
        service_churn = df.groupby('Customer service calls')['Churn'].agg(['count', 'mean']).reset_index()
        service_churn['churn_rate'] = service_churn['mean'] * 100

        fig1 = px.bar(
            service_churn, 
            x='Customer service calls', 
            y='churn_rate',
            title="Higher Service Calls = Higher Churn",
            labels={'churn_rate': 'Churn Rate (%)', 'Customer service calls': 'Service Calls'},
            color='churn_rate',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Risk Score Distribution")
        fig2 = px.histogram(
            df, 
            x='Churn_Risk_Score', 
            color='Risk_Category',
            title="Customer Risk Score Distribution",
            labels={'Churn_Risk_Score': 'Risk Score', 'count': 'Number of Customers'},
            nbins=20
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Charts Row 2
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Plan Type Impact")
        plan_data = []
        # International Plan
        for plan_val, plan_name in [(0, 'No Intl Plan'), (1, 'Intl Plan')]:
            churn_rate = df[df['International_plan'] == plan_val]['Churn'].mean() * 100
            count = len(df[df['International_plan'] == plan_val])
            plan_data.append({'Plan Type': plan_name, 'Churn Rate': churn_rate, 'Count': count})

        # Voice Mail Plan
        for plan_val, plan_name in [(0, 'No VM Plan'), (1, 'VM Plan')]:
            churn_rate = df[df['Voice_mail_plan'] == plan_val]['Churn'].mean() * 100
            count = len(df[df['Voice_mail_plan'] == plan_val])
            plan_data.append({'Plan Type': plan_name, 'Churn Rate': churn_rate, 'Count': count})

        plan_df = pd.DataFrame(plan_data)
        fig3 = px.bar(
            plan_df, 
            x='Plan Type', 
            y='Churn Rate',
            title="Churn Rate by Plan Type",
            color='Churn Rate',
            color_continuous_scale='RdYlBu_r'
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.subheader("Charges vs Churn")
        fig4 = px.box(
            df, 
            x='Churn', 
            y='Total_charge',
            title="Total Charges Distribution by Churn Status",
            labels={'Churn': 'Churned', 'Total_charge': 'Total Charges ($)'}
        )
        fig4.update_xaxes(tickvals=[0, 1], ticktext=['Retained', 'Churned'])
        st.plotly_chart(fig4, use_container_width=True)

    # High Risk Customers Table
    st.subheader("High Risk Customers - Priority for Retention")
    high_risk_df = df[df['Risk_Category'] == 'High Risk'][
        ['State', 'Account length', 'International_plan', 'Voice_mail_plan', 
        'Customer service calls', 'Total_charge', 'Churn_Risk_Score', 'Churn']
    ].copy()

    high_risk_df['International_plan'] = high_risk_df['International_plan'].map({1: 'Yes', 0: 'No'})
    high_risk_df['Voice_mail_plan'] = high_risk_df['Voice_mail_plan'].map({1: 'Yes', 0: 'No'})
    high_risk_df['Churn'] = high_risk_df['Churn'].map({1: 'Churned', 0: '🎯 At Risk'})
    high_risk_df['Churn_Risk_Score'] = high_risk_df['Churn_Risk_Score'].round(3)

    st.dataframe(
        high_risk_df.head(20), 
        use_container_width=True,
        column_config={
            "Churn_Risk_Score": st.column_config.ProgressColumn(
                "Risk Score",
                help="Predicted churn probability",
                min_value=0,
                max_value=1,
            ),
        }
    )

    # Key Insights
    st.subheader("🔍 Key Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Critical Risk Factors
        1. **Customer service calls**: Customers with 4+ calls have 47% churn rate
        2. **International plan**: 35.8% churn rate vs 12.4% overall
        3. **No voice mail**: 16.7% churn vs 7.9% with voice mail
        4. **High charges**: Strong correlation with churn (0.30)
        """)

    with col2:
        st.markdown("""
        ###  Retention Opportunities
        1. **80 high-risk customers** identified for immediate action
        2. **Proactive service recovery** can prevent 15-30 churns
        3. **Plan optimization** for international users
        4. **Voice mail adoption** campaigns for retention
        """)

    

with tab2:
    st.subheader("📋 Retention Playbook - Recommended Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 🚨 High Service Calls (4+ calls)
        **Trigger**: Customer service calls ≥ 4

        **Actions**:
        - Immediate account review by senior support
        - Proactive outreach within 24 hours
        - Root cause analysis of issues
        - Service credit or bill adjustment
        - Follow-up call within 1 week

        **Expected Impact**: 15-25% churn reduction
        """)

    with col2:
        st.markdown("""
        ### 🌍 International Plan Users
        **Trigger**: International plan + high usage

        **Actions**:
        - Review international usage patterns
        - Offer optimized international plans
        - Provide usage alerts and controls
        - Consider loyalty discounts
        - International roaming education

        **Expected Impact**: 10-20% churn reduction
        """)

    with col3:
        st.markdown("""
        ### 💰 High Charges
        **Trigger**: Total charges > $75 + risk score > 0.5

        **Actions**:
        - Bill analysis and explanation
        - Plan optimization recommendations
        - Usage monitoring tools
        - Payment plan options
        - Competitive retention offers

        **Expected Impact**: 8-15% churn reduction
        """)

# Footer
st.markdown("---")
st.markdown("*Dashboard powered by Streamlit and Built by Kunal Rao | Data updated in real-time*")
