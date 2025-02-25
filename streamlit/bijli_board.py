import streamlit as st
import pandas as pd
import re

# Title of the app
st.title("Bijli Board Outage Analysis")

# Upload button
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Show original data counts
        st.write(f"Original data: {len(df)} records")
        
        # Check if required columns exist
        required_columns = ["Feeding Grid", "Division", "Outage Reason", "Category", "Feeder", "Diff in mins"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            st.error("Please check your CSV file format and column names")
            # Display available columns to help troubleshoot
            st.write("Available columns in your file:", df.columns.tolist())
        else:
            # Filter rows where "Outage Reason" starts with "11KV"
            df = df[df["Outage Reason"].str.contains(r'^11[kK][vV]', regex=True)]
            
            # Remove rows where "Outage Reason" starts with "66KV" or "220KV"
            # Using non-capturing group (?:pattern) to avoid the warning
            df = df[~df["Outage Reason"].str.contains(r'^(?:66|220)[kK][vV]', regex=True)]
            
            st.write(f"After filtering for 11KV outages: {len(df)} records")
            
            # Count occurrences of each "Feeding Grid"
            feeding_grid_counts = df["Feeding Grid"].value_counts().reset_index()
            feeding_grid_counts.columns = ["Feeding Grid", "count"]
            
            # Filter to keep only rows where "Feeding Grid" appears more than 2 times
            frequent_grids = feeding_grid_counts[feeding_grid_counts["count"] > 2]["Feeding Grid"]
            df_filtered = df[df["Feeding Grid"].isin(frequent_grids)]
            
            st.write(f"After filtering for frequently affected grids: {len(df_filtered)} records")
            
            # Add count column by merging
            df_display = df_filtered.merge(feeding_grid_counts, on="Feeding Grid")
            
            # Select only the specified columns for display
            columns_to_display = ["Feeding Grid", "Division", "Outage Reason", "Category", "Feeder", "count", "Diff in mins"]
            df_display = df_display[columns_to_display]
            
            # Sort by count (descending)
            df_display = df_display.sort_values(by="count", ascending=False)
            
            # Display the results
            st.write("Filtered and Analyzed Results:")
            st.dataframe(df_display)
            
            # Download option for processed data
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="Download processed data as CSV",
                data=csv,
                file_name="processed_bijli_data.csv",
                mime="text/csv",
            )
            
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
        st.error("Please ensure your CSV has the expected columns and format.")
        # Show detailed error information
        import traceback
        st.text(traceback.format_exc())