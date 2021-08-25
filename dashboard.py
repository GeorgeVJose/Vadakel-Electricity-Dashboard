import gspread
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Vadakel Electricity Dashboard",
    page_icon="⚡",
    layout='wide'
)

credentials = {
    "type": st.secrets['type'],
    "project_id": st.secrets['project_id'],
    "private_key_id": st.secrets['private_key_id'],
    "private_key": st.secrets['private_key'],
    "client_email": st.secrets['client_email'],
    "client_id": st.secrets['client_id'],
    "auth_uri": st.secrets['auth_uri'],
    "token_uri": st.secrets['token_uri'],
    "auth_provider_x509_cert_url": st.secrets['auth_provider_x509_cert_url'],
    "client_x509_cert_url": st.secrets['client_x509_cert_url']
}

graph_template = 'simple_white'


@st.cache
def get_data():
    # client = gspread.service_account(
    #     filename='./electricity-dashboard-324008-0f4879b1f277.json')
    client = gspread.service_account_from_dict(credentials)
    sheets = client.open_by_key('1USbS6ptSKqm3UT5LdwgvVru174eMq_g5HnfGOASivJI')
    data = sheets.sheet1.get_all_values()

    df = pd.DataFrame(data[1:], columns=data[0])
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]])
    df[df.columns[1:-1]] = df[df.columns[1:-1]
                              ].apply(pd.to_numeric, errors='coerce')
    return df


def get_expected_bill_date():
    current_month = df['Bill Date'].dt.month.tail(1).to_list()[0]
    prev_month_indices = df.loc[df['Bill Date'].dt.month ==
                                current_month][:-1].index
    avg_days = df['Bill Date'].diff()[prev_month_indices + 1].mean()
    next_day = df['Bill Date'].tail(1).values[0] + avg_days
    return next_day.strftime('%d %B %Y')


df = get_data()


st.markdown("<h1 style='text-align: center;'>⚡Vadakel Electricity Dashboard⚡</h1>",
            unsafe_allow_html=True)

st.write('')
st.write('')

st.sidebar.title("Overall Metrics")
st.sidebar.caption(
    f"Data from {df['Bill Date'].dt.strftime('%d %B %Y').head(1).to_list()[0]} to {df['Bill Date'].dt.strftime('%d %B %Y').tail(1).to_list()[0]}")
st.sidebar.metric(label="Amount Paid",
                  value=f"₹ {float(df['Payable'].sum())}"
                  )
st.sidebar.metric(label="Energy Charges",
                  value=f"₹ {float(df['Energy Charges'].sum())}"
                  )
st.sidebar.metric(label="Units Consumed",
                  value=f"{int(df['Consumption'].sum())} kWh"
                  )

st.sidebar.markdown("***")
st.sidebar.metric(label="Estimated Bill Date",
                  value=get_expected_bill_date()
                  )

df = df.copy()
df[df.columns[0]] = df[df.columns[0]].dt.strftime('%d %B %Y')

currentinfo1, currentinfo2, currentinfo3 = st.columns(3)
with currentinfo1:
    st.metric(
        label="Current Bill Amount",
        value=f"₹ {float(df['Payable'].tail(1))}",
        delta=float((df['Payable'].tail(1) - df['Payable'].mean()).round(2)),
        delta_color='inverse'
    )
with currentinfo2:
    st.metric(
        label="Current Energy Charges",
        value=f"₹ {float(df['Energy Charges'].tail(1))}",
        delta=float((df['Energy Charges'].tail(1) -
                    df['Energy Charges'].mean()).round(2)),
        delta_color='inverse'
    )
with currentinfo3:
    st.metric(
        label="Current Units Consumed",
        value=f"{float(df['Consumption'].tail(1))} kWh",
        delta=float((df['Consumption'].tail(1) -
                    df['Consumption'].mean()).round(2)),
        delta_color='inverse'
    )

st.write('')
st.write('')

fig3 = px.bar(
    df,
    x='Bill Date',
    # y='Payable',
    y=['Fixed Charges', 'Meter Rent', 'Duty', 'Energy Charges'],
    color='Payable',
    template=graph_template,
    hover_data=['Payable', 'Logs']
)
fig3.update_layout(
    title={
        'text': "Bill Amount",
        'y': 0.92,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    }
)
fig3.add_shape(
    type='line',
    line_width=3, opacity=1,
    line_color="salmon", line_dash="dash",
    xref='paper', x0=0, x1=1,
    yref='y', y0=df['Payable'].mean(), y1=df['Payable'].mean()
)
st.plotly_chart(
    fig3,
    use_container_width=True
)

header1, header2 = st.columns(2)
with header1:
    fig1 = px.area(
        df,
        x='Bill Date',
        y='Price per Unit',
        markers=True,
        template=graph_template
    )
    fig1.update_layout(
        title={
            'text': "Price Per Unit",
            'y': 0.92,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    st.plotly_chart(
        fig1
    )

with header2:
    fig2 = px.line(
        df,
        x='Bill Date',
        y=['Consumption', 'Average'],
        # markers=True,
        template=graph_template
    )
    fig2.update_layout(
        title={
            'text': "Unit Consumption & Average",
            'y': 0.92,
            'x': 0.45,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    st.plotly_chart(
        fig2
    )


with st.expander("Raw Data"):
    highlight_columns = np.concatenate(
        (df.columns[3:5], df.columns[7:9], df.columns[12:14]), axis=None)
    st.dataframe(df.style.highlight_max(
        color='#F63366', subset=highlight_columns, axis=0))
