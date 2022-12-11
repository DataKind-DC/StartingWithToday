# Import required libraries
import webbrowser
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import numpy as np
import json
import requests

# Use CSS style sheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

# Ingest data of location of non-profit organizations
df = pd.read_csv('../StartingWithToday/data/non-profit-orgs-cleaned.csv')

# Create list of columns that will be excluded from data frame used to locate organizations on the map
df.rename(columns={'website':'Website:'},inplace=True)
excluded_cols = len(['org_url', 'name', 'location', 'website', 'about', 'services',
                     'org_type', 'lat', 'lng', 'zip'])

# Determine styling parameters
colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'font-family': 'Verdana',
    'font-weight': 'bold'
}

# Create a list of possible services provided by non-profits in the region
services = list(df.iloc[:,excluded_cols-len(df.columns):].sum().index)

# Ingest the data of the needs score generated in script 3.4
needs_score = pd.read_csv('../StartingWithToday/data/needs_score.csv')

# Access the geo-JSON file of DC census tracts
req = requests.get('https://raw.githubusercontent.com/arcee123/GIS_GEOJSON_CENSUS_TRACTS/master/11.geojson')

json = req.json()

# Create a choropleth map of the needs score
fig_score = px.choropleth(needs_score,
                    geojson=json,
                    locations='GEOID',
                    color='Needs Score',
                    color_continuous_scale="YlOrRd",
                    featureidkey="properties.GEOID",
                    scope="usa",
                    center={'lat':38.8938005,'lon':-77.1579293},
                    hover_data=['% pop below poverty line', 'Depression rate',
                                '% of households without health insurance', 'Gini index',
                                '% of households without vehicles',
                                'Zip Code','Ward'],
                    fitbounds="locations")
fig_score.update_layout(margin={"r":0,"t":0,"l":0,"b":0},title_text='Needs Score')

# Create another map of the race feature.
fig_race = px.choropleth(needs_score,
                    geojson=json,
                    locations='GEOID',
                    color='% Black residents',
                    color_continuous_scale="Blues",
                    featureidkey="properties.GEOID",
                    scope="usa",
                    center={'lat':38.8938005,'lon':-77.1579293},
                    hover_data=['% Black residents','Zip Code','Ward'],
                    fitbounds="locations")

fig_race.update_layout(margin={"r":0,"t":0,"l":0,"b":0},title_text='% Black residents')

# Generate data for number of organizations by type of service across DC
svcs = pd.DataFrame(df.iloc[:,excluded_cols-len(df.columns):].sum())
svcs.reset_index(inplace=True)
svcs.rename(columns={'index':'Service',0:'Number of organizations'},inplace=True)
svcs = svcs.sort_values(by='Number of organizations',ascending=False)
svcs = svcs[svcs['Number of organizations'] >= 5]

fig_svcs = px.bar(svcs, x="Service", y="Number of organizations")

# Generate data for number of organizations by type of service in Wards 7 and 8
svcs_wards_7_8 = pd.DataFrame(df[(df['zip'] == '20002') | (df['zip'] == '20003') | (df['zip'] == '20019') | \
                    (df['zip'] == '20020') | (df['zip'] == '20024') | (df['zip'] == '20373') | \
                    (df['zip'] == '20032')].iloc[:,excluded_cols-len(df.columns):].sum())
svcs_wards_7_8.reset_index(inplace=True)
svcs_wards_7_8.rename(columns={'index':'Service',0:'Number of organizations'},inplace=True)
svcs_wards_7_8 = svcs_wards_7_8.sort_values(by='Number of organizations',ascending=False)
svcs_wards_7_8 = svcs_wards_7_8[svcs_wards_7_8['Number of organizations'] >= 5]

fig_svcs_wards_7_8 = px.bar(svcs_wards_7_8, x="Service", y="Number of organizations")

# Create the title of the dashboard
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='StartingWithToday Business Intelligence Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'font-family': colors['font-family']
        }
    ),
    # Create the subtitle of the dashboard
    html.Div(children='Strategic partners, community needs, and demographics', style={
        'textAlign': 'center',
        'color': colors['text'],
        'font-family': colors['font-family']
    }),

    html.Div([
    # Add the dropdown of service type
        html.Div([
            html.Div([
                dcc.Dropdown(
                    services,
                    ['Mental Health','Economic Development'],
                    id='types-of-service',
                    multi=True
                ),
            ], style={'width': '100%','display':'inline-block','font-family': colors['font-family'],
                      'font-weight': colors['font-weight']})]),
        # Add the non-profit map graph
        dcc.Graph(id='non-profit-map'),
        html.Pre(id='data')],className='six columns'),
    # Add the needs score graph
    html.Div([
        html.Div(children='Needs Score: 0 represents lowest need, 100 highest need', style={
            'textAlign': 'center',
            'color': colors['text'],
            'font-family': colors['font-family']}),
            dcc.Graph(
                id='graph2',
                figure=fig_score)], className='six columns'),
    # Add the graph for the race feature
    html.Div([
        html.Div(children='Percentage of residents who are Black (Not-Hispanic/Latino)', style={
            'textAlign': 'center',
            'color': colors['text'],
            'font-family': colors['font-family']}),
            dcc.Graph(
                id='graph3',
                figure=fig_race)], className='six columns'),
    html.Div([
        html.Div(children='Number of non-profits by type of service in Washington, DC', style={
            'textAlign': 'center',
            'color': colors['text'],
            'font-family': colors['font-family']}),
            dcc.Graph(
                id='graph4',
                figure=fig_svcs)], className='six columns'),
    html.Div([
        html.Div(children='Number of non-profits by type of service, Wards 7 and 8', style={
            'textAlign': 'center',
            'color': colors['text'],
            'font-family': colors['font-family']}),
            dcc.Graph(
                id='graph5',
                figure=fig_svcs_wards_7_8)], className='six columns')
    ],className='row')

# Set up the callback that will change the data provided of location of non-profit orgs based on the service types selected
@app.callback(
    Output('non-profit-map','figure'),
    Input('types-of-service','value'))
def update_graph(service):
    dff = df[np.sum(df[service],axis=1) > 0]

    for serv in service:
        dff[serv] = dff[serv].replace(1,serv).replace(0,'')

    dff['Service Areas:'] = [' & '.join([val for val in sorted(list(val)) if val != '']) \
        for val in dff[sorted(service)].apply(tuple, axis=1)]

    fig = px.scatter_mapbox(dff,
                            lat="lat",
                            lon="lng",
                            hover_name="name",
                            hover_data={"Website:":True,'lat':False,'lng':False},
                            color='Service Areas:',
                            zoom=9.7,
                            height=500,
                            width=901)

    fig.update_layout(mapbox_style="open-street-map",
        legend=dict(orientation="h"))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'])
    fig.update_layout(clickmode='event+select')

    return fig

# Add the callback to allow clicking on a non-profit org data point and opening the hyperlink to the website
@app.callback(
    Output('data', 'children'),
    Input('non-profit-map', 'clickData'))
def open_url(clickData):
   if clickData:
       webbrowser.open(clickData["points"][0]["customdata"][0])
   else:
      raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1')
