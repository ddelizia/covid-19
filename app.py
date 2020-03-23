import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Output, Input

from data import data_ccaa, get_ccaa, data_exp

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def selector():
    ccaa = get_ccaa()
    return dcc.Dropdown(
        id='selector',
        options=[{'label': x, 'value': x} for x in ccaa],
        value='Total'
    )


def comparator_selector():
    ccaa = get_ccaa()
    return dcc.Dropdown(
        id='comporator-selector',
        options=[{'label': x, 'value': x} for x in filter(lambda i: i != 'Total', ccaa)],
        multi=True,
    )

def box(color, text, value):
    return html.Div(className=f'column is-3', children=[
            html.Div(className=f'notification {color}', children=[
                html.H1(className='title',  children=text),
                html.P(className='subtitle', children=value)
            ])
        ])

def info_box():
    df = data_ccaa('Total')

    all = df["all"][-1]
    remaining = df["remaining"][-1]
    deaths = df["deaths"][-1]
    uci = df["uci"][-1]
    recovered = df["recovered"][-1]

    return html.Div(className='columns', children=[
        box('is-info', 'All cases', all),
        box('is-warning', 'ICU', uci),
        box('is-success', 'Recovered', recovered),
        box('is-danger', 'Deaths', deaths),

    ])




app.layout = html.Div(className='container', children=[

    html.H1(className='title', children='Covid-19 Spain Dashboard'),

    html.P(className='subtitle', children='''
        Data exploration for Spain Cases evolution. Data from: https://github.com/datadista/datasets/tree/master/COVID%2019
    '''),
    info_box(),
    dcc.Tabs([
        dcc.Tab(label='Explore data', children=[
            selector(),
            html.Div(id='fig-overview'),
            html.Div(id='table')
        ]),
        dcc.Tab(label='Comparision', children=[
            comparator_selector(),
            html.Div(id='fig-comparator')
        ]),
    ])
])


@app.callback(
    Output(component_id='table', component_property='children'),
    [Input(component_id='selector', component_property='value')]
)
def table(ca):
    df = data_ccaa(ca)
    return dash_table.DataTable(
        id='table-data',
        columns=[
            {"name": 'All cases', "id": 'all'},
            {"name": 'Active cases', "id": 'remaining'},
            {"name": 'Recovered', "id": 'recovered'},
            {"name": 'Cases in ICU', "id": 'uci'},
            {"name": 'Deaths', "id": 'deaths'},
        ],
        data=df.to_dict('records'),
    )


def _build_figure_grid(layout_grid):
    return [html.Div(className='columns', children=[html.Div(className=f'column is-{12/len(row)}', children=[x]) for x in row])
            for row in layout_grid]


@app.callback(
    Output(component_id='fig-comparator', component_property='children'),
    [Input(component_id='comporator-selector', component_property='value')]
)
def fig_comparator(ca):
    if ca is None:
        return None
    df = data_ccaa('Total')
    all_cases = dcc.Graph(
        figure=dict(
            data=[{'x': df.index, 'y': data_ccaa(x)['all'], 'name': x} for x in ca],
            layout=dict(
                title=f"All cases [{', '.join(ca)}]"
            )
        ),
    )

    recovered = dcc.Graph(
        figure=dict(
            data=[{'x': df.index, 'y': data_ccaa(x)['recovered'], 'name': x} for x in ca],
            layout=dict(
                title=f"Recovered [{', '.join(ca)}]"
            )
        ),
    )

    deaths = dcc.Graph(
        figure=dict(
            data=[{'x': df.index, 'y': data_ccaa(x)['deaths'], 'name': x} for x in ca],
            layout=dict(
                title=f"Deaths [{', '.join(ca)}]"
            )
        ),
    )
    layout_grid = [
        [all_cases],
        [recovered, deaths]
    ]
    return _build_figure_grid(layout_grid)


@app.callback(
    Output(component_id='fig-overview', component_property='children'),
    [Input(component_id='selector', component_property='value')]
)
def fig_overview(ca):
    df = data_ccaa(ca)
    fig_all_cases = dcc.Graph(
        figure=dict(
            data=[
                {'x': df.index, 'y': df['all'], 'name': 'All cases'},
            ],
            layout=dict(
                title=f"All cases [{ca}]",
            )
        ),
    )

    fig_resume = dcc.Graph(
        figure=dict(
            data=[
                {'type': 'bar', 'x': df.index, 'y': df['remaining'], 'name': 'Remaining', 'marker': {'color': 'darkorange'}},
                {'type': 'bar', 'x': df.index, 'y': df['uci'], 'name': 'Icus', 'marker': {'color': 'crimson'}},
                {'type': 'bar', 'x': df.index, 'y': df['recovered'], 'name': 'Recovered', 'marker': {'color': 'forestgreen'}},
                {'type': 'bar', 'x': df.index, 'y': df['deaths'], 'name': 'Deaths', 'marker': {'color': 'black'}},
            ],
            layout=dict(
                title=f"Comparision [{ca}]",
            )
        ),
    )

    fig_all_cases_delta = dcc.Graph(
        figure=dict(
            data=[
                {'type': 'bar', 'x': df.index, 'y': df['all'].diff(), 'name': 'All cases delta'},
            ],
            layout=dict(title=f"All case delta [{ca}]",)
        ),
    )

    fig_all_cases_delta_pct = dcc.Graph(
        figure=dict(
            data=[
                {'type': 'bar', 'x': df.index, 'y': df['all'].diff().pct_change(), 'name': 'All cases delta %'},
            ],
            layout=dict(title=f"All case delta [{ca}]",)
        ),
    )

    fig_icus_cases_delta = dcc.Graph(
        figure=dict(
            data=[
                {'type': 'bar', 'x': df.index, 'y': df['uci'].diff(), 'name': 'Icus delta', 'marker': {'color': 'crimson'}},
            ],
            layout=dict(title=f"Icus case delta [{ca}]",)
        ),
    )

    fig_icus_cases_delta_pct = dcc.Graph(
        figure=dict(
            data=[
                {'type': 'bar', 'x': df.index, 'y': df['uci'].diff().pct_change(), 'name': 'Icus delta %', 'marker': {'color': 'crimson'}},
            ],
            layout=dict(title=f"Icus case delta [{ca}]",)
        ),
    )

    fig_recovered_cases_delta = dcc.Graph(
        figure=dict(
            data=[
                {'type': 'bar', 'x': df.index, 'y': df['recovered'].diff(), 'name': 'Icus delta', 'marker': {'color': 'forestgreen'}},
            ],
            layout=dict(title=f"Recovered case delta [{ca}]",)
        ),
    )

    fig_recovered_cases_delta_pct = dcc.Graph(
        figure=dict(
            data=[
                {'type': 'bar', 'x': df.index, 'y': df['recovered'].diff().pct_change(), 'name': 'Icus delta %', 'marker': {'color': 'forestgreen'}},
            ],
            layout=dict(title=f"Recovered case delta [{ca}]",)
        ),
    )

    fig_deaths_cases_delta = dcc.Graph(
        figure=dict(
            data=[
                {'type': 'bar', 'x': df.index, 'y': df['deaths'].diff(), 'name': 'Icus delta', 'marker': {'color': 'black'}},
            ],
            layout=dict(title=f"Deaths delta [{ca}]",)
        ),
    )

    fig_deaths_cases_delta_pct = dcc.Graph(
        figure=dict(
            data=[
                {'type': 'bar', 'x': df.index, 'y': df['deaths'].diff().pct_change(), 'name': 'Icus delta %', 'marker': {'color': 'black'}},
            ],
            layout=dict(title=f"Deaths delta [{ca}]",)
        ),
    )

    exp1, exp2, exp3, exp4 = data_exp()

    fig_exp_growth = dcc.Graph(
        figure=dict(
            data=[
                {'x': df.index, 'y': df['all'], 'name': 'All cases'},
                {'x': df.index, 'y': exp1, 'name': 'Doubling cases every day', 'marker': {'dash': 'dash', 'line': { 'width': 1, 'dash': 'dash'}}},
                {'x': df.index, 'y': exp2, 'name': 'Doubling cases every 2 days', 'marker': {'line': {'width': 1, 'dash': 'dash'}}},
                {'x': df.index, 'y': exp3, 'name': 'Doubling cases every 3 days', 'marker': {'line': {'width': 1, 'dash': 'dash'}}},
                {'x': df.index, 'y': exp4, 'name': 'Doubling cases every 4 days', 'marker': {'line': {'width': 1, 'dash': 'dash'}}},
            ],
            layout=dict(
                title=f"Exponential growth [{ca}]",
                yaxis={'type': 'log', 'autorange': True}
            )
        ),
    )


    layout_grid = [
        [fig_all_cases, fig_resume],
        [fig_all_cases_delta, fig_all_cases_delta_pct],
        [fig_icus_cases_delta, fig_icus_cases_delta_pct],
        [fig_recovered_cases_delta, fig_recovered_cases_delta_pct],
        [fig_deaths_cases_delta, fig_deaths_cases_delta_pct],
        [fig_exp_growth,]
    ]

    return _build_figure_grid(layout_grid)



server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)