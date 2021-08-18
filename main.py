import json
import discord
import datetime
import inspect

layerOneID = 111111111111111111
layerTwoID = 222222222222222222
botToken = "tokeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeen"

class BossClass :  

  #Class attuributes
  windowOpens = ""
  windowClose = ""
  canSpawn = False
  scouts = []

  def __init__(self, dictionary={}):
    #constructor from dictionary after import
    if dictionary != {}:
      self.windowOpens = dictionary['windowOpens']
      self.windowClose = dictionary['windowClose']
      self.canSpawn = dictionary['canSpawn']
      self.scouts = dictionary['scouts']
    #default constructor
    else:
      self.windowOpens = ""
      self.windowClose = ""
      self.canSpawn = False
      self.scouts = []

  def addScout(self, name) :
    if name not in self.scouts :
      self.scouts.append(name) 

  def removeScout(self, name) :
    if name in self.scouts :
      self.scouts.remove(name)

class LayerClass :
  #Class attuributes
  kaz = BossClass()
  doom = BossClass()
  lastMsgID = ""
  
  def __init__(self, dictionary={}):
    #constructor from dictionary after import
    if dictionary != {}:
      self.kaz = BossClass(dictionary['kaz'])
      self.doom = BossClass(dictionary['doom'])
      self.lastMsgID = dictionary['lastMsgID']
    #default constructor
    else:
      self.kaz = BossClass()
      self.doom = BossClass()
      self.lastMsgID = ""

#Method to convert the layer/boss classes to dictionaries, can be modified to work with multiple classes  
def props(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
          if name == "doom" or name == "kaz":
            pr[name] = props(value)
          else:
            pr[name] = value
    return pr

#Takes LayerClass array as input, converts to dict array and exports
def exportToJson(layers):
  jsonFileName = "layers.json"
  layersDict = []
  for layer in layers:
    layersDict.append(props(layer))
  jsonObj = json.dumps(layersDict, sort_keys=True, indent=4)
  with open(jsonFileName, "w") as jsonHandle:
    jsonHandle.write(jsonObj)

#Takes filename as input, reads a dict array from json, parses array and converts dict to LayerClass using the constructor
def importFromJson(jsonFileName):
  jsonObj = ""
  with open(jsonFileName, "r") as jsonHandle:
    jsonObj = jsonHandle.read()
  layersDict = json.loads(jsonObj)
  layers=[]
  for layer in layersDict:
    layers.append(LayerClass(layer))
  return layers

bot = discord.Client()
layers = importFromJson('layers.json')

#WoW server time has 2hr timedelta
def get_time_now():
  return datetime.datetime.now() + datetime.timedelta(hours=2)

#when discord bot launches successfully
@bot.event
async def on_ready():
  print('Logged as {0.user}'.format(bot))

  now = get_time_now()
  print(now.strftime("%d/%m/%Y, %H:%M:%S"))

#generating main message, reporting wboss status (scouts, timers)
def main_message(l):
  message = """```diff\nDoom Lord Kazzak\n"""

  if layers[l].kaz.canSpawn == True :
    if len(layers[l].kaz.scouts) > 0 :
      for scout in layers[l].kaz.scouts :
        message += "+ " + scout + '\n'
    else:
      message += '- No kaz scouts.\n'
  else :
    message += 'Window opens: {0}\n'.format(layers[l].kaz.windowOpens)
  message += 'Window closes: {0}\n'.format(layers[l].kaz.windowClose)

  message += '\n\nDoomwalker\n'

  if layers[l].doom.canSpawn == True :
    if len(layers[l].doom.scouts) > 0 :
      for scout in layers[l].doom.scouts :
        message += "+ " + scout + '\n'
    else:
      message += '- No doom scouts.\n'
  else :
    message += 'Window opens: {0}\n'.format(layers[l].doom.windowOpens)
  message += 'Window closes: {0}'.format(layers[l].doom.windowClose)  

  message += """\n```"""
  return message

#resets all timers as if server restarted
def reset(l):
  layers[l].kaz.scouts = []
  layers[l].doom.scouts = []
  now = get_time_now()
  open_time = now + datetime.timedelta(minutes=-1)
  layers[l].kaz.windowOpens = open_time.strftime("%d/%m/%Y, %H:%M:%S")
  layers[l].kaz.windowClose = (now + datetime.timedelta(hours=36)).strftime("%d/%m/%Y, %H:%M:%S")
  layers[l].doom.windowOpens = open_time.strftime("%d/%m/%Y, %H:%M:%S")
  layers[l].doom.windowClose = (now + datetime.timedelta(hours=36)).strftime("%d/%m/%Y, %H:%M:%S")
  layers[l].kaz.canSpawn = False
  layers[l].doom.canSpawn = False
  update_windows_status(l)

#check if something opened
def update_windows_status(l) :
  now = get_time_now()
  if layers[l].kaz.canSpawn == False :
    kazwindow = datetime.datetime.strptime(layers[l].kaz.windowOpens, "%d/%m/%Y, %H:%M:%S")
    if kazwindow < now :
      layers[l].kaz.canSpawn = True

  if layers[l].doom.canSpawn == False :
    doomwindow = datetime.datetime.strptime(layers[l].doom.windowOpens, "%d/%m/%Y, %H:%M:%S")
    if doomwindow < now :
      layers[l].doom.canSpawn = True

#main function for all the commands
@bot.event
async def on_message(msg):

  #filter own messages just in case
  if msg.author == bot.user :
    return
 
  #filter channels
  l = 1 if msg.channel.id == layerOneID else 2 if msg.channel.id == layerTwoID else 0
  if l == 0 : return

  flag = False
  l -= 1
  update_windows_status(l)

  formattedmsg = msg.content.lower()
  
  #!on command
  if msg.content.startswith("!on"):
    if 'kaz' in formattedmsg or 'both' in formattedmsg :
      if msg.author.name not in layers[l].kaz.scouts :
        layers[l].kaz.scouts.append(msg.author.name)
      flag = True
    if 'doom' in formattedmsg or 'both' in formattedmsg :
      if msg.author.name not in layers[l].doom.scouts :
        layers[l].doom.scouts.append(msg.author.name)
      flag = True

  #!off command
  if msg.content.startswith("!off"):
    cleanoff = False
    if msg.content == "!off" :
      cleanoff = True
    if 'kaz' in formattedmsg or 'both' in formattedmsg or cleanoff :
      if msg.author.name in layers[l].kaz.scouts :
        layers[l].kaz.scouts.remove(msg.author.name)
      flag = True
    if 'doom' in formattedmsg or 'both' in formattedmsg or cleanoff :
      if msg.author.name in layers[l].doom.scouts :
        layers[l].doom.scouts.remove(msg.author.name)
      flag = True
  
  #!kill command
  if msg.content.startswith("!kill"):
    now = get_time_now()
    if 'kaz' in formattedmsg or 'both' in formattedmsg :
      layers[l].kaz.scouts.clear()
      layers[l].kaz.canSpawn = False
      layers[l].kaz.windowOpens = (now + datetime.timedelta(hours=60)).strftime("%d/%m/%Y, %H:%M:%S")
      layers[l].kaz.windowClose = (now + datetime.timedelta(hours=120)).strftime("%d/%m/%Y, %H:%M:%S")
      flag = True
    if 'doom' in formattedmsg or 'both' in formattedmsg :
      layers[l].doom.scouts.clear()
      layers[l].doom.canSpawn = False
      layers[l].doom.windowOpens = (now + datetime.timedelta(hours=60)).strftime("%d/%m/%Y, %H:%M:%S")
      layers[l].doom.windowClose = (now + datetime.timedelta(hours=120)).strftime("%d/%m/%Y, %H:%M:%S")
      flag = True

  #!reset command
  if msg.content.startswith('!reset'):
    flag = True
    reset(l)

  #!open command
  if msg.content.startswith('!open'):
    flag = True
    timestr = datetime.datetime.strptime(msg.content.split("!")[2], "%d/%m/%Y, %H:%M:%S")
    if 'kaz' in formattedmsg or 'both' in formattedmsg :
      layers[l].kaz.canSpawn = True
      layers[l].kaz.windowClose = timestr.strftime("%d/%m/%Y, %H:%M:%S")
    if 'doom' in formattedmsg or 'both' in formattedmsg :
      layers[l].doom.canSpawn = True
      layers[l].doom.windowClose = timestr.strftime("%d/%m/%Y, %H:%M:%S")
      
  #if some command was successfull, send message and delete old one
  if flag == True :
    msgID = await msg.channel.send(main_message(l))
    oldMsgID = layers[l].lastMsgID
    layers[l].lastMsgID = msgID.id

    #also JANK write to file
    exportToJson(layers)
    
    if oldMsgID :
      msg = await msg.channel.fetch_message(oldMsgID)
      await msg.delete()

  #!help command
  if msg.content.startswith('!help'):
    message = "```!on <wboss> - set yourself as scout\n"
    message += "!off <wboss> - remove yourself from scouts\n"
    message += "!kill <wboss> - sets <wboss> dead, starts kill window timers\n"
    message += "!reset - use ONLY on server restart, starts 'restart' window timers\n"
    message += "!help - types this message again\n\n"
    message += "<wboss> keywords (so far): kaz, doom, both\n```"
    await msg.channel.send(message)


bot.run(botToken)