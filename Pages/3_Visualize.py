import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math  

# Styling
st.set_page_config(page_title="Dynamic Dashboard", layout="wide")

# Function to get number of rows
def num_rows():
    rows = st.text_input("Enter Number of Rows to Display in Charts", value="10")
    return int(rows) if rows.isdigit() else 10

# Functions using Plotly Graph Objects
def barchart(df, x, y):
    fig = go.Figure(go.Bar(x=df[x], y=df[y], marker_color='orange'))
    fig.update_layout(
        title="Bar Chart",
        xaxis_title=x,
        yaxis_title=y,
        template='plotly_dark',
        width=400,  # Adjusted width for better square fit
        height=400
    )
    return fig

def areachart(df, x, y):
    fig = go.Figure(go.Scatter(x=df[x], y=df[y], fill='tozeroy', mode='lines', line_color='cyan'))
    fig.update_layout(title="Area Chart", template='plotly_dark', width=400, height=400)
    return fig

def scatterplot(df, x, y):
    fig = go.Figure(go.Scatter(x=df[x], y=df[y], mode='markers', marker_color='magenta'))
    fig.update_layout(title="Scatter Plot", template='plotly_dark', width=400, height=400)
    return fig

def piechart(df, column):
    counts = df[column].value_counts().reset_index()
    fig = go.Figure(go.Pie(labels=counts['index'], values=counts[column]))
    fig.update_layout(title="Pie Chart", template='plotly_dark', width=400, height=400)
    return fig

# Load dataframe from session state
if 'df' in st.session_state:
    df = st.session_state.df

    # Initialize charts list
    if 'charts' not in st.session_state:
        st.session_state.charts = []

    st.title("Build Your Interactive Dashboard")

    with st.container():
        st.subheader("➤ Choose Charts to Add")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.write("#### Bar Chart")
            x_bar = st.selectbox("Select X for Bar", df.columns, key="xbar")
            y_bar = st.selectbox("Select Y for Bar", df.columns, key="ybar")
            if st.button("Add Bar Chart"):
                st.session_state.charts.append(('Bar', x_bar, y_bar))

        with c2:
            st.write("#### Area Chart")
            x_area = st.selectbox("Select X for Area", df.columns, key="xarea")
            y_area = st.selectbox("Select Y for Area", df.columns, key="yarea")
            if st.button("Add Area Chart"):
                st.session_state.charts.append(('Area', x_area, y_area))

        with c3:
            st.write("#### Scatter Plot")
            x_scat = st.selectbox("Select X for Scatter", df.columns, key="xscatter")
            y_scat = st.selectbox("Select Y for Scatter", df.columns, key="yscatter")
            if st.button("Add Scatter Plot"):
                st.session_state.charts.append(('Scatter', x_scat, y_scat))

        st.subheader("➤ Pie Chart Section")
        pie_col = st.selectbox("Select Column for Pie Chart", df.select_dtypes(exclude='number').columns, key="piecol")
        if st.button("Add Pie Chart"):
            st.session_state.charts.append(('Pie', pie_col))

        bins = num_rows()

        st.divider()

        st.subheader("Your Dashboard (Remove or Reorder Charts)")

        num_charts = len(st.session_state.charts)
        if num_charts > 0:
            cols = int(math.sqrt(num_charts))
            rows = math.ceil(num_charts / cols)

            for r in range(rows):
                chart_cols = st.columns(cols)
                for c in range(cols):
                    index = r * cols + c
                    if index < num_charts:
                        chart_type, *params = st.session_state.charts[index]
                        with chart_cols[c]:
                            if chart_type == 'Bar':
                                fig = barchart(df.head(bins), params[0], params[1])
                                st.plotly_chart(fig, use_container_width=True)
                            elif chart_type == 'Area':
                                fig = areachart(df.head(bins), params[0], params[1])
                                st.plotly_chart(fig, use_container_width=True)
                            elif chart_type == 'Scatter':
                                fig = scatterplot(df.head(bins), params[0], params[1])
                                st.plotly_chart(fig, use_container_width=True)
                            elif chart_type == 'Pie':
                                fig = piechart(df.head(bins), params[0])
                                st.plotly_chart(fig, use_container_width=True)
                            if st.button(f"Remove {index + 1}", key=f"remove_{index}"):
                                st.session_state.charts.pop(index)
                                st.rerun()
        else:
            st.info("No charts have been added yet.")

        # Allow downloads
        st.write("#")
        st.subheader("Save Your Dashboard")

        if st.button("Download as HTML"):
            with open("dashboard.html", "w") as f:
                f.write("<html><head><title>Streamlit Dashboard</title></head><body>")
                for chart_type, *params in st.session_state.charts:
                    if chart_type == 'Bar':
                        fig = barchart(df.head(bins), params[0], params[1])
                        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                    elif chart_type == 'Area':
                        fig = areachart(df.head(bins), params[0], params[1])
                        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                    elif chart_type == 'Scatter':
                        fig = scatterplot(df.head(bins), params[0], params[1])
                        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                    elif chart_type == 'Pie':
                        fig = piechart(df.head(bins), params[0])
                        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
                f.write("</body></html>")
            st.success("Dashboard saved as HTML!")

else:
    st.warning("Please upload or extract data first to visualize.")