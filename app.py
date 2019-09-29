import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import dash_flexbox_grid as dfx
from dash.dependencies import Input, Output, State
import pandas_datareader.data as web
from datetime import datetime as dt
import pandas as pd
import os
import plotly.graph_objs as go

os.environ["TIINGO_API_KEY"] = "40231a5007eef7ce495a2a14fe16093e614e8226"

 external_scripts = [
     'https://fonts.googleapis.com/css?family=Roboto&display=swap'
 ]

 USERNAME_PASSWORD_PAIRS = [
     ['dynvis', 'dynvis2019']
 ]

auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
    external_scripts=external_scripts
)

server = app.server

nsdq = pd.read_csv('data/NASDAQcompanylist.csv')
nsdq.set_index('Symbol', inplace=True)
stock = web.get_data_tiingo('GOOG', api_key=os.getenv('TIINGO_API_KEY'))

app.layout = dfx.Grid(
    className='layout',
    fluid=True,
    children=[
        html.H1(className='heading', children="Stock Ticker Dashboard 1.0"),
        dfx.Row(className='filter_container', children=[
            dfx.Col(
                xs=12,
                lg=6,
                className='stock_filter_container',
                children=[
                    html.Label("Select stock symbols:"),
                    dcc.Dropdown(
                        id="stock_filter",
                        options=[
                            {
                                'label': '{} - {}'.format(i, nsdq.loc[i]['Name']),
                                'value':i
                            } for i in nsdq.index
                        ],
                        multi=True,
                        value=["GOOG"]
                    )
                ]
            ),
            dfx.Col(
                xs=12,
                lg=4,
                className='date_filter_container',
                children=[
                    html.Label("Select start and end dates:"),
                    dcc.DatePickerRange(
                        id='date_filter',
                        start_date=dt(2018, 1, 1),
                        end_date=dt.today(),
                        min_date_allowed=dt(2014, 1, 1),
                        max_date_allowed=dt.today(),
                    )
                ]
            ),
            dfx.Col(
                xs=12,
                lg=2,
                className="submit_button",
                children=[
                    html.Div(
                        id="submit_button",
                        children="Submit"
                    )
                ]
            )
        ]),
        dfx.Row(
            className='graph_container', children=[
                dfx.Col(
                    xs=12,
                    children=[
                        dcc.Graph(
                            id="stock_graph",
                            config={
                                "responsive": True,
                                "displaylogo": False
                            },
                            figure={
                                'data': [
                                    {'x': stock.loc["GOOG"].index,
                                    'y': stock.loc["GOOG"]["close"]}
                                ],
                                'layout': {
                                    'title': 'Stock Name'                            
                                }
                            }
                        )
                    ]
                )
            ]
        )
    ]
)


@app.callback(
    Output('stock_graph', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('stock_filter', 'value'),
     State('date_filter', 'start_date'),
     State('date_filter', 'end_date')]
)
def update_graph(n_clicks, stock_value, start, end):
    traces = []
    for i in stock_value:
        stock = web.get_data_tiingo(
            stock_value,
            api_key=os.getenv('TIINGO_API_KEY'),
            start=start,
            end=end
        )
        traces.append(
            {'x': stock.loc[i].index, 'y': stock.loc[i]["close"], 'name': i})

    figure = {
        'data': traces,
        'layout': {
            'title': ', '.join(stock_value)+' Closing Prices',
        }
    }
    return figure


if __name__ == "__main__":
    app.run_server()
