import streamlit as st 
import plotly.express as px #to generate charts
import pandas as pd #data handling
import os #to navigate files
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Sales Analysis - Superstore",page_icon=":bar_chart:", layout="wide") # streamlit emoji icons 
# this gives the site a title just like in html

st.title(" :bar_chart: Superstore EDA") # normal page title

st.markdown('<style>div.block-container{padding-top:2.2rem;}</style>',unsafe_allow_html=True) #add padding to the top

fl=st.file_uploader(":file_folder: Upload a file", type=(["csv","txt","xlsx","xls"]))
# if fl is not None:
#     filename = fl.name
#     st.write(filename)
#     df = pd.read_csv(filename, encoding="ISO-8859-1")
# else:
#     os.chdir(r"C:\Data Analysis YT\Python n Streamlit")
#     df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")
if fl is not None:
    filename = fl.name
    if filename.endswith('.csv'):
        df = pd.read_csv(fl, encoding="ISO-8859-1")
    elif filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(fl, engine='openpyxl')  # for .xlsx and .xls files
    elif filename.endswith('.txt'):
        df = pd.read_csv(fl, delimiter='\t', encoding="ISO-8859-1")  # assuming tab-delimited text files
    else:
        st.error("Unsupported file format!")
else:
    os.chdir(r"C:\Data Analysis YT\Python n Streamlit")
    df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")

col1,col2 = st.columns(2) #creating two colums for start date and end date
df["Order Date"] = pd.to_datetime(df["Order Date"],dayfirst=True)

# To get min and max date:
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Create a sidebar for more filters:
st.sidebar.header("Choose your filter: ")
#For Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()  #if nothing is selected
else:
    df2 = df[df["Region"].isin(region)]

#For State
state = st.sidebar.multiselect("Pick your State", df2["State"].unique())
if not state:
    df3 = df2.copy()  #if nothing is selected
else:
    df3 = df2[df2["State"].isin(state)]

#For City
city = st.sidebar.multiselect("Pick your City", df3["City"].unique())
if not city:
    df4 = df3.copy()  #if nothing is selected
else:
    df4 = df3[df3["City"].isin(city)] 

# Filter the data based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

#Column charts for category & region:
category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]], template = "seaborn",color="Category",
        color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"])
    fig.update_traces(marker_line_color='rgb(0, 0, 0)', marker_line_width=1.5)
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.5,color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
    fig.update_traces(text = filtered_df["Region"], textposition ="outside")
    st.plotly_chart(fig,use_container_width=True)


#to view live data and download csv for it
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')

#For time series analysis:


filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M") #creating a new column in the dataframe
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index() #filtering based on month_year, sales sum and on x axis Year, Month
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("TimeSeries_ViewData"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')


# Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path = ["Region","Category","Sub-Category"], values = "Sales",hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("Segment Wise Sales")
    fig4 = px.pie(filtered_df, values = "Sales", names = "Segment", hole = 0 ,color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"], template="plotly_dark")
    fig4.update_traces(text = filtered_df["Segment"], textposition ="inside")
    st.plotly_chart(fig4,use_container_width=True)

with chart2:
    st.subheader("Category Wise Sales")
    fig5 = px.pie(filtered_df, values = "Sales", names = "Category", hole = 0 ,color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"], template="gridon")
    fig5.update_traces(text = filtered_df["Category"], textposition ="inside")
    st.plotly_chart(fig5,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x = "Sales", y = "Profit", size = "Quantity")
data1['layout'].update(title="Relationship between Sales and Profits using Scatter Plot.",
                       titlefont = dict(size=20),xaxis = dict(title="Sales",titlefont=dict(size=19)),
                       yaxis = dict(title = "Profit", titlefont = dict(size=19)))
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges")) # first 500 rows, random colum from 1 t 20, every second column

# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")