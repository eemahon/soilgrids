import rasterio
from rasterio.features import rasterize
import geopandas
import numpy as np

# Import the land use shapefile
landuse_shapefile_path = r"c:\SoilGrids\cobertura_vegetal\Cobertura_vegetal_ECUADOR_2022_100k_UTM_WGS84_17S.shp"
landuse_gdf = geopandas.read_file(landuse_shapefile_path)
print("Land use shapefile loaded:")
print(landuse_gdf.head())
print(f"\nColumns: {landuse_gdf.columns.tolist()}")

# Load the Mazar Basin shapefile for clipping
mazar_basin_path = r"C:\SoilGrids\mazar_basin\mazar_basin.shp"
mazar_basin_gdf = geopandas.read_file(mazar_basin_path)
print(f"\nMazar Basin shapefile loaded:")
print(f"  CRS: {mazar_basin_gdf.crs}")
print(f"  Number of features: {len(mazar_basin_gdf)}")

# Reproject Mazar Basin to match land use CRS if needed
if mazar_basin_gdf.crs != landuse_gdf.crs:
    print(f"Reprojecting Mazar Basin from {mazar_basin_gdf.crs} to {landuse_gdf.crs}")
    mazar_basin_gdf = mazar_basin_gdf.to_crs(landuse_gdf.crs)

# Clip land use data to Mazar Basin extent
landuse_gdf = geopandas.clip(landuse_gdf, mazar_basin_gdf)
print(f"\nLand use clipped to Mazar Basin:")
print(f"  Number of features after clipping: {len(landuse_gdf)}")

# Create a lookup table for ctn2 values
lookup_table_path = r"c:\SoilGrids\cobertura_vegetal\landuse_lookup_table.csv"
# Get unique ctn2 values and their descriptions if available
lookup_df = landuse_gdf[['ctn2']].drop_duplicates().sort_values('ctn2').reset_index(drop=True)
lookup_df.to_csv(lookup_table_path, index=False)
print(f"\nLookup table saved to: {lookup_table_path}")

# DEM file to match raster grid
dem_path = r"C:\SoilGrids\inputs_swat\dem_mazar_reprojected.tif"

# Read the DEM to get its properties (transform, shape, CRS)
with rasterio.open(dem_path) as dem_src:
    dem_transform = dem_src.transform
    dem_shape = (dem_src.height, dem_src.width)
    dem_crs = dem_src.crs
    dem_profile = dem_src.profile.copy()

print(f"\nDEM properties:")
print(f"  Shape: {dem_shape}")
print(f"  CRS: {dem_crs}")

# Reproject land use data to match DEM CRS if needed
if landuse_gdf.crs != dem_crs:
    print(f"\nReprojecting from {landuse_gdf.crs} to {dem_crs}")
    landuse_gdf = landuse_gdf.to_crs(dem_crs)

# Create geometry-value pairs for rasterization (geometry, ctn2 value)
shapes = [(geom, value) for geom, value in zip(landuse_gdf.geometry, landuse_gdf['ctn2'])]

# Rasterize the land use data using ctn2 values
landuse_raster = rasterize(
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

# Save the rasterized land use data
output_path = r"C:\SoilGrids\cobertura_vegetal\landuse_mazar_rasterized.tif"
with rasterio.open(output_path, 'w', **dem_profile) as dst:
    dst.write(landuse_raster, 1)

print(f"\nRasterized land use data saved to: {output_path}")
print(f"Raster shape: {dem_shape}")
print(f"CRS: {dem_crs}")
print(f"Unique ctn2 values in raster: {np.unique(landuse_raster)}")
