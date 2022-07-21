from lxml import etree
from ptx2svg import *
import sys

fig_count = 0

tags = {
    'coordinates': Coordinates,
    'line': Line,
    'grid': Grid,
    'axes': Axes,
    'point': Point,
    'graph': Graph,
    'circle': Circle
}

try:
    filename = sys.argv[1]
except:
    print('Usage python parsesvg.py xml_filename')
    sys.exit()

tree = etree.parse(filename)

def parse(figure, count):
    global filename
    beginfigure(figure)

    for element in figure:
        graphic = tags.get(element.tag, None)
        if graphic != None:
            graphic(element).draw()

    index = filename.rfind('/')
    if index >= 0:
        print(index, filename)
        filename = filename[index+1:]
    output = 'output/' + filename[:-4] + '.html'
    print(output)
    endfigure(output)

for element in tree.iter(tag='svgfigure'):
    parse(element, fig_count)
        
        

    
