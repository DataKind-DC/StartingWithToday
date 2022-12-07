import webbrowser
from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import numpy as np
import json 

app = Dash(__name__)

df = pd.read_csv('../StartingWithToday/data/non-profit-orgs-cleaned.csv')

df.rename(columns={'website':'Website:'},inplace=True)
excluded_cols = len(['org_url', 'name', 'location', 'website', 'about', 'services',
                     'org_type', 'lat', 'lng', 'zip'])

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'font-family': 'Verdana',
    'font-weight': 'bold'
}

services = list(df.iloc[:,excluded_cols-len(df.columns):].sum().index)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='StartingWithToday Business Intelligence Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'font-family': colors['font-family']
        }
    ),

    html.Div(children='Strategic partners, community needs, and demographics', style={
        'textAlign': 'center',
        'color': colors['text'],
        'font-family': colors['font-family']
    }),

    html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    services,
                    ['Mental Health','Economic Development'],
                    id='types-of-service',
                    multi=True
                ),
            ], style={'width': '26.5%','display':'inline-block','font-family': colors['font-family'],
                      'font-weight': colors['font-weight']})
        ]),
        dcc.Graph(id='non-profit-map'),
        html.Pre(id='data')
    ])
])
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
                            width=501)

    fig.update_layout(mapbox_style="open-street-map",
        legend=dict(orientation="h"))
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'])
    fig.update_layout(clickmode='event+select')

    return fig

@app.callback(
    Output('data', 'children'),
    Input('non-profit-map', 'clickData'))
def open_url(clickData):
   if clickData:
       webbrowser.open(clickData["points"][0]["customdata"][0])
   else:
      raise PreventUpdate
      # return json.dumps(clickData, indent=2)

if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1')
