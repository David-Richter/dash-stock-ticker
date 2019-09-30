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
import dash_table

os.environ["TIINGO_API_KEY"] = "40231a5007eef7ce495a2a14fe16093e614e8226"

# USERNAME_PASSWORD_PAIRS = {
#     'dynvis': 'jupyterDynvis'
# }

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
)

#auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

server = app.server

nsdq = pd.read_csv('data/NASDAQcompanylist.csv')
nsdq.set_index('Symbol', inplace=True)
stock = web.get_data_tiingo('GOOG', api_key=os.getenv('TIINGO_API_KEY'))

table_test = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Stock Ticker",
    className='layout',
    fluid=True,
)

table_data = stock.reset_index()
table_data["date"] = table_data["date"].dt.strftime('%d.%m.%Y ')

app.layout = dfx.Grid(
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
                    className='dataTable',
                    id='stock_data_table',
                    children=[
                        dash_table.DataTable(
                            id='table',
                            columns=[{"name": i, "id": i, "deletable": True, "selectable": True} for i in table_data.columns],
                            data = table_data.to_dict("records"),
                            fixed_rows={ 'headers': True, 'data': 0 },
                            style_table={
                                'maxHeight': '300px',
                                'overflowY': 'scroll',
                                'overflowX': 'scroll',
                                'border': 'thin lightgrey solid'
                            },
                            style_cell={
                                'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                            },
                            editable=True,
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            column_selectable="single",
                            row_selectable="multi",
                            row_deletable=True,
                            selected_columns=[],
                            selected_rows=[],
                            page_action="native",
                            page_current= 0,
                            page_size= 10
                        )
                    ]
                ),
                dfx.Col(
                    xs=12,
                    children=[
                        dcc.Graph(
                            id="stock_graph",
                            config={
                                "displaylogo": False
                            },
                            figure={
                                'data': [
                                    {'x': stock.loc["GOOG"].index,
                                    'y': stock.loc["GOOG"]["close"]}
                                ],
                                'layout': {
                                    'title': 'Stock Name',
                                                            'plot_bgcolor': 'rgba(255,255,255,1)'
                                }
                            }
                        )
                    ]
                ),
                dfx.Col(
                    xs=12,
                    children=[
                        dcc.Graph(
                            id="stock_graph_candle",
                            config={
                                "displaylogo": False
                            },
                            figure = go.Figure(
                                data=[
                                    go.Candlestick(
                                        x=stock.loc["GOOG"].index,
                                        open=stock.loc["GOOG"]["open"],
                                        high=stock.loc["GOOG"]["high"],
                                        low=stock.loc["GOOG"]["low"],
                                        close=stock.loc["GOOG"]["close"]
                                    )
                                ],
                                layout= go.Layout(
                                    plot_bgcolor='rgba(255,255,255,1)'
                                )
                            )
                        )
                    ]
                )
            ]
        )
    ]
)


@app.callback(
    Output('table', 'style_data_conditional'),
    [Input('table', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]



@app.callback(
    Output('stock_data_table', 'children'),
    [Input('submit_button', 'n_clicks')],
    [State('stock_filter', 'value'),
     State('date_filter', 'start_date'),
     State('date_filter', 'end_date')]
)
def update_table(n_clicks, stock_value, start, end):
    tables = []
        
    if len(stock_value) < 2:
        table_size = 12
    else:
        table_size = 6
    
    for i in stock_value:

        stock = web.get_data_tiingo(
            stock_value,
            api_key=os.getenv('TIINGO_API_KEY'),
            start=start,
            end=end
        )

        table_data = stock.reset_index()[stock.reset_index()["symbol"] == i]
        table_data["date"] = table_data["date"].dt.strftime('%d.%m.%Y ')
        
        tables.append(
            dfx.Col(
                xs=12,
                lg=table_size,
                children=[
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i, "deletable": True, "selectable": True} for i in table_data.columns],
                        data = table_data.to_dict("records"),
                        fixed_rows={ 'headers': True, 'data': 0 },
                        style_table={
                            'maxHeight': '300px',
                            'overflowY': 'scroll',
                            'overflowX': 'scroll',
                            'border': 'thin lightgrey solid'
                        },
                        style_cell={
                            'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                        },
                            editable=True,
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            column_selectable="single",
                            row_selectable="multi",
                            row_deletable=True,
                            selected_columns=[],
                            selected_rows=[],
                            page_action="native",
                            page_current= 0,
                            page_size= 10
                    )
                ]
            )
        )

    return tables



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
            'plot_bgcolor': 'rgba(255,255,255,1)'
        }
    }
    return figure



@app.callback(
    Output('stock_graph_candle', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('stock_filter', 'value'),
     State('date_filter', 'start_date'),
     State('date_filter', 'end_date')]
)
def update_candle_graph(n_clicks, stock_value, start, end):
    data = []
    for i in stock_value:
        stock = web.get_data_tiingo(
            stock_value,
            api_key=os.getenv('TIINGO_API_KEY'),
            start=start,
            end=end
        )
        data.append(
            go.Candlestick(
                x=stock.loc[i].index,
                open=stock.loc[i]["open"],
                high=stock.loc[i]["high"],
                low=stock.loc[i]["low"],
                close=stock.loc[i]["close"],
                name = i
            )
        )

    figure=go.Figure(
        data=data,
        layout = go.Layout(
            plot_bgcolor='rgba(255,255,255,1)',
            xaxis=dict(
                gridcolor= "#eee"
            ),
            yaxis=dict(
                gridcolor= "#eee"
            )
        )
    )

    return figure


if __name__ == "__main__":
    app.run_server()
