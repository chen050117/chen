import pandas as pd
import geopandas as gpd
import os
from shapely.geometry import LineString

# 整个文件的输出目录
input_folder = "wgs_84"
output_folder = "shp"
output_folder2 = "line_shp"
output_combine = "combine_shp"

os.makedirs(output_folder, exist_ok=True)
os.makedirs(output_folder2, exist_ok=True)
os.makedirs(output_combine, exist_ok=True)

combine_shp = gpd.GeoDataFrame(columns=['SchoolName', 'geometry'])

for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    df = pd.read_csv(file_path, sep=",", header=None, names=["longitude", "latitude"], encoding='utf-8')

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["longitude"], df["latitude"]))
    gdf.set_crs(epsg=4326, inplace=True)

    points = list(gdf.geometry)
    line = LineString(points)
    school_name = os.path.splitext(filename)[0]
    school_name = school_name.split("_")[0]
    line_gdf = gpd.GeoDataFrame({'SchoolName': [school_name], 'geometry': [line]}, crs="EPSG:4326")

    combine_shp = combine_shp._append(line_gdf, ignore_index=True)

    output_file = os.path.join(output_folder, f"{school_name}.shp")
    output_file2 = os.path.join(output_folder2, f"{school_name}_line.shp")

    gdf.to_file(output_file, driver="ESRI Shapefile")
    line_gdf.to_file(output_file2, driver="ESRI Shapefile")

    print(f"{school_name}已成功转换为shp文件")
    print(f"{school_name}已成功转换成line_shp文件")

combine_shp.to_file(os.path.join(output_combine, "combine.shp"), driver="ESRI Shapefile")
print(f"合成成功, 合成文件的相对路径为 {output_combine}")
