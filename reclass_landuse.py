import rasterio
from rasterio.features import rasterize
import geopandas
import numpy as np

# Import the land use shapefile
# C:\SoilGrids\cobertura_vegetal\landuse_clipped_MB2.shp
landuse_shapefile_path = r"C:\SoilGrids\cobertura_vegetal\landuse_clipped_MB2.shp"
landuse_gdf = geopandas.read_file(landuse_shapefile_path)

# Print the unique values of the 'ctn1' and 'ctn2' columns
print("Unique values in 'ctn1' column:")
print(landuse_gdf['ctn1'].unique())
print("\nUnique values in 'ctn2' column:")
print(landuse_gdf['ctn2'].unique())

"""# Create a mapping from unique ctn2 values to numeric codes
unique_ctn2 = landuse_gdf['ctn2'].unique()
ctn2_to_code = {value: idx + 1 for idx, value in enumerate(unique_ctn2)}

# Print the mapping
print("\nctn2 to numeric code mapping:")
for value, code in ctn2_to_code.items():
    print(f"  {code}: {value}")

# Create a new column with the numeric codes
landuse_gdf['ctn2_code'] = landuse_gdf['ctn2'].map(ctn2_to_code)

print("\nNew column 'ctn2_code' added to the geodataframe.")

# Save the updated geodataframe back to the shapefile
landuse_gdf.to_file(landuse_shapefile_path)
print(f"Shapefile saved with new 'ctn2_code' column: {landuse_shapefile_path}")

"""