import pandas as pd
import geopandas as gpd
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource
from bokeh.palettes import brewer
from bokeh.models import LinearColorMapper
from bokeh.models import ColorBar
from bokeh.models import Slider
from bokeh.models import HoverTool
from bokeh.layouts import widgetbox, column
from bokeh.io import curdoc


# Helper functions
def get_geojson(num):
    """Input a year (int) and return corresponding GeoJSON"""
    gdf_year = gdf[gdf["year"] == num]
    return gdf_year.to_json()


def update_plot(attr, old, new):
    """Change properties / attributes of the datasource and title depending on slider value / position."""

    yr = slider.value
    geosource.geojson = get_geojson(yr)  # our custom function from before
    p.title.text = f"Avg. Monthly Temperature Anomaly for Year {yr}"


# Read in the data
DATA = "data/all_country_temp_data_CLEAN.csv"
SHAPEFILE = "data/ne_110m_admin_0_countries.shp"

df = pd.read_csv(DATA)
# Group by country and year
df = (
    df.groupby(["country", "year"])[["monthly_anomaly"]]
    .mean()["monthly_anomaly"]
    .reset_index()
)

gdf = gpd.read_file(SHAPEFILE, encoding="utf-8")[["ADMIN", "geometry"]]
gdf = gdf.rename(columns={"ADMIN": "country"})

# Merge DataFrames together
gdf = pd.merge(gdf, df, how="left", on="country")


# Set variables for map
geosource = GeoJSONDataSource(geojson=get_geojson(1900))
palette = brewer["RdBu"][6]

# Draw figure
p = figure(
    title="Avg. Monthly Temperature Anomaly for Year 1900",
    plot_height=600,
    plot_width=1000,
)

# Define colormap
color_mapper = LinearColorMapper(palette=palette, low=-3, high=3, nan_color="white")

# Set a color bar on the bottom left
color_bar = ColorBar(
    color_mapper=color_mapper,
    label_standoff=8,
    width=400,
    height=20,
    location=(0, 0),
    orientation="horizontal",
)

# Add colorbar to figure
p.add_layout(color_bar, "below")

# Add map to figure
p.patches(
    "xs",
    "ys",
    source=geosource,
    fill_color={"field": "monthly_anomaly", "transform": color_mapper},
    line_color="black",
    line_width=1,
)

# Add tooltips to figure
hover = HoverTool(
    tooltips=[("Country", "@country"), ("Temp. Anomaly", "@monthly_anomaly")]
)
p.tools.append(hover)

# Implement slider
slider = Slider(title="Year", start=1900, end=2013, step=1, value=1900)
slider.on_change("value", update_plot)

# Add slider to figur
layout = column(p, widgetbox(slider))

curdoc().add_root(layout)
