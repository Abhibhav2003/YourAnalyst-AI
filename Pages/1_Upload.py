import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from bs4 import BeautifulSoup
from streamlit_lottie import st_lottie

# ------------------- Extract From Web ------------------ #
# Function to extract tables from a webpage
def Func(webpage):
    soup = BeautifulSoup(webpage.content, "html.parser")
    list_of_tables = list(soup.find_all("table"))
    list_of_trs = []
    for i in list_of_tables:
        list_of_trs.append(i.find_all("tr"))
    return list_of_trs

def Extract(URL, HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/132.0.0.0 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'}):
    webpage = requests.get(URL, headers=HEADERS)
    if webpage.status_code == 200:
        return Func(webpage)
    else:
        st.error("Failed to fetch webpage content")
        return None

def WebScrape(url):
    result = []
    dicti = {}
    m = 1
    list_of_trs = Extract(url)
    if list_of_trs:
        for k in list_of_trs:
            for i in k:
                data = [j.text.strip() for j in i.find_all("td")]
                if data:
                    result.append(np.array(data))
            index = "table" + str(m)
            dicti[index] = result
            result = []
            m += 1
    return dicti

def GetDfs(result):
    dict_dfs = {}
    for k in result:
        df = pd.DataFrame(result[k])
        dict_dfs[k] = df
    return dict_dfs

# ----------------------------------------------------------- #

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Streamlit UI
st.title("Data Acquisition")

# Dropdown to select data source
option = st.selectbox("Choose Data Source", ["Upload File", "Get Data from Web"])

if option == "Upload File":
    st.header("Upload Files")
    uploaded_file = st.file_uploader("Choose Your File", type=['csv', 'xlsx', 'txt'])

    if uploaded_file is not None:
        progress_container = st.empty()
        bar = progress_container.progress(0)

        for percent_complete in range(100):
            time.sleep(0.01)
            bar.progress(percent_complete + 1)

        st.session_state["uploaded_file"] = uploaded_file 
        st.success("File Uploaded")
        anim_placeholder = st.empty()
        anim = load_lottie_url("https://lottie.host/a9bdf4d8-ce93-46e7-85dd-01937e872f64/rBFm9SBGgF.json")
        st_lottie(anim, height=100, key="done")
        progress_container.empty()

elif option == "Get Data from Web":
    st.header("Get Data from Web")
    url = st.text_input("Enter URL to scrape tables:", "")

    if st.button("Extract Tables"):
        if url:
            with st.spinner("Extracting tables..."):
                data = WebScrape(url)
                if data:
                    dict_dfs = GetDfs(data)
                    st.session_state.tables_extracted = dict_dfs
                    st.success("Tables extracted successfully!")
                else:
                    st.error("No tables found on the page.")
        else:
            st.warning("Please enter a valid URL.")

    if "tables_extracted" in st.session_state and st.session_state.tables_extracted:
        table_options = list(st.session_state.tables_extracted.keys())
        selected_table = st.selectbox("Select a table to display:", table_options)
        show_table = st.checkbox("Show Selected Table")
        
        if show_table and selected_table:
            st.session_state.selected_df = st.session_state.tables_extracted[selected_table]
            st.subheader(f"{selected_table}")
            st.dataframe(st.session_state.selected_df)
