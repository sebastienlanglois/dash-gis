import functools
import time
from my_project.global_scheme import fig_config, mapping_dictionary
import pandas as pd
import json
from pandas import json_normalize
import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
from dash_extensions.javascript import assign
from dash import html, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import copy
import intake
import geopandas as gpd

def code_timer(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer


def generate_chart_name(tab_name, meta=None, custom_inputs=None, units=None):
    figure_config = copy.deepcopy(fig_config)
    custom_str = ""
    if custom_inputs:
        custom_str += f"_{custom_inputs}"
    if units:
        custom_str += f"_{units}"
    if meta:
        figure_config["toImageButtonOptions"][
            "filename"
        ] = f"{meta['city']}_{meta['country']}_{tab_name}{custom_str}"
    else:
        figure_config["toImageButtonOptions"]["filename"] = f"{tab_name}{custom_str}"
    return figure_config

def generate_units(si_ip):
    return "SI" if si_ip == "si" else "IP" if si_ip == "ip" else None

def generate_units_degree(si_ip):
    return "C" if si_ip == "si" else "F" if si_ip == "ip" else None

def generate_custom_inputs(var):
    if var in mapping_dictionary:
        var_fullname = mapping_dictionary[var]["name"]
        custom_inputs = ''.join(word.capitalize() for word in var_fullname.split(' '))
        return custom_inputs
    else:
        return None

def generate_custom_inputs_time(start_month, end_month, start_hour, end_hour):
    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    start_month_abbr = month_names[int(start_month)]
    end_month_abbr = month_names[int(end_month)]
    custom_inputs = f"{start_month_abbr}-{end_month_abbr}_{start_hour:02d}-{end_hour:02d}"
    return custom_inputs

def generate_custom_inputs_nv(start_month, end_month, start_hour, end_hour, min_dbt_val, max_dbt_val):
    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    start_month_abbr = month_names[int(start_month)]
    end_month_abbr = month_names[int(end_month)]
    custom_inputs = f"{min_dbt_val:02d}-{max_dbt_val:02d}_{start_month_abbr}-{end_month_abbr}_{start_hour:02d}-{end_hour:02d}"
    return custom_inputs

def generate_custom_inputs_explorer(var, start_month, end_month, start_hour, end_hour, filter_var, min_val, max_val):
    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    start_month_abbr = month_names[int(start_month)]
    end_month_abbr = month_names[int(end_month)]
    if var in mapping_dictionary:
        var_fullname = ''.join(word.capitalize() for word in mapping_dictionary[var]["name"].split(' '))
    else:
        var_fullname = var
    if filter_var in mapping_dictionary:
        filter_fullname = ''.join(word.capitalize() for word in mapping_dictionary[filter_var]["name"].split(' '))
    else:
        filter_fullname = filter_var
    custom_inputs = f"{var_fullname}_{start_month_abbr}-{end_month_abbr}_{start_hour:02d}-{end_hour:02d}_{filter_fullname}_{min_val}-{max_val}"
    return custom_inputs

def generate_custom_inputs_psy(start_month, end_month, start_hour, end_hour, colorby_var, data_filter_var, min_val, max_val):
    month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    start_month_abbr = month_names[int(start_month)]
    end_month_abbr = month_names[int(end_month)]
    if colorby_var in mapping_dictionary:
        colorby_fullname = ''.join(word.capitalize() for word in mapping_dictionary[colorby_var]["name"].split(' '))
    else:
        colorby_fullname = colorby_var
    if data_filter_var in mapping_dictionary:
        data_filter_fullname = ''.join(word.capitalize() for word in mapping_dictionary[data_filter_var]["name"].split(' '))
    else:
        data_filter_fullname = data_filter_var

    if colorby_var == "None":
        custom_inputs = f"{start_month_abbr}-{end_month_abbr}_{start_hour:02d}-{end_hour:02d}_{data_filter_fullname}_{min_val}-{max_val}"
    else:
        custom_inputs = f"{colorby_fullname}_{start_month_abbr}-{end_month_abbr}_{start_hour:02d}-{end_hour:02d}_{data_filter_fullname}_{min_val}-{max_val}"
    return custom_inputs

def plot_location_epw_files():

    path = 'https://raw.githubusercontent.com/hydrocloudservices/catalogs/main/catalogs/hydrology.yaml'

    cat = intake.open_catalog(path)

    ds = cat.melcc.to_dask()


    # with open("./assets/data/epw_location.json", encoding="utf8") as data_file:
    #     data = json.load(data_file)

    # df = json_normalize(data["features"])
    # df[["lon", "lat"]] = pd.DataFrame(df["geometry.coordinates"].tolist())
    # df["lat"] += 0.005
    # df["lat"] += 0.005
    # df = df.rename(columns={"properties.epw": "Source"})

    # df_one_building = pd.read_csv("./assets/data/one_building.csv", compression="gzip")

    df = ds.basin_id.load().to_dataframe()


    colorscale = ['red', 'yellow', 'green', 'blue', 'purple']  # rainbow
    chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"  # js lib used for colors
    color_prop = 'drainage_area'
    # Pre process the data into geobuf.

    dicts = df.to_dict('rows')
    for item in dicts:
        item["tooltip"] = "{} ({:.1f})".format(item['basin_id'], item[color_prop])  # bind tooltip
    geojson = dlx.dicts_to_geojson(dicts, lon="longitude", lat='latitude')  # convert to geojson
    geobuf = dlx.geojson_to_geobuf(geojson)  # convert to geobuf
    # Create a colorbar.
    vmax = df[color_prop].max()
    colorbar = dl.Colorbar(colorscale=colorscale, width=20, height=150, min=0, max=vmax, unit='/km2')
    # Geojson rendering logic, must be JavaScript as it is executed in clientside.
    point_to_layer = assign("""function(feature, latlng, context){
        const {min, max, colorscale, circleOptions, colorProp} = context.props.hideout;
        const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
        circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop.
        return L.circleMarker(latlng, circleOptions);  // sender a simple circle marker.
    }""")
    cluster_to_layer = assign("""function(feature, latlng, index, context){
        const {min, max, colorscale, circleOptions, colorProp} = context.props.hideout;
        const csc = chroma.scale(colorscale).domain([min, max]);
        // Set color based on mean value of leaves.
        const leaves = index.getLeaves(feature.properties.cluster_id);
        let valueSum = 0;
        for (let i = 0; i < leaves.length; ++i) {
            valueSum += leaves[i].properties[colorProp]
        }
        const valueMean = valueSum / leaves.length;
        // Render a circle with the number of leaves written in the center.
        const icon = L.divIcon.scatter({
            html: '<div style="background-color:white;"><span>' + feature.properties.point_count_abbreviated + '</span></div>',
            className: "marker-cluster",
            iconSize: L.point(40, 40),
            color: csc(valueMean)
        });
        return L.marker(latlng, {icon : icon})
    }""")
                            
    draw_flag = assign("""function(feature, latlng){
    const flag = L.icon({iconUrl: `https://www.hydroquebec.com/libs/widgets/assets/images/cartes/hq-site.svg`, iconSize: [36, 36]});
    return L.marker(latlng, {icon: flag});
    }""")
    # Create geojson.
    geojson = dl.GeoJSON(data=geobuf, id="geojson", format="geobuf",
                        zoomToBounds=True,  # when true, zooms to bounds when data changes
                        cluster=True,  # when true, data are clustered
                        clusterToLayer=cluster_to_layer,  # how to draw clusters
                        zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. cluster) on click
                        options=dict(pointToLayer=draw_flag),  # how to draw points
                        superClusterOptions=dict(radius=150),   # adjust cluster size
                        hideout=dict(colorProp=color_prop, circleOptions=dict(fillOpacity=1, stroke=False, radius=5),
                                    min=0, max=vmax, colorscale=colorscale))

    # fig = px.scatter_mapbox(
    #     df,
    #     lat="latitude",
    #     lon="longitude",
    #     hover_name="basin_id",
    #     color_discrete_sequence=["#3a0ca3"],
    #     hover_data=["drainage_area","start_date", "end_date"],
    #     zoom=2,
    #     height=500,
    # )
    # fig.update_traces(cluster=dict(enabled=True))
    # fig.update_layout(mapbox_style="carto-positron")
    # fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    #polygon = dl.Polygon(positions=[[57, 10], [57, 11], [56, 11], [57, 10]])

    #from random import randrange

    #data= gdf.iloc[[randrange(30)]].__geo_interface__
    
    

    return [
            dl.LayersControl([
                dl.BaseLayer(dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'), name="Topography", checked=True),
                dl.BaseLayer(dl.TileLayer(
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"),
                 name="satellite", checked=False),
            
                dl.Overlay(dl.WMSTileLayer(url="https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                                            layers="nexrad-n0r-900913", format="image/png", transparent=True),
                                            checked=True, name='radar')
            
        ], position='bottomleft'),

            dl.FeatureGroup([
                    dl.EditControl(id="edit_control"),
                    ], id='features'),
            
            #dl.GeoJSON(data=data, id="polygons"),
            geojson,
            colorbar]


def plot_stations_data(ds, basin_id):

    coords_to_drop = list(ds.coords)
    coords_to_drop.remove('time')
    df = ds.sel(basin_id=basin_id).value.drop_vars(coords_to_drop).load().to_dataframe().reset_index()

    fig = px.line(df, x="time", y="value", title='Flow')

    return fig



def title_with_tooltip(text, tooltip_text, id_button):

    display_tooltip = "none"
    if tooltip_text:
        display_tooltip = "block"

    return html.Div(
        className="container-row",
        style={"padding": "1rem", "marginTop": "1rem"},
        children=[
            html.H5(text, style={"marginRight": "0.5rem"}),
            html.Div(
                [
                    html.Sup(
                        html.Img(
                            id=id_button,
                            src="../assets/icons/help.png",
                            alt="help",
                            style={
                                "width": "1rem",
                                "height": "1rem",
                            },
                        ),
                    ),
                    dbc.Tooltip(
                        tooltip_text,
                        target=id_button,
                        placement="right",
                    ),
                ],
                style={"display": display_tooltip},
            ),
        ],
    )


def summary_table_tmp_rh_tab(df, value, si_ip):
    df_summary = (
        df.groupby(["month_names", "month"])[value]
        .describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99])
        .round(2)
    )
    df_summary = df_summary.reset_index(level="month_names").sort_index()
    df_summary = df_summary.drop(["count"], axis=1)
    df_summary = df_summary.rename(columns={"month_names": "month"})

    df_sum = (
        df[value]
        .describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99])
        .round(2)
        .to_frame()
    )
    df_sum = df_sum.T.assign(count="Year").rename(columns={"count": "month"})

    df_summary = pd.concat([df_summary, df_sum])

    unit = (
        mapping_dictionary[value][si_ip]["unit"]
        .replace("<sup>", "")
        .replace("</sup>", "")
    )
    return dash_table.DataTable(
        columns=[
            {"name": i, "id": i} if i == "month" else {"name": f"{i} ({unit})", "id": i}
            for i in df_summary.columns
        ],
        style_table={"overflowX": "auto"},
        data=df_summary.to_dict("records"),
        style_cell={"textAlign": "center", "padding": "5px 10px"},
        style_cell_conditional=[{"if": {"column_id": "month"}, "textAlign": "right"}],
        style_header={"backgroundColor": "rgb(220, 220, 220)", "fontWeight": "bold"},
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "white"},
            {"if": {"row_index": "even"}, "backgroundColor": "rgb(250, 250, 250)"},
            {"if": {"row_index": [12]}, "backgroundColor": "rgb(220, 220, 220)"},
        ],
        style_as_list_view=True,
    )


def determine_month_and_hour_filter(month, hour, invert_month, invert_hour):
    start_month, end_month = month
    if invert_month == ["invert"] and (start_month != 1 or end_month != 12):
        end_month, start_month = month
    start_hour, end_hour = hour
    if invert_hour == ["invert"] and (start_hour != 1 or end_hour != 24):
        end_hour, start_hour = hour

    return start_month, end_month, start_hour, end_hour
