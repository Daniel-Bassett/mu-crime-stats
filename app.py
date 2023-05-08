import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu

@st.experimental_memo
def load_data(dir):
    df = pd.read_csv(dir)
    return df

def create_map(crime_df, crimes_filter):

    # if the user selects specific crime types, filter them. Otherwise create map of all crimes combined
    if crimes_filter:
        crime_df = crime_df.query('general_offense.isin(@crimes_filter)')
        crimes_map_title = ' '.join(crimes_filter)
    else:
        crimes_map_title = 'All Crimes'

    # create a dataframe that has count of number of crimes at each location
    temp_df = crime_df.groupby(['latitude', 'longitude', 'location_of_occurrence'], as_index=False).size().sort_values(by='size', ascending=False)

    # rename size column to n_crimes
    temp_df = temp_df.rename(columns={'size': 'n_crimes'})

    # for sake of clearer visualization, filter out locations that have less than 3 crimes
    temp_df = temp_df.query('n_crimes > 2')

    # new column in temp_df that contains all the info for hovering in map
    temp_df['hover_info'] = 'Address: ' + temp_df.location_of_occurrence.astype(str) + '<br>' + 'Num of Crimes: ' + temp_df.n_crimes.astype(str)

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

    fig.update_layout(width=800, height=600, title=f'Number of Crimes by Location 2019-2023 ({crimes_map_title})', title_x=0.5)
    return fig

# load data 
crime_df = load_data('data/crime-df.csv')

# define crime type options
crime_options = crime_df.general_offense.value_counts().sort_values(ascending=False).index.tolist()

# end user selects crimes they are interested in
crimes_filter = st.multiselect('Choose crime category', options=crime_options)

fig = create_map(crime_df, crimes_filter)

st.plotly_chart(fig)