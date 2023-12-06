import json
import boto3
import os
import uuid
import base64
import pathlib
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: proj03_upload**")
    
    #
    # setup AWS based on config file:
    #
    config_file = 'config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    print(event)
    #
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')
    

    print("**Accessing request body**")
    
    if "body" not in event:
      raise Exception("event has no body")
      
    body = json.loads(event["body"]) # parse the json
    name = body["Name"]
    type1 = body["Type1"]
    type2 = body["Type2"]
    total = body["Total"]
    hp = body["HP"]
    attack = body["Attack"]
    defense = body["Defense"]
    sp_Atk = body["Sp_Atk"]
    sp_Def = body["Sp_Def"]
    speed = body["Speed"]
    generation = body["Generation"]
    
    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    #
    # first we need to make sure the userid is valid:
    #
    print("**Checking if userid is valid**")
    
    sql = "select max(ind) from pokemon_stats;"
    
    row = datatier.retrieve_one_row(dbConn, sql)
    ind = int(row[0])+1
    sql = '''INSERT into pokemon_stats(ind,Name,Type1,Type2,Total,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed,Generation) values 
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    row = datatier.perform_action(dbConn,sql,[ind,name,type1,type2,total,hp,attack,defense,sp_Atk,sp_Def,speed,generation])
    print(row)

  
    
  

    
    return {
      'statusCode': 200,
      'body': json.dumps(str(ind))
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': json.dumps(str(err))
    }
