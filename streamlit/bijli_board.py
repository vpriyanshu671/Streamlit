import streamlit as st
import pandas as pd

# Title of the app
st.title("CSV File Uploader")

# Upload button
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    
    # Select only the specified columns
    columns_to_display = ["Feeding Grid", "Outage Reason", "Diff in mins"]
    df = df[columns_to_display]
    
    # Filter rows where "Outage Reason" is one of the specified values
    outage_reasons = ["11kV line/DT Maintenance Work", "11kV line Disc/Pin Insulator damaged/ flashed"]
    df = df[df["Outage Reason"].isin(outage_reasons)]
    
    # Count occurrences of each "Feeding Grid" and include "Outage Reason" and "Diff in mins"
    df_grouped = df.groupby(["Feeding Grid", "Outage Reason", "Diff in mins"]).size().reset_index(name='count')
    
    # Filter groups with more than one occurrence
    df_grouped = df_grouped[df_grouped['count'] > 1]
    
    # Sort the dataframe by "count"
    df_grouped = df_grouped.sort_values(by="count", ascending=False)
    
    # Display the dataframe
    st.write("Uploaded CSV file:")
    st.dataframe(df_grouped)

# requirements
# pip install streamlit pandas