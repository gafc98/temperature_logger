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


def style_time_series_figure(figure, title, y_axis_title, tick_format):
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        colorway=["#267557", "#e87957", "#447da8"],
        font=dict(color="#25342e", family="Trebuchet MS"),
        title=dict(text=title, x=0.02, xanchor="left", font=dict(size=18)),
        xaxis=dict(title="Time", tickformat=tick_format, gridcolor="#e4e9e2"),
        yaxis=dict(title=y_axis_title, gridcolor="#e4e9e2"),
        margin=dict(l=54, r=20, t=66, b=48),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

def empty_figure(title):
    figure = go.Figure()
    figure.add_annotation(text="No readings in this period", showarrow=False)
    figure.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(color="#65746c", family="Trebuchet MS"),
        title=dict(text=title, x=0.02, xanchor="left", font=dict(size=18, color="#25342e")),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=66, b=20),
    )
    return figure


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

    if not time_stamp_list:
        info_data = [{"Latest Value": "Status", "Interior": "No recent readings", "Exterior": "No recent readings"}]
        empty_figures = [
            empty_figure(title) for title in (
                "Temperature, humidity, and pressure",
                "Temperature",
                "Relative humidity",
                "Atmospheric pressure",
                "Specific humidity",
                "Legacy analog sensor",
            )
        ]
        return (*empty_figures, info_data)
    
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
        go.Scatter(x=time_stamp_list, y=P_interior_list, mode='lines+markers', name='Interior'), go.Scatter(x=time_stamp_list, y=P_exterior_list, name='Exterior')
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
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        template='plotly_white',
        colorway=["#267557", "#e87957"],
        font=dict(color="#25342e", family="Trebuchet MS"),
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
        height=620,
        margin=dict(l=0, r=0, t=58, b=0),
        showlegend=False
    )
    style_time_series_figure(temperature_fig, "Temperature", "Temperature [°C]", tick_format)
    style_time_series_figure(humidity_fig, "Relative humidity", "Humidity [%]", tick_format)
    style_time_series_figure(pressure_fig, "Atmospheric pressure", "Pressure [bar]", tick_format)
    style_time_series_figure(specific_humidity_fig, "Specific humidity", "S.H. [g/kg]", tick_format)
    style_time_series_figure(analog_temperature_fig, "Legacy analog sensor", "Temperature [°C]", tick_format)
    
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
    html.Header([
        html.Div([
            html.P("MICROCLIMATE / EINDHOVEN", className="eyebrow"),
            html.H1("Weather, in context"),
            html.P("Live conditions, measured indoors and out.", className="intro-copy"),
        ]),
        html.Nav([
            html.A("Project source", href="https://github.com/gafc98/temperature_logger", target="_blank", rel="noreferrer"),
            html.A("Weekly report", href=NEWSLETTER_LINK, target="_blank", rel="noreferrer"),
        ], className="header-links"),
    ], className="masthead"),
    html.Section([
        html.Div([
            html.P("HISTORY WINDOW", className="eyebrow"),
            html.P("Choose a period", className="section-title"),
        ]),
        dcc.Slider(
            id="slider",
            min=0,
            max=len(MARKS_TO_DAYS) - 1,
            value=0,
            step=None,
            marks={i: {"label": f"{MARKS_TO_DAYS[i]}d"} for i in range(len(MARKS_TO_DAYS))},
            className="range-slider",
        ),
    ], className="range-panel"),
    html.Section([
        html.Div([
            html.P("LATEST READINGS", className="eyebrow"),
            html.P("Interior and exterior", className="section-title"),
        ], className="section-heading"),
        dash_table.DataTable(
            id="info-data",
            columns=[
                {"id": "Latest Value", "name": "Measure"},
                {"id": "Interior", "name": "Inside"},
                {"id": "Exterior", "name": "Outside"},
            ],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "14px 18px", "border": "none"},
            style_header={"fontWeight": "600", "border": "none"},
        ),
    ], className="readings-panel"),
    html.Section([
        html.Div([
            html.P("THE SENSOR RECORD", className="eyebrow"),
            html.P("Explore the measurements", className="section-title"),
        ], className="section-heading"),
        dbc.Row([
            dbc.Col(dcc.Loading(dcc.Graph(id="3d-scatter-graph", config={"displayModeBar": False}, style={"height": "560px"})), width=12),
        ], className="chart-row"),
        dbc.Row([
            dbc.Col(dcc.Loading(dcc.Graph(id="temperature-graph", config={"displayModeBar": False}, style={"height": "350px"})), xs=12, lg=6),
            dbc.Col(dcc.Loading(dcc.Graph(id="humidity-graph", config={"displayModeBar": False}, style={"height": "350px"})), xs=12, lg=6),
            dbc.Col(dcc.Loading(dcc.Graph(id="pressure-graph", config={"displayModeBar": False}, style={"height": "350px"})), xs=12, lg=6),
            dbc.Col(dcc.Loading(dcc.Graph(id="specific-humidity-graph", config={"displayModeBar": False}, style={"height": "350px"})), xs=12, lg=6),
        ], className="chart-row g-3"),
    ], className="charts-section"),
    html.Details([
        html.Summary("Legacy analog sensor"),
        dcc.Graph(id="analog-temperature-graph", config={"displayModeBar": False}, style={"height": "350px"}),
    ], className="legacy-panel"),
    html.Footer("Temperature Logger · Eindhoven", className="page-footer"),
], fluid=True, className="dashboard")


if __name__ == '__main__':
    app.run(debug=os.getenv('WEBAPP_DEBUG', False)=='true', host='0.0.0.0')