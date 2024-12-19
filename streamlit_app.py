import streamlit as st
import pandas as pd
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="AI IVR Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

@st.cache_data
def load_data():
    """
    Load and prepare the data from base_dod_data.csv
    We will rename certain columns to match the desired naming convention.
    """
    DATA_FILENAME = Path(__file__).parent / 'data/base_dod_data.csv'
    df = pd.read_csv(DATA_FILENAME)
    
    # Convert date_ column to datetime
    if df['date_'].dtype == 'object':
        df['date_'] = pd.to_datetime(df['date_'])
    
    # Rename columns to match the requested naming:
    rename_map = {
        "sb_sessions": "sb_hardware_sessions",
        "sb_messages": "sb_hardware_messages",
        "edc_sessions": "edc_hardware_sessions",
        "edc_messages": "edc_hardware_messages",
        "payment_acceptence_sessions": "payment_acceptance_sessions",
        "payment_acceptence_messages": "payment_acceptance_messages"
    }
    df.rename(columns=rename_map, inplace=True)
    
    return df

df = load_data()

# Mapping display names to column name prefixes
category_mapping = {
    "Soundbox Hardware": "sb_hardware",
    "Device Return": "device_return",
    "Business Loan": "business_loan",
    "Customer Care": "customer_care",
    "Profile": "profile",
    "EDC Hardware": "edc_hardware",
    "Payment Acceptence": "payment_acceptance",
    "Refund": "refund",
    "Rental Charges": "rental_charges",
    "Generic Query": "generic_query",
    "Settlement & Deductions": "settlement_deductions",
    "Others": "other"
}

st.title("AI IVR Dashboard")

st.markdown("""
Welcome to the AI IVR Dashboard.  
Use the filters below to explore daily sessions/messages across different intent categories.
""")

# Overall Metrics
st.subheader("Overall Metrics")

col1, col2 = st.columns(2)
with col1:
    total_sessions = df['overall_sessions'].sum()
    st.metric("Total Sessions (Nov Upwards)", f"{total_sessions:,}")

with col2:
    total_messages = df['overall_messages'].sum()
    st.metric("Total Messages (Nov Upwards)", f"{total_messages:,}")

st.markdown("---")

# Filters Above Charts
st.header("Filters")

col_cat = st.columns([2])[0]

with col_cat:
    selected_categories = st.multiselect(
        "Select categories:",
        list(category_mapping.keys()),
        default=[
            "Soundbox Hardware",
            "Business Loan",
            "Profile",
            "Payment Acceptence",
            "Settlement & Deductions",
            "EDC Hardware"
        ]
    )

st.markdown("---")

filtered_df = df

# Filtered Overall Metrics
st.subheader("Filtered Overall Metrics")
col3, col4 = st.columns(2)
with col3:
    filtered_total_sessions = filtered_df['overall_sessions'].sum()
    st.metric("Total Sessions (Filtered)", f"{filtered_total_sessions:,}")

with col4:
    filtered_total_messages = filtered_df['overall_messages'].sum()
    st.metric("Total Messages (Filtered)", f"{filtered_total_messages:,}")

st.markdown("""
*These values reflect activity across all dates since we've removed the date filter.*  
""")

selected_intent_sessions = [f"{category_mapping[cat]}_sessions" for cat in selected_categories]
selected_intent_messages = [f"{category_mapping[cat]}_messages" for cat in selected_categories]

st.header("Daily Intent-wise Sessions")

if selected_categories:
    sessions_melted = filtered_df.melt(
        id_vars=['date_'],
        value_vars=selected_intent_sessions,
        var_name='Intent',
        value_name='Sessions'
    )

    sessions_melted['Intent'] = sessions_melted['Intent'].apply(
        lambda x: [k for k,v in category_mapping.items() if x.startswith(v)][0]
    )

    # Ensure zero is included
    if not sessions_melted.empty:
        min_date = sessions_melted['date_'].min()
        # Add a zero baseline row
        zero_row = pd.DataFrame({'date_':[min_date], 'Intent':[sessions_melted['Intent'].iloc[0]], 'Sessions':[0]})
        sessions_melted = pd.concat([sessions_melted, zero_row], ignore_index=True)
        
        # Add a top buffer row to ensure top value is fully visible
        max_val = sessions_melted['Sessions'].max()
        top_buffer = pd.DataFrame({'date_':[min_date], 'Intent':[sessions_melted['Intent'].iloc[0]], 'Sessions':[max_val*1.05]})
        sessions_melted = pd.concat([sessions_melted, top_buffer], ignore_index=True)

    st.line_chart(
        data=sessions_melted,
        x='date_',
        y='Sessions',
        color='Intent',
        height=600
    )
else:
    st.info("Please select at least one category.")

st.markdown("""
Use this chart to analyze daily trends in sessions across intents.
""")

st.header("Daily Intent-wise Messages")

if selected_categories:
    messages_melted = filtered_df.melt(
        id_vars=['date_'],
        value_vars=selected_intent_messages,
        var_name='Intent',
        value_name='Messages'
    )

    messages_melted['Intent'] = messages_melted['Intent'].apply(
        lambda x: [k for k,v in category_mapping.items() if x.startswith(v)][0]
    )

    # Ensure zero is included
    if not messages_melted.empty:
        min_date = messages_melted['date_'].min()
        # Add a zero baseline row
        zero_row_msg = pd.DataFrame({'date_':[min_date], 'Intent':[messages_melted['Intent'].iloc[0]], 'Messages':[0]})
        messages_melted = pd.concat([messages_melted, zero_row_msg], ignore_index=True)
        
        # Add a top buffer row for messages
        max_val_msg = messages_melted['Messages'].max()
        top_buffer_msg = pd.DataFrame({'date_':[min_date], 'Intent':[messages_melted['Intent'].iloc[0]], 'Messages':[max_val_msg*1.05]})
        messages_melted = pd.concat([messages_melted, top_buffer_msg], ignore_index=True)

    st.line_chart(
        data=messages_melted,
        x='date_',
        y='Messages',
        color='Intent',
        height=600
    )
else:
    st.info("Please select at least one category.")

st.markdown("""
Use this chart to analyze daily trends in messages across intents.
""")
