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
            # Remove rows where "Outage Reason" starts with "66KV" or "220KV"
            # Using non-capturing group (?:pattern) to avoid the warning
            df = df[~df["Outage Reason"].str.contains(r'^(?:66|220)[kK][vV]', regex=True)]
            
            st.write(f"After filtering out 66KV/220KV outages: {len(df)} records")
            
            # Group by all key columns to find exact duplicates
            # Count occurrences of each unique combination across key columns
            columns_to_group = ["Feeding Grid", "Division", "Outage Reason", "Category", "Feeder", "Diff in mins"]
            combined_counts = df.groupby(columns_to_group).size().reset_index(name="count")
            
            # Filter to keep only combinations that appear more than once
            duplicate_records = combined_counts[combined_counts["count"] > 1]
            
            st.write(f"Duplicate records found: {len(duplicate_records)}")
            
            # If we have duplicates, merge them back with original data
            if not duplicate_records.empty:
                # Join the counts back with the original filtered data
                # Use merge to match rows having the same combination of key columns
                df_final = df.merge(duplicate_records, on=columns_to_group)
                
                # Sort by count (descending)
                df_final = df_final.sort_values(by="count", ascending=False)
                
                # Select only the columns we want to display
                columns_to_display = ["Feeding Grid", "Division", "Outage Reason", "Category", "Feeder", "count", "Diff in mins"]
                df_display = df_final[columns_to_display]
                
                # Display the results
                st.write("Duplicate Entries Analysis:")
                st.dataframe(df_display)
                
                # Download option for processed data
                csv = df_display.to_csv(index=False)
                st.download_button(
                    label="Download processed data as CSV",
                    data=csv,
                    file_name="processed_bijli_data.csv",
                    mime="text/csv",
                )
            else:
                st.write("No duplicate entries found, all entries are unique!")
            
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
        st.error("Please ensure your CSV has the expected columns and format.")
        # Show detailed error information
        import traceback
        st.text(traceback.format_exc())