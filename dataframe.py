import boto3
import json
import pandas as pd
from sqlalchemy import create_engine


def upload_to_sql(club):
    DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    HOST = 'aicore-db.ckoq1wsuhqob.us-east-1.rds.amazonaws.com'
    USER = 'postgres'
    PASSWORD = 'Ne0ntetras'
    DATABASE = 'data-pipeline-project'
    PORT = 5432
    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket('premier-league-bucket')

    stats_dict_list = []
    name_short = {
            'Arsenal': 'ARS',
            'Aston Villa': 'AVL',
            'Brentford': 'BRE',
            'Brighton': 'BHA',
            'Burnley': 'BUR',
            'Chelsea': 'CHE',
            'Crystal Palace': 'CRY',
            'Everton': 'EVE',
            'Leeds': 'LEE',
            'Leicester': 'LEI',
            'Liverpool': 'LIV',
            'Man City': 'MCI',
            'Man Utd': 'MUN',
            'Newcastle': 'NEW',
            'Norwich': 'NOR',
            'Southampton': 'SOU',
            'Spurs': 'TOT',
            'Watford': 'WAT',
            'West Ham': 'WHU',
            'Wolves': 'WOL'
        }
    for obj in my_bucket.objects.all():
        if obj.key[-3:] == name_short[club]:
            stats_dict_list.append(json.loads(obj.get()['Body'].read()))
    df = pd.DataFrame(stats_dict_list).fillna(0)  # Create panda

    stats2int =['Shots on target', 'Shots', 'Touches', 'Passes', 'Tackles', 'Clearances',
        'Corners', 'Offsides', 'Fouls conceded', 'Yellow cards', 'Red cards']
    for stat in stats2int:
        df[stat] = df[stat].astype('int64')
    df['Date'] = df['Date'].astype('datetime64').dt.date  # Converts to datetime without time
    df['Location'] = df['Location'].astype('category')
    df['Possession %']=df['Possession %'].astype('float64')

    df.to_sql(club, engine, if_exists='replace', index=False)



