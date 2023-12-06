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
    pokemons = pokemonName.split(":")
    pokemon1 = pokemons[0]
    pokemon2  = pokemons[1]
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    #
    # first we need to make sure the userid is valid:
    #
    print("**Checking if pokemonName is valid**")
    
    sql = "SELECT * FROM pokemon_stats WHERE Name = %s;"
    
    p1 = datatier.retrieve_one_row(dbConn, sql, [pokemon1])
    p2 = datatier.retrieve_one_row(dbConn, sql, [pokemon2])
    if p1 == () or p2 ==():  # no such pokemonName
      print("**No such pokemonName, returning...**")
      return {
        'statusCode': 400,
        'body': json.dumps("no such pokemonName...")
      }
    
    print(p1)
    print(p2)
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
    poke1 = Pokemon(p1[1],p1[5],p1[6],p1[7],p1[10],p1[2])
    poke2 = Pokemon(p2[1],p2[5],p2[6],p2[7],p2[10],p2[2])
    winner = battle(poke1,poke2)
    body ={
        "name" : winner.name,
        "hp": winner.hp
    }
    return {
     'statusCode': 200,
     'body': json.dumps(body)
    }
      
     
    
    
 
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 400,
      'body': json.dumps(str(err))
    }

class Pokemon:
    def __init__(self, name, hp, attack, defense, speed, type1):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.type = type1

    def is_defeated(self):
        return self.hp <= 0

    def take_damage(self, damage):
        self.hp -= damage

    def calculate_damage(self, other):
        type_effectiveness = self.type_effectiveness(other.type)
        damage = max(1, (self.attack / other.defense) * type_effectiveness*10)
        return damage

    def type_effectiveness(self, other_type):
        effectiveness = {
            'grass': {'water': 2, 'fire': 0.5, 'rock': 2, 'ground': 2, 'grass': 0.5, 'poison': 0.5, 'flying': 0.5, 'bug': 0.5},
            'water': {'fire': 2, 'grass': 0.5, 'ground': 2, 'rock': 2, 'water': 0.5, 'electric': 0.5},
            'fire': {'grass': 2, 'water': 0.5, 'bug': 2, 'rock': 0.5, 'fire': 0.5, 'steel': 2, 'ice': 2, 'dragon': 0.5},
            'bug': {'grass': 2, 'fire': 0.5, 'fighting': 0.5, 'poison': 0.5, 'flying': 0.5, 'psychic': 2, 'ghost': 0.5, 'dark': 2, 'steel': 0.5, 'fairy': 0.5},
            'normal': {'rock': 0.5, 'ghost': 0, 'steel': 0.5},
            'poison': {'grass': 2, 'poison': 0.5, 'ground': 0.5, 'rock': 0.5, 'ghost': 0.5, 'steel': 0, 'fairy': 2},
            'electric': {'water': 2, 'electric': 0.5, 'grass': 0.5, 'ground': 0, 'flying': 2, 'dragon': 0.5},
            'ground': {'fire': 2, 'electric': 2, 'grass': 0.5, 'poison': 2, 'flying': 0, 'bug': 0.5, 'rock': 2, 'steel': 2},
            'fairy': {'fighting': 2, 'poison': 0.5, 'steel': 0.5, 'fire': 0.5, 'dragon': 2, 'dark': 2},
            'fighting': {'normal': 2, 'ice': 2, 'poison': 0.5, 'flying': 0.5, 'psychic': 0.5, 'bug': 0.5, 'rock': 2, 'ghost': 0, 'dark': 2, 'steel': 2, 'fairy': 0.5},
            'psychic': {'fighting': 2, 'poison': 2, 'psychic': 0.5, 'dark': 0, 'steel': 0.5},
            'rock': {'fire': 2, 'ice': 2, 'fighting': 0.5, 'ground': 0.5, 'flying': 2, 'bug': 2, 'steel': 0.5},
            'ghost': {'normal': 0, 'psychic': 2, 'ghost': 2, 'dark': 0.5},
            'ice': {'grass': 2, 'fire': 0.5, 'ice': 0.5, 'fighting': 0.5, 'rock': 0.5, 'steel': 0.5, 'dragon': 2, 'flying': 2},
            'dragon': {'dragon': 2, 'steel': 0.5, 'fairy': 0},
            'dark': {'fighting': 0.5, 'psychic': 2, 'ghost': 2, 'dark': 0.5, 'fairy': 0.5},
            'steel': {'ice': 2, 'rock': 2, 'steel': 0.5, 'fire': 0.5, 'water': 0.5, 'electric': 0.5, 'fairy': 2},
            'flying': {'grass': 2, 'electric': 0.5, 'fighting': 2, 'bug': 2, 'rock': 0.5, 'steel': 0.5}
        }
        return effectiveness.get(self.type, {}).get(other_type, 1)

def battle(pokemon1, pokemon2):
    if pokemon1.speed >= pokemon2.speed:
        attacker, defender = pokemon1, pokemon2
    else:
        attacker, defender = pokemon2, pokemon1
    while not pokemon1.is_defeated() and not pokemon2.is_defeated():
       

        damage = attacker.calculate_damage(defender)
        defender.take_damage(damage)
        print(f"{attacker.name} attacks {defender.name} for {damage} damage.")


        attacker, defender =  defender,attacker

    winner = pokemon1 if pokemon2.is_defeated() else pokemon2
    print(f"{winner} wins the battle!,left hp is {winner.hp}")
    return winner