import logging
import os
import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly.graph_objs import *
import plotly.graph_objs as go
import plotly.figure_factory as FF
import matplotlib.cm as cm
from flask import send_from_directory
import serial.tools.list_ports
import OpenEIT.dashboard
import queue
import numpy

PORT = 8050
S_TO_MS = 1000
PLOT_REFRESH_INTERVAL = 1.0 * S_TO_MS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)
_LOGGER.addHandler(logging.StreamHandler())

layout = html.Div([html.H5('Hello, world!')])
# Suppress unnecessary debug / warning messages from Flask
os.environ['FLASK_ENV'] = 'development'
flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.INFO)

class Tomogui(object):

    def __init__(self, controller, app):

        self.controller = controller
        self.app 		= app 

        self.n_el = self.controller.n_el
        self.algorithm = self.controller.algorithm

        self.controller.register(
            "recording_state_changed",
            self.on_record_state_changed
        )

        self.controller.register(
            "connection_state_changed",
            self.on_connection_state_changed
        )
        self.connected = False
        self.recording = False 
        self.currentport = ''
        full_ports = list(serial.tools.list_ports.comports())
        self.portnames  = [item[0] for item in full_ports]

        # b followed by \r gives bioimpedance spectroscopy data. 
        self.freqs = [200,500,800,1000,2000,5000,8000,10000,15000,20000,30000,40000,50000,60000,70000]
        self.psd   = [0,0,0,0,0,0,0,0,0,0,0,0,0,0] 
        self.data_dict = {}
        self.data_dict = dict(zip(self.freqs, self.psd))

        if self.algorithm  == 'greit':
            self.gx,self.gy,self.ds = self.controller.greit_params()
            self.img = self.ds # numpy.zeros((32,32),dtype=float)
        else: 
            self.x,self.y,self.tri,self.el_pos = self.controller.plot_params()
            self.img = numpy.zeros(self.x.shape[0]) 

    # Get's new data off the serial port. 
    def process_data(self):

        try:
            self.img = self.controller.image_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            logger.info("rendering new image ...")
            # before = time.time()
            # self.update_figure()
            # self.text = 'render time: %.2f' % (
            #     time.time() - before)
            # logger.info(self.text)

    def dist_origin(self,x, y, z):
        return z

    def on_connection_state_changed(self, connected):
        if connected:
            self.connected = True
        else:
            self.connected = False 

    def on_record_state_changed(self, recording):
        if recording:
            self.recording = True
        else:
            self.recording = False 

    def return_layout(self):

        self.layout = html.Div( [
                html.Div( [

                    html.Div( [
                        html.P('Realtime Control: '),
                    ], style={'width': '10%', 'display': 'inline-block','text-align': 'center'} ),
                    

                    html.Div( [
                    # the button controls      
                    dcc.Dropdown(
                        id='name-dropdownim',
                        options=[{'label':name, 'value':name} for name in self.portnames],
                        placeholder = 'Select Port',
                        value = self.portnames[0]
                        ),
                    ], style={'width': '30%', 'display': 'inline-block','text-align': 'center'} ),

                    html.Div( [
                    html.Button(children='Connect', id='connectbuttonim', type='submit'),
                    ], style={'width': '10%', 'display': 'inline-block','text-align': 'center'} ),

                    html.Div( [
                    html.Button(children='Save Current Spectrum', id='savebuttonim', type='submit'),
                    ] , style={'width': '10%', 'display': 'inline-block','text-align': 'center'}),

                    html.Div( [
                    html.Button(children='Baseline', id='baseline', type='submit'),
                    ] , style={'width': '10%', 'display': 'inline-block','text-align': 'center'}),

                    html.Div( [
                    html.Button(children='Autoscale', id='autoscale', type='submit'),
                    ] , style={'width': '15%', 'display': 'inline-block','text-align': 'center'}),

                    html.Div( [
                    html.Button(children='Update Histogram', id='histogram', type='submit'),
                    ] , style={'width': '15%', 'display': 'inline-block','text-align': 'center'}),

                ], style={'width': '100%', 'display': 'inline-block'} ),

                html.Div( [
                                        # the button controls      
                    html.Div( [
                    html.P('Offline File Control: '),
                    ], style={'width': '15%', 'display': 'inline-block','text-align': 'center'} ),

                    # the button controls      
                    html.Div( [
                    html.Button(children='Read from File', id='readfromfile', type='submit'),
                    ], style={'width': '15%', 'display': 'inline-block','text-align': 'center'} ),

                    html.Div( [
                    html.Button(children='Step', id='stepfile', type='submit'),
                    ], style={'width': '10%', 'display': 'inline-block','text-align': 'center'} ),

                    html.Div( [
                    html.Button(children='Step Back', id='stepbackfile', type='submit'),
                    ] , style={'width': '10%', 'display': 'inline-block','text-align': 'center'}),

                    html.Div( [
                    html.Button(children='Run', id='runfile', type='submit'),
                    ] , style={'width': '10%', 'display': 'inline-block','text-align': 'center'}),

                    html.Div( [
                    html.Button(children='Reset File Marker', id='resetfilem', type='submit'),
                    ] , style={'width': '10%', 'display': 'inline-block','text-align': 'center'}),                    

                ], style={'width': '100%', 'display': 'inline-block'} ),

                html.Div( [

                    html.Div( [
                    html.P('Range Min: '),
                    ], style={'width': '10%', 'display': 'inline-block','text-align': 'center'} ),

                    html.Div( [
                    dcc.Input(
                        id='minimum_range',
                        placeholder='Enter',
                        type='text',
                        value=''
                    ),
                    ] , style={'width': '10%', 'display': 'inline-block','text-align': 'center'}), 

                    html.Div( [
                        dcc.RangeSlider(
                            id='range-slider',
                            count=1,
                            min=-5,
                            max=10,
                            step=0.5,
                            value=[-3, 7]
                        ),
                    ] , style={'width': '60%', 'display': 'inline-block','text-align': 'center'}),                     

                    html.Div( [
                    html.P('Range Max: '),
                    ], style={'width': '10%', 'display': 'inline-block','text-align': 'center'} ),

                    html.Div( [
                    dcc.Input(
                        id='maximum_range',
                        placeholder='Enter',
                        type='text',
                        value=''
                    ),
                    ] , style={'width': '10%', 'display': 'inline-block','text-align': 'center'}), 
                    

                ], style={'width': '100%', 'display': 'inline-block'} ),

                html.Div( [
                    html.Div(id='output-container-range-slider')
                ], style={'width': '100%', 'display': 'inline-block'} ),

                  
                # The graph. 
                dcc.Graph(
                    id='live-update-image',
                    animate=False,
                    config={
                        'displayModeBar': False
                    }
                ),
                dcc.Graph(
                    id='live-update-histogram',
                    animate=False,
                    config={
                        'displayModeBar': False
                    }
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=PLOT_REFRESH_INTERVAL
                ),

            
            ] )      

        @self.app.callback( 
            dash.dependencies.Output('savebuttonim', 'children'),
            [dash.dependencies.Input('savebuttonim', 'n_clicks')])
        def callback_dropdown(n_clicks):
            if n_clicks is not None:
                try: 
                    if self.recording == False:
                        print('start recording')
                        self.controller.start_recording()
                    else:
                        print ('stop recording')
                        self.controller.stop_recording()
                except: 
                    print('could not record')
                    self.recording = False 
            if self.recording is True: 
                return 'Stop Recording' 
            else:
                return 'Record'


        @self.app.callback(
            dash.dependencies.Output(component_id='connectbuttonim', component_property='children'),
            [dash.dependencies.Input(component_id='connectbuttonim', component_property='n_clicks'),
            dash.dependencies.Input(component_id='name-dropdownim', component_property='value')]
        )
        def connect(n_clicks, dropdown_value):
            if n_clicks is not None:
                try: 
                    if self.connected == False:
                        print('connect')
                        self.controller.connect(str(dropdown_value))
                    else:
                        print('disconnect')
                        self.controller.disconnect()
                except: 
                    print('could not connect, is the device plugged in?')
                    self.connected = False 
            if self.connected is True: 
                return 'Disconnect' 
            else:
                return 'Connect'
     
        @self.app.callback(
            dash.dependencies.Output('output-container-range-slider', 'children'),
            [dash.dependencies.Input('range-slider', 'value')])
        def update_output(value):
            return 'You have selected "{}"'.format(value)

        @self.app.callback(
            Output('live-update-image', 'figure'),
            events=[Event('interval-component', 'interval')])
        def update_graph_scatter():
            # update the data queue. 
            self.process_data()

            if self.algorithm  == 'greit':
                self.gx,self.gy,self.ds = self.controller.greit_params()
                self.img = self.ds # numpy.zeros((32,32),dtype=float)
                # If algorithm is GREIT 
                layout = go.Layout(
                    width = 400,
                    height = 400,
                    # title = "EIT reconstruction",
                    xaxis = dict(
                      #nticks = 10,
                      domain = [0.0, 0.0],
                      showgrid=False,
                      zeroline=False,
                      showline=False,
                      ticks='',
                      showticklabels=False,
                      # autorange = 'reversed',
                      title='EIT',
                    ),
                    yaxis = dict(
                      scaleanchor = "x",
                      domain = [0, 0.0],
                      showgrid=False,
                      zeroline=False,
                      showline=False,
                      ticks='',
                      showticklabels=False,
                      # autorange = 'reversed',
                    ),
                    showlegend= False
                )

                data = [
                    go.Heatmap(
                        z=self.img,
                        colorscale='Jet',
                        zmin=1, zmax=1500,
                        colorbar=dict(
                                #title='Colorbar',
                                lenmode = 'fraction',
                                len = 1.0,
                                x=1.2,
                                y = 0.5
                            ),
                    )
                ]
            else: 
                self.x,self.y,self.tri,self.el_pos = self.controller.plot_params()
                #self.gx,self.gy,self.ds = self.controller.greit_params()
                #self.img = self.ds # numpy.zeros((32,32),dtype=float)
                #self.img = numpy.zeros(self.x.shape[0]) 
 
                camera = dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=0.0, y=0.0, z=2.5)
                )

                noaxis=dict(showbackground=False,
                            showline=False,
                            zeroline=False,
                            showgrid=False,
                            showticklabels=False,
                            title=''
                          )

                layout = go.Layout(
                         width=400,
                         height=400,
                         scene=dict(
                            xaxis=noaxis,
                            yaxis=noaxis,
                            zaxis=noaxis,
                            aspectratio=dict(
                                x=1.0,
                                y=1.0,
                                z=0.0),
                            camera =camera,
                            )

                        )

                self.img[0] = 5 
                data = FF.create_trisurf(x=self.x, y=self.y, z=self.img,
                                         simplices=self.tri,
                                         color_func=self.dist_origin, # this is equivalent to the mask in tripcolor. 
                                         colormap='Portland',
                                         show_colorbar=False,
                                         title="mesh",
                                         aspectratio=dict(x=1.0, y=1.0, z=0.01),
                                         showbackground=False,
                                         plot_edges=False,
                                         height=600, width=600, 
                                         scale=None,
                                         ) 


            return {'data': data, 'layout': layout}

        @self.app.callback(
            Output('live-update-histogram', 'figure'),
            events=[Event('interval-component', 'interval')])
        def update_graph_scatter():
            # update the data queue. 
            # self.process_data()
            # this is just dummy data filling in here for now, later it should be the updated img data. 
            # 
            #self.gx,self.gy,self.ds = self.controller.greit_params()
            #self.img = self.ds # numpy.zeros((32,32),dtype=float)

            self.x,self.y,self.tri,self.el_pos = self.controller.plot_params()
            self.img = numpy.zeros(self.x.shape[0]) 

            nanless = self.img[~numpy.isnan(self.img)]
            flatimg = (nanless).flatten()

            # print (flatimg)

            data = [go.Histogram(x=flatimg)]

            layout = go.Layout(
                title='Histogram',
                xaxis=dict(
                    title='Amplitudes',
                    type='linear',
                    autorange=True
                ),
                yaxis=dict(
                    title='Frequency',
                    autorange=True
                )
            )

            return {'data': data, 'layout': layout}

        return self.layout


