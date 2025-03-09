import os
import s3fs
import geopandas as gpd
import pandas as pd

def list_gpkg_files(year: str) -> List[str]:
    """
    Lists all .gpkg files in the S3 bucket for a given year.

    Parameters:
    -----------
    year : str
        The year to filter files.

    Returns:
    --------
    List[str]
        A list of .gpkg file paths found in the S3 bucket.
    """
    folder_year = f"projet-hackathon-ntts-2025/data-predictions/CLCplus-Backbone/SENTINEL2/{year}/250/"
    
    # Initialize S3 filesystem connection
    fs = s3fs.S3FileSystem(
        client_kwargs={"endpoint_url": f"https://{os.environ['AWS_S3_ENDPOINT']}"},
        key=os.getenv("AWS_ACCESS_KEY_ID"),
        secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    # List all .gpkg files in the directory
    gpkg_files = [f for f in fs.ls(folder_year) if f.endswith(".gpkg")]
    
    return gpkg_files


def extract_surface_from_gpkg(gpkg_s3_path: str, fs, year) -> dict:
    """
    Extracts the total surface area of label=1 from a GeoPackage file.

    Parameters:
    -----------
    gpkg_s3_path : str
        The full S3 path to the .gpkg file.
    fs : s3fs.S3FileSystem
        The initialized S3 filesystem instance.

    Returns:
    --------
    dict
        A dictionary containing the extracted year, NUTS3 code, and total surface area.
    """
    # Extract year and NUTS3 code from filename
    filename = os.path.basename(gpkg_s3_path)
    year = year  # Extract year from path structure
    nuts3 = filename.replace("predictions_", "").replace(".gpkg", "")
    print(nuts3)
    # Download locally
    local_gpkg = f"/tmp/{filename}"
    with fs.open(gpkg_s3_path, "rb") as remote_file:
        with open(local_gpkg, "wb") as f:
            f.write(remote_file.read())

    # Read the GeoPackage
    gdf = gpd.read_file(local_gpkg)

    # Compute the total surface for label = 1
    total_surface_label_1 = gdf[gdf["label"] == 1].geometry.area.sum()

    return {"Year": year, "NUTS3": nuts3, "Total_Surface_Label_1": total_surface_label_1}


def get_surface_for_all_years(years: List[str]) -> pd.DataFrame:
    """
    Loops through all available .gpkg files for multiple years and extracts surface data.

    Parameters:
    -----------
    years : List[str]
        A list of years to process.

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing Year, NUTS3, and Total_Surface_Label_1.
    """
    fs = s3fs.S3FileSystem(
        client_kwargs={"endpoint_url": f"https://{os.environ['AWS_S3_ENDPOINT']}"},
        key=os.getenv("AWS_ACCESS_KEY_ID"),
        secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    results = []

    for year in years:
        # year = "2021"
        print(year)
        gpkg_files = list_gpkg_files(year)
        for gpkg_s3_path in gpkg_files:
            result = extract_surface_from_gpkg(gpkg_s3_path, fs, year)
            results.append(result)

    return pd.DataFrame(results)


# Example usage: Get surfaces for years 2021 and 2022
years_to_process = ["2021", "2024"]
df_surfaces = get_surface_for_all_years(years_to_process)



# open surfaces
# Remplacez par le chemin exact vers votre fichier .gpkg sur S3
gpkg_s3_path = "projet-hackathon-ntts-2025/NUTS_RG_01M_2021_4326_LEVL_3.gpkg"

# Téléchargement local du GeoPackage depuis S3
local_gpkg = "/tmp/NUTS_RG_01M_2021_4326_LEVL_3.gpkg"
with fs.open(gpkg_s3_path, "rb") as remote_file:
    with open(local_gpkg, "wb") as f:
        f.write(remote_file.read())

gdf = gpd.read_file(local_gpkg)
gdf = gdf.to_crs(epsg=3035)

# Calculer la surface en m²
gdf["surface_m2"] = gdf.geometry.area
gdf = gdf[["NUTS_ID","surface_m2"]]

gdf.NUTS3


# Rename NUTS_ID to NUTS3 in gdf for merging
gdf.rename(columns={"NUTS_ID": "NUTS3"}, inplace=True)

# Merge df_surfaces with gdf on NUTS3
df_merged = df_surfaces.merge(gdf, on="NUTS3", how="left")

# Calculate artificial ratio for each year
df_merged["artificial_ratio"] = (df_merged["Total_Surface_Label_1"] / df_merged["surface_m2"]) * 100

# Pivot the dataframe to have years as columns
df_pivot = df_merged.pivot(index="NUTS3", columns="Year", values="artificial_ratio")

# Rename columns to include "artificial_ratio_{year}"
df_pivot.columns = [f"artificial_ratio_{int(col)}" for col in df_pivot.columns]

# Reset index for better readability
df_pivot.reset_index(inplace=True)


# Construct full S3 path
path_name_nuts="projet-hackathon-ntts-2025/indicators/NUTS2021.xlsx"

# Open the file using s3fs and read it with pandas
with fs.open(path_name_nuts, "rb") as f:
    df_label = pd.read_excel(f,1)

# Ensure column names are correct and standardized for merging
df_label.rename(columns={"Code 2021": "NUTS3","NUTS level 3": "name"}, inplace=True)

# Merge df_indicators with df_label on NUTS3
data = df_pivot.merge(df_label[["NUTS3","name"]], on="NUTS3", how="left")
