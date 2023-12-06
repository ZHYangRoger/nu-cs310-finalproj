import json
import boto3
import os
import base64
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: proj03_download**")

    #
    # setup AWS based on config file:
    #
    config_file = 'config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
  
    #
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')
    
    #
    # jobid from event: could be a parameter
    # or could be part of URL path ("pathParameters"):
    #
    print("event:",event)
    if "pokemonName" in event:
      pokemonName = event["pokemonName"]
    elif "pathParameters" in event:
      if "pokemonName" in event["pathParameters"]:
        pokemonName = event["pathParameters"]["pokemonName"]
      else:
        raise Exception("requires pokemonName parameter in pathParameters")
    else:
        raise Exception("requires pokemonName parameter in event")
        
    print("pokemonName:", pokemonName)


    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    #
    # first we need to make sure the userid is valid:
    #
    print("**Checking if pokemonName is valid**")
    
    sql = "SELECT * FROM pokemon_stats WHERE Name = %s;"
    
    row = datatier.retrieve_one_row(dbConn, sql, [pokemonName])
    
    if row == ():  # no such pokemonName
      print("**No such pokemonName, returning...**")
      return {
        'statusCode': 400,
        'body': json.dumps("no such pokemonName...")
      }
    
    print(row)
    '''
    name = row[1]
    type1 = row[2]
    type2 = row[3]
    total = row[4]
    hp = row[5]
    attack = row[6]
    defense = row[7]
    sp_atk = row[8]
    sp_def = row[9]
    speed = row[10]
    generation = row[11]
    legendary = row[12]
    '''
    return {
     'statusCode': 200,
     'body': json.dumps(row)
    }
      
     
    
    
 
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': json.dumps(str(err))
    }
