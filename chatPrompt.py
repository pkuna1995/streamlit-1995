import streamlit as st
import pandas as pd


@st.cache_data
def load_data():
    conn = st.connection('snowflake')
    df = conn.query("SELECT * from WORKAREA_DB_PRD1.WORKAREA_PCL_H_OPS.SUITE_DASHBOARD_DATA_DUMP limit 20000;", ttl=0)
    df = pd.DataFrame(df)
    df['SAILINGDATE'] = pd.to_datetime(df['SAILINGDATE'])
    df['SAILINGENDDATE'] = pd.to_datetime(df['SAILINGENDDATE'])
    return df

def get_top_cruises(data):
    if 'PAX_COUNT' in data.columns:
        return data.groupby('SHIP_CODE')['PAX_COUNT'].sum().nlargest(5)
    else:
        st.error("The dataset does not contain the 'PAX_COUNT' column.")
        return pd.DataFrame()

def get_voyage_duration(data):
    data['VoyageDuration'] = (data['SAILINGENDDATE'] - data['SAILINGDATE']).dt.days
    return data[['VOYAGENUMBER', 'VoyageDuration']]

def get_average_scores(data):
    if 'ANSWER_SCORE_NUM' in data.columns and 'QUESTION_ID' in data.columns:
        grouped_data = data.groupby('QUESTION_ID')['ANSWER_SCORE_NUM'].mean()
        result_df = grouped_data.reset_index()
        result_df.columns = ['QUESTION_ID', 'AVERAGE_ANSWER_SCORE']
        return result_df
    else:
        raise ValueError("Required columns are not present in the data")
    
def get_cabin_meta_distribution(data):
    if 'CABIN_META' in data.columns:
        grouped_data= data['CABIN_META'].value_counts()
        result_df=grouped_data
        result_df.columns=['Cabin_Type','Count of Passengers']
        return result_df
    else:
        st.error("The dataset does not contain the 'CABIN_META' column.")
        return pd.DataFrame()

def handle_query(query, data):
    print("inside handle query")
    query = query.lower()
    print(query)
    if 'top 5 cruises' in query and 'passengers' in query:
        return get_top_cruises(data)
    elif 'voyage duration' in query:
        return get_voyage_duration(data)
    elif 'average scores' in query:
        return get_average_scores(data)
    elif 'cabin data' in query:
        return get_cabin_meta_distribution(data)
    else:
        return "Please ask about top 5 cruises, voyage duration, average scores and cabin data"


# def main():
#     st.title('Cruise Data Explorer')
#     data = load_data()

#     st.sidebar.header('Chat')
#     query = st.chat_input('Ask me about cruises:')
#     print(query)

#     if query:
#         print("inside if block")
#         response = handle_query(query, data)
#         if isinstance(response, pd.DataFrame):
#             if not response.empty:
#                 st.write('Here is the information you requested:')
#                 st.dataframe(response) 
#             else:
#                 st.write("No data available to display.")
#         else:
#             st.write(response)
# main()
