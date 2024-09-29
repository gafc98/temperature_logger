import dash
from dash import dcc, html
import plotly.graph_objects as go
from include.print_logs import logs_to_list
import dash_bootstrap_components as dbc
import datetime
import os
from dotenv import load_dotenv # pip install python-dotenv
from pathlib import Path

DATE_FORMAT = "%a %b %d %H:%M:%S %Y"
MARKS_TO_DAYS = (1, 2, 3, 4, 5, 6, 7, 14, 28, 56) # converts from slider mark idx to respective days

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ])
app.title = 'The Weather Dash'

# load .env variables
curr_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = curr_dir / ".env"
load_dotenv(envars)
NEWSLETTER_LINK = os.getenv("UNSUBSCRIBE_LINK")

@app.callback(
    [dash.Output('3d-scatter-graph', 'figure'),
     dash.Output('temperature-graph', 'figure'),
     dash.Output('humidity-graph', 'figure'),
     dash.Output('pressure-graph', 'figure'),
     dash.Output('analog-temperature-graph', 'figure')],
    [dash.Input('slider', 'value')]
)
def update_figures(slider_value):
    time_stamp_list, T_list, H_list, P_list, Tint_list = get_latest_log_data(days_before=MARKS_TO_DAYS[slider_value])
    threed_fig = go.Figure(data=[go.Scatter3d(
        x=T_list,
        y=H_list,
        z=P_list,
        mode='markers',
        marker=dict(
            color=[t.timestamp() for t in time_stamp_list],
            colorscale='Viridis',  # Choose a color scale
            opacity=0.8
        )
    )])
    temperature_fig = go.Figure(data=[go.Scatter(x=time_stamp_list, y=T_list, mode='lines+markers')])
    humidity_fig = go.Figure(data=[go.Scatter(x=time_stamp_list, y=H_list, mode='lines+markers')])
    pressure_fig = go.Figure(data=[go.Scatter(x=time_stamp_list, y=P_list, mode='lines+markers')])
    analog_temperature_fig = go.Figure(data=[go.Scatter(x=time_stamp_list, y=Tint_list, mode='markers+text')])
    
    # Customize the plot appearance
    tick_format = '%H:%M'
    if slider_value > 1:
        tick_format = '%d/%m ' + tick_format

    threed_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        template='plotly_dark',
        title='Temperature, Humidity, and Pressure',
        scene=dict(
            xaxis_title='Temperature [°C]',
            yaxis_title='Humidity [%]',
            zaxis_title='Pressure [bar]',
            annotations=[
                {'x': T_list[0], 'y': H_list[0], 'z': P_list[0], 'text': time_stamp_list[0].strftime('%d/%m %H:%M')},
                {'x': T_list[-1], 'y': H_list[-1], 'z': P_list[-1], 'text': time_stamp_list[-1].strftime('%d/%m %H:%M')}
            ]
        ),
        height=800
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
    analog_temperature_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Old Analog Temperature Sensor (deprecated)",
        xaxis_title="Time",
        yaxis_title="Temperature [°C]",
        xaxis_tickformat=tick_format,  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    
    return threed_fig, temperature_fig, humidity_fig, pressure_fig, analog_temperature_fig


def get_latest_log_data(days_before = 1):
    to_date = datetime.datetime.now()
    from_date = to_date - datetime.timedelta(days = days_before) # checks for last N days
    logs_list = logs_to_list(from_date, to_date, subsample=days_before)
    time_stamp_list = []
    T_list = []
    H_list = []
    P_list = []
    Tint_list = []
    for log in logs_list:
        time_stamp, T, H, P, Tint, _ = log.split('\t')
        time_stamp_list.append(datetime.datetime.strptime(time_stamp, DATE_FORMAT))
        T_list.append(float(T))
        H_list.append(float(H))
        P_list.append(float(P))
        Tint_list.append(float(Tint))

    print(f'Webpage refreshed at {to_date}.')

    return time_stamp_list, T_list, H_list, P_list, Tint_list

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
                        dbc.Col(dcc.Loading(id='loading-output5', children=dcc.Graph(id='analog-temperature-graph')), width=12)
                    ])
                ]),
                className="border rounded"
            )
        )
    ])
])


if __name__ == '__main__':
    app.run_server(debug=bool(os.getenv('WEBAPP_DEBUG', False)))
