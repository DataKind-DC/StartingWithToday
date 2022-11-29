from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'font-family': 'Verdana',
    'font-weight': 'bold'
}

df = pd.read_csv('../StartingWithToday/data/non-profit-orgs-cleaned.csv')

excluded_cols = len(['org_url', 'name', 'location', 'website', 'about', 'services',
                     'org_type', 'lat', 'lng', 'zip'])

services = list(df.iloc[:,excluded_cols-len(df.columns):].sum().index)

# Generate data for number of organizations by type of service across DC
svcs = pd.DataFrame(df.iloc[:,excluded_cols-len(df.columns):].sum())
svcs.reset_index(inplace=True)
svcs.rename(columns={'index':'Service',0:'Number of organizations'},inplace=True)

# Generate data for number of organizations by type of service in Wards 7 and 8
svcs_wards_7_8 = pd.DataFrame(df[(df['zip'] == '20002') | (df['zip'] == '20003') | (df['zip'] == '20019') | \
                    (df['zip'] == '20020') | (df['zip'] == '20024') | (df['zip'] == '20373') | \
                    (df['zip'] == '20032')].iloc[:,excluded_cols-len(df.columns):].sum())
svcs_wards_7_8.reset_index(inplace=True)
svcs_wards_7_8.rename(columns={'index':'Service',0:'Number of organizations'},inplace=True)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Non-profit providers by service area in Washington, DC',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'font-family': colors['font-family']
        }
    ),

    html.Div(children='Data source: idealist.org', style={
        'textAlign': 'center',
        'color': colors['text'],
        'font-family': colors['font-family']
    }),

    html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    services,
                    'Mental Health',
                    id='types-of-service',
                    multi=True
                ),
            ], style={'width': '36%','display':'inline-block','font-family': colors['font-family'],
                      'font-weight': colors['font-weight']})
        ]),

        dcc.Graph(id='non-profit-map')
    ])
])
@app.callback(
    Output('non-profit-map','figure'),
    Input('types-of-service','value'))
def update_graph(service):
    dff = df[df['services'].str.contains(' & '.join(sorted(service)))]

    fig = px.scatter_mapbox(dff,
                            lat="lat",
                            lon="lng",
                            hover_name="name",
                            hover_data={"website":True,'lat':False,'lng':False},
                            zoom=10,
                            height=500,
                            width=400)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'])

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1')
