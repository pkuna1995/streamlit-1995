import streamlit as st
import pandas as pd
import chatPrompt
import snowflake.connector


st.set_page_config(
	layout="wide",
	page_title='Oapy by Impression',
	initial_sidebar_state="expanded"
)
with st.container():
        st.markdown("<div style='text-align: center; color: grey;'>", unsafe_allow_html=True)
        st.image("Princess_RGB_1line_2022.png",width=500)
        st.markdown("</div>",unsafe_allow_html=True)
with st.container():
        st.markdown(f'<div class="header"><h1>Welcome to Princess Cruises Chatbot!</h1><h3>A web app that generates data at scale based on a given prompt.</h3></div>', unsafe_allow_html=True)

def handle_query(query, df):
    data=chatPrompt.handle_query(query,df)
    return data
   
def load_css(file_path):
    """Load CSS from a file."""
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# @st.cache_data
# def load_data():
#     conn = st.connection(st.secrets["connections"]["snowflake"])
#     df = conn.query("SELECT * from WORKAREA_DB_PRD1.WORKAREA_PCL_H_OPS.SUITE_DASHBOARD_DATA_DUMP limit 20000;", ttl=0)
#     df = pd.DataFrame(df)
#     df['SAILINGDATE'] = pd.to_datetime(df['SAILINGDATE'])
#     df['SAILINGENDDATE'] = pd.to_datetime(df['SAILINGENDDATE'])
#     return df

# df = load_data()
snowflake_params=st.secrets["connections"]["snowflake"]

@st.cache_resource
def get_snowflake_connection():
    snowflake_params = st.secrets["connections"]["snowflake"]
    return snowflake.connector.connect(
        user=snowflake_params["user"],
        password=snowflake_params["password"],
        account=snowflake_params["account"],
        warehouse=snowflake_params["warehouse"],
        database=snowflake_params["database"],
        schema=snowflake_params["schema"]
    )

@st.cache_data
def load_data():
    conn = get_snowflake_connection()
    query = "SELECT * from WORKAREA_DB_PRD1.WORKAREA_PCL_H_OPS.SUITE_DASHBOARD_DATA_DUMP limit 20000"
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [col[0] for col in cur.description]  # Get column names from cursor
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=columns)
        df['SAILINGDATE'] = pd.to_datetime(df['SAILINGDATE'])
        df['SAILINGENDDATE'] = pd.to_datetime(df['SAILINGENDDATE'])  # Create DataFrame with column names
        return df


df=load_data()

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []


    

query = st.chat_input('Ask me about cruises:')

if query:
   
    st.session_state['chat_history'].append({"role": "user", "content": query})
    response = handle_query(query, df)
    st.session_state['chat_history'].append({"role": "assistant", "content": response})


for message in st.session_state['chat_history']:
    with st.chat_message(name=message["role"]):
        st.write(message["content"])


filtered_shipcode = st.sidebar.selectbox('Choose your ship code', df['SHIP_CODE'].unique())
filtered_voyage = st.sidebar.selectbox('Select voyage:', df['VOYAGENUMBER'].unique())
start_date = st.sidebar.date_input('Select start date:', df['SAILINGDATE'].min())
end_date = st.sidebar.date_input('Select end date:', df['SAILINGENDDATE'].max())
filtered_question = st.sidebar.selectbox('Select Question:', df['QUESTION_ID'].unique())


if st.sidebar.button('Apply Filters'):
    filtered_df = df[
        (df['SHIP_CODE'] == filtered_shipcode) &
        (df['VOYAGENUMBER'] == filtered_voyage) &
        (df['SAILINGDATE'] >= pd.Timestamp(start_date)) &
        (df['SAILINGENDDATE'] <= pd.Timestamp(end_date)) &
        (df['QUESTION_ID'] == filtered_question)
    ]

    if filtered_df.empty:
         with st.container():
            st.write("No data matches the selected filters.")
    else:
        with st.container():
            st.dataframe(filtered_df)

if st.sidebar.button('Clear Filters'):
    st.rerun()

load_css("file.css")
