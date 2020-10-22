import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from sqlalchemy import create_engine
import plotly.express as px
import requests
import pandas as pd
from aggregate_data import load_community_district_data
import dash_bootstrap_components as dbc
import dash_ui as dui
from control_panel import create_control_panel  
from plot_figure import community_district_choropleth
from plot_figure import plot_bar
from aggregate_data import load_bar_units_agg
from aggregate_data import load_num_dev_res_units_data
from plot_figure import citywide_choropleth
# for local testing with .env file
import os
from dotenv import load_dotenv, find_dotenv

# get the enviromental variable in local testing 
load_dotenv(find_dotenv())

database = os.getenv('BUILD_ENGINE')

mapbox_token = os.getenv('MAPBOX_TOKEN')

print(database)

app = dash.Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

grid = dui.Grid(_id='grid', num_rows=4, num_cols=2, grid_padding=0)

controlpanel = create_control_panel()

grid.add_element(row=1, col=1, width=2, height=2, element=html.Div([ 

    # 
    html.H1(
        children='Choropleth Map',
        style={
            'textAlign': 'left',
            'color': colors['text']
        }
    ),

    html.Div(children='Example Subtitle', style={
        'textAlign': 'left',
        'color': colors['text']
    }),
    
    html.Div([
                dcc.Slider(
                    id='year-slider',
                    min=2010,
                    max=2020,
                    value=2010,
                    marks={str(year): str(year) for year in range(2010, 2020)},
                    included=False
                )
        ],
        style={'width': '100%', 'float': 'center', 'display': 'inline-block'}
    ),

    html.Div([
        dcc.Graph(id='choro-graphic'),
    ], style={'width': '70%', 'float': 'right', 'display': 'inline-block'})
]))

#grid.add_graph(row=1, col=1, width=2, height=2, graph_id='cd-graphic')

grid.add_graph(row=3, col=1,  width=2, height=1, graph_id='bar-chart')


app.layout = html.Div(
    dui.Layout(
        grid=grid,
        controlpanel=controlpanel
    ),
    style={
        'height': '100vh',
        'width': '100vw'
    }
)	

#### new function 
@app.callback(
    [Output('choro-graphic', 'figure'),
    Output('bar-chart', 'figure')],
    [Input('quick-dropdown', 'value'),
    Input('boro-dropdown', 'value'),
    Input('job-type-dropdown', 'value'),
    Input('year-slider', 'value')]
)
def update_comm_district_graph(quick, boro, job_type, year):

    if quick == 'First Look':

        df = load_num_dev_res_units_data(database, year, job_type)

        choro = citywide_choropleth(df, job_type, mapbox_token)

        df_bar = load_bar_units_agg(database)

        bar = plot_bar(df_bar, job_type)

    else:
        df = load_community_district_data(boro, database)

        choro, bar = community_district_choropleth(df, mapbox_token)

    return choro, bar


if __name__ == '__main__':

    app.run_server(debug=True)

