import base64
import io
import json
import re
import dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
from dash_extensions.javascript import assign
import plotly.express as px

from app import app
from my_project.extract_df import create_df, get_data, get_location_info
from my_project.utils import plot_location_epw_files, generate_chart_name, plot_stations_data
from my_project.global_scheme import mapping_dictionary
from my_project.extract_df import convert_data

from dash_extensions.enrich import ServersideOutput, Output, Input, State, html, dcc

import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
import intake
import geopandas as gpd

path = 'https://raw.githubusercontent.com/hydrocloudservices/catalogs/main/catalogs/hydrology.yaml'

cat = intake.open_catalog(path)

ds = cat.melcc.to_dask()

#gdf = gpd.read_file("assets/data/Bassins Outaouais HSAMI.geojson")
storage_options = {'anon': True,
                   'client_kwargs': {'endpoint_url': 'https://s3.wasabisys.com',
                                     'region_name': 'us-east-1'}
                }
gdf = gpd.read_parquet('s3://hydrometric/watershed/combined_spatial.parquet', 
                    storage_options=storage_options)

messages_alert = {
    "start": "To start, upload an EPW file or click on a point on the map!",
    "not_available": "The EPW for this location is not available",
    "success": "The EPW was successfully loaded!",
    "invalid_format": "The format of the EPW file you have uploaded is invalid.",
    "wrong_extension": "The file you have uploaded is not an EPW file",
}

children = plot_location_epw_files()


def layout_select():
    """Contents in the first tab 'Select Weather File'"""
    return html.Div(
        className="container-col tab-container",
        children=[
            # dcc.Loading(
            #     id="loading-1",
            #     type="circle",
            #     fullscreen=True,
            #     children=alert(),
            # ),
            # dcc.Upload(
            #     id="upload-data",
            #     children=dbc.Button(
            #         [
            #             "Drag and Drop or ",
            #             html.A("Select an EPW file from your computer"),
            #         ],
            #         id="upload-data-button",
            #         outline=True,
            #         color="secondary",
            #         className="mt-2",
            #         style={"borderRadius": "5px", "borderStyle": "dashed"},
            #     ),
            #     # Allow multiple files to be uploaded
            #     multiple=True,
            #     className="d-grid",
            # ),

            dl.Map(id="test-map",
                   children=children,
                   center=(45, -75), zoom=8, style={'height': '40vh'}
                   ),
            dcc.Dropdown(id='dropdown-year',
                         placeholder="Year",
                         className="m-1"
            ),
            dcc.Loading(id='loading',
                        children=[dcc.Graph(id="data-chart", 
                                            figure={'layout': dict(rangeslider=dict(visible=True))},
                                            )],
                        type='circle'
                        ),

            # dcc.Graph(id="data-chart",    
            #           figure={'layout': {'transition':{'duration': 300, 'easing': 'cubic-in-out'}}}),
                                            
                                            

            # dbc.Modal(
            #     [
            #         # dbc.ModalHeader("Header"),
            #         dbc.ModalHeader(id="modal-header"),
            #         dbc.ModalFooter(
            #             children=[
            #                 dbc.Button(
            #                     "Close",
            #                     id="modal-close-button",
            #                     className="ml-2",
            #                     color="light",
            #                 ),
            #                 dbc.Button(
            #                     "Yes",
            #                     id="modal-yes-button",
            #                     className="ml-2",
            #                     color="primary",
            #                 ),
            #             ]
            #         ),
            #     ],
            #     id="modal",
            #     is_open=False,
            # ),
        ],
    )


# def alert():
#     """Alert layout for the submit button."""
#     return html.Div(
#         [
#             dbc.Alert(
#                 messages_alert["start"],
#                 color="primary",
#                 id="alert",
#                 dismissable=False,
#                 is_open=True,
#                 style={"maxHeight": "66px"},
#             )
#         ]
#     )


# # add si-ip and map dictionary in the output
# @app.callback(
#     [
#         Output("meta-store", "data"),
#         Output("lines-store", "data"),
#         Output("alert", "is_open"),
#         Output("alert", "children"),
#         Output("alert", "color"),
#     ],
#     [
#         Input("modal-yes-button", "n_clicks"),
#         Input("upload-data-button", "n_clicks"),
#         Input("upload-data", "contents"),
#     ],
#     [
#         State("upload-data", "filename"),
#         State("url-store", "data"),
#     ],
#     prevent_initial_call=True,
# )
# # @code_timer
# def submitted_data(
#     use_epw_click,
#     upload_click,
#     list_of_contents,
#     list_of_names,
#     url_store,
# ):
#     """Process the uploaded file or download the EPW from the URL"""
#     ctx = dash.callback_context

#     if ctx.triggered[0]["prop_id"] == "modal-yes-button.n_clicks":
#         lines = get_data(url_store)
#         if lines is None:
#             return (
#                 None,
#                 None,
#                 True,
#                 messages_alert["not_available"],
#                 "warning",
#             )
#         location_info = get_location_info(
#             lines, url_store
#         )  # we might need to split this call into two, one returns df and one returns location_info
#         return (
#             location_info,
#             lines,
#             True,
#             messages_alert["success"],
#             "success",
#         )

#     elif (
#         ctx.triggered[0]["prop_id"] == "upload-data.contents"
#         and list_of_contents is not None
#     ):
#         content_type, content_string = list_of_contents[0].split(",")

#         decoded = base64.b64decode(content_string)
#         try:
#             if "epw" in list_of_names[0]:
#                 # Assume that the user uploaded a CSV file
#                 lines = io.StringIO(decoded.decode("utf-8")).read().split("\n")
#                 df, location_info = create_df(lines, list_of_names[0])
#                 return (
#                     location_info,
#                     lines,
#                     True,
#                     messages_alert["success"],
#                     "success",
#                 )
#             else:
#                 return (
#                     None,
#                     None,
#                     True,
#                     messages_alert["invalid_format"],
#                     "warning",
#                 )
#         except Exception as e:
#             # print(e)
#             return (
#                 None,
#                 None,
#                 True,
#                 messages_alert["wrong_extension"],
#                 "warning",
#             )
#     raise PreventUpdate


# # add switch_si_ip function and convert the data-store
# @app.callback(
#     [
#         ServersideOutput("df-store", "data"),
#         Output("si-ip-unit-store", "data"),
#     ],
#     [
#         Input("lines-store", "modified_timestamp"),
#         Input("si-ip-radio-input", "value"),
#     ],
#     [State("url-store", "data"), State("lines-store", "data")],
# )
# def switch_si_ip(ts, si_ip_input, url_store, lines):
#     if lines is not None:
#         df, _ = create_df(lines, url_store)
#         map_json = json.dumps(mapping_dictionary)
#         if si_ip_input == "ip":
#             map_json = convert_data(df, map_json)
#         return df, si_ip_input
#     else:
#         return (
#             None,
#             None,
#         )


# @app.callback(
#     [
#         Output("tab-summary", "disabled"),
#         Output("tab-t-rh", "disabled"),
#         Output("tab-sun", "disabled"),
#         Output("tab-wind", "disabled"),
#         Output("tab-psy-chart", "disabled"),
#         Output("tab-data-explorer", "disabled"),
#         Output("tab-outdoor-comfort", "disabled"),
#         Output("tab-natural-ventilation", "disabled"),
#         Output("banner-subtitle", "children"),
#     ],
#     [
#         Input("meta-store", "data"),
#         Input("df-store", "data"),
#     ],
# )
# def enable_tabs_when_data_is_loaded(meta, data):
#     """Hide tabs when data are not loaded"""
#     default = "Current Location: N/A"
#     if data is None:
#         return (
#             True,
#             True,
#             True,
#             True,
#             True,
#             True,
#             True,
#             True,
#             default,
#         )
#     else:
#         return (
#             False,
#             False,
#             False,
#             False,
#             False,
#             False,
#             False,
#             False,
#             "Current Location: " + meta["city"] + ", " + meta["country"],
#         )


# @app.callback(
#     [
#         Output("modal", "is_open"),
#         Output("url-store", "data"),
#     ],
#     [
#         Input("modal-yes-button", "n_clicks"),
#         Input("tab-one-map", "clickData"),
#         Input("modal-close-button", "n_clicks"),
#     ],
#     [State("modal", "is_open")],
#     prevent_initial_call=True,
# )
# def display_modal_when_data_clicked(clicks_use_epw, click_map, close_clicks, is_open):
#     """display the modal to the user and check if he wants to use that file"""
#     if click_map:
#         url = re.search(
#             r'href=[\'"]?([^\'" >]+)', click_map["points"][0]["customdata"][-1]
#         ).group(1)
#         return not is_open, url
#     return is_open, ""


# @app.callback(
#     [
#         Output("modal-header", "children"),
#     ],
#     [
#         Input("tab-one-map", "clickData"),
#     ],
#     prevent_initial_call=True,
# )
# def display_modal_when_data_clicked(click_map):
#     """change the text of the modal header"""
#     if click_map:
#         return [f"Analyse data from {click_map['points'][0]['hovertext']}?"]
#     return ["Analyse data from this location?"]


@app.callback(
    [
        Output("features", "children"),
    ],
    [
        Input("geojson", "n_clicks"),
        Input("geojson", "click_feature"),
    ],
    [
        State("features", "children"),
    ],
    prevent_initial_call=True,
)
def display_modal_when_data_clicked(n_cli, feature_cli, children):
    """display the modal to the user and check if he wants to use that file"""
    # if click_map:
    #     url = re.search(
    #         r'href=[\'"]?([^\'" >]+)', click_map["points"][0]["customdata"][-1]
    #     ).group(1)
    #     return not is_open, url
    #print(n_cli)
    #print(feature_cli)
    if feature_cli != None and feature_cli['properties']['cluster'] == False:
        #from random import randrange
        #data= gdf.iloc[[randrange(30)]].__geo_interface__
        basin_id = feature_cli['properties']['basin_id']
        data = gdf.loc[gdf.id == basin_id].__geo_interface__

        children.append(dl.GeoJSON(data=data, id="polygons"))
        #children = plot_location_epw_files(gdf=gdf)
        

    return children


@app.callback(
    [Output("data-chart", "figure", allow_duplicate=True), 
     Output("dropdown-year", "options")],
     
    [
        Input("geojson", "n_clicks"),
        Input("geojson", "click_feature"),
    ],
    prevent_initial_call=True,
)
def update_line_chart(n_cli, feature_cli):
    x = None
    y = None
    basin_id = None
    options = None
    if feature_cli != None:
        basin_id = feature_cli['properties']['basin_id']
        if basin_id != None:

            # fig=plot_stations_data(ds, basin_id)

            coords_to_drop = list(ds.coords)
            coords_to_drop.remove('time')
            df = \
                ds.sel(basin_id=basin_id).value.drop_vars(coords_to_drop).load().to_dataframe().dropna().reset_index()
            x = df['time']
            y = df['value']

            print(df['time'].dt.year.min())
            print(df['time'].dt.year.max())

            options = list(range(df['time'].dt.year.min(), df['time'].dt.year.max())) 

            # fig = px.line(df, x="time", y="value", title='Flow')
            # print(fig)

    return [{'data': [{
        'hovertemplate': 'time=%{x}<br>value=%{y}<extra></extra>',
        'legendgroup': '',
        'line': {'color': '#636efa', 'dash': 'solid'},
        'marker': {'symbol': 'circle'},
        'mode': 'lines',
        'name': basin_id,
        'showlegend': False,
        'connectgaps': False,
        'type': 'scattergl',
        'x': x,
        'xaxis': 'x',
        'y': y,
        'yaxis': 'y',
        }], 'layout': {
        'legend': {'tracegroupgap': 0},
        'title': {'text': f'Flow - {basin_id}'},
        'xaxis': dict(rangeselector=dict(buttons=list([dict(count=1,
                      label='1m', step='month', stepmode='backward'),
                      dict(count=6, label='6m', step='month',
                      stepmode='backward'), dict(count=1, label='YTD',
                      step='year', stepmode='todate'), dict(count=1,
                      label='1y', step='year', stepmode='backward'),
                      dict(step='all')])),
                      rangeslider=dict(visible=True), type='date'),
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        # 'xaxis': {'anchor': 'y', 'domain': [0.0, 1.0],
        #           'title': {'text': 'time'}},
        # 'yaxis': {'anchor': 'x', 'domain': [0.0, 1.0],
        #           'title': {'text': 'value'}},
        }}, options]


# @app.callback(
#     Output("data-chart", "figure"), 
#     [
#     Input("dropdown-year", "value")
#     ],
#     [State("data-chart", "figure"), ]
# )
# def update_year_chart(options, fig):
#     print(options)
    
#     return fig
#     # if fig:

#     #     print(fig['data'])
#     #     fig.update_layout(xaxis_range=['1950-01-01','2022-01-01'])

