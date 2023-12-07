#
# Client-side python app for benford app, which is calling
# a set of lambda functions in AWS through API Gateway.
# The overall purpose of the app is to process a PDF and
# see if the numeric values in the PDF adhere to Benford's
# law.
#
# Authors:
#   Prof. Joe Hummel
#   Northwestern University
#   CS 310, Project 03
#

import requests
import jsons

import uuid
import pathlib
import logging
import sys
import os
import base64

from configparser import ConfigParser


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
  print(">> Enter a command:")
  print("   0 => end")
  print("   1 => users")
  print("   2 => jobs")
  print("   3 => upload")
  print("   4 => download")
  print("   5 => reset")
  print("   6 => getPokeMonByName")
  print("   7 => getTop10PokeMonsByAttributes")
  print("   8 => battle")
  print("   9 => create new pokemon")
  print("   10 => get all pokemon")
  cmd = input()

  if cmd == "":
    cmd = -1
  elif not cmd.isnumeric():
    cmd = -1
  else:
    cmd = int(cmd)

  return cmd


############################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api

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
    # deserialize and extract users:
    #
    body = res.json()

    #
    # let's map each row into a User object:
    #
    users = []
    for row in body:
      user = User(row)
      users.append(user)
    #
    # Now we can think OOP:
    #
    if len(users) == 0:
      print("no users...")
      return

    for user in users:
      print(user.userid)
      print(" ", user.username)
      print(" ", user.pwdhash)
    #
    return

  except Exception as e:
    logging.error("users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# jobs
#
def jobs(baseurl):
  """
  Prints out all the jobs in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/jobs'
    url = baseurl + api

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
    # deserialize and extract jobs:
    #
    body = res.json()
    #
    # let's map each row into an Job object:
    #
    jobs = []
    for row in body:
      job = Job(row)
      jobs.append(job)
    #
    # Now we can think OOP:
    #
    if len(jobs) == 0:
      print("no jobs...")
      return

    for job in jobs:
      print(job.jobid)
      print(" ", job.userid)
      print(" ", job.status)
      print(" ", job.originaldatafile)
      print(" ", job.datafilekey)
      print(" ", job.resultsfilekey)
    #
    return

  except Exception as e:
    logging.error("jobs() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# upload
#
def upload(baseurl):
  """
  Prompts the user for a local filename and user id, 
  and uploads that asset (PDF) to S3 for processing. 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  print("Enter PDF filename>")
  local_filename = input()

  if not pathlib.Path(local_filename).is_file():
    print("PDF file '", local_filename, "' does not exist...")
    return

  print("Enter user id>")
  userid = input()

  try:
    #
    # build the data packet:
    #
    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()

    #
    # now encode the pdf as base64. Note b64encode returns
    # a bytes object, not a string. So then we have to convert
    # (decode) the bytes -> string, and then we can serialize
    # the string as JSON for upload to server:
    #
    data = base64.b64encode(bytes)
    datastr = data.decode()

    data = {"filename": local_filename, "data": datastr}

    #
    # call the web service:
    #
    api = '/upload'
    url = baseurl + api + "/" + userid

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

    print("PDF uploaded, job id =", jobid)
    return

  except Exception as e:
    logging.error("upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# download
#
def download(baseurl):
  """
  Prompts the user for the job id, and downloads
  that asset (PDF).

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  print("Enter job id>")
  jobid = input()

  try:
    #
    # call the web service:
    #
    api = '/download'
    url = baseurl + api + '/' + jobid
    print(url)
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

    datastr = body

    base64_bytes = datastr.encode()
    bytes = base64.b64decode(base64_bytes)
    results = bytes.decode()

    print(results)
    return

  except Exception as e:
    logging.error("download() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
def createPokemon(baseurl):
  """
  Prompts the user for a local filename and user id, 
  and uploads that asset (PDF) to S3 for processing. 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  print("Enter name>")
  name = input()
  print("Enter Type1>")
  type1 = input()
  print("Enter Type2>")
  type2 = input()
  print("Enter Total>")
  total = input()
  print("Enter HP>")
  hp = input()
  print("Enter Attack>")
  attack = input()
  print("Enter Defense>")
  defense = input()
  print("Enter Sp_Atk>")
  sp_atk = input()
  print("Enter Sp_Def>")
  sp_def  = input()
  print("Enter Speed>")
  speed = input()
  print("Enter Generation>")
  generation = input()


  

  try:
   


    data = {"Name": name,
            "Type1": type1,
            "Type2": type2,
           "Total":total,
           "HP":hp,
           "Attack":attack,
           "Defense":defense,
           "Sp_Atk":sp_atk,
           "Sp_Def":sp_def,
           "Speed":speed,
           "Generation":generation
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

    print("ind =", jobid)
    return

  except Exception as e:
    logging.error("upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def get_pokemon_by_name(baseurl):
  """
  Prompts the user for the job id, and downloads
  that asset (PDF).

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  print("Enter pokemon name>")
  pokemonName = input()

  try:
    #
    # call the web service:
    #
    api = '/pokemon'
    url = baseurl + api + '/' + pokemonName
    print(url)
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


    print(body)
    return

  except Exception as e:
    logging.error("getPokemon() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
def get_top10pokemon_by_attributes(baseurl):
  """
  Prompts the user for the job id, and downloads
  that asset (PDF).

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  print("Selet attribute you want to get>")
  print("1 -> Total")
  print("2 -> HP")
  print("3 -> Attack")
  print("4 -> Defense")
  print("5 -> Sp_Atk")
  print("6 -> Sp_Def")
  print("7 -> Speed")
  cmd = input()
  attributeList = ["Total","HP","Attack","Defense","Sp_Atk","Sp_Def","Speed"]
  try:
    #
    # call the web service:
    #
    attribute  = attributeList[int(cmd)-1]
    api = '/top10'
    url = baseurl + api + '/' + attribute
    print(url)
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


    print(body)
    return

  except Exception as e:
    logging.error("getPokemon() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
def getAllPokemon(baseurl):
  """
  Prompts the user for the job id, and downloads
  that asset (PDF).

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

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
    body = res.json()
    print(body)
    print("Enter 'y' to coninue>")
    cmd = input()
    while cmd =='y':
      pageIndex = pageIndex+1
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
      print(body)
      print("Enter 'y' to coninue>")
      cmd = input()

    
    return

  except Exception as e:
    logging.error("getAllPokemon() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
def battle(baseurl):
  """
  Prompts the user for the job id, and downloads
  that asset (PDF).

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  print("Enter the first pokemon name>")

  pokemon1 = input()
  print("Enter the second pokemon name>")
  pokemon2 = input()

  try:
    #
    # call the web service:
    #
    pokemonName = f"{pokemon1}:{pokemon2}"
    
    api = '/battle'
    url = baseurl + api + '/' + pokemonName
    print(url)
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


    print(body)
    return

  except Exception as e:
    logging.error("getPokemon() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
############################################################
#
# reset
#
def reset(baseurl):
  """
  Resets the database back to initial state.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/reset'
    url = baseurl + api

    res = requests.delete(url)

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
    # deserialize and print message
    #
    body = res.json()

    msg = body

    print(msg)
    return

  except Exception as e:
    logging.error("reset() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
# main
#
try:
  print('** Welcome to BenfordApp **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = 'pokemon-client-config.ini'

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    config_file = s

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
      users(baseurl)
    elif cmd == 2:
      jobs(baseurl)
    elif cmd == 3:
      upload(baseurl)
    elif cmd == 4:
      download(baseurl)
    elif cmd == 5:
      reset(baseurl)
    elif cmd == 6:
      get_pokemon_by_name(baseurl)
    elif cmd == 7:
      get_top10pokemon_by_attributes(baseurl)
    elif cmd == 8:
      battle(baseurl)
    elif cmd == 9:
      createPokemon(baseurl)
    elif cmd == 10:
      getAllPokemon(baseurl)
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
