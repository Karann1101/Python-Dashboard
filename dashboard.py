import streamlit as st 
import plotly.express as px 
import pandas as pd 
import os 
import warnings 
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!", page_icon=":bar_chart:", layout="wide") 
st.title(":bar_chart: Sample Dataset")
st.markdown('<style>div.block-container{padding-top:38px;}</style>', unsafe_allow_html=True)

# Upload file section
fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))

if fl is not None:
    filename = fl.name
    st.write(f"Uploaded File: **{filename}**")
    if filename.endswith(".csv") or filename.endswith(".txt"):
        df = pd.read_csv(fl, encoding="utf-8-sig")
    else:
        df = pd.read_excel(fl)
else:
    os.chdir(r"C:\Desktop\dashboard")
    df = pd.read_csv("superstore.csv", encoding="utf-8-sig")

# Parse Order Date as datetime
df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors='coerce')
df = df.dropna(subset=["Order Date"])  # Remove invalid dates

# Create a display column with formatted dates
df["Order Date Display"] = df["Order Date"].dt.strftime('%d/%m/%Y')

# Get min and max dates for date picker (using datetime column)
startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

# Date range selection
col1, col2 = st.columns((2))
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filter based on selected dates using datetime column
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

st.sidebar.header("Choose your filter: ")

# Filters
region = st.sidebar.multiselect("Pick your region ", df["Region"].unique()) 
if not region: 
    df2 = df.copy() 
else: 
    df2 = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick your state", df2["State"].unique()) 
if not state:  # fix here, should check if state is empty, not region
    df3 = df2.copy() 
else: 
    df3 = df2[df2["State"].isin(state)] 

city = st.sidebar.multiselect("Pick your city", df3["City"].unique())  # Fix: city should be filtered on City column, not State

# Filter the data based on Region, State, City
if not region and not state and not city: 
    filtered_df = df.copy()
elif region and not state and not city: 
    filtered_df = df[df["Region"].isin(region)] 
elif not region and state and not city: 
    filtered_df = df[df["State"].isin(state)] 
elif not region and not state and city: 
    filtered_df = df[df["City"].isin(city)]
elif region and state and not city:
    filtered_df = df[(df["Region"].isin(region)) & (df["State"].isin(state))]
elif region and not state and city:
    filtered_df = df[(df["Region"].isin(region)) & (df["City"].isin(city))]
elif not region and state and city:
    filtered_df = df[(df["State"].isin(state)) & (df["City"].isin(city))]
else:
    filtered_df = df[(df["Region"].isin(region)) & (df["State"].isin(state)) & (df["City"].isin(city))]

# Group by Category
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1: 
    st.subheader("Category wise sales") 
    fig = px.bar(
        category_df, 
        x="Category", 
        y="Sales", 
        text=[f'${x:,.2f}' for x in category_df["Sales"]],
        template="seaborn"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2: 
    st.subheader("Region wise sales") 
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5) 
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True) 
    
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.dataframe(category_df)
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                            help='Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region_sales = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.dataframe(region_sales)
        csv = region_sales.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                        help='Click here to download the data as a CSV file')
        
# Here, use datetime column "Order Date" to get month_year period
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum().reset_index(name="Sales")
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.dataframe(linechart.T)
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

# TreeMap
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path=["Region","Category","Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df.loc[0:4, ["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.dataframe(sub_category_Year)

# Scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1.update_layout(
    title=dict(
        text="Relationship between Sales and Profits using Scatter Plot.",
        font=dict(size=20)
    ),
    xaxis=dict(
        title=dict(text="Sales", font=dict(size=19))
    ),
    yaxis=dict(
        title=dict(text="Profit", font=dict(size=19))
    )
)
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.dataframe(filtered_df.iloc[:500, 1:20:2])

# Download original DataSet
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")
