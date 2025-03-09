import sys
from utils.wrappers import dataframe_to_parquet_bytes
import s3fs
import os
import pandas as pd

# Initialize S3 filesystem connection
fs = s3fs.S3FileSystem(
    client_kwargs={"endpoint_url": f"https://{os.environ['AWS_S3_ENDPOINT']}"},
    key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# Construct full S3 path
path_name_nuts="projet-hackathon-ntts-2025/indicators/NUTS2021.xlsx"

# Open the file using s3fs and read it with pandas
with fs.open(path_name_nuts, "rb") as f:
    df_label = pd.read_excel(f,1)

# Ensure column names are correct and standardized for merging
df_label.rename(columns={"Code 2021": "NUTS3","NUTS level 3": "name"}, inplace=True)

path="projet-hackathon-ntts-2025/indicators/indicateurs_departements.parquet"
data = pd.read_parquet(path, filesystem=fs)

# Merge df_indicators with df_label on NUTS3
data = data.merge(df_label[["NUTS3","name"]], on="NUTS3", how="left")

# Sorting the DataFrame by NUTS3
data = data.sort_values(by="NUTS3")

# Calcul de artificial_2018
data["artificial_2018"] = data["artificial_2021"] - data["artificial_net"]

# Calcul de artificial_ratio_2018
data["artificial_ratio_2018"] = 100*data["artificial_2018"] / data["surface_m2"]

data.rename(columns={"artificial_ratio": "artificial_ratio_2021"}, inplace=True)

# Calcul de l'évolution de l'artificial ratio (en pourcentage)
data["artificial_ratio_evolution"] = ((data["artificial_ratio_2021"] - data["artificial_ratio_2018"]) / data["artificial_ratio_2018"]) * 100

data = data[["NUTS3","name","artificial_ratio_2018", "artificial_ratio_2021", "artificial_ratio_evolution"]]

buf_bytes = dataframe_to_parquet_bytes(data)

# Write the bytes to standard output
sys.stdout.buffer.write(buf_bytes)

