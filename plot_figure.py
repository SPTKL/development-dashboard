import plotly.express as px
import requests
import pandas as pd
from pandas import json_normalize
import plotly.graph_objects as go

def citywide_choropleth(df, job_type, mapbox_token):

    # get the geojson needed for the mapping 
    response = requests.get('https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Census_Tracts_for_2010_US_Census/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson')
    #response = requests.get('https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Census_Tracts_for_2010_US_Census_Water_Included/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson')

    geojson = response.json()

    geofeatures = json_normalize(geojson["features"])

    geofeatures['acreage'] = geofeatures['properties.Shape__Area'].astype(float) / 43560.

    merged = df.merge(geofeatures[['properties.BoroCT2010', 'acreage']], left_on='bct2010', right_on='properties.BoroCT2010', how='inner')

    merged['units_per_acre'] = merged.total_res_units_net / merged.acreage

    params = {
        'max': merged.total_res_units_net.max(),
        'min': merged.total_res_units_net.min(),
        'job_type': job_type
    }

    if params['job_type'] == 'Demolition':
        cs = 'Reds'
        rs = True
    elif params['job_type'] == 'New Building':
        cs = 'Blues'
        rs = False
    else:
        cs = 'Bluered'
        rs = None


    fig = px.choropleth_mapbox(merged, geojson=geojson, locations='bct2010', color=merged.units_per_acre, hover_data=['acreage', 'total_res_units_net'],
    featureidkey="properties.BoroCT2010")

    fig.update_layout(mapbox_accesstoken=mapbox_token, mapbox_style="carto-positron",
                    mapbox_zoom=10, mapbox_center = {"lat": 40.615806929667485, "lon": -73.98003930292397})

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

def plot_bar(year_agg, job_type):
    
    newbuild = year_agg.loc[year_agg.job_type == 'New Building']

    demo = year_agg.loc[year_agg.job_type == 'Demolition']


    fig2 = go.Figure()

    if job_type == 'Demolition':

        for uclass in demo.units_class.unique():

            fig2.add_trace(
                go.Bar(x=demo.loc[demo.units_class == uclass].year, 
                    y=demo.loc[demo.units_class == uclass].net_residential_units, 
                    name=uclass, 
                )
            )

    elif job_type == 'New Building':

        for uclass in newbuild.units_class.unique():

            fig2.add_trace(
                go.Bar(x=newbuild.loc[newbuild.units_class == uclass].year, 
                    y=newbuild.loc[newbuild.units_class == uclass].net_residential_units, 
                    name=uclass, 
                )
            )
    
    else:
        for flag in alteration.units_flag.unique():

            fig2.add_trace(
                go.Bar(x=alteration.loc[alteration.units_flag == flag].year, 
                    y=alteration.loc[alteration.units_flag == flag].total_classa_net, 
                )
            )

    
    fig2.update_layout(title=job_type + ' Completed Residential Units by Number of Units in Buildings', 
        barmode='stack', xaxis_tickangle=-45)

    return fig2



def community_district_choropleth(agg_db, mapbox_token):

    response = requests.get('https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Community_Districts/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson')
    
    geojson = response.json()

    # aggregate by community district 
    cd_choro = agg_db.groupby('cd')['num_net_units'].sum().reset_index()

    fig_cd = px.choropleth_mapbox(cd_choro, geojson=geojson, locations='cd', color=cd_choro.num_net_units,
    featureidkey="properties.BoroCD")

    fig_cd.update_layout(mapbox_accesstoken=mapbox_token, mapbox_style="carto-positron",
                    mapbox_zoom=10, mapbox_center = {"lat": 40.7831, "lon": -73.9712})

    fig_cd.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # the bar chart graphic
    fig_bar_cd = px.bar(agg_db, x='cd', y='num_net_units', color='year', barmode='stack')

    fig_bar_cd.update_layout(xaxis={"type":"category"})

    return fig_cd, fig_bar_cd
