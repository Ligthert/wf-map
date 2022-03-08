#!/usr/bin/env python3

# Imports
import os
import postgresql
from PIL import Image, ImageDraw

# Connect to DB
db = postgresql.open("pq://"+os.environ["WF_RENDER_DB_USER"]+":"+os.environ["WF_RENDER_DB_PASSWORD"]+"@192.168.178.74/wf")

q_maxims = db.prepare("select min(x), max(x), min(y), max(y) from systems")
q_systems = db.prepare("SELECT * FROM systems ORDER BY id ASC")
q_system = db.prepare("SELECT * FROM systems WHERE id=$1")
maxims = q_maxims()[0]

factor = 20
factor = 22
#factor = 100

minx = maxims[0]
maxx = maxims[1]
miny = maxims[2]
maxy = maxims[3]

sumx = abs(minx) + maxx
sumy = abs(miny) + maxy

centerx = int(abs(minx)/factor)
centery = int(abs(miny)/factor)

def drawStar(x,y,colour):
  x = relposx(x)
  y = relposy(y)
  draw.rectangle([(x-5, y-5),(x+5,y+5)], colour)

def drawText(x,y,text,colour="black"):
  draw.text( (relposx(x+200),relposy(y+90)), text, fill=colour )

def relpos(x,y):
  relx = int(centerx + (x/factor))
  rely = int(sumy/factor) - int( centery + (y/factor) )
  return relx,rely

def relposx(x):
  return int(centerx + (x/factor))

def relposy(y):
  return int(sumy/factor) - int( centery + (y/factor) )

def drawAnnotations(annotations, colour):
  for annotation in annotations:
    if annotation[0] == "system":
      system = q_system(annotation[1])[0]
      drawStar( system[1], system[2], colour )
      drawText( system[1], system[2], annotation[2], colour )
    if annotation[0] == "coords":
      drawStar( annotation[1], annotation[2], colour )
      drawText( annotation[1], annotation[2], annotation[3], colour )

image = Image.new('RGBA', ( int(sumx/factor), int(sumy/factor) ), (255, 255, 255) )
draw = ImageDraw.Draw(image)

# Fetch systems
systems = q_systems()

# Stuff we need to draw.
# Currently supported:
# system: type, system id, text
# coords: type, x, y, text
#
# Using https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
#
friendly = [
  ("system", 5984, "Amsterdam"),
  ("system", 5304, "Wynnyk" ),
  ("system", 5842, "London" )
  ]
enemy = [ ]
steerpoints = [ ]


# Draw all the nice systems
for system in systems:
  drawStar( system[1], system[2], "black" )


# Draw annontations
drawAnnotations( friendly, "green" )
drawAnnotations( enemy, "red" )
drawAnnotations( steerpoints, "orange" )


# Save the file for now
image.save('test.png')
