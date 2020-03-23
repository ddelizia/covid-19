import dash
import dash_core_components as dcc
import dash_table
import dash_html_components as html
from dash.dependencies import Output, Input

from data import data_ccaa, get_ccaa

external_stylesheets = ['"https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def selector():
    ccaa = get_ccaa()
    return dcc.Dropdown(
        id='selector',
        options=[{'label': x, 'value': x} for x in ccaa],
        value='Total'
    )


app.layout = html.Div(className='container', children=[

    html.H1(className='title', children='Covid-19 Spain Dashboard'),

    html.P(className='subtitle', children='''
        Data exploration for Spain Cases evolution. Data available provided by: https://github.com/datadista/datasets/tree/master/COVID%2019
    '''),
    selector(),

    html.Div(id='fig-overview'),
    html.Div(id='table'),

])

@app.callback(
    Output(component_id='table', component_property='children'),
    [Input(component_id='selector', component_property='value')]
)
def table(ca):
    df = data_ccaa(ca)
    return dash_table.DataTable(
        id='table-data',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
    )

@app.callback(
    Output(component_id='fig-overview', component_property='children'),
    [Input(component_id='selector', component_property='value')]
)
def fig_overview(ca):
    df = data_ccaa(ca)
    return dcc.Graph(
        figure=dict(
            data=[
                dict(
                    x=df.index,
                    y=df['remaining'],
                    name='Ramaining'
                ),
                dict(
                    x=df.index,
                    y=df['uci'],
                    name='Icus'
                ),
                dict(
                    x=df.index,
                    y=df['recovered'],
                    name='Recovered'
                ),
                dict(
                    x=df.index,
                    y=df['deaths'],
                    name='Deaths'
                ),
            ],
            layout=dict(
                title=f"Data {ca}",
            )
        ),
    )

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)