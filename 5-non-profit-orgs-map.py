# Import required libraries
import webbrowser
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import requests

import base64
from PIL import Image

# Use CSS style sheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# Ingest data of location of non-profit organizations
df = pd.read_csv('https://startingwithtoday.s3.amazonaws.com/non-profit-orgs-cleaned.csv')

# Ingest data of needs score for DC and PG counties
needs_score_dc = pd.read_csv('https://startingwithtoday.s3.amazonaws.com/needs_score_dc.csv')

needs_score_md = pd.read_csv('https://startingwithtoday.s3.amazonaws.com/needs_score_md.csv')

# Ingest data of features that make up the needs score
display_data = pd.read_csv('https://startingwithtoday.s3.amazonaws.com/display-data.csv')

# Ingest data of locations where SWT services are provided
locs = pd.read_csv('https://startingwithtoday.s3.amazonaws.com/swt-services-locations.csv')

# Ingest GEOJSON file of census tracts in DC
req_dc = requests.get('https://raw.githubusercontent.com/arcee123/GIS_GEOJSON_CENSUS_TRACTS/master/11.geojson')

# Ingest GEOJSON file of census tracts in MD
req_md = requests.get('https://raw.githubusercontent.com/arcee123/GIS_GEOJSON_CENSUS_TRACTS/master/24.geojson')

# Create list of columns that will be excluded from data frame used to locate organizations on the map of
# non-profit organizations located in the DMV area
df.rename(columns={'website':'Website:'},inplace=True)
excluded_cols = len(['org_url', 'name', 'location', 'website', 'about',
                    'services','org_type', 'lat', 'lng', 'zip'])

# Create a list of possible services provided by non-profits in the region
services = list(df.iloc[:,excluded_cols-len(df.columns):].sum().index)

# Generate data for number of organizations by type of service across DC
svcs = pd.DataFrame(df.iloc[:,excluded_cols-len(df.columns):].sum())
svcs.reset_index(inplace=True)
svcs.rename(columns={'index':'Service',0:'Number of organizations'},inplace=True)
svcs = svcs.sort_values(by='Number of organizations',ascending=False)

# Generate data for number of organizations by type of service in Wards 7 and 8
svcs_wards_7_8 = pd.DataFrame(df[(df['zip'] == '20002') | (df['zip'] == '20003') | (df['zip'] == '20019') | \
                    (df['zip'] == '20020') | (df['zip'] == '20024') | (df['zip'] == '20373') | \
                    (df['zip'] == '20032')].iloc[:,excluded_cols-len(df.columns):].sum())
svcs_wards_7_8.reset_index(inplace=True)
svcs_wards_7_8.rename(columns={'index':'Service',0:'Number of organizations'},inplace=True)
svcs_wards_7_8 = svcs_wards_7_8.sort_values(by='Number of organizations',ascending=False)

# Join the two data sets by service type.
svcs.rename(columns={'Number of organizations':'Number of organizations in DC'},inplace=True)
svcs_wards_7_8.rename(columns={'Number of organizations':'Number of organizations in Wards 7 & 8'},inplace=True)

svcs = svcs.merge(svcs_wards_7_8, how = 'left', on = 'Service')
svcs = svcs[(svcs['Service']!='svcs') & (svcs['Service']!='nbr_orgs')]
svcs['Number of organizations in DC'] = svcs['Number of organizations in DC'].astype(int)
svcs['Number of organizations in Wards 7 & 8'] = svcs['Number of organizations in Wards 7 & 8'].astype(int)
svcs['diff_in_scvs'] = svcs['Number of organizations in DC'] - svcs['Number of organizations in Wards 7 & 8']
svcs = svcs.sort_values(by=['diff_in_scvs'],ascending=True)
svcs = svcs[svcs['Number of organizations in Wards 7 & 8'] != 0]
svcs['Number of organizations in DC'] = svcs['Number of organizations in DC'] - svcs['Number of organizations in Wards 7 & 8']
svcs.rename(columns={'Number of organizations in DC':'Number of organizations in DC excluding Wards 7 & 8'},
    inplace=True)

# Generate a graph to present the difference in number of organizations based in Washington, DC, overall
# and Wards 7 and 8.
fig_svcs = go.Figure()

fig_svcs.add_trace(go.Bar(
    y=svcs['Service'],
    x=svcs['Number of organizations in Wards 7 & 8'],
    name='Number of organizations in Wards 7 & 8',
    orientation='h',
    marker=dict(color='red')))

fig_svcs.add_trace(go.Bar(
    y=svcs['Service'],
    x=svcs['Number of organizations in DC excluding Wards 7 & 8'],
    name='Number of organizations in DC excluding Wards 7 & 8',
    orientation='h',
    marker=dict(color='silver')))

fig_svcs.update_layout(barmode='group',xaxis_title='Number of organizations',
                 title_text='The plot below shows the disparity in the number of organizations based in DC overall and Wards 7 and 8',
                 height=1200,paper_bgcolor="white",font_color="black")

# Create a list of features to plot in choropleth map below
features = ['Percentage of population below poverty line', 'Depression rate',
            'Percentage of households without health insurance','Gini inequality index',
            'Percentage of households without vehicles','Percentage of Black residents',
            'Percentage of residents with internet access','Percentage of residents with a high school diploma',
            'Walkability score']

# Set up the layout for the app
app.layout = html.Div(style={'backgroundColor': 'black'}, children=[
    # Insert logo
    html.Img(src='https://startingwithtoday.s3.amazonaws.com/swt-v2.png',style={
                'height': '10%',
                'width': '10%',
                'display': 'block',
                'margin-left': 'auto',
                'margin-right': 'auto'}),
    # Create the title of the dashboard
    html.H1(
        children='Starting With Today',
        style={
            'textAlign': 'left',
            'color': 'white',
            'backgroundColor':'black',
            'font-family': 'arial',
            'font-weight': 'bold',
            'font-size': 40
        }
    ),
    # Add subtitle
    html.Div(
        children='Community Needs & Resources',
        style={
            'textAlign': 'left',
            'color': 'white',
            'backgroundColor':'black',
            'font-family': 'arial',
            'font-weight': 'regular',
            'font-size': 28
        }
    ),
    # Add section name
    html.Div(children='Non-Profit Organizations in the District of Columbia and Surrounding Areas.', style={
        'textAlign': 'left',
        'color': 'black',
        'backgroundColor': 'white',
        'font-family': 'arial',
        'font-weight': 'bold',
        'font-size': 24
    }),
    # Add section name description
    html.Div(children="The map below locates non-profit organizations by service type in the District of Columbia and nearby areas. Choose different services types \
        in the drop down menu to find organizations that offer the selected services. Click on each dot to be directed to the organization's website.", style={
        'textAlign': 'left',
        'color': 'black',
        'backgroundColor': 'white',
        'font-family': 'arial',
        'font-weight': 'regular',
        'font-size': 16
    }),
    # Add the dropdown of service type
    html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    services,
                    ['Mental Health','Economic Development'],
                    id='types-of-service',
                    multi=True
                ),
            ], style={'width': '100%',
                      'display':'inline-block',
                      'textAlign': 'left',
                      'color': 'black',
                      'backgroundColor': 'white',
                      'font-family': 'arial',
                      'font-weight': 'regular',
                      'font-size': 16})])]),
    # Add the non-profit map graph
    html.Div([
        dcc.Graph(id='non-profit-map'),
        html.Pre(id='data')]),
    # Add section for number of organizations based in DC overall and Wards 7 and 8
    html.Div(children='Number of non-profit organizations by service area in DC and Wards 7 and 8', style={
            'textAlign': 'left',
            'color': 'black',
            'backgroundColor':'white',
            'font-family': 'arial',
            'font-weight': 'bold',
            'font-size': 24
    }),
    # Add plot of the number of organizations by service type
    html.Div([
        html.Div(style={
            'textAlign': 'center',
            'color': 'black',
            'font-family': 'arial'}),
            dcc.Graph(
                id='svcs',
                figure=fig_svcs)]),
    # Add section for community needs score
    html.Div(children="Census Tract Areas With Highest Level of Need for Starting With Today's Services", style={
            'textAlign': 'left',
            'color': 'black',
            'backgroundColor':'white',
            'font-family': 'arial',
            'font-weight': 'bold',
            'font-size': 16
    }),
    # Add section description
    html.Div(children='A Community Needs Score is created by weighting each of the community needs factors between 0% to 100%. The percentage value in the box to the right of each factor sets the weight or importance of that factor. A larger  percentage indicates greater importance. All weights must sum up to 100%. The blue points in the map represent locations where Starting With Today is currently providing its services.',
        style={'textAlign': 'left','color': 'black','backgroundColor':'white','font-family': 'arial','font-weight': 'regular','font-size': 16}),

    html.Div(children="Set the importance of each factor below.", style={
            'textAlign': 'left',
            'color': 'black',
            'backgroundColor':'white',
            'font-family': 'arial',
            'font-weight': 'bold',
            'font-size': 16
    }),
    # Add weight inputs to provide ability for user to modify weights
    html.Div([
        "Poverty: ",
        dcc.Input(id='my-input1', value=30, type='number')], style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'bold',
                'font-size': 16
        }),
    html.Div([
        "Health Insurance: ",
        dcc.Input(id='my-input2', value=20, type='number')], style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'bold',
                'font-size': 16
        }),
    html.Div([
        "Depression: ",
        dcc.Input(id='my-input3', value=20, type='number')], style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'bold',
                'font-size': 16
        }),
    html.Div([
        "Income inequality (Gini) index: ",
        dcc.Input(id='my-input4', value=10, type='number')], style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'bold',
                'font-size': 16
        }),
    html.Div([
        "High school degree attainment: ",
        dcc.Input(id='my-input5', value=10, type='number')], style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'bold',
                'font-size': 16
        }),
    html.Div([
        "Vehicle Access: ",
        dcc.Input(id='my-input6', value=5, type='number')], style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'bold',
                'font-size': 16
        }),
    html.Div([
        "Internet Acces: ",
        dcc.Input(id='my-input7', value=2.5, type='number')], style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'bold',
                'font-size': 16
        }),
    html.Div([
        "Walkability Score: ",
        dcc.Input(id='my-input8', value=2.5, type='number')], style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'bold',
                'font-size': 16
        }),
    # Add submit button to input updated weights for computation of needs score
    html.Div(children='Press SUBMIT below to update needs as desired in the needs score.',
        style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'regular',
                'font-size': 16
        }),

    html.Button(id='submit-button-state', n_clicks=0, children='Submit',
        style={
                'textAlign': 'left',
                'color': 'black',
                'backgroundColor':'white',
                'font-family': 'arial',
                'font-weight': 'bold',
                'font-size': 20
        }),
    # Add the needs score map
    html.Div(children=[
        dcc.Graph(id="graph2")]),

    # Add a section to display individual components of the needs score
    html.Div(children='Choose one of the factors in the needs score and demographic data to compare each factor to the composite needs score.',style={
                        'textAlign': 'left',
                        'color': 'black',
                        'backgroundColor':'white',
                        'font-family': 'arial',
                        'font-weight': 'regular',
                        'font-size': 16
                }),
    # Add a drop down list to allow the user to select the desired feature
    html.Div(children=[
        dcc.Dropdown(features,'Percentage of Black residents',id='xaxis-column',
                style={'textAlign': 'left','color': 'black','backgroundColor':'white','font-family': 'arial','font-weight': 'bold','font-size': 16}),
    # Add the map of each feature
        html.Div(children=[
            dcc.Graph(id="indicator-graphic")])])
])

# Add map for location of non-profit orgs
@app.callback(
    Output('non-profit-map','figure'),
    Input('types-of-service','value'))
def update_graph(service):
    dff = df[np.sum(df[service],axis=1) > 0]

    for serv in service:
        dff[serv] = dff[serv].replace(1,serv).replace(0,'')

    dff['Service Areas Legend:'] = [' & '.join([val for val in sorted(list(val)) if val != '']) \
        for val in dff[sorted(service)].apply(tuple, axis=1)]

    fig = px.scatter_mapbox(dff,
                            lat="lat",
                            lon="lng",
                            hover_name="name",
                            hover_data={"Website:":True,'lat':False,'lng':False},
                            color='Service Areas Legend:',
                            zoom=11,
                            height=600)

    fig.update_layout(mapbox_style="open-street-map",
        legend=dict(orientation="h"))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='black')
    fig.update_layout(clickmode='event+select',legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(color='black',size=12)),paper_bgcolor="white")

    return fig

# Add maps for needs score
@app.callback(
    Output('graph2', 'figure'),
    Input('submit-button-state', 'n_clicks'),
    State('my-input1', 'value'),
    State('my-input2', 'value'),
    State('my-input3', 'value'),
    State('my-input4', 'value'),
    State('my-input5', 'value'),
    State('my-input6', 'value'),
    State('my-input7', 'value'),
    State('my-input8', 'value'))
def update_needs_score(n_clicks,input1, input2, input3, input4, input5, input6, input7, input8, locs = locs,
    needs_score_dc = needs_score_dc,needs_score_md = needs_score_md, req_dc = req_dc, req_md = req_md):

    for i in range(1,9):
        weighti = 0

    if input1 != 30:
        weight1 = input1
    else:
        weight1 = 30

    if input2 != 20:
        weight2 = input2
    else:
        weight2 = 20

    if input3 != 20:
        weight3 = input3
    else:
        weight3 = 20

    if input4 != 10:
        weight4 = input4
    else:
        weight4 = 10

    if input5 != 10:
        weight5 = input5
    else:
        weight5 = 10

    if input6 != 5:
        weight6 = input6
    else:
        weight6 = 5

    if input7 != 2.5:
        weight7 = input7
    else:
        weight7 = 2.5

    if input8 != 2.5:
        weight8 = input8
    else:
        weight8 = 2.5

    needs_score_dc = pd.read_csv('https://startingwithtoday.s3.amazonaws.com/needs_score_dc.csv')

    needs_score_md = pd.read_csv('https://startingwithtoday.s3.amazonaws.com/needs_score_md.csv')
    #Create another map of the race feature.
    needs_score_dc['zw_blw_pov_lvl_pe'] = needs_score_dc['z_blw_pov_lvl_pe'] * float(weight1/100)
    needs_score_dc['zw_no_health_ins_pe'] = needs_score_dc['z_no_health_ins_pe'] * float(weight2/100)
    needs_score_dc['zw_depression_rate'] = needs_score_dc['z_depression_rate'] * float(weight3/100)
    needs_score_dc['zw_gini_ind_inequality_e'] = needs_score_dc['z_gini_ind_inequality_e'] * float(weight4/100)
    needs_score_dc['zw_hs_grad_pe_gap'] = needs_score_dc['z_hs_grad_pe_gap'] * float(weight5/100)
    needs_score_dc['zw_no_veh_pe'] = needs_score_dc['z_no_veh_pe'] * float(weight6/100)
    needs_score_dc['zw_broadband_pe_gap'] = needs_score_dc['z_broadband_pe_gap'] * float(weight7/100)
    needs_score_dc['zw_median_natwalkind_gap'] = needs_score_dc['z_median_natwalkind_gap'] * float(weight8/100)

    needs_score_dc['zw_overall'] = np.sum(needs_score_dc[['zw_blw_pov_lvl_pe','zw_depression_rate','zw_no_health_ins_pe',
                                'zw_gini_ind_inequality_e','zw_no_veh_pe','zw_hs_grad_pe_gap',
                                'zw_broadband_pe_gap','zw_median_natwalkind_gap']],axis=1)

    needs_score_dc['zr_overall'] = needs_score_dc['zw_overall'] - needs_score_dc['zw_overall'].min()

    needs_score_dc['rf_overall'] = 100 * (needs_score_dc['zr_overall'] / needs_score_dc['zr_overall'].max())

    needs_score_dc.rename(columns={'rf_overall':'Needs Score'},inplace=True)

    #Create another map of the race feature.
    needs_score_md['zw_blw_pov_lvl_pe'] = needs_score_md['z_blw_pov_lvl_pe'] * float(weight1/100)
    needs_score_md['zw_no_health_ins_pe'] = needs_score_md['z_no_health_ins_pe'] * float(weight2/100)
    needs_score_md['zw_depression_rate'] = needs_score_md['z_depression_rate'] * float(weight3/100)
    needs_score_md['zw_gini_ind_inequality_e'] = needs_score_md['z_gini_ind_inequality_e'] * float(weight4/100)
    needs_score_md['zw_hs_grad_pe_gap'] = needs_score_md['z_hs_grad_pe_gap'] * float(weight5/100)
    needs_score_md['zw_no_veh_pe'] = needs_score_md['z_no_veh_pe'] * float(weight6/100)
    needs_score_md['zw_broadband_pe_gap'] = needs_score_md['z_broadband_pe_gap'] * float(weight7/100)
    needs_score_md['zw_median_natwalkind_gap'] = needs_score_md['z_median_natwalkind_gap'] * float(weight8/100)

    needs_score_md['zw_overall'] = np.sum(needs_score_md[['zw_blw_pov_lvl_pe','zw_depression_rate','zw_no_health_ins_pe',
                                'zw_gini_ind_inequality_e','zw_no_veh_pe','zw_hs_grad_pe_gap',
                                'zw_broadband_pe_gap','zw_median_natwalkind_gap']],axis=1)

    needs_score_md['zr_overall'] = needs_score_md['zw_overall'] - needs_score_md['zw_overall'].min()

    needs_score_md['rf_overall'] = 100 * (needs_score_md['zr_overall'] / needs_score_md['zr_overall'].max())

    needs_score_md.rename(columns={'rf_overall':'Needs Score'},inplace=True)

    json_dc = req_dc.json()

    json_md = req_md.json()

    locs = px.scatter_geo(locs,
                   lat='latitude',
                   lon='longitude',
                   hover_data={'Location':True,
                              'Address':True,
                              'latitude':False,
                              'longitude':False},
                   center={'lat':38.8938005,'lon':-77.1579293},
                   scope="usa",
                   size_max=12,
                   height=700)
    locs.update_traces(marker=dict(size=12),hoverinfo="location")

    fig_score_dc = px.choropleth(needs_score_dc,
                        geojson=json_dc,
                        locations='GEOID',
                        color='Needs Score',
                        color_continuous_scale="YlOrRd",
                        featureidkey="properties.GEOID",
                        scope="usa",
                        center={'lat':38.8938005,'lon':-77.1579293},
                        hover_data=['Percentage of population below poverty line', 'Depression rate',
                               'Percentage of households without health insurance',
                               'Gini inequality index', 'Percentage of households without vehicles',
                               'Percentage of Black residents',
                               'Percentage of residents with internet access',
                               'Percentage of residents with a high school diploma',
                               'Walkability score', 'Zip Code', 'Ward/County'],
                        fitbounds="locations",
                        height=700)

    fig_score_dc.add_trace(locs.data[0])
    fig_score_dc.update_layout(autosize=True,paper_bgcolor="white", font_color="black")

    fig_score_md = px.choropleth(needs_score_md,
                        geojson=json_md,
                        locations='GEOID',
                        color='Needs Score',
                        color_continuous_scale="YlOrRd",
                        featureidkey="properties.GEOID",
                        scope="usa",
                        center={'lat':38.8938005,'lon':-77.1579293},
                        hover_data=['Percentage of population below poverty line', 'Depression rate',
                               'Percentage of households without health insurance',
                               'Gini inequality index', 'Percentage of households without vehicles',
                               'Percentage of Black residents',
                               'Percentage of residents with internet access',
                               'Percentage of residents with a high school diploma',
                               'Walkability score', 'Zip Code', 'Ward/County'],
                        fitbounds="locations",
                        height=700)

    fig_score_dc.add_trace(fig_score_md.data[0])

    return fig_score_dc

# Add map plotting each feature included in the composite score
@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'))
def update_map(xaxis_column_name,display_data = display_data, req_dc = req_dc, req_md = req_md):

    json_dc = req_dc.json()

    fig_map_dc = px.choropleth(display_data[display_data['countyname'] == 'District of Columbia'],
                        geojson=json_dc,
                        locations='GEOID',
                        color=xaxis_column_name,
                        color_continuous_scale="Blues",
                        featureidkey="properties.GEOID",
                        scope="usa",
                        center={'lat':38.8938005,'lon':-77.1579293},
                        hover_data=[xaxis_column_name,'Zip Code','Ward/County'],
                        fitbounds="locations",
                        height=700)
    fig_map_dc.update_layout(paper_bgcolor="white", font_color="black")

    json_md = req_md.json()

    fig_map_pg = px.choropleth(display_data[display_data['countyname'] == "Prince George's"],
                        geojson=json_md,
                        locations='GEOID',
                        color=xaxis_column_name,
                        color_continuous_scale="Blues",
                        featureidkey="properties.GEOID",
                        scope="usa",
                        center={'lat':38.8938005,'lon':-77.1579293},
                        hover_data=[xaxis_column_name,'Zip Code','Ward/County'],
                        fitbounds="locations",
                        height=700)
    fig_map_pg.update_layout(paper_bgcolor="white", font_color="black")

    fig_map_dc.add_trace(fig_map_pg.data[0])

    return fig_map_dc

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
