import dash_core_components as dcc
import dash_html_components as html

from data import getData

data = getData()


def build_figure_grid(layout_grid):
    return [html.Div(className='columns',
                     children=[html.Div(className=f'column is-12-mobile is-{12 / len(row)}', children=[x]) for x in row])
            for row in layout_grid]


def selector():
    ccaa = data.get_ccaa()
    return dcc.Dropdown(
        id='selector',
        options=[{'label': x, 'value': x} for x in ccaa],
        value='Total'
    )


def comparator_selector():
    ccaa = data.get_ccaa()
    return dcc.Dropdown(
        id='comporator-selector',
        options=[{'label': x, 'value': x} for x in filter(lambda i: i != 'Total', ccaa)],
        multi=True,
    )


def box(color, value, text):
    return html.Div(className=f'column is-3', children=[
        html.Div(className=f'notification {color}', children=[
            html.H1(className='title', children=text),
            html.P(className='subtitle', children=value)
        ])
    ])