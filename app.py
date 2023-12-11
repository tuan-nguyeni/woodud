import base64
import io
from fileinput import filename

import pandas as pd
from flask import Flask
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State

app = Flask(__name__)
dash_app = dash.Dash(__name__, server=app, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = dash_app.server  # Expose the Flask server instance for Gunicorn

import plotly.express as px
from datetime import datetime

def create_data_quality_time_chart():
    # Mock data
    data = [
        {"date": "2023-12-04", "quality": 80},
        {"date": "2023-11-27", "quality": 70},
        {"date": "2023-11-20", "quality": 40},
        {"date": "2023-11-13", "quality": 30}
    ]
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    # Create a line chart
    fig = px.line(df, x='date', y='quality', title='Data Quality Over Time', markers=True)
    # Set more detailed date information in x-axis
    fig.update_xaxes(tickformat="%d %b %Y")
    fig.update_layout(xaxis_title='Date', yaxis_title='Data Quality (%)')

    return dcc.Graph(figure=fig)

# Dash layout
dash_app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    ),
    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='Data Quality Dashboard', children=[
            html.Div(id='data-quality-content'),
            html.Div(id='chart-container')  # Container for the interactive chart
        ]),
        dcc.Tab(label='Data View', children=[
            html.Div(id='data-view-content')
        ]),
        # Directly add the chart in the tab's content
        dcc.Tab(label='Data Quality Over Time', children=[
            html.Div(id='data-quality-time-content', children=create_data_quality_time_chart())
        ]),

    ])
])

@dash_app.callback(
    [Output('data-quality-content', 'children'),
     Output('data-view-content', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children_quality = []
        children_view = []
        for contents, name in zip(list_of_contents, list_of_names):
            df = parse_contents(contents, name)
            if df is not None:
                # Processing for Data Quality Dashboard
                gauge_chart = compute_data_quality(df, name)
                column_qualities = column_quality_analysis(df)
                column_chart = create_column_quality_chart(column_qualities)
                children_quality.extend([gauge_chart, column_chart])

                # Processing for Data View
                highlighted_data = highlight_bad_data(df)
                children_view.append(html.H5(f'Data View for {name}'))
                children_view.append(highlighted_data)

        return children_quality, children_view

    return None, None


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'xlsx' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
            return df
    except Exception as e:
        print(e)
        return None

import plotly.graph_objs as go

def compute_data_quality(df, filename):
    if "Rückmelder" not in df.columns:
        return html.Div("Column 'Rückmelder' not found", style={'color': 'red'})

    total_rows = len(df)
    good_data_rows = len(df[df["Rückmelder"] != "tmm"])

    if total_rows == 0:
        return html.Div("No data available", style={'color': 'red'})

    data_quality_percentage = (good_data_rows / total_rows) * 100
    quality_rounded = round(data_quality_percentage, 2)

    # Gauge chart component
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=quality_rounded,
        title={'text': f"Data Quality for {filename}"},
        gauge={'axis': {'range': [0, 100]}}
    ))

    return dcc.Graph(figure=fig)



def highlight_bad_data(df):
    # Replace with your logic for highlighting bad data
    return html.Div(str(df))  # Placeholder for displaying DataFrame


import plotly.express as px

def create_interactive_chart(df):
    # Modify this to match your data's columns
    fig = px.bar(df, x="YourColumn", y="AnotherColumn")  # Replace 'YourColumn' and 'AnotherColumn' with actual column names
    return fig



# Callback to update the chart
@dash_app.callback(
    Output('chart-container', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_chart(list_of_contents, list_of_names):
    if list_of_contents is not None:
        for contents, name in zip(list_of_contents, list_of_names):
            df = parse_contents(contents, name)
            if df is not None:
                fig = create_interactive_chart(df)
                return dcc.Graph(figure=fig)

    return html.Div("Upload a file to view the chart")


def column_quality_analysis(df):
    column_qualities = []
    for col in df.columns:
        total_rows = len(df)
        good_data_rows = len(df[df[col] != "tmm"])
        column_quality = (good_data_rows / total_rows) * 100 if total_rows > 0 else 0
        column_qualities.append((col, column_quality))
    return column_qualities

def create_column_quality_chart(column_qualities):
    columns, qualities = zip(*column_qualities)
    fig = px.bar(x=columns, y=qualities, labels={'x': 'Column', 'y': 'Data Quality (%)'})
    fig.update_layout(title_text='Column-Wise Data Quality')
    return dcc.Graph(figure=fig)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
