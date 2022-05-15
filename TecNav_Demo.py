### IMPORTS

# Data Management
import numpy as np
import pandas as pd
import pickle

# Visualization
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Dashboard
import streamlit as st
from contextlib import contextmanager, redirect_stdout
from io import StringIO

# TecNav navigator
from uc_navigator import *

# Read in necessary data files
past_patients_df = pd.read_pickle('./pickled_objects/past_patients_df.pkl')
new_patients_df = pd.read_pickle('./pickled_objects/new_patients_df.pkl')
clinics_df = pd.read_csv('./uc_clinics.csv', index_col='branch_name')
clinics_df['nearby_clinics'] = clinics_df.nearby_clinics.apply(lambda x: ast.literal_eval(x))
model = pickle.load(open('./pickled_objects/rf_model.pkl', 'rb'))

# Set dashboard layout and title
st.set_page_config(layout="wide")
c1, c2, c3, c4, c5 = st.columns((1, 1, 1, 1, 1))
c3.title("""TecNav""")

# Setup sidebar with date toggle-menu
st.sidebar.header('Simulate a past day: ')
selected_date = st.sidebar.selectbox('Date: ', past_patients_df.visit_date.unique())
st.markdown(f'''
    <style>
    section[data-testid="stSidebar"] .css-ng1t4o {{width: 14rem;}}
    </style>
''',unsafe_allow_html=True)

# Filter data based on selected date
df = past_patients_df.copy()
df = df[df.visit_date == selected_date]

# Ensure std output streams to dashboard
@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write
        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret
        stdout.write = new_write
        yield

# Set up separate columns for visuals and std out        
col1, col2 = st.columns((1, 1.25))

# Stream stdout to right column
col2.subheader(f'Navigation Activity Log for {selected_date}:')
output = col2.empty()
with st_capture(output.code):
    nav = TecNav(df, clinics_df, model)
    nav.execute_navigation()
    df['current_num_techs'] = nav.current_num_techs_col
    df.to_csv('./uc_log.csv')


# Retreive necessary logged data based on navigation execution
results = pd.read_csv('uc_log.csv')
results['checkin_time'] = results.checkin_time.apply(lambda x: x[:-3])
denver_df = results[results.visit_location == 'denver']
wheatridge_df = results[results.visit_location == 'wheatridge']
edgewater_df = results[results.visit_location == 'edgewater']
rino_df = results[results.visit_location == 'rino']
lakewood_df = results[results.visit_location == 'lakewood']

col1.subheader(f'Technician Count on {selected_date}:')

### PLOTLY PLOTS
dfs = [denver_df, wheatridge_df, edgewater_df, rino_df, lakewood_df]
locs = ['Denver', 'Wheatridge', 'Edgewater', 'RiNo', 'Lakewood']
for i in range(5):
    col1.write(f'{locs[i]}:')
    
    fig = go.Figure()
    loc_df = dfs[i]

    line1 = go.Scatter(
        x=loc_df['checkin_time'], y=loc_df['assigned_num_techs'], 
        name='Scheduled', marker_color='yellow', line = dict(color='yellow', width=4, dash='dash'), mode='lines'
    )
    line2 = go.Scatter(
        x=loc_df['checkin_time'], y=loc_df['current_num_techs'], 
        name='Current', marker_color='#17becf', mode='lines'
    )
    line3 = go.Scatter(
        x=loc_df['checkin_time'], y=loc_df['needed_num_techs'], 
        name='Needed', marker_color='red', mode='lines'
    )


    fig.add_trace(line1)
    fig.add_trace(line2)
    fig.add_trace(line3)
    fig.update_traces(opacity=0.7)
    fig.update_layout(height=300, width=1200, showlegend=True, legend_tracegroupgap=250)
    fig.update_xaxes(showgrid=False, tickangle=-45)
    fig.update_yaxes(showgrid=False)
    
    col1.plotly_chart(fig, use_container_width=True)


#######################################

# IN COMMAND LINE, NAVIGATE TO PROJECT DIRECTORY AND EXECUTE:
# streamlit run 5_visualizer.py