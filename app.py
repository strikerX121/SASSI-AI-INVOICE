import streamlit as st
from os.path import exists
import os
from analyse import analyze_invoice

files = st.file_uploader("Upload Invoices (PDF)", ['pdf','jpg','png','gif', 'tiff', 'bmp'], accept_multiple_files=True)
analyze = st.button("Analyze")

if analyze:
    if not files:
        st.warning("No files uploaded.")

    else:
        for file in files:
            st.header(f"Invoice: {file.name}")
            details = analyze_invoice(file)
            for i in range(len(details['description'])):
                with st.container():
                    cols = st.columns(2)
                    st.markdown(f"""<style> div[data-testid="column"]:nth-of-type({2*i}) {{ text-align: end; }} </style>""", unsafe_allow_html=True)
                    with cols[0]:
                        st.subheader(details['description'][i])
                        st.write("category: ", details['categories'][i])
                    with cols[1]:
                        try:
                            st.write(details['unit_price'][i])
                        except IndexError:
                            st.write(details['amount'][i])
            cols = st.columns(2)
            st.markdown(f"""<style> div[data-testid="column"]:nth-of-type({2}) {{ text-align: end; }} </style>""", unsafe_allow_html=True)
            with cols[0]:
                st.header("Total")
            with cols[1]:
                if details['subtotal'] == 0:
                    st.write(details['total'])
                else:
                    st.write(details['subtotal'])

            st.markdown("---")