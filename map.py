import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import folium
import os


script_dir = os.path.dirname(__file__)
del_path = os.path.normpath(os.path.join(script_dir, "./data", "railway_stations_delay_data.csv"))
delay_data = pd.read_csv(del_path)
delay_data = delay_data[['station_name', 'district']].drop_duplicates()

print(delay_data.head(10))
delay_data.to_csv('data/stations.csv')
