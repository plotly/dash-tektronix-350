import dash
from dash.dependencies import Input, Output, State
import dash_daq as daq
from dash_daq import DarkThemeProvider
import dash_html_components as html
import dash_core_components as dcc

import numpy as np
import plotly.graph_objs as go
from scipy import signal
from time import sleep

app = dash.Dash(__name__)

app.config['suppress_callback_exceptions'] = True

server = app.server

font_color = {'dark': '#ffffff', 'light': "#222"}
background_color = {'dark': '#2a3f5f', 'light': '#ffffff'}
title_color = {'dark': '#ffffff', 'light': '#447EFF'}

light_layout = html.Div(className='container', children=[
    # Function Generator Panel - Left
    html.Div(
        id='header',
        children=[
            html.H2("Dash DAQ: Function Generator & Oscilloscope Control Panel",
                    style={
                        'color': '#EBF0F8',
                        'marginLeft': '40px',
                        'display': 'inline-block',
                        'text-align': 'center'
                    }),
            html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/" +
                         "excel/dash-daq/dash-daq-logo-by-plotly-stripe+copy.png",
                     style={
                         'position': 'relative',
                         'float': 'right',
                         'right': '10px',
                         'height': '75px'
                     }
                     )
        ],
        className='banner',
        style={
            'backgroundColor': '#447EFF'
        }),

    html.Div([
        html.Div([
            html.Div([
                html.H3("POWER", id="power-title")
            ], className='Title'),
            html.Div([
                html.Div(
                    [
                        daq.PowerButton(
                            id='function-generator',
                            on=True,
                            label="Function Generator",
                            labelPosition='bottom',
                            color="#447EFF"),
                    ],
                    className='six columns',
                    style={'margin-bottom': '15px'}),
                html.Div(
                    [
                        daq.PowerButton(
                            id='oscilloscope',
                            on=True,
                            label="Oscilloscope",
                            labelPosition='bottom',
                            color="#447EFF")
                    ],
                    className='six columns',
                    style={'margin-bottom': '15px'}),
            ], style={'margin': '15px 0'})
        ], className='row power-settings-tab'),
        html.Div([
            html.Div(
                [html.H3("FUNCTION", id="function-title")],
                className='Title'),
            html.Div([
                daq.Knob(
                    value=1E6,
                    id="frequency-input",
                    label="Frequency (Hz)",
                    labelPosition="bottom",
                    size=75,
                    color="#447EFF",
                    scale={'interval': 1E5},
                    max=2.5E6,
                    min=1E5,
                    className='four columns'
                ),
                daq.Knob(
                    value=1,
                    id="amplitude-input",
                    label="Amplitude (mV)",
                    labelPosition="bottom",
                    size=75,
                    scale={'labelInterval': 10},
                    color="#447EFF",
                    max=10,
                    className='four columns'
                ),
                daq.Knob(
                    value=0,
                    id="offset-input",
                    label="Offset (mV)",
                    labelPosition="bottom",
                    size=75,
                    scale={'labelInterval': 10},
                    color="#447EFF",
                    max=10,
                    className='four columns'
                )], style={'marginLeft': '20%', 'textAlign': 'center'}),
            html.Div([
                daq.LEDDisplay(
                    id='frequency-display',
                    size=10, value=1E6,
                    label="Frequency (Hz)",
                    labelPosition="bottom",
                    color="#447EFF",
                    style={'marginBottom': '30px'},
                    className='four columns'),
                daq.LEDDisplay(
                    id='amplitude-display',
                    size=10,
                    value=1,
                    label="Amplitude (mV)",
                    labelPosition="bottom",
                    color="#447EFF",
                    className='four columns'),
                daq.LEDDisplay(
                    id='offset-display',
                    size=10,
                    value=10,
                    label="Offset (mV)",
                    labelPosition="bottom",
                    color="#447EFF",
                    className='four columns'),
            ], style={'marginLeft': '20%', 'textAlign': 'center'}),
            dcc.RadioItems(
                id='function-type',
                options=[
                    {'label': 'Sine', 'value': 'SIN'},
                    {'label': 'Square', 'value': 'SQUARE'},
                    {'label': 'Ramp', 'value': 'RAMP'},
                ],
                value='SIN',
                labelStyle={'display': 'inline-block'},
                style={'margin': '30px auto 0px auto',
                       'display': 'flex',
                       'width': '80%',
                       'alignItems': 'center',
                       'justifyContent': 'space-between'}
            )
        ], className='row power-settings-tab'),
        html.Hr(),
        daq.ColorPicker(
            id="color-picker",
            label="Color Picker",
            value=dict(hex="#447EFF"),
            size=164,
        ),
    ], className='four columns left-panel'),

    # Oscillator Panel - Right
    html.Div([
        html.Div([html.H3("GRAPH", id="graph-title")], className='Title'),
        dcc.Tabs(
            id='tabs',
            children=[dcc.Tab(
                label='Run #1',
                value='1'
            )],
            value='1',
            style={'backgroundColor': '#447EFF'},
            className='oscillator-tabs'
        ),

        html.Div([
            html.Div([
                html.Div([
                    html.Div(
                        id="graph-info",
                        style={
                            'border': '2px solid #447EFF'}),
                ], className="row graph-param"),
            ], className="six columns"),
            html.Button('+',
                        id='new-tab',
                        n_clicks=0,
                        type='submit',
                        style={'height': '20px', 'width': '20px',
                               'padding': '2px', 'lineHeight': '10px',
                               'float': 'right'}),
        ], className='row oscope-info', style={'margin': '15px'}),
        html.Hr(),
        dcc.Graph(
            id='oscope-graph',
            figure=dict(
                data=[dict(x=np.linspace(-0.000045, 0.000045, 1000),
                           y=[0] * len(np.linspace(-0.000045, 0.000045, 1000)),
                           marker={'color': '#2a3f5f'})],
                layout=go.Layout(
                    xaxis={'title': 's', 'color': '#506784',
                           'titlefont': dict(
                               family='Dosis',
                               size=15,
                           )},
                    yaxis={'title': 'Voltage (mV)', 'color': '#506784',
                           'titlefont': dict(
                               family='Dosis',
                               size=15,
                           ), 'autorange': False, 'range': [-10, 10]},
                    margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                    plot_bgcolor='#F3F6FA',
                )
            ),
            config={'displayModeBar': True,
                    'modeBarButtonsToRemove': ['pan2d',
                                               'zoomIn2d',
                                               'zoomOut2d',
                                               'autoScale2d',
                                               'hoverClosestCartesian',
                                               'hoverCompareCartesian']}
        )
    ], className='seven columns right-panel')
])

dark_layout = DarkThemeProvider(
    [
        html.Div(
            id='page-content-inner',
            style={'backgroundColor': background_color['dark'], 'color': font_color['dark']},
            className='container',
            # Function Generator Panel - Left
            children=[
                html.Div(
                    id='dark-header',
                    children=[
                        html.H2("Dash DAQ: Function Generator & Oscilloscope Control Panel",
                                style={
                                    'color': 'white',
                                    'marginLeft': '40px',
                                    'display': 'inline-block',
                                    'text-align': 'center'
                                }),
                        html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/" +
                                     "excel/dash-daq/dash-daq-logo-by-plotly-stripe+copy.png",
                                 style={
                                     'position': 'relative',
                                     'float': 'right',
                                     'right': '10px',
                                     'height': '75px'
                                 }
                                 )
                    ],
                    className='banner',
                    style={
                        'backgroundColor': '#1d1d1d'
                    }),

                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("POWER", id="power-title-dark", style={'color': title_color['dark']})
                        ], className='Title'),
                        html.Div([
                            html.Div(
                                [
                                    daq.PowerButton(
                                        id='function-generator-dark',
                                        on=True,
                                        label="Function Generator",
                                        labelPosition='bottom',
                                        color="#EBF0F8"),
                                ],
                                className='six columns',
                                style={'margin-bottom': '15px'}),
                            html.Div(
                                [
                                    daq.PowerButton(
                                        id='oscilloscope-dark',
                                        on=True,
                                        label="Oscilloscope",
                                        labelPosition='bottom',
                                        color="#EBF0F8")
                                ],
                                className='six columns',
                                style={'margin-bottom': '15px'}),
                        ], style={'margin': '15px 0'})
                    ], className='row power-settings-tab'),
                    html.Div([
                        html.Div(
                            [html.H3("FUNCTION", id="function-title-dark", style={'color': title_color['dark']})],
                            className='Title'),
                        html.Div([
                            daq.Knob(
                                value=1E6,
                                id="frequency-input-dark",
                                label="Frequency (Hz)",
                                labelPosition="bottom",
                                size=75,
                                color="#EBF0F8",
                                scale={'interval': 1E5},
                                max=2.5E6,
                                min=1E5,
                                className='four columns'
                            ),
                            daq.Knob(
                                value=1,
                                id="amplitude-input-dark",
                                label="Amplitude (mV)",
                                labelPosition="bottom",
                                size=75,
                                scale={'labelInterval': 10},
                                color="#EBF0F8",
                                max=10,
                                className='four columns'
                            ),
                            daq.Knob(
                                value=0,
                                id="offset-input-dark",
                                label="Offset (mV)",
                                labelPosition="bottom",
                                size=75,
                                scale={'labelInterval': 10},
                                color="#EBF0F8",
                                max=10,
                                className='four columns'
                            )], style={'marginLeft': '20%', 'textAlign': 'center'}),
                        html.Div([
                            daq.LEDDisplay(
                                id='frequency-display-dark',
                                size=10, value=1E6,
                                label="Frequency (Hz)",
                                labelPosition="bottom",
                                color="#EBF0F8",
                                style={'marginBottom': '30px'},
                                className='four columns'),
                            daq.LEDDisplay(
                                id='amplitude-display-dark',
                                size=10,
                                value=1,
                                label="Amplitude (mV)",
                                labelPosition="bottom",
                                color="#EBF0F8",
                                className='four columns'),
                            daq.LEDDisplay(
                                id='offset-display-dark',
                                size=10,
                                value=10,
                                label="Offset (mV)",
                                labelPosition="bottom",
                                color="#EBF0F8",
                                className='four columns'),
                        ], style={'marginLeft': '20%', 'textAlign': 'center'}),
                        dcc.RadioItems(
                            id='function-type-dark',
                            options=[
                                {'label': 'Sine', 'value': 'SIN'},
                                {'label': 'Square', 'value': 'SQUARE'},
                                {'label': 'Ramp', 'value': 'RAMP'},
                            ],
                            value='SIN',
                            labelStyle={'display': 'inline-block'},
                            style={'margin': '30px auto 0px auto',
                                   'display': 'flex',
                                   'width': '80%',
                                   'alignItems': 'center',
                                   'justifyContent': 'space-between'}
                        )
                    ], className='row power-settings-tab'),
                    html.Hr(),
                    daq.ColorPicker(
                        id="color-picker-dark",
                        label="Color Picker",
                        value=dict(hex="#EBF0F8"),
                        size=164,
                        theme={'dark': True}
                    ),
                ], className='four columns left-panel'),

                # Oscillator Panel - Right
                html.Div([
                    html.Div([html.H3("GRAPH", id="graph-title-dark", style={'color': title_color['dark']})],
                             className='Title'),
                    dcc.Tabs(
                        id='dark-tabs',
                        children=[dcc.Tab(
                            label='Run #1',
                            value='1'
                        )],
                        value='1',
                        style={
                            'backgroundColor': '#EBF0F8'
                        },
                        className='oscillator-tabs'
                    ),

                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div(
                                    id="dark-graph-info",
                                    style={
                                        'color': font_color['dark'],
                                        'border': '2px solid #EBF0F8'}),
                            ], className="row graph-param"),
                        ], className="six columns"),
                        html.Button('+',
                                    id='new-tab-dark',
                                    n_clicks=0,
                                    type='submit',
                                    style={
                                        'backgroundColor': '#EBF0F8',
                                        'height': '20px',
                                        'width': '20px',
                                        'padding': '2px',
                                        'lineHeight': '10px',
                                        'float': 'right'}),
                    ], className='row oscope-info', style={'margin': '15px'}),
                    html.Hr(),
                    # dcc.Graph(
                    #     id='dark-oscope-graph',
                    #
                    #     figure=dict(
                    #         data=[dict(x=np.linspace(-0.000045, 0.000045, 1000),
                    #                    y=[0] * len(np.linspace(-0.000045, 0.000045, 1000)),
                    #                    marker={'color': '#f2f5fa'})],
                    #         layout=go.Layout(
                    #             xaxis={'title': 's', 'color': '#EBF0F8',
                    #                    'titlefont': dict(
                    #                        family='Dosis',
                    #                        size=15,
                    #                    )},
                    #             yaxis={'title': 'Voltage (mV)', 'color': '#EBF0F8',
                    #                    'titlefont': dict(
                    #                        family='Dosis',
                    #                        size=15,
                    #                    ), 'autorange': False, 'range': [-10, 10]},
                    #             margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                    #             plot_bgcolor='rgba(0,0,0,0)',
                    #             paper_bgcolor='rgba(0,0,0,0)'
                    #         )
                    #     ),
                    #     config={'displayModeBar': True,
                    #             'modeBarButtonsToRemove': ['pan2d',
                    #                                        'zoomIn2d',
                    #                                        'zoomOut2d',
                    #                                        'autoScale2d',
                    #                                        'hoverClosestCartesian',
                    #                                        'hoverCompareCartesian']}
                    # )
                ],
                    className='seven columns right-panel')
            ])])

tab = '1'

app.layout = html.Div(
    id='root-content',
    className='container',
    children=[
        dcc.Location(id='url', refresh=False),

        html.Div([
            daq.ToggleSwitch(
                id='toggleTheme',
                style={
                    'position': 'absolute',
                    'transform': 'translate(-50%, 20%)',
                    'z-index': '9999'
                },
                size=25
            ),
        ], id="toggleDiv",
            style={
                'width': 'fit-content',
                'margin': '0 auto'
            }),

        html.Div(id='page-content', children=[
            html.Div(id='light-layout', children=light_layout),
            html.Div(id='dark-layout', style={'display': 'none'}, children=dark_layout),
        ]),
        dcc.Store(id='runs', data={}),  # sharing running information
        dcc.Store(id='tab-number', data=1)  # sharing tab number
    ]
)


# Callback to update theme
@app.callback(
    [Output('light-layout', 'style'), Output('dark-layout', 'style')],
    [Input('toggleTheme', 'value')])
def page_layout(value):
    if not value:
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}


# Multi-output callbacks for color picker
@app.callback([Output('frequency-input', 'color'),
               Output('amplitude-input', 'color'),
               Output('offset-input', 'color'),
               Output('frequency-display', 'color'),
               Output('amplitude-display', 'color'),
               Output('offset-display', 'color'),
               Output('function-generator', 'color'),
               Output('oscilloscope', 'color'),
               Output('power-title', 'style'),
               Output('function-title', 'style'),
               Output('graph-title', 'style'),
               Output('graph-info', 'style'),
               Output('tabs', 'style'),
               Output('header', 'style'),
               ],
              [Input('color-picker', 'value')])
def color_update(color):
    return list(color['hex'] for _ in range(8)) + list({'color': color['hex']} for _ in range(3)) + [
        {'border': ("2px solid " + color['hex'])}] + list(
        {'backgroundColor': color['hex']} for _ in range(2))


# Multi-output callbacks for dark color picker
@app.callback([Output('frequency-input-dark', 'color'),
               Output('amplitude-input-dark', 'color'),
               Output('offset-input-dark', 'color'),
               Output('frequency-display-dark', 'color'),
               Output('amplitude-display-dark', 'color'),
               Output('offset-display-dark', 'color'),
               Output('function-generator-dark', 'color'),
               Output('oscilloscope-dark', 'color'),
               Output('power-title-dark', 'style'),
               Output('function-title-dark', 'style'),
               Output('graph-title-dark', 'style'),
               Output('dark-graph-info', 'style'),
               Output('dark-tabs', 'style'),
               Output('dark-header', 'style'),
               ],
              [Input('color-picker-dark', 'value')])
def color_update_dark(color):
    return list(color['hex'] for _ in range(8)) + list({'color': color['hex']} for _ in range(3)) + [
        {'border': ("2px solid " + color['hex']), 'color': font_color['dark']}] + list(
        {'backgroundColor': color['hex']} for _ in range(2))


# Callbacks for knob inputs
@app.callback(Output('frequency-display', 'value'),
              [Input('frequency-input', 'value')], )
def update_frequency_display(value):
    return value


@app.callback(Output('amplitude-display', 'value'),
              [Input('amplitude-input', 'value')], )
def update_amplitude_display(value):
    return value


@app.callback(Output('offset-display', 'value'),
              [Input('offset-input', 'value')])
def update_offset_display(value):
    return value


@app.callback(Output('frequency-display-dark', 'value'),
              [Input('frequency-input-dark', 'value')], )
def update_frequency_display(value):
    return value


@app.callback(Output('amplitude-display-dark', 'value'),
              [Input('amplitude-input-dark', 'value')], )
def update_amplitude_display(value):
    return value


@app.callback(Output('offset-display-dark', 'value'),
              [Input('offset-input-dark', 'value')])
def update_offset_display(value):
    return value


#
# Callbacks graph and graph info
@app.callback(
    Output('graph-info', 'children'),
    [
     Input('tabs', 'value'),
     Input('runs', 'data')
    ]
)
def update_info(value, cur_runs):
    if value in cur_runs:
        return cur_runs[value][1]
    return "-"


@app.callback([Output('oscope-graph', 'figure'), Output('runs', 'data')],
              [
                  Input('tabs', 'value'),
                  Input('frequency-input', 'value'),
                  Input('function-type', 'value'),
                  Input('amplitude-input', 'value'),
                  Input('offset-input', 'value'),
                  Input('oscilloscope', 'on'),
                  Input('function-generator', 'on')
              ],
              [State('runs', 'data')]
              )
def update_output(value, frequency, wave, amplitude, offset, osc_on, fnct_on, cur_runs):
    global tab
    time = np.linspace(-0.000045, 0.000045, 1000)
    zero = dict(
        data=[dict(x=time, y=[0] * len(time),
                   marker={'color': '#2a3f5f'})],
        layout=go.Layout(
            xaxis={'title': 's', 'color': '#506784',
                   'titlefont': dict(
                       family='Dosis',
                       size=15,
                   )},
            yaxis={'title': 'Voltage (mV)', 'color': '#506784',
                   'titlefont': dict(
                       family='Dosis',
                       size=15,
                   ), 'autorange': False, 'range': [-10, 10]},
            margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
            plot_bgcolor='#F3F6FA',
        )
    )

    if not osc_on:
        return dict(
            data=[],
            layout=go.Layout(
                xaxis={'title': 's', 'color': '#506784', 'titlefont': dict(
                    family='Dosis',
                    size=15,
                ), 'showticklabels': False, 'ticks': '', 'zeroline': False},
                yaxis={'title': 'Voltage (mV)', 'color': '#506784',
                       'titlefont': dict(
                           family='Dosis',
                           size=15,
                       ), 'showticklabels': False, 'zeroline': False},
                margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                plot_bgcolor='#506784',
            )
        )

    if not fnct_on:
        return zero, cur_runs

    if tab is not value:
        if value in cur_runs:
            tab = value
            figure = cur_runs[value][0]
            figure['data'][0]['marker']['color'] = '#2a3f5f'
            figure['layout'] = go.Layout(
                xaxis={'title': 's', 'color': '#506784',
                       'titlefont': dict(
                           family='Dosis',
                           size=15,
                       )},
                yaxis={'title': 'Voltage (mV)', 'color': '#506784',
                       'titlefont': dict(
                           family='Dosis',
                           size=15,
                       ), 'autorange': False, 'range': [-10, 10]},
                margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                plot_bgcolor='#F3F6FA',
            )
            return figure, cur_runs
        tab = value
        return zero, cur_runs

    else:
        if wave == 'SIN':
            y = [float(offset) +
                 (float(amplitude) *
                  np.sin(np.radians(2.0 * np.pi * float(frequency) * t)))
                 for t in time]

        elif wave == 'SQUARE':
            y = [float(offset) +
                 float(amplitude) *
                 (signal.square(2.0 * np.pi * float(frequency) / 10 * t))
                 for t in time]

        elif wave == 'RAMP':
            y = float(amplitude) * \
                (np.abs(signal.sawtooth(2 * np.pi * float(frequency) / 10 * time)))
            y = float(offset) + 2 * y - float(amplitude)

        figure = dict(
            data=[dict(x=time, y=y, marker={'color': '#2a3f5f'})],
            layout=go.Layout(
                xaxis={'title': 's', 'color': '#506784',
                       'titlefont': dict(
                           family='Dosis',
                           size=15,
                       )},
                yaxis={'title': 'Voltage (mV)', 'color': '#506784',
                       'titlefont': dict(
                           family='Dosis',
                           size=15,
                       ), 'autorange': False, 'range': [-10, 10]},
                margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
                plot_bgcolor='#F3F6FA',
            )
        )

        cur_runs[value] = figure, str(wave) + " | " + str(frequency) + \
                          "Hz" + " | " + str(amplitude) + "mV" + " | " + str(offset) + "mV"

        # wait to update the runs variable
        sleep(0.10)

        return figure, cur_runs


# todo: update runs, graph-info, figure contains {key: value} when inputs are toggled.

# toggles -> graph-info, figure in runs,  update runs
# run-update + current tab number - > light-figure/dark-figure.
#
#
# ## Updating graph info
# @app.callback(
#     Output('graph-info', 'children'),
#     [Input('tabs', 'value'), Input('runs', 'data')]
# )
# def update_graph(tab_selected, run_data):
#     if str(tab_selected) in run_data:
#         tab_data = run_data[str(tab_selected)]
#         if len(tab_data) > 0:
#             info = str(tab_data[1]) + " | " + str(tab_data[0]) + "Hz" + " | " + str(tab_data[2]) + "mV" + " | " + str(
#                 tab_data[3]) + "mV"
#             return info
#
#     return " - "


# @app.callback(
#     Output('dark-graph-info', 'children'),
#     [Input('dark-tabs', 'value'), Input('runs', 'data')]
# )
# def update_graph(dtab_selected, run_data):
#     if str(dtab_selected) in run_data:
#         tab_data = run_data[str(dtab_selected)]
#         info = str(tab_data[1]) + " | " + str(tab_data[0]) + "Hz" + " | " + str(tab_data[2]) + "mV" + " | " + str(
#             tab_data[3]) + "mV"
#         return info
#
#     return " - "


#
# #
# # @app.callback(Output('dark-oscope-graph', 'figure'),
# #               [Input('dark-tabs', 'value'),
# #                Input('frequency-input', 'value'),
# #                Input('function-type', 'value'),
# #                Input('amplitude-input', 'value'),
# #                Input('offset-input', 'value'),
# #                Input('oscilloscope', 'on'),
# #                Input('function-generator', 'on')])
# # def update_doutput(value, frequency, wave, amplitude, offset, osc_on, fnct_on):
# #     global tab
# #     time = np.linspace(-0.000045, 0.000045, 1e3)
# #     zero = dict(
# #         data=[dict(x=time, y=[0] * len(time), marker={'color': '#f2f5fa'})],
# #         layout=go.Layout(
# #             xaxis={'title': 's', 'color': '#EBF0F8',
# #                    'titlefont': dict(
# #                        family='Dosis',
# #                        size=15,
# #                    )},
# #             yaxis={'title': 'Voltage (mV)', 'color': '#EBF0F8',
# #                    'titlefont': dict(
# #                        family='Dosis',
# #                        size=15,
# #                    ), 'autorange': False, 'range': [-10, 10]},
# #             margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
# #             plot_bgcolor='rgba(0,0,0,0)',
# #             paper_bgcolor='rgba(0,0,0,0)'
# #         )
# #     )
# #
# #     if not osc_on:
# #         return dict(
# #             data=[],
# #             layout=go.Layout(
# #                 xaxis={'title': 's', 'color': 'rgba(0,0,0,0)',
# #                        'titlefont': dict(
# #                            family='Dosis',
# #                            size=15,
# #                        ), 'showticklabels': False,
# #                        'ticks': '', 'zeroline': False},
# #                 yaxis={'title': 'Voltage (mV)', 'color': 'rgba(0,0,0,0)',
# #                        'titlefont': dict(
# #                            family='Dosis',
# #                            size=15,
# #                        ), 'showticklabels': False, 'zeroline': False},
# #                 margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
# #                 plot_bgcolor='rgba(0,0,0,0)',
# #                 paper_bgcolor='rgba(0,0,0,0)'
# #             )
# #         )
# #
# #     if not fnct_on:
# #         return zero
# #
# #     if tab is not value:
# #         if '' + str(value) in runs:
# #             tab = value
# #             figure = runs['' + str(value)][0]
# #             figure['data'][0]['marker']['color'] = "#f2f5fa"
# #             figure['layout'] = go.Layout(
# #                 xaxis={'title': 's', 'color': '#EBF0F8',
# #                        'titlefont': dict(
# #                            family='Dosis',
# #                            size=15,
# #                        )},
# #                 yaxis={'title': 'Voltage (mV)', 'color': '#EBF0F8',
# #                        'titlefont': dict(
# #                            family='Dosis',
# #                            size=15,
# #                        ), 'autorange': False, 'range': [-10, 10]},
# #                 margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
# #                 plot_bgcolor='rgba(0,0,0,0)',
# #                 paper_bgcolor='rgba(0,0,0,0)'
# #             )
# #             return figure
# #         tab = value
# #         return zero
# #
# #     else:
# #         if wave == 'SIN':
# #             y = [float(offset) +
# #                  (float(amplitude) *
# #                   np.sin(np.radians(2.0 * np.pi * float(frequency) * t)))
# #                  for t in time]
# #
# #         elif wave == 'SQUARE':
# #             y = [float(offset) +
# #                  float(amplitude) *
# #                  (signal.square(2.0 * np.pi * float(frequency) / 10 * t))
# #                  for t in time]
# #
# #         elif wave == 'RAMP':
# #             y = float(amplitude) * \
# #                 (np.abs(signal.sawtooth(2 * np.pi * float(frequency) / 10 * time)))
# #             y = float(offset) + 2 * y - float(amplitude)
# #
# #         figure = dict(
# #             data=[dict(x=time, y=y, marker={'color': '#f2f5fa'})],
# #             layout=go.Layout(
# #                 xaxis={'title': 's', 'color': '#EBF0F8',
# #                        'titlefont': dict(
# #                            family='Dosis',
# #                            size=15,
# #                        )},
# #                 yaxis={'title': 'Voltage (mV)', 'color': '#EBF0F8',
# #                        'titlefont': dict(
# #                            family='Dosis',
# #                            size=15,
# #                        ), 'autorange': False, 'range': [-10, 10]},
# #                 margin={'l': 40, 'b': 40, 't': 0, 'r': 50},
# #                 plot_bgcolor='rgba(0,0,0,0)',
# #                 paper_bgcolor='rgba(0,0,0,0)'
# #             )
# #         )
# #
# #         runs['' + str(value)] = figure, str(wave) + " | " + str(frequency) + \
# #                                 "Hz" + " | " + str(amplitude) + "mV" + " | " + str(offset) + "mV"
# #
# #         # wait to update the runs variable
# #         sleep(0.10)
# #
# #         return figure
#
#


# Callback to update total tab number
@app.callback(
    Output('tab-number', 'data'),
    [Input('new-tab', 'n_clicks'), Input("new-tab-dark", 'n_clicks')],
    [State('tab-number', 'data')]
)
def update_total_tab_number(n_clicks, n_clicks_dark, cur_total_tab):
    # callback context
    ctx = dash.callback_context
    if ctx.triggered:
        prop_type = ctx.triggered[0]["prop_id"].split(".")[1]
        prop_value = ctx.triggered[0]['value']
        if prop_type == 'n_clicks' and prop_value:
            return cur_total_tab + 1
    return cur_total_tab


# Update tabs
@app.callback(
    [Output('tabs', 'children'), Output('dark-tabs', 'children')],
    [Input('tab-number', 'data')]
)
def update_tabs(total_tab_number):
    light_tabs = dark_tabs = list(dcc.Tab(
        label='Run #{}'.format(i),
        value='{}'.format(i)
    ) for i in range(1, total_tab_number + 1))
    return light_tabs, dark_tabs


if __name__ == '__main__':
    app.run_server(port=8051, debug=True)
