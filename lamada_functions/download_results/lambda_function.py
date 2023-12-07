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
    print(event)
    #
    # setup AWS based on config file:
    #
    config_file = 'config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    #
    # configure for S3 access:
    #
    s3_profile = 's3readonly'
    boto3.setup_default_session(profile_name=s3_profile)
    
    bucketname = configur.get('s3', 'bucket_name')
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketname)
    
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
    pokemons = pokemonName.split(":")
    pokemon1 = pokemons[0]
    pokemon2  = pokemons[1]

    
    local_filename = "/tmp/results.txt"
    results_file_key =  pokemonName+":battle_result.txt"
    print("**Downloading results from S3**")
    
    bucket.download_file(results_file_key, local_filename)
    
    #
    #infile = open(local_filename, "r")
    #ines = infile.readlines()
    #infile.close()
    #
    #for line in lines:
    #  print(line)
    #
  
    #
    # open the file and read as raw bytes:
    #
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()
    
    #
    # now encode the data as base64. Note b64encode returns
    # a bytes object, not a string. So then we have to convert
    # (decode) the bytes -> string, and then we can serialize
    # the string as JSON for download:
    #
    data = base64.b64encode(bytes)
    datastr = data.decode()

    print("**DONE, returning results**")
    print(datastr)
    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    return {
      'statusCode': 200,
      'body': json.dumps(datastr)
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': json.dumps(str(err))
    }
