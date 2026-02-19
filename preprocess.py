import rasterio
from rasterio.features import rasterize
import geopandas
import shapely
import numpy as np

# import the shape file with the soil data "C:\SoilGrids\inputs_swat\soils_mazar_4326.shp"
soil_shapefile_path = r"C:\SoilGrids\inputs_swat\soils_mazar_4326.shp"
soil_gdf = geopandas.read_file(soil_shapefile_path)
print(soil_gdf.head())

#TODO: before rasterizing, we need to make a csv look up table. save the columns SNUM and FAOSOIL to a csv file
lookup_table_path = r"C:\SoilGrids\inputs_swat\soil_lookup_table.csv"
soil_gdf[['SNUM', 'FAOSOIL']].to_csv(lookup_table_path, index=False)

# Set CRS if not defined (filename suggests EPSG:4326)
if soil_gdf.crs is None:
    soil_gdf = soil_gdf.set_crs(epsg=4326)

print(soil_gdf.head())

# now rasterize the soil data to match the raster grid of a given DEM file and burn in the SNUM column (first one)
dem_path = r"C:\SoilGrids\inputs_swat\dem_mazar_reprojected.tif"

# Read the DEM to get its properties (transform, shape, CRS)
with rasterio.open(dem_path) as dem_src:
    dem_transform = dem_src.transform
    dem_shape = (dem_src.height, dem_src.width)
    dem_crs = dem_src.crs
    dem_profile = dem_src.profile.copy()

# Reproject soil data to match DEM CRS if needed
if soil_gdf.crs != dem_crs:
    soil_gdf = soil_gdf.to_crs(dem_crs)

# Create geometry-value pairs for rasterization (geometry, SNUM value)
shapes = [(geom, value) for geom, value in zip(soil_gdf.geometry, soil_gdf['SNUM'])]

# Rasterize the soil data using SNUM values
soil_raster = rasterize(
    shapes=shapes,
    out_shape=dem_shape,
    transform=dem_transform,
    fill=0,  # NoData value for areas outside polygons
    dtype=np.int32
)

# Update profile for output raster
dem_profile.update(
    dtype=np.int32,
    count=1,
    nodata=0
)

# Save the rasterized soil data
output_path = r"C:\SoilGrids\inputs_swat\soils_mazar_rasterized.tif"
with rasterio.open(output_path, 'w', **dem_profile) as dst:
    dst.write(soil_raster, 1)

print(f"Rasterized soil data saved to: {output_path}")
print(f"Raster shape: {dem_shape}")
print(f"CRS: {dem_crs}")
print(f"Lookup table saved to: {lookup_table_path}")