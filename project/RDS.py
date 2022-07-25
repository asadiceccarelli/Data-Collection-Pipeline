import boto3
import json
import pandas as pd
import matplotlib.pyplot as plt
from valid_inputs import valid_clubs
from sqlalchemy import create_engine, inspect



def rds_connect():
    DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    HOST = 'aicore-db.ckoq1wsuhqob.us-east-1.rds.amazonaws.com'
    USER = 'postgres'
    PASSWORD = 'Ne0ntetras'
    DATABASE = 'data-pipeline-project'
    PORT = 5432
    return create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")


def upload_to_sql(club, year):
    engine = rds_connect()
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('premier-league-bucket')

    stats_dict_list = []
    name_short = valid_clubs()[club]
    for obj in my_bucket.objects.all():
        if obj.key[-3:] == name_short:
            stats_dict_list.append(json.loads(obj.get()['Body'].read()))
    df = pd.DataFrame(stats_dict_list).fillna(0)  # Create panda

    stats2int =['Shots on target', 'Shots', 'Touches', 'Passes', 'Tackles', 'Clearances',
        'Corners', 'Offsides', 'Fouls conceded', 'Yellow cards', 'Red cards']
    for stat in stats2int:
        df[stat] = df[stat].astype('int64')
    df['Date'] = df['Date'].astype('datetime64').dt.date  # Converts to datetime without time
    df['Location'] = df['Location'].astype('category')
    df['Possession %']=df['Possession %'].astype('float64')

    df_name = f'{club}-{year[-5:-3]}{year[-2:]}'
    df.to_sql(df_name, engine, if_exists='replace', index=False)
    return df


def prevent_rescraping():
    engine = rds_connect()
    inspector = inspect(engine)
    return inspector.get_table_names()

