import dash
from dash import dcc, html, dash_table
import plotly.graph_objects as go
from include.print_logs import logs_to_list
import dash_bootstrap_components as dbc
import datetime
import os
from dotenv import load_dotenv # pip install python-dotenv
from pathlib import Path
import math

DATE_FORMAT = "%a %b %d %H:%M:%S %Y"
MARKS_TO_DAYS = (1, 2, 3, 4, 5, 6, 7, 14, 28, 56) # converts from slider mark idx to respective days

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ])
app.title = 'The Weather Dash'

# load .env variables
curr_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = curr_dir / ".env"
load_dotenv(envars)
NEWSLETTER_LINK = os.getenv("FORM_LINK")

@app.callback(
    [dash.Output('3d-scatter-graph', 'figure'),
     dash.Output('temperature-graph', 'figure'),
     dash.Output('humidity-graph', 'figure'),
     dash.Output('pressure-graph', 'figure'),
     dash.Output('specific-humidity-graph', 'figure'),
     dash.Output('analog-temperature-graph', 'figure'),
     dash.Output('info-data', 'data')],
    [dash.Input('slider', 'value')]
)
def update_figures(slider_value):
    time_stamp_list, T_interior_list, H_interior_list, P_interior_list, Tint_list, T_exterior_list, H_exterior_list, P_exterior_list = get_latest_log_data(days_before=MARKS_TO_DAYS[slider_value])
    
    info_data = [
        {'Latest Value': 'Temperature', 'Interior': f'{T_interior_list[0]:.2f} \u2103', 'Exterior': f'{T_exterior_list[0]:.2f} \u2103'},
        {'Latest Value': 'Humidity', 'Interior': f'{H_interior_list[0]:.1f} %', 'Exterior': f'{H_exterior_list[0]:.1f} %'},
        {'Latest Value': 'Pressure', 'Interior': f'{P_interior_list[0]:.3f} bar', 'Exterior': f'{P_exterior_list[0]:.3f} bar'}
    ]

    specific_humidity_interior_list = compute_specific_humidity(T_interior_list, H_interior_list, P_interior_list)
    specific_humidity_exterior_list = compute_specific_humidity(T_exterior_list, H_exterior_list, P_exterior_list)

    threed_fig = go.Figure(data=[
        go.Scatter3d(
            x=T_interior_list,
            y=H_interior_list,
            z=P_interior_list,
            mode='markers',
            marker=dict(
                color=[t.timestamp() for t in time_stamp_list],
                colorscale='Turbo',  # Choose a color scale
                opacity=0.8
            ),
            name='Interior'),
        go.Scatter3d(
            x=T_exterior_list,
            y=H_exterior_list,
            z=P_exterior_list,
            mode='markers',
            marker=dict(
                color=[t.timestamp() for t in time_stamp_list],
                colorscale='Inferno',  # Choose a color scale
                opacity=0.8
            ),
            name='Exterior')
    ])
    temperature_fig = go.Figure(data=[
        go.Scatter(x=time_stamp_list, y=T_interior_list, mode='lines+markers', name='Interior'), go.Scatter(x=time_stamp_list, y=T_exterior_list, mode='lines+markers', name='Exterior')
        ])
    humidity_fig = go.Figure(data=[
        go.Scatter(x=time_stamp_list, y=H_interior_list, mode='lines+markers', name='Interior'), go.Scatter(x=time_stamp_list, y=H_exterior_list, mode='lines+markers', name='Exterior')
        ])
    pressure_fig = go.Figure(data=[
        go.Scatter(x=time_stamp_list, y=P_interior_list, mode='lines+markers', name='Interior'), go.Scatter(x=time_stamp_list, y=P_exterior_list, mode='lines+markers', name='Exterior')
        ])
    specific_humidity_fig = go.Figure(data=[
        go.Scatter(x=time_stamp_list, y=specific_humidity_interior_list, mode='lines+markers', name='Interior'), go.Scatter(x=time_stamp_list, y=specific_humidity_exterior_list, mode='lines+markers', name='Exterior')
        ])
    analog_temperature_fig = go.Figure(data=[go.Scatter(x=time_stamp_list, y=Tint_list, mode='markers+text')])
    
    # Customize the plot appearance
    tick_format = '%H:%M'
    if slider_value > 1:
        tick_format = '%d/%m ' + tick_format

    threed_fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        template='plotly_dark',
        title='Temperature, Humidity, and Pressure',
        scene=dict(
            xaxis_title='Temperature [°C]',
            yaxis_title='Humidity [%]',
            zaxis_title='Pressure [bar]',
            annotations=[
                {'x': T_interior_list[0], 'y': H_interior_list[0], 'z': P_interior_list[0], 'text': time_stamp_list[0].strftime('Interior - %d/%m %H:%M')},
                {'x': T_interior_list[-1], 'y': H_interior_list[-1], 'z': P_interior_list[-1], 'text': time_stamp_list[-1].strftime('Interior -%d/%m %H:%M')},
                {'x': next(x for x in T_exterior_list if not math.isnan(x)), 'y': next(y for y in H_exterior_list if not math.isnan(y)), 'z': next(z for z in P_exterior_list if not math.isnan(z)), 'text': time_stamp_list[0].strftime('Exterior - %d/%m %H:%M')},
                {'x': next(x for x in reversed(T_exterior_list) if not math.isnan(x)), 'y': next(y for y in reversed(H_exterior_list) if not math.isnan(y)), 'z': next(z for z in reversed(P_exterior_list) if not math.isnan(z)), 'text': time_stamp_list[-1].strftime('Exterior - %d/%m %H:%M')}
            ]
        ),
        height=800,
        showlegend=False
    )
    temperature_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Temperature",
        xaxis_title="Time",
        yaxis_title="Temperature [°C]",
        xaxis_tickformat=tick_format,  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    humidity_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Relative Humidity",
        xaxis_title="Time",
        yaxis_title="Humidity [%]",
        xaxis_tickformat=tick_format,  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    pressure_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Atmospheric Presssure",
        xaxis_title="Time",
        yaxis_title="Pressure [bar]",
        xaxis_tickformat=tick_format,  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    specific_humidity_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Specific Humidity",
        xaxis_title="Time",
        yaxis_title="S.H. [g/Kg]",
        xaxis_tickformat=tick_format,  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    analog_temperature_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Old Analog Temperature Sensor (Interior, deprecated)",
        xaxis_title="Time",
        yaxis_title="Temperature [°C]",
        xaxis_tickformat=tick_format,  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    
    return threed_fig, temperature_fig, humidity_fig, pressure_fig, specific_humidity_fig, analog_temperature_fig, info_data


def get_latest_log_data(days_before = 1):
    to_date = datetime.datetime.now()
    from_date = to_date - datetime.timedelta(days = days_before) # checks for last N days
    logs_list = logs_to_list(from_date, to_date, subsample=days_before)
    time_stamp_list = []
    T_interior_list = []
    H_interior_list = []
    P_interior_list = []
    Tint_list = []
    T_exterior_list = []
    H_exterior_list = []
    P_exterior_list = []
    for log in logs_list:
        #time_stamp, T, H, P, Tint, _ = log.split('\t')
        split_line = log.split('\t')
        time_stamp_list.append(datetime.datetime.strptime(split_line[0], DATE_FORMAT))
        T_interior_list.append(float(split_line[1]))
        H_interior_list.append(float(split_line[2]))
        P_interior_list.append(float(split_line[3]))
        Tint_list.append(float(split_line[4]))
        if len(split_line) > 6:
            T_exterior_list.append(float(split_line[6]))
            H_exterior_list.append(float(split_line[7]))
            P_exterior_list.append(float(split_line[8]))
        else:
            T_exterior_list.append(float('nan'))
            H_exterior_list.append(float('nan'))
            P_exterior_list.append(float('nan'))

    print(f'Webpage refreshed at {to_date}.')

    return time_stamp_list, T_interior_list, H_interior_list, P_interior_list, Tint_list, T_exterior_list, H_exterior_list, P_exterior_list

def compute_specific_humidity(T_interior_list, H_interior_list, P_interior_list):
    # T_interior_list in degC
    # H_interior_list in percentage
    # P_interior_list in bar
    specific_humidity_list = []
    for i in range(len(T_interior_list)):
        saturation_press = 0.0061078 * math.exp((17.27 * T_interior_list[i]) / (T_interior_list[i] + 237.3)) # bar
        vapor_press = H_interior_list[i] / 100 * saturation_press
        specific_humidity_list.append(1000 * vapor_press / (1.6078 * P_interior_list[i] - 0.6078 * vapor_press))
    return specific_humidity_list # g H2O per Kg of humid air


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.H1("Weather Dashboard", className="text-center"), width=12),
                    ]),
                    dbc.Row([
                        dbc.Col(html.H2(f"The best dashboard shows you weather data up to the past {MARKS_TO_DAYS[-1]} days!", className="text-center"), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(
                            html.Div(
                                [
                                    'Like what you see? Check out the ',
                                    html.A(
                                        'source code', href='https://github.com/gafc98/temperature_logger', target='_blank', style={'fontSize': '12px', 'color': '#dbdbdb'}
                                    ),
                                    '. Would you like to receive a weekly newsletter? Check out this ',
                                    html.A(
                                        'form', href=NEWSLETTER_LINK, target='_blank', style={'fontSize': '12px', 'color': '#dbdbdb'}
                                    ),
                                    '.'
                                ],
                                style={'display': 'inline-block', 'fontSize': '12px'}
                            ),
                            width=12,
                            style={'text-align': 'center', 'margin-bottom': '20px'}
                        )
                    ]),
                    dbc.Row([
                        dbc.Col(
                            dcc.Slider(
                                id='slider',
                                min=0,
                                max=len(MARKS_TO_DAYS)-1,
                                value=0,
                                step=None,
                                marks={i: {'label': f'{MARKS_TO_DAYS[i]} days', 'style': {'color': 'white', 'font-family': 'Arial', 'white-space': 'nowrap'}} for i in range(len(MARKS_TO_DAYS))}
                            ),
                            width=12,
                            style={'text-align': 'center', 'margin-bottom': '20px'}
                        )
                    ]),
                    dbc.Row([
                        dash_table.DataTable(
                            id='info-data',
                            columns=[{'id': 'Latest Value', 'name': 'Latest Value'}, {'id': 'Interior', 'name': 'Interior'}, {'id': 'Exterior', 'name': 'Exterior'}],
                            style_table={'minWidth': '300px'},
                            style_cell={'textAlign': 'center', 'backgroundColor': 'rgba(0, 0, 0, 0.2)'},
                            style_header={'backgroundColor': 'rgba(0, 0, 0, 0.4)', 'fontWeight': 'bold'}
                        )
                            
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output1', children=dcc.Graph(id='3d-scatter-graph')), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output2', children=dcc.Graph(id='temperature-graph')), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output3', children=dcc.Graph(id='humidity-graph')), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output4', children=dcc.Graph(id='pressure-graph')), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output5', children=dcc.Graph(id='specific-humidity-graph')), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output6', children=dcc.Graph(id='analog-temperature-graph')), width=12)
                    ])
                ]),
                className="border rounded"
            )
        )
    ])
])


if __name__ == '__main__':
    app.run_server(debug=os.getenv('WEBAPP_DEBUG', False)=='true')
