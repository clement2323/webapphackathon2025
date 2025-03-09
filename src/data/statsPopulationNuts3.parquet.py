import pandas as pd
import s3fs
import os
import sys
from utils.wrappers import dataframe_to_parquet_bytes


# Initialize S3 filesystem connection
fs = s3fs.S3FileSystem(
    client_kwargs={"endpoint_url": f"https://{os.environ['AWS_S3_ENDPOINT']}"},
    key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

file_path = "s3://projet-hackathon-ntts-2025/indicators/estat_demo_r_pjanaggr3.tsv.gz"

with fs.open(file_path, 'rb') as f:
    df = pd.read_csv(f, sep="\t", compression="gzip", dtype=str)

df[['freq', 'unit', 'sex', 'age', 'geo']] = df.iloc[:, 0].str.split(",", expand=True)
df = df.drop(columns=df.columns[0])
cols = ['freq', 'unit', 'sex', 'age', 'geo'] + list(df.columns[:-5])  # Les années en dernier
df = df[cols]

df.replace(': ', 0, inplace=True)

df = df[(df['sex'] == 'T') & (df['age'] == 'TOTAL')]
df = df.drop(columns=['freq', 'unit', 'sex', 'age', '1990 ', '1991 ', '1992 ', '1993 ',
       '1994 ', '1995 ', '1996 ', '1997 ', '1998 ', '1999 ', '2000 ', '2001 ',
       '2002 ', '2003 ', '2004 ', '2005 ', '2006 ', '2007 ', '2008 ', '2009 ',
       '2010 ', '2011 ', '2012 ', '2013 ', '2014 ', '2015 ', '2016 ', '2017 '])


def extract_number(value):
    if isinstance(value, str):
        num = "".join(c for c in value if c.isdigit())
        return int(num) if num else None
    return value


years = ['2018 ', '2019 ', '2020 ', '2021 ', '2022 ', '2023 ', '2024 ']
for year in years:
    df[year] = df[year].apply(extract_number)
    df[year].astype("Int64")

df_nuts3 = df[df['geo'].str.len() == 5]
# df_country = df[df['geo'].str.len() == 2]

buf_bytes = dataframe_to_parquet_bytes(df_nuts3)
sys.stdout.buffer.write(buf_bytes)
