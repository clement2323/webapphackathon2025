import sys
from utils.wrappers import dataframe_to_parquet_bytes
import s3fs
import os
import pandas as pd
import geopandas as gpd
import numpy as np
from tqdm import tqdm


# Initialize S3 filesystem connection
fs = s3fs.S3FileSystem(
    client_kwargs={"endpoint_url": f"https://{os.environ['AWS_S3_ENDPOINT']}"},
    key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def get_nuts_proportion_classe(year, fs):
    #year ="2018"
    polygon_files_nuts = fs.ls(f"s3://projet-hackathon-ntts-2025/data-predictions/CLCplus-Backbone/SENTINEL2/{str(year)}/250/")
    polygon_files_nuts = [file for file in polygon_files_nuts if not file.endswith("_UE.gpkg")]

    df = pd.DataFrame(columns=["nuts_id", "proportion_classe_0", "proportion_classe_1", "proportion_classe_2", "proportion_classe_3", "proportion_classe_4", "proportion_classe_5", "proportion_classe_6", "proportion_classe_7", "proportion_classe_8", "proportion_classe_9", "proportion_classe_10", "proportion_classe_11", "area_total"])

    for polygon_file_nuts in tqdm(polygon_files_nuts):
        with fs.open("s3://"+polygon_file_nuts, 'rb') as f:
            gdf = gpd.read_file(f)

        new_row = {"nuts_id": polygon_file_nuts.split('/')[-1].split('.')[0].split('_')[-1]}
        new_row['area_total'] = float(np.sum(gdf.geometry.area))

        for classe in np.unique(gdf['label']):
            var_name = f"proportion_classe_{str(classe)}"
            proportion_classe = float(np.sum(gdf[gdf['label'] == classe].geometry.area))/new_row['area_total']
            new_row[var_name] = proportion_classe

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df_filled = df.fillna(0)
    return df_filled


df_2018 = get_nuts_proportion_classe("2018", fs)
df_2021 = get_nuts_proportion_classe("2021", fs)
df_2024 = get_nuts_proportion_classe("2024", fs)


# Renommer la colonne 'proportion_classe_1' en 'artificial_ratio_2021'
df_2018.rename(columns={'proportion_classe_1': 'artificial_ratio_2018'}, inplace=True)
df_2018=df_2018[["nuts_id","artificial_ratio_2018"]]

df_2021.rename(columns={'proportion_classe_1': 'artificial_ratio_2021'}, inplace=True)
df_2021=df_2021[["nuts_id","artificial_ratio_2021"]]

df_2024.rename(columns={'proportion_classe_1': 'artificial_ratio_2024'}, inplace=True)
df_2024=df_2024[["nuts_id","artificial_ratio_2024"]]

# Fusionner les DataFrames sur 'nuts_id'
df_merged = df_2018.merge(df_2021, on='nuts_id', how='outer').merge(df_2024, on='nuts_id', how='outer')

# Renommer 'nuts_id' en 'NUTS3'
df_merged.rename(columns={'nuts_id': 'NUTS3'}, inplace=True)

# Calculer l'évolution de l'artificialisation entre les années
df_merged["artificial_evolution_2018_2024"] = ((df_merged["artificial_ratio_2024"] - df_merged["artificial_ratio_2018"]) / df_merged["artificial_ratio_2018"]) * 100
df_merged["artificial_evolution_2021_2024"] = ((df_merged["artificial_ratio_2024"] - df_merged["artificial_ratio_2021"]) / df_merged["artificial_ratio_2021"]) * 100

# Multiplier les colonnes "artificial_ratio" par 100 pour les exprimer en pourcentage
df_merged["artificial_ratio_2018"] *= 100
df_merged["artificial_ratio_2021"] *= 100
df_merged["artificial_ratio_2024"] *= 100



# Construct full S3 path
path_name_nuts="projet-hackathon-ntts-2025/indicators/NUTS2021.xlsx"

# Open the file using s3fs and read it with pandas
with fs.open(path_name_nuts, "rb") as f:
    df_label = pd.read_excel(f,1)

# Ensure column names are correct and standardized for merging
df_label.rename(columns={"Code 2021": "NUTS3","NUTS level 3": "name"}, inplace=True)
# Merge df_indicators with df_label on NUTS3
data = df_merged.merge(df_label[["NUTS3","name"]], on="NUTS3", how="left")

data = data[["NUTS3","name","artificial_ratio_2018","artificial_ratio_2021","artificial_ratio_2024","artificial_evolution_2018_2024","artificial_evolution_2021_2024"]]

buf_bytes = dataframe_to_parquet_bytes(data)

# Write the bytes to standard output
sys.stdout.buffer.write(buf_bytes)
