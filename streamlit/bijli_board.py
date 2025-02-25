import streamlit as st
import pandas as pd
import re
import numpy as np

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
        required_columns = ["Feeding Grid", "Division", "Outage Reason", "Category", "Feeder", "Diff in mins", "Zone", "Circle", "Start Time"]
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
            
            # Modified: Group only by "Feeding Grid" and "Diff in mins"
            columns_to_group = ["Feeding Grid", "Diff in mins"]
            combined_counts = df.groupby(columns_to_group).size().reset_index(name="count")
            
            # Filter to keep only combinations that appear more than once
            duplicate_records = combined_counts[combined_counts["count"] > 1]
            
            st.write(f"Duplicate records found: {len(duplicate_records)}")
            
            # If we have duplicates, merge them back with original data
            if not duplicate_records.empty:
                # Join the counts back with the original filtered data
                # Use merge to match rows having the same combination of key columns
                df_final = df.merge(duplicate_records, on=columns_to_group)
                
                # Display all columns so differences in other fields are visible
                columns_to_display = ["Feeding Grid", "Zone", "Circle", "Division", "Outage Reason", "Category", "Feeder", "Start Time","Diff in mins", "count"]
                df_display = df_final[columns_to_display].copy()  # Create an explicit copy
                
                # Create a unique group identifier for coloring
                df_display['group_id'] = pd.factorize(df_display['Feeding Grid'] + '_' + df_display['Diff in mins'].astype(str))[0]
                
                # Sort first by group_id to keep groups together, then by count (descending)
                df_display = df_display.sort_values(by=['group_id', 'count'], ascending=[True, False])
                
                # Create a styled dataframe with background colors based on group_id
                def highlight_groups(row):
                    group_id = row['group_id']
                    # Generate a color based on group_id (alternating blue and white)
                    colors = ['#D7DEF8', '#ffffff']  # Light blue and white
                    color = colors[group_id % len(colors)]
                    return [f'background-color: {color}; color: black; font-weight: normal'] * len(row)
                
                # Create styled dataframe
                styled_df = df_display.style.apply(highlight_groups, axis=1)
                
                # Remove group_id column before displaying
                df_display = df_display.drop(columns=['group_id'])
                
                # Display the results
                st.write("Duplicate Entries Analysis (grouped by color):")
                st.dataframe(styled_df)
                
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