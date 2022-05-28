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

# Utils
from datetime import datetime, timedelta, date
from random import shuffle

# Read in necessary data files
past_patients_df = pd.read_pickle('./pickled_objects/past_patients_df.pkl')
new_patients_df = pd.read_pickle('./pickled_objects/new_patients_df.pkl')

clinics_df = pd.read_csv('./fabricated_data/uc_clinics.csv', index_col='branch_name')
clinics_df['nearby_clinics'] = clinics_df.nearby_clinics.apply(lambda x: ast.literal_eval(x))
model = pickle.load(open('./pickled_objects/rf_model.pkl', 'rb'))

# Set dashboard layout and title
st.set_page_config(layout="wide")
c1, c2, c3, c4, c5 = st.columns((1, 1, 1, 1, 1))
c3.title("""TecNav""")

# Setup sidebar with date toggle-menu
st.sidebar.header('Simulate a past day: ')
unique_dates = list(past_patients_df.visit_date.unique())
selected_date = st.sidebar.selectbox('Date: ', unique_dates)
st.sidebar.header('Examine movement: ')
selected_loc = st.sidebar.selectbox('Location: ', ['Denver', 'Edgewater', 'Wheatridge', 'Rino', 'Lakewood'])

st.markdown(f'''
    <style>
    section[data-testid="stSidebar"] .css-ng1t4o {{width: 14rem;}}
    </style>
''',unsafe_allow_html=True)

# Filter data based on selected date
df = past_patients_df.copy()
df = df[df.visit_date == selected_date]
df['new_num_techs'] = df['assigned_num_techs'] - 1

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

### GEO PLOT
def floor_dt(current_time):
    today = date.today()
    current_time = datetime.combine(today, current_time)
    rounded_time = current_time - (current_time - datetime.min) % timedelta(minutes=15)
    return str(rounded_time.time())[:-3]
df['interval_time'] = df.checkin_time.apply(lambda x: floor_dt(x))
all_intervals = df.interval_time.unique()
rows = []
for i in all_intervals:
    rows.append(['denver', i])
    rows.append(['wheatridge', i])
    rows.append(['edgewater', i])
    rows.append(['rino', i])
    rows.append(['lakewood', i])
new_df = pd.DataFrame(rows, columns=['visit_location', 'time'])
new_df['lat'] = new_df.visit_location.map(clinics_df.to_dict()['lat'])
new_df['lon'] = new_df.visit_location.map(clinics_df.to_dict()['lon'])
new_df = new_df.sort_values(by=['visit_location', 'time'])
new_df['rolling_ct'] = new_df[['visit_location', 'time']].apply(lambda x: df[(df.visit_location == x[0]) & (df.interval_time == x[1])]['rolling_ct'].tolist(), axis=1)
new_df['rolling_ct'] = new_df['rolling_ct'].apply(lambda x: round(np.mean(x)) if x != [] else np.nan)
new_df['rolling_ct'] = new_df['rolling_ct'].fillna(method='ffill')
new_df['needed_num_techs'] = new_df[['visit_location', 'time']].apply(lambda x: df[(df.visit_location == x[0]) & (df.interval_time == x[1])]['needed_num_techs'].tolist(), axis=1)
new_df['needed_num_techs'] = new_df['needed_num_techs'].apply(lambda x: round(np.mean(x)) if x != [] else np.nan)
new_df['needed_num_techs'] = new_df['needed_num_techs'].fillna(method='ffill')
new_df = new_df.fillna(0)
col1.subheader(f'Rolling Patient & Tech Count on {selected_date}:')
fig = px.scatter_mapbox(
    new_df,
    lat="lat",
    lon="lon",
    size="rolling_ct",
    color='needed_num_techs',
    hover_data=["needed_num_techs"],
    animation_frame="time",
    size_max=50,
    color_continuous_scale='YlOrRd', #'YlOrRd',
    # title=f'Rolling Patient Count on {selected_date}'
).update_layout(height=400, width=600,
    mapbox={"style": "carto-positron", "zoom":10.5}, margin={"l": 0, "r": 0, "t": 0, "b": 0})

col1.plotly_chart(fig, use_container_width=True)



# Retreive necessary logged data based on navigation execution
results = pd.read_csv('uc_log.csv')
results['checkin_time'] = results.checkin_time.apply(lambda x: x[:-3])
denver_df = results[results.visit_location == 'denver']
wheatridge_df = results[results.visit_location == 'wheatridge']
edgewater_df = results[results.visit_location == 'edgewater']
rino_df = results[results.visit_location == 'rino']
lakewood_df = results[results.visit_location == 'lakewood']

# col1.subheader(f'Technician Count on {selected_date}:')


### TECH COUNT PLOTS
dfs = [denver_df, wheatridge_df, edgewater_df, rino_df, lakewood_df]
locs = ['Denver', 'Wheatridge', 'Edgewater', 'RiNo (River-North District)', 'Lakewood']

def plot_tech_needs(loc, loc_df):
    fig = go.Figure()

    line1 = go.Scatter(
        x=loc_df['checkin_time'], y=loc_df['assigned_num_techs'],
        name='Before', marker_color='yellow', line = dict(color='yellow', width=4, dash='dash'), mode='lines'
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
    fig.update_layout(height=350, width=1200, showlegend=True, legend_tracegroupgap=250)
    fig.update_xaxes(showgrid=False, tickangle=-45)
    fig.update_yaxes(showgrid=False)
    fig.update_layout(
    title={
        'text': loc,
        # 'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

    col1.plotly_chart(fig, use_container_width=True)

plot_specs = {'Denver': ['Denver', denver_df],
              'Wheatridge':['Wheatridge', wheatridge_df],
              'Edgewater':['Edgewater', edgewater_df],
              'Rino':['RiNo (River-North Art District)', rino_df],
              'Lakewood':['Lakewood', lakewood_df]}
plot_tech_needs(plot_specs[selected_loc][0], plot_specs[selected_loc][1])


#######################################

# IN COMMAND LINE, NAVIGATE TO PROJECT DIRECTORY AND EXECUTE:
# streamlit run 5_visualizer.py