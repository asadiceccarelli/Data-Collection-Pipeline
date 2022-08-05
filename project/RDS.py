import os
from datetime import date
import logging
import boto3
import json
import pandas as pd
import numpy as np
from valid_inputs import valid_clubs
from sqlalchemy import create_engine, inspect

logging.basicConfig(level = logging.INFO)


def rds_connect():
    DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    HOST = 'aicore-db.ckoq1wsuhqob.us-east-1.rds.amazonaws.com'
    USER = 'postgres'
    PASSWORD = os.environ['rds_password']
    DATABASE = 'data-pipeline-project'
    PORT = 5432
    return create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")


def upload_to_sql(club, year):
    engine = rds_connect()
    s3_resource = boto3.resource(
            's3',
            region_name = 'eu-west-2',
            aws_access_key_id = os.environ['aws_access_key_id'],
            aws_secret_access_key = os.environ['aws_secret_access_key']   
            )
    my_bucket = s3_resource.Bucket('premier-league-bucket')
    
    logging.info('Creating data fram using pandas...')
    stats_dict_list = []
    name_short = valid_clubs()[club]
    for obj in my_bucket.objects.all():
        if obj.key[-3:] == name_short:
            stats_dict_list.append(json.loads(obj.get()['Body'].read()))
    df = pd.DataFrame(stats_dict_list).fillna(0)  # Create panda

    stats2int =[
        'Shots on target', 'Shots', 'Touches', 'Passes', 'Tackles', 'Clearances',
        'Corners', 'Offsides', 'Fouls conceded', 'Yellow cards', 'Red cards'
        ]
    for stat in stats2int:
        df[stat] = df[stat].astype('int64')
    
    df['Date'] = df['Date'].astype('datetime64').dt.date  # Converts to datetime without time
    if int(year[5:]) > 90:
        end_year = int('19' + str(year[5:]))
    else:
        end_year = int('20' + str(year[5:]))
    df = df[(df['Date'] > date(int(year[:4]), 8, 1)) & (df['Date'] < date(end_year, 7, 31))]  # Only show dates within selected season

    df['Location'] = df['Location'].astype('category')
    df['Possession %']=df['Possession %'].astype('float64')

    logging.info('Uploading to RDS...')
    df_name = f'{club}-{year[-5:-3]}{year[-2:]}'
    df.to_sql(df_name, engine, if_exists='replace', index=False)
    return df


def _prevent_rescraping():
    engine = rds_connect()
    inspector = inspect(engine)
    return inspector.get_table_names()
