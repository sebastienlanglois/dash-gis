import os
import dash
import dash_html_components as html
import dash_leaflet as dl

app = dash.Dash()

app.layout = html.Div([
    dl.Map(children=[
        dl.LayersControl([
            dl.BaseLayer(dl.TileLayer(
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"),
                         name="satellite", checked=True),
            dl.BaseLayer(dl.TileLayer(), name="map", checked=False),
        ], position='bottomleft'),
        dl.Pane(dl.WMSTileLayer(url="https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                                layers="nexrad-n0r-900913", format="image/png", transparent=True))
    ], center=(40, -100), zoom=4, style={'height': '99vh'}),
])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=True, use_reloader=False)