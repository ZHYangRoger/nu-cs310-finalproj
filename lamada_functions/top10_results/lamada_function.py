import json
import boto3
import os
import base64
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: top10**")

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
    if "attributes" in event:
      attributes = event["attributes"]
    elif "pathParameters" in event:
      if "attributes" in event["pathParameters"]:
        attributes = event["pathParameters"]["attributes"]
      else:
        raise Exception("requires attributes parameter in pathParameters")
    else:
        raise Exception("requires attributes parameter in event")

    print("attributes:", attributes)


    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)


    print("**Checking if pokemonName is valid**")
    
    sql = f"SELECT * FROM pokemon_stats Order by {attributes} desc limit 10;"
    print(sql)
    row = datatier.retrieve_all_rows(dbConn, sql)
    
    if not row :  # no such result
      print("**No results, returning...**")
      return {
        'statusCode': 400,
        'body': json.dumps("no results...")
      }
    
    print(row)

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
