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
    s3_profile = 's3readonly'
    boto3.setup_default_session(profile_name=s3_profile)
    
    bucketname = configur.get('s3', 'bucket_name')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)
    
    
    
   ## bucketkey_results_file = "battle_result.txt"

    
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
    local_filename = "/tmp/results.jpg"
    results_file_key = "images/"+pokemonName+"/0.jpg"
    bucket.download_file(results_file_key, local_filename)
    print("line 62")
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()
    data = base64.b64encode(bytes)
    datastr = data.decode()

    return {
     'statusCode': 200,
     'headers': {
            'Content-Type': 'image/jpeg',
            'Content-Disposition': f'attachment; filename={results_file_key}', 
        },
     'body': json.dumps(datastr),
     'isBase64Encoded': True
    }
      
     
    
    
 
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': json.dumps(str(err))
    }

