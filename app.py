import base64
import io
from fileinput import filename

import pandas as pd
from dash.dash_table import DataTable
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
    fig = px.line(df, x='date', y='quality', title='Data Quality Over Time (With Dummy Data)', markers=True)
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
    dcc.Loading(
        id="loading-1",
        type="default",  # Can choose from "graph", "cube", "circle", "dot", or "default"
        children=dcc.Tabs(id='tabs', children=[
                dcc.Tab(label='Data Quality Dashboard', children=[
                    html.Div([
                        dcc.Dropdown(
                            id='column-select-dropdown',
                            # Initially, options will be empty. They will be set when a file is uploaded.
                            options=[],
                            value=None,
                            style={'width': '50%'}
                        ),
                        html.Div(id='quality-chart-container')  # Container for the interactive chart
                    ]),
                    html.Div(id='data-quality-content'),
                    html.Div(id='chart-container')  # Container for the interactive chart

                ]),
                dcc.Tab(label='Full Data View', children=[
                    html.Div(id='data-view-content')
                ]),
                dcc.Tab(label='Data Error', children=[
                    html.Div(id='data-error-content')
                ]),
                # Directly add the chart in the tab's content
                # dcc.Tab(label='Data Quality Over Time', children=[
                #   html.Div(id='data-quality-time-content', children=create_data_quality_time_chart())
                # ]),

        ])
    ),
])

@dash_app.callback(
    [Output('data-quality-content', 'children'),
     Output('data-view-content', 'children'),
     Output('data-error-content', 'children')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children_quality = []
        children_view = []
        children_error = []
        for contents, name in zip(list_of_contents, list_of_names):
            df = parse_contents(contents, name)
            if df is not None:
                # Processing for Data Quality Dashboard
                gauge_chart = compute_data_quality(df, name)
                children_quality.append(gauge_chart)  # Removed column chart logic

                # Processing for Data View
                data_table = highlight_bad_data(df)
                children_view.append(html.H5(f'Data View for {name}'))
                children_view.append(data_table)

                # Processing for Data Error tab
                bad_data_table = display_bad_data(df)
                children_error.append(html.H5(f'Bad Data for {name}'))
                children_error.append(bad_data_table)

        return children_quality, children_view, children_error

    return None, None, None

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

import plotly.graph_objs as go

def compute_data_quality(df, filename):
    try:
        df = identify_bad_data(df)
    except ValueError as e:
        return html.Div(str(e), style={'color': 'red'})

    total_rows = len(df)
    bad_data_rows = len(df[df['is_bad']])
    good_data_rows = total_rows - bad_data_rows
    data_quality_percentage = (good_data_rows / total_rows) * 100 if total_rows > 0 else 0
    quality_rounded = round(data_quality_percentage, 2)

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",  # Include delta for change indication
        value=quality_rounded,
        number={'suffix': "%", 'font': {'size': 20}},  # Show percent symbol
        title={
            'text': f"Data Quality for {filename} (%)",
            'font': {'size': 24}  # Increase the font size of the title
        },
        delta={'reference': 100},  # Set reference for delta
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': 'red'},
                {'range': [50, 75], 'color': 'yellow'},
                {'range': [75, 100], 'color': 'green'}
            ],  # Color steps for different ranges
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }  # Threshold for indicating target quality
        }
    ))

    fig.update_layout(
        paper_bgcolor="lavender",  # Set background color
        font={'color': "darkblue", 'family': "Arial"}  # Set font style
    )

    return dcc.Graph(figure=fig)


def highlight_bad_data(df):
    try:
        # Use the identify_bad_data function to mark bad data
        df = identify_bad_data(df)
    except ValueError as e:
        # Handle the case where required columns are not found
        return html.Div(str(e), style={'color': 'red'})

    # Conditional formatting for bad data rows
    style = [{
        'if': {
            'filter_query': '{is_bad} eq True',
        },
        'backgroundColor': '#FF4136',  # Red color for bad data
        'color': 'white'
    }]

    # Create DataTable with the necessary columns except 'is_bad'
    table = DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns if i != 'is_bad'],
        data=df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        page_size=10,
        filter_action="native",
        sort_action="native",
        export_headers='display',
        export_format='csv',
        style_data_conditional=style
    )

    # Remove the 'is_bad' column from df to avoid affecting other functions
    df.drop('is_bad', axis=1, inplace=True)

    return table


import plotly.express as px




def display_bad_data(df):
    try:
        # Use the identify_bad_data function to identify bad data
        df_with_bad_data_flag = identify_bad_data(df)
    except ValueError as e:
        # Handle the case where required columns are not found
        return html.Div(str(e), style={'color': 'red'})

    # Filter out the bad data
    bad_data_df = df_with_bad_data_flag[df_with_bad_data_flag['is_bad'] == True]

    # Create a DataTable for displaying bad data
    return DataTable(
        id='bad-data-table',
        columns=[{"name": i, "id": i} for i in bad_data_df.columns if i != 'is_bad'],  # Exclude 'is_bad' column
        data=bad_data_df.to_dict('records'),
        style_table={'overflowX': 'auto'},  # Handle extra-wide tables
        page_size=10,  # Number of rows per page
        filter_action="native",  # Allow filtering of data by user
        sort_action="native",    # Allow sorting of data by user
        export_format='csv',  # Enable exporting of data
        export_headers='display',  # Use displayed headers in export
    )


from dash.dependencies import Input, Output


# Callback to update dropdown options based on uploaded file
@dash_app.callback(
    Output('column-select-dropdown', 'options'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_dropdown_options(list_of_contents, list_of_names):
    if list_of_contents is not None:
        for contents, name in zip(list_of_contents, list_of_names):
            df = parse_contents(contents, name)
            if df is not None:
                # Create options from dataframe columns
                return [{'label': col, 'value': col} for col in df.columns]
    # Return empty options if no file is uploaded
    return []


@dash_app.callback(
    Output('quality-chart-container', 'children'),
    [Input('column-select-dropdown', 'value'),
     Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_quality_chart(selected_column, list_of_contents, list_of_names):
    if selected_column is not None and list_of_contents is not None:
        for contents, name in zip(list_of_contents, list_of_names):
            df = parse_contents(contents, name)
            if df is not None and selected_column in df.columns:
                try:
                    # Use identify_bad_data function
                    df_with_bad_data_flag = identify_bad_data(df)
                except ValueError as e:
                    # Handle the case where required columns are not found
                    return html.Div(str(e), style={'color': 'red'})

                # Group by the selected column and count bad data
                bad_data_count = df_with_bad_data_flag.groupby(selected_column)['is_bad'].sum().reset_index()
                bad_data_count.columns = ['Value', 'Bad Data Count']

                # Create the plot
                fig = px.bar(bad_data_count, x='Value', y='Bad Data Count', title=f'Bad Data Count by {selected_column}')
                return dcc.Graph(figure=fig)

    return html.Div("Select a column and upload a file to view data quality.")


def identify_bad_data(df):
    """
    Identifies bad data based on specific conditions.
    """
    if "Zuständiger Bearbeiter" not in df.columns or \
            "Rückgemeldete Gutmenge in Lagereinheit" not in df.columns or \
            "Bemerkungen" not in df.columns:
        raise ValueError("Required columns not found.")

    # Define the bad data conditions
    condition1 = (df["Zuständiger Bearbeiter"] == "tmm") & (df["Rückgemeldete Gutmenge in Lagereinheit"] > 0)
    condition2 = (df["Zuständiger Bearbeiter"] == "tmm") & (df["Bemerkungen"].str.contains("BDE:", na=False))

    # Create a new column 'is_bad' to mark bad data rows
    df['is_bad'] = condition1 | condition2
    return df


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
