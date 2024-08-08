import streamlit as st
import utils as utl
import pandas as pd
import chatPrompt


st.set_page_config(
	layout="wide",
	page_title='Oapy by Impression',
	initial_sidebar_state="expanded"
)
@st.cache_data
def load_data():
    conn = st.connection(st.secrets["snowflake"])
    df = conn.query("SELECT * from WORKAREA_DB_PRD1.WORKAREA_PCL_H_OPS.SUITE_DASHBOARD_DATA_DUMP limit 20000;", ttl=0)
    df = pd.DataFrame(df)
    df['SAILINGDATE'] = pd.to_datetime(df['SAILINGDATE'])
    df['SAILINGENDDATE'] = pd.to_datetime(df['SAILINGENDDATE'])
    return df

df=load_data()

with st.container():
    st.markdown(f'<div class="header"><h1>Welcome to Cruises!</h1><h3>Chat web app that generates adhoc cruise data based on a given prompt.</h3></div>', unsafe_allow_html=True)


query = st.chat_input('Ask me about cruises:')
print(query)

if query:
    print("inside if block")
    response = chatPrompt.handle_query(query, df)
    if isinstance(response, pd.DataFrame):
        if not response.empty:
            st.write('Here is the information you requested:')
            st.dataframe(response) 
        else:
            st.write("No data available to display.")
    else:
        st.write(response)



# Model selector sidebar
filtered_shipcode = st.sidebar.selectbox('Choose your ship code', df['SHIP_CODE'].unique())

# Output sidebar
filtered_voyage = st.sidebar.selectbox('Select voyage:', df['VOYAGENUMBER'].unique())

start_date = st.sidebar.date_input('Select start date:', df['SAILINGDATE'].min())
end_date = st.sidebar.date_input('Select end date:', df['SAILINGENDDATE'].max())
filtered_question = st.sidebar.selectbox('Select Question:', df['QUESTION_ID'].unique())


if st.sidebar.button('Apply Filters'):
    # Apply filters based on user input
    filtered_df = df[(df['SHIP_CODE'] == filtered_shipcode) & (df['VOYAGENUMBER']==filtered_voyage)& (df['SAILINGDATE'] >= pd.Timestamp(start_date)) &
    (df['SAILINGENDDATE'] <= pd.Timestamp(end_date)) &
    (df['QUESTION_ID'] == filtered_question)]

    if filtered_df.empty:
        st.write("No data matches the selected filters.")
    else:
        with st.container():
            st.write("Filtered DataFrame:")
        with st.container():
            st.write(filtered_df)
if st.sidebar.button('Clear Filters'):
    st.experimental_rerun() 


  




# Loading CSS
utl.local_css("file.css")
