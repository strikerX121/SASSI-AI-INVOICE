import streamlit as st
from os.path import exists
import os
from analyse import analyze_invoice
import pandas as pd


files = st.file_uploader("Upload Invoices (PDF)", ['pdf','jpg','png','gif', 'tiff', 'bmp'], accept_multiple_files=True)
analyze = st.button("Analyze")

df = pd.DataFrame(columns=["Category", "Item", "Price"])

if analyze:
    if not files:
        st.warning("No files uploaded.")
    else:
        df = pd.DataFrame(columns=['Category', 'Item', 'Price'])
        for file in files:
            st.header(f"Invoice: {file.name}")
            details = analyze_invoice(file)
            
            file_df = pd.DataFrame({
                'Category': details['categories'],
                'Item': details['description'],
                'Price': details['amount']
            })      
            
            head_row = pd.Series({'Category': file.name, 'Item': pd.NA, 'Price': pd.NA}).to_frame().T
            file_df = pd.concat([head_row, file_df], ignore_index=True)
            
            for i in range(1, len(file_df)):  
                with st.container():
                    cols = st.columns(2)
                    st.markdown(f"""<style> div[data-testid="column"]:nth-of-type({2*i}) {{ text-align: end; }} </style>""", unsafe_allow_html=True)
                    with cols[0]:
                        st.subheader(file_df.iloc[i]['Item'])
                        st.write("Category: ", file_df.iloc[i]['Category'])
                    with cols[1]:
                        try:
                            st.write(details['amount'][i-1])  
                        except (IndexError, KeyError):
                            st.write(file_df.iloc[i]['Price'])
                      
            cols = st.columns(2)
            st.markdown(f"""<style> div[data-testid="column"]:nth-of-type({2}) {{ text-align: end; }} </style>""", unsafe_allow_html=True)
            with cols[0]:
                st.header("Total")
            with cols[1]:
                if details['subtotal'] == 0:
                    try:
                        st.write(details['total'])
                    except KeyError:
                        st.write(0)
                else:
                    st.write(details['subtotal'])
            
            empty_row = pd.Series({'Category': pd.NA, 'Item': pd.NA, 'Price': pd.NA}).to_frame().T
            file_df = pd.concat([file_df, empty_row], ignore_index=True)
                  
            df = pd.concat([df, file_df], ignore_index=True)
            
            st.markdown("---")
         
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="output.csv",
            mime="text/csv",
            help="Click here to download the invoice data as a CSV file."
        )