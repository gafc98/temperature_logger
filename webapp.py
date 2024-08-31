import dash
from dash import dcc, html
import plotly.graph_objects as go
from print_logs import logs_to_list
import dash_bootstrap_components as dbc
import datetime

DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ])

@app.callback(
    [dash.Output('3d-scatter-graph', 'figure'),
     dash.Output('temperature-graph', 'figure'),
     dash.Output('humidity-graph', 'figure'),
     dash.Output('pressure-graph', 'figure'),
     dash.Output('analog-temperature-graph', 'figure')],
    [dash.Input('temperature-graph', 'figure')]
)
def update_figures(id):
    time_stamp_list, T_list, H_list, P_list, Tint_list = get_latest_log_data()
    threed_fig = go.Figure(data=[go.Scatter3d(
        x=T_list,
        y=H_list,
        z=P_list,
        mode='markers',
        marker=dict(
            color=P_list,  # Use pressure for color
            colorscale='Viridis',  # Choose a color scale
            opacity=0.8
        )
    )])
    temperature_fig = go.Figure(data=[go.Scatter(x=time_stamp_list, y=T_list, mode='lines+markers')])
    humidity_fig = go.Figure(data=[go.Scatter(x=time_stamp_list, y=H_list, mode='lines+markers')])
    pressure_fig = go.Figure(data=[go.Scatter(x=time_stamp_list, y=P_list, mode='lines+markers')])
    analog_temperature_fig = go.Figure(data=[go.Scatter(x=time_stamp_list, y=Tint_list, mode='lines+markers')])
    # Customize the plot appearance
    threed_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        template='plotly_dark',
        title='Temperature, Humidity, and Pressure',
        scene=dict(
            xaxis_title='Temperature [°C]',
            yaxis_title='Humidity [%]',
            zaxis_title='Pressure [bar]'
        ),
        height=800
    )
    temperature_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Temperature",
        xaxis_title="Time",
        yaxis_title="Temperature [°C]",
        xaxis_tickformat="%H:%M",  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    humidity_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Relative Humidity",
        xaxis_title="Time",
        yaxis_title="Humidity [%]",
        xaxis_tickformat="%H:%M",  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    pressure_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Atmospheric Presssure",
        xaxis_title="Time",
        yaxis_title="Pressure [bar]",
        xaxis_tickformat="%H:%M",  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    analog_temperature_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0.2)',
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        title="Old Analog Temperature Sensor (deprecated)",
        xaxis_title="Time",
        yaxis_title="Temperature [°C]",
        xaxis_tickformat="%H:%M",  # Format time axis as HH:MM
        template="plotly_dark",  # Choose a dark theme for better contrast
    )
    
    return threed_fig, temperature_fig, humidity_fig, pressure_fig, analog_temperature_fig


def get_latest_log_data():
    to_date = datetime.datetime.now()
    from_date = to_date - datetime.timedelta(days = 1) # checks for last 24 hours
    logs_list = logs_to_list(from_date, to_date)
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
                        dbc.Col(html.H2("The best interactive weather dashboard shows you weather data from the past 24 hours! Message to the world: PEDRO IS SUPER MEGA GAY."))
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output', children=dcc.Graph(id='3d-scatter-graph')), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output', children=dcc.Graph(id='temperature-graph')), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output', children=dcc.Graph(id='humidity-graph')), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output', children=dcc.Graph(id='pressure-graph')), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Loading(id='loading-output', children=dcc.Graph(id='analog-temperature-graph')), width=12)
                    ])
                ]),
                className="border rounded"
            )
        )
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True)
