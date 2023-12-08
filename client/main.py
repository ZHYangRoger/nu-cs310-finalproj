# CS310 Final Project
# Work by: Zihui Yang (zyj6631), Tiansheng Zhang (tzo4717), Yiran Mo (yme2729)
# Some code borrowed from CS310 class projects

import requests
import jsons

import uuid
import pathlib
import logging
import sys
import os
import base64

from configparser import ConfigParser

import matplotlib.pyplot as plt
import matplotlib.image as img

import time


############################################################
#
# classes
#
class User:

  def __init__(self, row):
    self.userid = row[0]
    self.username = row[1]
    self.pwdhash = row[2]


class Job:

  def __init__(self, row):
    self.jobid = row[0]
    self.userid = row[1]
    self.status = row[2]
    self.originaldatafile = row[3]
    self.datafilekey = row[4]
    self.resultsfilekey = row[5]


############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  print()
  print(">> Please Enter a Command:")
  print("   0 => Exit Pokedex")
  print("   1 => Get Pokemon Information by Name")
  print("   2 => Get the Top 10 Pokemons by Attribute")
  print("   3 => Create a New Pokemon")
  print("   4 => Get All Pokemons, 10 per Table")
  print("   5 => Get the Picture of a Pokemon")
  print("   6 => Pokemon Battle")
  
  cmd = input()

  if cmd == "":
    cmd = -1
  elif not cmd.isnumeric():
    cmd = -1
  else:
    cmd = int(cmd)

  return cmd


def battle(baseurl):
  print("Enter pokemon name1 >")
  pokeMonName1 = input()
  print("Enter pokemon name2 >")
  pokeMonName2 = input()

  print()
  print("Battle Simulator Starting...")

  start_battle(pokeMonName1, pokeMonName2)

  try:
    #
    # call the web service:
    #
    pokemonName = f"{pokeMonName1}:{pokeMonName2}"
    api = '/download'
    url = baseurl + api + '/' + pokemonName
    # print(url)
    time.sleep(1)
    res = requests.get(url)
    #
    # let's look at what we got back:
    #
    i = 0
    while res.status_code != 200 and i < 10:
      res = requests.get(url)
      time.sleep(0.5)
      i += 1
      
    if res.status_code != 200:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract results:
    #
    body = res.json()

    datastr = body

    base64_bytes = datastr.encode()
    bytes = base64.b64decode(base64_bytes)
    results = bytes.decode()

    print()
    print(f"{pokeMonName1} vs. {pokeMonName2}")
    time.sleep(1)
    print("Battle Starts!")
    print()

    lines = results.split("\n")

    i = 3
    while i < len(lines):
      time.sleep(0.5)
      if i == len(lines) - 1:
        print()
        print(f"RESULT: {lines[i]}")
      else:
        print(lines[i])
      i += 1
      
    return

  except Exception as e:
    logging.error("download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def createPokemon(baseurl):

  print("Enter name >")
  name = input()
  print("Enter first type >")
  type1 = input()
  print("Enter second type >")
  type2 = input()
  print("Enter Total CP point>")
  total = input()
  print("Enter HP >")
  hp = input()
  print("Enter Attack >")
  attack = input()
  print("Enter Defense >")
  defense = input()
  print("Enter Special Attack >")
  sp_atk = input()
  print("Enter Special Defsnse >")
  sp_def = input()
  print("Enter Speed >")
  speed = input()
  print("Enter Generation >")
  generation = input()

  try:

    data = {
      "Name": name,
      "Type1": type1,
      "Type2": type2,
      "Total": total,
      "HP": hp,
      "Attack": attack,
      "Defense": defense,
      "Sp_Atk": sp_atk,
      "Sp_Def": sp_def,
      "Speed": speed,
      "Generation": generation
    }

    #
    # call the web service:
    #
    api = '/upload'
    url = baseurl + api

    res = requests.post(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # success, extract jobid:
    #
    body = res.json()

    jobid = body

    # print("ind =", jobid)
    pokelist = [["null", name, type1, type2, total, hp, attack, defense, sp_atk, sp_def, speed, generation, False]]
    print()
    print("You have successfully created the following pokemon:")
    format_pokemon(pokelist)
    return

  except Exception as e:
    logging.error("upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def get_pokemon_by_name(baseurl):
  
  print("Enter a pokemon name >")
  pokemonName = input()

  try:
    #
    # call the web service:
    #
    api = '/pokemon'
    url = baseurl + api + '/' + pokemonName
    # print(url)
    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      # print("Failed with status code:", res.status_code)
      # print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("No such pokemon...")
      #
      return

    #
    # deserialize and extract results:
    #
    body = res.json()

    print(f"Pokemon ID: {body[0]}")
    print(f"Pokemon Name: {body[1]}")
    print(f"Pokemon First Element: {body[2]}")
    if len(body[3]) > 0:
      print(f"Pokemon Second Element: {body[3]}")
    else:
      print("Pokemon Second Element: None")
    print(f"Overall Combat Power (CP) Score: {body[4]}")
    print(f"HP: {body[5]}")
    print(f"Attack Strength: {body[6]}")
    print(f"Defense Strength: {body[7]}")
    print(f"Special Attack Strength: {body[8]}")
    print(f"Special Defense Strength: {body[9]}")
    print(f"Speed: {body[10]}")
    print(f"Generation: {body[11]}")
    if body[12] > 0:
      print("Legendary: True")
    else:
      print("Legendary: False")

    print()
    time.sleep(1)
    print("Do you want to download a picture of it? (y/n)")

    choice = input()
    if choice == "y":
      getPicture(baseurl, pokemonName)
    
    # print(body)
    return

  except Exception as e:
    logging.error("getPokemon() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def get_top10pokemon_by_attributes(baseurl):

  print("Selet the attribute >")
  print("1 -> Total")
  print("2 -> HP")
  print("3 -> Attack")
  print("4 -> Defense")
  print("5 -> Special Attack")
  print("6 -> Special Defense")
  print("7 -> Speed")
  cmd = input()
  if int(cmd) < 1 or int(cmd) > 7:
    print("Invalid option...")
    return
  attributeList = [
    "Total", "HP", "Attack", "Defense", "Sp_Atk", "Sp_Def", "Speed"
  ]
  try:
    #
    # call the web service:
    #
    attribute = attributeList[int(cmd) - 1]
    api = '/top10'
    url = baseurl + api + '/' + attribute
    # print(url)
    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract results:
    #
    body = res.json()
    print()
    for index, pokemon in enumerate(body):
      print(f"{index + 1}: {pokemon[1]}")
    return

  except Exception as e:
    logging.error("getPokemon() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def format_pokemon(pokelist):
  headers = ["Index", "Name", "Element 1", "Element 2", "CP", "HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed", "Generation", "Legendary"]

  column_widths = [len(header) for header in headers]
  for row in pokelist:
      for i, item in enumerate(row):
          column_widths[i] = max(column_widths[i], len(str(item)))

  divider = '+' + '+'.join('-' * (width + 2) for width in column_widths) + '+'

  header_row = '|' + '|'.join(f' {header.ljust(column_widths[i])} ' for i, header in enumerate(headers)) + '|'

  table = divider + '\n' + header_row + '\n' + divider + '\n'

  for row in pokelist:
      formatted_row = '|' + '|'.join(f' {str(item).ljust(column_widths[i])} ' for i, item in enumerate(row)) + '|'
      table += formatted_row + '\n' + divider + '\n'

  print(table)

def getAllPokemon(baseurl):
  pageIndex = 0
  try:
    #
    # call the web service:
    #

    api = '/getPokemon'
    url = baseurl + api + '/' + str(pageIndex)

    res = requests.get(url)
    print(res)
    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract results:
    #
    print("Please ensure that the window is wide enough to fit the table")
    body = res.json()
    format_pokemon(body)
    print()
    print("Enter 'y' to coninue>")
    cmd = input()
    while cmd == 'y':
      pageIndex = pageIndex + 1
      url = baseurl + api + '/' + str(pageIndex)
      res = requests.get(url)
      if res.status_code != 200:
        # failed:
        print("Failed with status code:", res.status_code)
        print("url: " + url)
        if res.status_code == 400:
          # we'll have an error message
          body = res.json()
          print("Error message:", body)
        #
        return
      body = res.json()
      if not body or len(body) == 0:
        print("This is the last page")
        break
      format_pokemon(body)
      print()
      print("Enter 'y' to coninue>")
      cmd = input()

    return

  except Exception as e:
    logging.error("getAllPokemon() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def start_battle(pokemon1, pokemon2):
  try:
    #
    # call the web service:
    #
    pokemonName = f"{pokemon1}:{pokemon2}"

    api = '/battle'
    url = baseurl + api + '/' + pokemonName
    # print(url)
    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract results:
    #
    body = res.json()

    # print(body)
    return

  except Exception as e:
    logging.error("getPokemon() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def getPicture(baseurl, pokemonName="None"):

  if pokemonName == "None":
    print("Enter the pokemon name >")
    pokemonName = input()

  try:
    #
    # call the web service:
    #

    api = '/getPicture'
    url = baseurl + api + '/' + pokemonName
    # print(url)
    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract results:
    #

    base64_image = res.json()

    image_data = base64.b64decode(base64_image)
    filename = pokemonName + ".jpg"
    with open(filename, "wb") as file:
      file.write(image_data)
    image = img.imread(filename)
    plt.imshow(image)
    print()
    print("Image downloaded. Go check it out!")
    plt.show()
    return

  except Exception as e:
    logging.error("getPokemon() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return



############################################################
# main
#
try:
  print('** Welcome to Pokedex, a Tool for Pokemon Searching, Creating, and Battling! **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = 'pokemon-client-config.ini'

  # print("Config file to use for this session?")
  # print("Press ENTER to use default, or")
  # print("enter config file name>")
  # s = input()

  # if s == "":  # use default
  #   pass  # already set
  # else:
  #   config_file = s

  #
  # does config file exist?
  #
  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  #
  # setup base URL to web service:
  #
  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config.ini file with your gateway endpoint")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      get_pokemon_by_name(baseurl)
    elif cmd == 2:
      get_top10pokemon_by_attributes(baseurl)
    elif cmd == 3:
      createPokemon(baseurl)
    elif cmd == 4:
      getAllPokemon(baseurl)
    elif cmd == 5:
      getPicture(baseurl)
    elif cmd == 6:
      battle(baseurl)
    else:
      print("** Unknown command. Please try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** Pokedex exited. Hope you had fun! **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)