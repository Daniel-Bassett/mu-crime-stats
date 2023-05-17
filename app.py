import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu

@st.experimental_memo
def load_data(dir):
    df = pd.read_csv(dir, parse_dates=['time_started'])
    df['week'] = df.time_started.dt.week
    return df

# set population constant for calculating crime rate, based on 2021 figure
POPULATION = 126853

def create_map(crime_df, crimes_filter, start_date, end_date):

    # if the user selects specific crime types, filter them. Otherwise create map of all crimes combined
    if crimes_filter:
        crime_df = crime_df.query('general_offense.isin(@crimes_filter)')
        list_of_crimes = [crime.capitalize() for crime in crimes_filter]
        crimes_map_title = ' '.join(list_of_crimes)
        
    else:
        crimes_map_title = 'All Crimes'

    # apply start and end date
    temp_df = crime_df.query('time_started >= @start_date and time_started <= @end_date')

    # create a dataframe that has count of number of crimes at each location
    temp_df = temp_df.groupby(['latitude', 'longitude', 'location_of_occurrence'], as_index=False).size().sort_values(by='size', ascending=False)

    # rename size column to n_crimes
    temp_df = temp_df.rename(columns={'size': 'n_crimes'})

    # drop duplicate latitude and longitude, this should be cleaned in pandas
    temp_df = temp_df.sort_values(by='n_crimes', ascending=False)
    temp_df = temp_df.drop_duplicates(subset=['latitude', 'longitude'], keep='first')

    # new column in temp_df that contains all the info for hovering in map
    temp_df['hover_info'] = 'Address: ' + temp_df.location_of_occurrence.astype(str) + '<br>' + 'Num of Incidents: ' + temp_df.n_crimes.astype(str)



    # Create heatmap of criminal activity
    fig = px.scatter_mapbox(
        temp_df,
        lat='latitude',
        lon='longitude',
        center=dict(lat=38.94244, lon=-92.3269),
        zoom=14,
        size='n_crimes',
        mapbox_style='carto-positron',
        hover_data={'latitude': False, 'longitude': False, 'n_crimes': False},
        hover_name='hover_info',
        color_discrete_sequence=["red"]
    )

    fig.update_layout(title=f'Number of Crimes by Location - {crimes_map_title}')

    return fig


def create_area(crime_df, crimes_filter, start_date, end_date, time_period, time_period_options):

    crime_df = crime_df.query('time_started >= "2020-01-01"')

    # crime_df = crime_df.groupby(['year', 'month'], as_index=False).size()

    # crime_df['start_date'] = crime_df.year.astype(str) + '-' + crime_df.month.astype(str)
    
    if crimes_filter:
        crime_df = (
            crime_df
            .query('time_started >= @start_date and time_started <= @end_date and general_offense.isin(@crimes_filter)')
            .groupby(pd.Grouper(key='time_started', freq=f'{time_period_options[time_period]}'))
            .size()
            .reset_index()
            .rename(columns={0: 'count', 'time_started': 'period_ended'})
        )


    else:
        crime_df = (
            crime_df
            .query('time_started >= @start_date and time_started <= @end_date')
            .groupby(pd.Grouper(key='time_started', freq=f'{time_period_options[time_period]}'))
            .size()
            .reset_index()
            .rename(columns={0: 'count', 'time_started': 'period_ended'})
        )   

    fig = px.area(
        crime_df,
        x='period_ended',
        y='count'
    )

    fig.update_layout(
        title={
            'text': 'Crime Over Time',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title=time_period,
        yaxis_title='Number of Incidents'
        
    )
    return fig


def create_heatmap(crime_df, crimes_filter, locations_filter, start_date, end_date):
    # filter dataframe for crimes, locations, and dates from use input
    crime_df = crime_df.query('general_offense.isin(@crimes_filter) and location_of_occurrence.isin(@locations_filter)')
    crime_df = crime_df.query('time_started >= @start_date and time_started <= @end_date')

    # rename column from size
    crime_df = crime_df.groupby(['location_of_occurrence', 'general_offense'], as_index=False).size().sort_values(by='size', ascending=False)
    crime_df = crime_df.rename(columns={'size': 'n_crimes'})
    crime_df = crime_df.pivot(index='location_of_occurrence', columns='general_offense', values='n_crimes').fillna(0)
    fig = px.imshow(crime_df, color_continuous_scale=['white', 'red'])
    fig.update_layout(
                      title=f'Crime by Location - Heatmap', 
                      xaxis_title='location',
                      yaxis_title='crime category'
                      )
    return fig

# load data 
crime_df = load_data('data/crime-df.csv')
date_min = pd.to_datetime('2019-01-01')
date_max = pd.to_datetime('2023-12-31')
min_default = crime_df.time_started.dt.date.min()
max_default = crime_df.time_started.dt.date.max()

# create sidebar menu with options
selected = option_menu(
    menu_title=None,
    menu_icon='cast',
    default_index=0,
    options=['Crime Map', 'Crime Over Time', 'Crime Category', 'Crime by Location'],
    orientation='horizontal',
    icons=['pin-map', 'graph-up', 'filter-square'],
    styles= {'container': {
                'font-size': '12px'
    }}
)


# define crime type options
crime_options = crime_df.general_offense.value_counts().sort_values(ascending=False).index.tolist()

graph_container = st.container()


input_col1, input_col2, input_col3, input_col4 = st.columns([4, 4, 4, 4])

with input_col1:
    # get date range
    start_date = st.date_input(label='Start Date', min_value=date_min, max_value=date_max, value=min_default, label_visibility='visible')
with input_col2:
    end_date = st.date_input(label='End Date', min_value=date_min, max_value=date_max, value=max_default)
with input_col3:
    #  user selects crimes they are interested in
    crimes_filter = st.multiselect('Choose crime type', options=crime_options)

if selected == 'Crime Map':
    with graph_container:
        fig = create_map(crime_df, crimes_filter, start_date=start_date, end_date=end_date)
        st.plotly_chart(fig, use_container_width=True)


if selected == 'Crime Over Time':

    time_period_options = {'Year': 'Y', 'Month': 'M','Week': 'W', 'Day': 'D'}
    with input_col4:
        time_period = st.selectbox(options=time_period_options.keys(), label='Time Period', index=list(time_period_options.keys()).index('Month'))

    fig = create_area(crime_df, crimes_filter, start_date, end_date, time_period, time_period_options)
    
    with graph_container:
        st.plotly_chart(fig, use_container_width=True)

if selected == 'Crime Category':
    st.write('Two or more crimes to compare')
    if len(crimes_filter) >= 2:
        crime_df = (crime_df
                .query('time_started >= @start_date and time_started <= @end_date and general_offense.isin(@crimes_filter)')
                .groupby('general_offense', as_index=False)
                .size()
                .sort_values(by='size', ascending=True)
                )
        fig = px.bar(crime_df, x='size', y='general_offense', orientation='h')
        fig.update_traces(textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

if selected == 'Crime by Location':

    # this filters the available options for locations without typos, this should be cleaned in pandas
    temp_df = crime_df.groupby(['latitude', 'longitude', 'location_of_occurrence'], as_index=False).size().sort_values(by='size', ascending=False)
    temp_df = temp_df.rename(columns={'size': 'n_crimes'})
    temp_df = temp_df.sort_values(by='n_crimes', ascending=False)
    temp_df = temp_df.drop_duplicates(subset=['latitude', 'longitude'], keep='first')

    # create location options
    location_options = temp_df.location_of_occurrence.unique()

    with input_slot:
        # multiselect of available locations
        locations_filter = st.multiselect('Choose locations', options=location_options)
    
    fig = create_heatmap(crime_df, crimes_filter, locations_filter, start_date, end_date)

    with graph_container:
        st.plotly_chart(fig, use_container_width=True)