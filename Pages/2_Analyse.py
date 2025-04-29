import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
from streamlit_lottie import st_lottie
from scipy import stats
from sklearn.linear_model import LinearRegression

# Load Lottie animation
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

anim = load_lottie_url("https://lottie.host/524288b4-4896-4182-918f-16a8904579d9/1OjzOkf3OG.json")

# Function to initialize the DataFrame in session state
def init_dataframe(file):
    if file.name.endswith('csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('txt'):
        df = pd.read_csv(file, delimiter="\t")
    elif file.name.endswith('xlsx'):
        df = pd.read_excel(file)
    else:
        st.error("Unsupported File Format!")
        return None
    return df

if 'uploaded_file' in st.session_state :
    file = st.session_state["uploaded_file"]
    st.session_state.df = init_dataframe(file)  # Ensure it's always updated

elif 'selected_df' in st.session_state :
    st.session_state.df = st.session_state.selected_df  # Ensure web-extracted table updates

else:
    st.warning("No table selected. Please go to the Upload page or extract a table from the web first.")

df = st.session_state.get("df")
if df is not None:
    st.write("## Uploaded Data / Extracted Data")
    st.dataframe(df)
else:
    st.error("Data not loaded.")

# Initialize history in session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Data cleaning functions
def save_state():
    st.session_state.history.append(st.session_state.df.copy())

def undo_last_action():
    if st.session_state.history:
        st.session_state.df = st.session_state.history.pop()
        st.success("Last action undone.")
    else:
        st.warning("No actions to undo.")

def drop_cols(column_name):
    if column_name in df.columns:
        save_state()  # Save current state before making changes
        df.drop(columns=column_name, inplace=True)
        st.success(f"Dropped column: {column_name}")
    else:
        st.error(f"Column '{column_name}' does not exist.")

def trim(a, col_name, expr):
    if col_name in df.columns and isinstance(df[col_name][0], str):
        save_state()  # Save current state before making changes
        if a == 'Right':
            df[col_name] = df[col_name].str.rstrip(expr)
        elif a == 'Left':
            df[col_name] = df[col_name].str.lstrip(expr)
        elif a == 'Both':
            df[col_name] = df[col_name].str.strip(expr)
        else:
            st.error("Please enter valid input!")
    else:
        st.error("Please ensure the column exists and is a string type.")

def SetIndex(column_name):
    save_state()
    df.set_index(column_name,inplace=True)

def DropDuplicates():
    save_state()
    df.drop_duplicates(inplace=True)

def Replace(old_expr,new_expr,column_name):
    if(isinstance(df[column_name][0], str)):
       save_state()
       df[column_name] = df[column_name].str.replace(old_expr,new_expr,regex=True)
    else:
        st.error("Please Convert the Column to String First")

def Fillna(val):
    save_state()
    df.fillna(val,inplace=True)

def dropNA():
    save_state()
    df.dropna(inplace=True)

def DropRowIf(column_name,expr):
    save_state()
    for x in df.index:
      if df.loc[x,column_name] == expr:
         df.drop(x,inplace = True) 

def ResetIndex():
    save_state()
    df = df.reset_index(drop=True)

def ChangeTypeCol(col_name, change):
    save_state()
    if change == 'str':
        df[col_name] = df[col_name].astype(str)

    elif change == 'int':
        try:
            df[col_name] = df[col_name].apply(pd.to_numeric)
        except ValueError:
            st.error("Conversion to integer failed. Check for non-numeric values.")
            
    elif change == 'float':
        try:
            df[col_name] = df[col_name].astype(float)
        except ValueError:
            st.error("Conversion to float failed. Check for non-numeric values.")

# Analysis and statistics
def mean_df(col):
    sum = 0
    n = len(col)
    for i in col:
        sum += i
    mean = sum/n
    return mean

def ConfidenceInterval(col_name, confidence = 0.95):

    data = df[col_name].dropna()
    
    mean = data.mean()
    sem = stats.sem(data)
    
    interval = stats.t.interval(confidence, len(data)-1, loc=mean, scale=sem)
    
    st.write(f"Confidence Interval ({confidence*100}%): {interval}")
    
    x = np.linspace(mean - 4*sem, mean + 4*sem, 1000)
    y = stats.t.pdf(x, len(data)-1, loc=mean, scale=sem)
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='t-distribution curve', line=dict(color='blue')))

    fig.add_trace(go.Scatter(
        x=np.concatenate(([interval[0]], x[(x >= interval[0]) & (x <= interval[1])], [interval[1]])),
        y=np.concatenate(([0], y[(x >= interval[0]) & (x <= interval[1])], [0])),
        fill='toself',
        fillcolor='rgba(144, 238, 144, 0.5)',
        line=dict(color='rgba(255,255,255,0)'), # no line
        name='Confidence Interval Range'
    ))

    # Add a dashed line at the mean
    fig.add_trace(go.Scatter(
        x=[mean, mean],
        y=[0, max(y)],
        mode='lines',
        name=f'Mean: {mean:.2f}',
        line=dict(color='red', dash='dash')
    ))

    # Add a dashed line at lower bound of CI
    fig.add_trace(go.Scatter(
        x=[interval[0], interval[0]],
        y=[0, max(y)*0.9],
        mode='lines',
        name=f'Lower Bound: {interval[0]:.2f}',
        line=dict(color='green', dash='dash')
    ))

    # Add a dashed line at upper bound of CI
    fig.add_trace(go.Scatter(
        x=[interval[1], interval[1]],
        y=[0, max(y)*0.9],
        mode='lines',
        name=f'Upper Bound: {interval[1]:.2f}',
        line=dict(color='green', dash='dash')
    ))

    # Update layout for aesthetics
    fig.update_layout(
        title=f'Confidence Interval ({confidence*100}%) and t-Distribution',
        xaxis_title='Data values',
        yaxis_title='Probability Density',
        showlegend=True,
        width=600,
        height=400,
        template='plotly_dark'  # use dark background like your previous plot
    )
    
    # Display the plot
    st.plotly_chart(fig)

def Covariance(col1, col2):
    meanCol1 = mean_df(df[col1])
    meanCol2 = mean_df(df[col2])
    n = len(df[col1])
    cov = 0
    res = 0
    for i, j in zip(df[col1], df[col2]):
        res = res + (i-meanCol1)*(j-meanCol2)
    cov = res/(n-1)
    st.write(f"Covariance between {col1} and {col2}: {cov:.3f}")

def Correlation(col1, col2):
    meanCol1 = mean_df(df[col1])
    meanCol2 = mean_df(df[col2])

    numerator = 0
    sum_sq_col1 = 0
    sum_sq_col2 = 0

    for i, j in zip(df[col1], df[col2]):
        numerator += (i - meanCol1) * (j - meanCol2)
        sum_sq_col1 += (i - meanCol1) ** 2
        sum_sq_col2 += (j - meanCol2) ** 2

    denominator = (sum_sq_col1 * sum_sq_col2) ** 0.5
    correlation = numerator / denominator

    st.write(f"Correlation between {col1} and {col2}: {correlation:.3f}")

    x = df[col1]
    y = df[col2]

    trace = go.Scatter(
        x=x,
        y=y,
        mode='markers',   
        name='Data',
        marker=dict(color='cyan')
    )

    # Layout
    layout = go.Layout(
        title=f'Scatter plot of {col1} vs {col2}',
        xaxis_title=col1,
        yaxis_title=col2,
        template='plotly_dark',
        width=600,
        height=400
    )

    # Combine and plot
    fig = go.Figure(data=[trace], layout=layout)
    st.plotly_chart(fig)

def StdDev(col_name):
    std = df[col_name].std()
    st.write(f"Standard Deviation of {col_name}: {std:.3f}")

def Predict(x_col, y_col, input_val):
    model = LinearRegression()
    X = df[[x_col]].dropna()
    y = df[y_col].dropna()
    if len(X) != len(y):
        st.error("Mismatch in data size after removing NA values.")
        return
    model.fit(X, y)
    pred = model.predict(np.array([[input_val]]))
    st.success(f"Predicted {y_col} for {x_col}={input_val}: {pred[0]}")

def Overview():
    df.info()

def NullVals():
    st.write(df.isnull().sum())

def Describe():
    st.write("### Description :")
    st.write(df.describe())

def Unique(): 
    st.write(df.nunique())

def Avg(col_name):
    st.write("### Average:")
    mean_val = mean_df(df[col_name])
    mean_val = np.round(mean_val)
    st.markdown(f"<h5 style='font-size:25px; color:orange;'>{mean_val}</h5>", unsafe_allow_html=True)

def Sum(col_name):
    st.write("### Sum:")
    sum_val = df[col_name].sum()
    st.markdown(f"<h5 style='font-size:25px; color:orange;'>{sum_val}</h5>", unsafe_allow_html=True)

def Sorting(col_name , B):
    save_state()
    if B == '0':
       df.sort_values(by = col_name , ascending = True , inplace=True)
       st.write(df)
    elif B == '1':
       df.sort_values(by=col_name , ascending = False , inplace=True)
       st.write(df)
    else:
        st.warning("Enter Appropriate Column")

def TopN(col_name, N):
    top = df.sort_values(by = col_name , ascending = True).head(int(N))
    st.write(top)

def BottomN(col_name, N):
    bottom = df.sort_values(by = col_name , ascending = True).tail(int(N))
    st.write(bottom)

# Display data cleaning options
if df is not None:
    with st.container(key="Data_Cleaning"):
        left_col, mid_col, right_col, more = st.columns([1, 1, 1, 1])
        with left_col:
            st.write("## Data Cleaning")
        with mid_col:
            st_lottie(anim, height=60, key="cleaning")

    with st.container(key="Cleaning_Options"):
        option = st.selectbox("Cleaning Options", ["Drop Columns", "Strip", "Replace", "dropNa", "Fill Null Vals", "Set Index", "Reset Index", "Drop Duplicates", "Drop Row", "Change Type"])

        if option == "dropNa":
            if st.button("Drop"):
                dropNA()

        if option == 'Drop Columns':
            col_name = st.selectbox("Select Column to Drop", df.columns)
            if st.button("Drop"):
                drop_cols(col_name)

        elif option == 'Strip':
            side = st.selectbox("Select Side to Strip", ["Right", "Left", "Both"])
            col_name = st.selectbox("Select Column to Strip", df.columns)
            expr = st.text_input("Enter Expression to Strip")
            if st.button("Strip"):
                trim(side, col_name, expr)
                st.success("Trimmed Successfully!")

        elif option == 'Replace':
            col_name = st.selectbox("Select Column ", df.columns)
            expr1 = st.text_input("Enter Old Expression")
            expr2 = st.text_input("Enter New Expression")
            if st.button('Replace'):
                Replace(expr1, expr2, col_name)
                st.success("Replaced Successfully!")

        elif option == 'Set Index':
            col_name = st.selectbox("Select Column ", df.columns)
            if st.button('SetIndex'):
                SetIndex(col_name)
                st.success("Set Successfully!")

        elif option == 'Reset Index':
            if st.button('ResetIndex'):
                ResetIndex()
                st.success("Reset Successfully!")

        elif option == 'Drop Duplicates':
            if st.button('Drop', key="Duplicates"):
                DropDuplicates()
                st.success("Dropped Successfully!")

        elif option == 'Fill Null Vals':
            val = st.text_input("Enter Value")
            if st.button('Fill'):
                Fillna(val)
                st.success("Filled Successfully!")

        elif option == 'Drop Row':
            val = st.text_input("Enter the Value")
            col_name = st.selectbox("Select Column ", df.columns)
            if st.button('Drop'):
                DropRowIf(col_name, val)
                st.success("Dropped Successfully!")

        elif option == 'Change Type':
            col_name = st.selectbox("Select Column ", df.columns)
            type = st.text_input("Enter the Value")
            if st.button('Type'):
                ChangeTypeCol(col_name, type)
                st.success("Changed Successfully!")

        # Undo option
        if st.button("Undo"):
            undo_last_action()

        # Display the updated DataFrame after cleaning operations
        st.write("## Updated Data")
        updated_data = st.session_state.df
        st.write(st.session_state.df)  # Display the DataFrame from session state after possible undo

        # Save updated DataFrame back to session state
        st.session_state.df = df

# ---------------------Analysis------------------------#
if df is not None:
    st.write("#")
    anim2 = load_lottie_url("https://lottie.host/e7b626ff-351f-40f0-9f31-8f22bbefe1b0/jbBiungPOi.json")

    with st.container(key="Head_Analysis"):
        left, mid, right, more, more4 = st.columns([1, 0.8, 0.1, 1, 1])
        with left:
            st.write("## Summarize")
        with mid:
            st.lottie(anim2, height=100, key="analyse")

    with st.container(key="Main_Analysis"): 
         st.write("### Final DataFrame")
         st.write(updated_data) 
         st.write("#")
         option = st.selectbox("Select Operation", ["None", "Sum", "Average", "Sorting", "TopN", "BottomN", "Overview", "Null Vals", "Describe", "Unique"])

         if option == 'Sum':
            col_name = st.selectbox("Column Name", df.columns)
            Sum(col_name)

         if option == 'Average':
            col_name = st.selectbox("Column Name", df.columns)
            Avg(col_name)

         if option == 'Sorting':
            col_name = st.selectbox("Column Name", df.columns)
            bool = st.text_input("Ascending (Type 0) or Descending (Type 1)")
            Sorting(col_name, bool)

         if option == 'TopN':
            col_name = st.selectbox("Column Name", df.columns)
            nums = st.text_input("Enter Number of Rows")
            TopN(col_name, nums)

         if option == 'BottomN':
            col_name = st.selectbox("Column Name", df.columns)
            nums = st.text_input("Enter Number of Rows")
            BottomN(col_name, nums)

         if option == 'Overview':
            Overview()

         if option == 'Null Vals':
            NullVals()

         if option == 'Describe':
            Describe()

         if option == 'Unique':
            Unique()

    with st.container(key="Advanced_Analysis"):
         st.write("#")
         st.write("### Advanced Analysis")
         option = st.selectbox("Select Operation", ["None","Standard Deviation","Confidence Interval","Covariance","Correlation"])
         if option == "Standard Deviation":
            col_name = st.selectbox("Column Name", df.columns)
            StdDev(col_name)
        
         if option == "Confidence Interval":
            col_name = st.selectbox("Column Name", df.columns)
            confidence = st.slider("Confidence Level", 0.80, 0.99, 0.95)
            ConfidenceInterval(col_name, confidence)
         
         if option == "Covariance":
            left, right = st.columns([1, 1])
            with left:
              col_name1 = st.selectbox("First Column Name",df.columns)
            with right:
              col1_name2 = st.selectbox("Second Column Name",df.columns) 
            Covariance(col_name1,col1_name2)
         
         if option == "Correlation":
            left, right = st.columns([1, 1])
            with left:
              col_name1 = st.selectbox("First Column Name",df.columns)
            with right:
              col1_name2 = st.selectbox("Second Column Name",df.columns) 
            Correlation(col_name1,col1_name2) 
