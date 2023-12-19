#layout.py

from dash import dcc, html
from constants import *

def create_layout():
    layout = html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([LABEL_SELECT_FILES, html.A('Select Files')]),
            style=UPLOAD_STYLE,
            multiple=True
        ),
        html.Div(id='output-container'),
        dcc.Loading(
            id="loading-1",
            type=LABEL_LOADING_TYPE_DEFAULT,
            children=dcc.Tabs(id='tabs', children=[
                dcc.Tab(label=LABEL_DATA_QUALITY_DASHBOARD, children=[
                    html.Div([
                        dcc.Dropdown(
                            id='column-select-dropdown',
                            options=[],
                            value=None,
                            style={'width': '50%'}
                        ),
                        html.Div(id='quality-chart-container')
                    ]),
                    html.Div(id='data-quality-content'),
                    html.Div(id='chart-container')
                ]),
                dcc.Tab(label=LABEL_FULL_DATA_VIEW, children=[
                    html.Div(id='data-view-content')
                ]),
                dcc.Tab(label=LABEL_DATA_ERROR, children=[
                    html.Div(id='data-error-content')
                ]),
            ])
        ),
    ])
    return layout
