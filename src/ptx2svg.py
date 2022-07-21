from math import *
from lxml import etree

id_num = 0

newline = '\n'
ctm = [[1, 0, 0], [0, 1, 0]]
ctmstack = [ctm]

def dot(u, v):
    return sum([u[i] * v[i] for i in range(len(u))])

def transform(p):
    p = list(p).copy()
    p.append(1)
    return [dot(ctm[i], p) for i in range(2)]

def write(output, tag, attr):
    args = ' '.join([k + r'="' + attr.get(k) + r'"' for k in attr.keys()])
    output.write(r'<' + tag + ' ' + args + r'/>'+newline)

def writeln(s):
    output.write(s + newline)

def concat(m, n):
    c = [[n[0][0], n[1][0], 0],
         [n[0][1], n[1][1], 0],
         [n[0][2], n[1][2], 1]]
    return [[dot(m[0], c[0]), dot(m[0], c[1]), dot(m[0], c[2])],
            [dot(m[1], c[0]), dot(m[1], c[1]), dot(m[1], c[2])]]

def translate(x, y):
    global ctm
    m = [[1,0,x], [0,1,y]]
    ctm = concat(ctm, m)

def scale(x, y):
    global ctm
    s = [[x, 0, 0], [0, y, 0]]
    ctm = concat(ctm, s)

def rotate(theta):
    global ctm
    c = cos(theta)
    s = sin(theta)
    m = [[c, -s, 0], [s, c, 0]]
    ctm = concat(ctm, m)

def add_id(element):
    global id_num
    element.set('id', 'element-'+str(id_num))
    id_num += 1

def beginfigure(element):
    global root, bbox
    width = eval(element.get('width'))
    height = eval(element.get('height'))
    margin = element.get('margin', '0')
    margin = eval(margin)
    w = width + 2*margin
    h = height + 2*margin
    root = etree.Element("svg", width=str(w), height=str(h))
    add_id(root)

    translate(0, height+2*margin)
    scale(1,-1)
    translate(margin, margin)
    bbox = [margin, margin, width+margin, height+margin]
    ctmstack = [[ctm, bbox]]

def endfigure(filename):
    et = etree.ElementTree(root)
    et.write(filename, pretty_print=True)

def drawline(p0, p1, color, width=1, user_coords=True):
    if user_coords:
        p0 = transform(p0)
        p1 = transform(p1)
    x1, y1 = p0
    x2, y2 = p1
    writeln(r'<line x1="'+str(x1)+r'" y1="'+str(y1)+ 
                    r'" x2="'+str(x2)+r'" y2="'+str(y2)+r'" stroke="'+
            color+'" stroke-width="'+str(width)+'" />')

def mk_line(p0, p1, user_coords = True):
    line = etree.Element('line')
    add_id(line)
    if user_coords:
        p0 = transform(p0)
        p1 = transform(p1)
    line.set('x1', str(p0[0]))
    line.set('y1', str(p0[1]))
    line.set('x2', str(p1[0]))
    line.set('y2', str(p1[1]))
    return line

def add_attr(element, attr):
    for k, v in attr.items():
        element.set(k, str(v))

class Coordinates():
    def __init__(self, element):
        self.element = element
    
    def draw(self):
        global bbox
        element = self.element
        mbox = eval(element.get("mbox"))
        pbox = bbox
        
        translate(pbox[0], pbox[1])
        scale( (pbox[2]-pbox[0])/float(mbox[2]-mbox[0]),
               (pbox[3]-pbox[1])/float(mbox[3]-mbox[1]) )
        translate(-mbox[0], -mbox[1])
        bbox = mbox

class Line():    
    def __init__(self, element):
        self.p1 = eval(element.get('p1'))
        self.p2 = eval(element.get('p2'))
        self.color = element.get('color', r'#000')
        self.width = element.get('width', r'1')

    def draw(self):
        line = mk_line(self.p1, self.p2)
        line.set('stroke', self.color)
        line.set('stroke-width', self.width)
        root.append(line)

class Grid():
    def __init__(self, element):
        self.rx = eval(element.get('rx'))
        self.ry = eval(element.get('ry'))
        self.color = element.get('color', '#999')
        self.width = element.get('width', 1)

    def draw(self):
        rx = self.rx
        ry = self.ry
        x = rx[0]
        grid = etree.Element('g')
        add_id(grid)
        attr = {'stroke': self.color,
                'stroke-width': self.width}
        add_attr(grid, attr)
        root.append(grid)
        while x <= rx[2]:
            grid.append(mk_line((x,bbox[1]), (x,bbox[3])))
            x += rx[1]
            
        y = ry[0]
        while y <= ry[2]:
            grid.append(mk_line((bbox[0], y), (bbox[2], y)))
            y += ry[1]

class Axes():
    def __init__(self, element):
        self.hticks = element.get('hticks', "none")
        self.vticks = element.get('vticks', "none")
        self.color =  element.get('color', r'#000')

    def draw(self):
        axes = etree.Element('g')
        add_id(axes)
        root.append(axes)
        axes.set('stroke', self.color)
        axes.append(mk_line((bbox[0], 0), (bbox[2], 0)))
        axes.append(mk_line((0, bbox[1]), (0, bbox[3])))

        hticks = etree.Element('g')
        add_id(hticks)
        axes.append(hticks)
        vticks = etree.Element('g')
        add_id(vticks)
        axes.append(vticks)

        if self.hticks != "none":
            self.hticks = eval(self.hticks)
            x = self.hticks[0]
            while x <= self.hticks[2]:
                p = transform((x,0))
                hticks.append(mk_line((p[0], p[1]+3),(p[0], p[1]-3),
                                      user_coords=False))

                x += self.hticks[1]
        if self.vticks != "none":
            self.vticks = eval(self.vticks)
            y = self.vticks[0]
            while y <= self.vticks[2]:
                p = transform((0, y))
                vticks.append(mk_line((p[0]-3, p[1]),(p[0]+3, p[1]),
                                      user_coords=False))
                y += self.vticks[1]
                
class Graph():
    def __init__(self, element):
        self.element = element

    def draw(self):
        element = self.element
        f = lambda x: eval(element.get('function'))
        domain = eval(element.get('domain', '[bbox[0], bbox[2]]'))
        N = int(element.get('N', 100))
        color = element.get('color', r'#000')
        width = element.get('width', '1')

        dx = (domain[1] - domain[0])/N
        x = domain[0]
        cmd = 'M '
        p = transform((x,f(x)))
        cmd += str(p[0]) + " " + str(p[1])
        while x <= domain[1]:
            p = transform((x,f(x)))
            cmd += ' L ' + str(p[0]) + ' ' + str(p[1])
            x += dx

        path = etree.Element('path')
        add_id(path)
        root.append(path)
        path.set('d', cmd)
        path.set('fill', 'none')
        path.set('stroke', color)
        path.set('stroke-width', width)

class Circle():
    def __init__(self, element):
        self.element = element

    def draw(self):
        element = self.element
        center = eval(element.get('center'))
        radius = eval(element.get('r', '0'))
        right = [center[0] + radius, center[1]]
        top   = [center[0], center[1] + radius]
        center, right, top = map(transform, [center, right, top])

        circle = etree.Element('ellipse')
        add_id(circle)
        root.append(circle)
        circle.set('cx', str(center[0]))
        circle.set('cy', str(center[1]))
        circle.set('rx', str(right[0]-center[0]))
        circle.set('ry', str(top[1]-center[1]))
        circle.set('stroke', element.get('color', 'none'))
        circle.set('fill', element.get('fill', "none"))
        circle.set('stroke-width', element.get('width', '1'))
    
class Label():
    def __init__(self, element):
        self.element = element

    def draw(self):
        pass
    
class Point():
    def __init__(self, element):
        self.element = element
    def draw(self):
        element = self.element
        p = transform(eval(self.element.get('p')))
        width = self.element.get('width', '1')
        fill = self.element.get('fill', r'#000')
        stroke = self.element.get('stroke', r'#000')
        attr = {'stroke-width': element.get('width', '1'),
                'fill': element.get('fill', r'#000'),
                'stroke': element.get('stroke', r'#000'),
                'cx':str(p[0]),
                'cy':str(p[1]),
                'r':element.get('size')
        }
        circle = etree.Element('circle')
        add_id(circle)
        root.append(circle)
        add_attr(circle, attr)
