import plotly.graph_objects as go
import plotly.io as pio

# Data for service calls churn analysis
service_calls = [0, 1, 2, 3, 4, 5, 6]
churn_rate = [9.2, 9.7, 16.6, 8.6, 36.4, 64.7, 80.0]
customer_count = [142, 236, 151, 81, 33, 17, 5]

# Create bar chart
fig = go.Figure(data=go.Bar(
    x=service_calls,
    y=churn_rate,
    marker_color='#1FB8CD',
    text=[f'{rate}%' for rate in churn_rate],
    textposition='outside',
    hovertemplate='Calls: %{x}<br>Churn Rate: %{y}%<br>Customers: %{customdata}<extra></extra>',
    customdata=customer_count,
    cliponaxis=False
))

fig.update_layout(
    title='Churn Rate by Service Calls',
    xaxis_title='Service Calls',
    yaxis_title='Churn Rate (%)'
)

fig.update_xaxes(tickmode='linear', tick0=0, dtick=1)
fig.update_yaxes(range=[0, max(churn_rate) * 1.1])

fig.write_image('churn_service_calls.png')