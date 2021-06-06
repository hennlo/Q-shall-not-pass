import numpy
import qisge

loading = qisge.Text('Loading Qiskit', 16,2)
loading.x = 6
loading.y = 8
loading.set_font_color( (0,0,255) )
loading_visible = True

qisge.update()

from microqiskit import QuantumCircuit, simulate
from quantumgraph import QuantumGraph

loading.width = 0
qisge.update()

# Measure the time you took to solve the level
import time
import math
import random

map_width = 28
map_height = 16

Lx,Ly = 28,16 # screen size in tiles
Mx,My = 10,10 # mountain size in screens


FPS = 10

## These are mainly used to fill out the map in the current state
images = qisge.ImageList([
    '../img/terrain-water.png',
    '../img/terrain-red-flower.png',
    '../img/terrain-grass.png',
    '../img/terrain-path.png',
    '../img/terrain-grass.png',
    '../img/terrain-purple-flower.png',
    '../img/terrain-tree.png',
    '../img/backrock.png',
    '../img/Square.png',
    '../img/SquareBlack.png',
    '../img/SquareBlue.png',
    '../img/SquareRed.png',
    '../img/fly_r.png',
    '../img/fly_l.png',
    '../img/walk_r.png',
    '../img/walk_l.png',
    '../img/flap_r.png',
    '../img/flap_l.png',
    '../img/dive.png'])


#images = qisge.ImageList([
#    '../img/terrain-water.png',
#    '../img/terrain-red-flower.png',
#    '../img/terrain-grass.png',
#    '../img/terrain-path.png',
#    '../img/terrain-grass.png',
#    '../img/terrain-purple-flower.png',
#    '../img/terrain-tree.png',
#    ])

#terrain_types = len(images)
terrain_types = 7
current_level = 0

# determines whether there is a collision with the map when the player is at a given position
def collide(new_x,new_y):
    
    
    global collision_map
    #check if new coordinates are within blocked pixel
    eps = 0.3
    for xx,yy in [(eps,eps),(eps,1-eps),(1-eps,eps),(1-eps,1-eps)]:
        if collision_map[(int)(new_y+yy)][(int)(new_x+xx)]:
            return True

    #TODO screen border should collide ONLY gate should be passthrough

    return False

# Get valid start position of character, e.g. do not start within tree
# Only works if world is created before character
def get_character_start_position():
    
    valid_pos = False

    while not valid_pos:
        x = random.randint(0,27)
        y = random.randint(0,15) 
        valid_pos = not collide(x,y)
        
    return x,y


class Passage():
    
    # Get changes position at the border of the screen
    # either horizontally alligned or 
    # Maybe include QuantumGraph and manipulate the second qubit and if they allign
    # we can pass through
    def __init__(self,img):

        self.x, self.y, self.orientation, self.side = self.replace_passage()
        
        # Red Square
        self.sprite = qisge.Sprite(11, self.x, self.y, size = 1) 
        self.z = 1
        self.sprite.z = 0.9
        


    def replace_passage(self):
    
        valid_pos = False

        while not valid_pos:
             
            # 1 = vertically , 0 horizontally
            orientation = random.randint(0,2)
        
            # 0 = left/bottom , 1 = right/top 
            side = random.randint(0,2)
            
            if orientation == 1:
                # If side is 0 (left)
                if side == 0:
                    x = 0
                else:
                    x = 27
                y = random.randint(0,14)
            else:
                x = random.randint(0,26)
                # If side is 0 (bottom) otherwise twaop of screen
                if side == 0:
                    y = 0
                else:
                    y = 15

            ## check valid_pos if length is not out of range instead of collide
            #valid_pos = not collide(x,y)
            valid_pos = True

        #TODO Check if gate is even accessible

    	
        collision_map[y][x] = False
        return x, y, orientation, side

    def draw_on_map(self):
        self.sprite.z = 0.9




##################################################


class Player():
    def __init__(self,img,speed=0.25,health=10):

        self.x, self.y = get_character_start_position()
        self.sprite = qisge.Sprite(img, self.x, self.y,size = 0.5) 
        self.z = 0
        self.sprite.z = 1
        self.speed = speed
        self.direction = 1

        self.health = health

        

        self.height, self.width, self.color = self.generate_character()


    def reposition_character(self):
        self.x, self.y = get_character_start_position()

    #### Use Quantum Graph and get_bloch to get the expectation values of <X>, <Y>, <Z>
    # Depending on that distribution we create our character sprite Z for HEIGHT, X for WIDTH and  Y for COLOR       
    # Since <X>^2, <Y>^2, <Z>^2 <= 1, the character properties are somewhat"proportional" 
    def generate_character(self):
                                                                                                                                                                                                                                                                

    
        f = [ s+math.cos(s*math.pi/100) for s in seed ]
        tx = (f[0] + f[1] )*math.pi/7
        ty = (f[2] - f[3] )*math.pi/7
        tz = (f[4] + f[5] )*math.pi/7

        theta = math.pi/math.sqrt(2)

        global qubits
        qubits.qc.rx(tx,0)
        qubits.qc.rz(tz,0)
        qubits.qc.ry(ty,0)

        qubits.update_tomography()

        character_properties = qubits.get_bloch(0)

        return character_properties.get('X'),character_properties.get('Y'),character_properties.get('Z')


    def update_character_proportions(self,gate):

        global  qubits

        if gate == 'X':
            #qubits.qc.x(0)
            qubits.qc.rx(numpy.pi/4,0)
        if gate == 'Z':
            #qubits.qc.z(0)
            qubits.qc.rz(numpy.pi/4,0)
        if gate == 'H':
            qubits.qc.h(0)

        qubits.update_tomography()
        character_properties = qubits.get_bloch(0)

        self.height = character_properties.get('X') **2
        self.width = character_properties.get('Z') **2
        self.color = character_properties.get('Y') **2

        #Automatically adjusts the size of the character/sprite 
        self.sprite.height = self.height
        self.sprite.width = self.width
        #self.sprite.angle = self.color*360

       
        



    def update(self,pos_x=0,pos_y=0,gate=''):
        
        #Update player qubit respectiviely the expectation values which leads to new proportions 
        if gate != '':
            self.update_character_proportions(gate)

        #right direction
        if (pos_x > 0):
           self.direction = 1
        if (pos_x < 0):
            self.direction = 0
        

        if self.direction == 1:
            img = 14
        if self.direction == 0:
            img = 15

        new_x = self.x+self.speed*pos_x
        new_y = self.y+self.speed*pos_y

        if not collide(new_x,self.y):
            self.x = new_x
        if not collide(self.x,new_y):
            self.y = new_y

        self.sprite.x = self.x%Lx
        self.sprite.y = self.y%Ly
        self.sprite.z = 1

        self.sprite.image_id = img

    def draw_on_map(self):
        self.sprite.z = 1
        
        
        


seed  = [0.5*random.random() for _ in range(6)]
pos_x = 0
pos_y = 0
sprite = {}

collision_map =  [[False for _ in range(28)] for _ in range(16)] 


def draw_map():

    
    global collision_map    

    # Draw complete map
    for dx in range(28):
        for dy in range(16):
            
            # artificially place border around screenedge
            if ( dx == 0 or dx == 27 or dy == 0 or dy == 15 ):
                #backrock
                image_id = 7
                collision_map[dy][dx] = True
                #sprite[dx,dy] = qisge.Sprite(image_id, x=dx,y=dy,z=0.7)
                
            else:
                image_id = get_image_id(pos_x+dx, pos_y+dy)
                if ( image_id == 6 ):
                # collision object
                    collision_map[dy][dx] = True
                else:
                    collision_map[dy][dx] = False
            sprite[dx,dy] = qisge.Sprite(image_id, x=dx,y=dy,z=0)

    


def initialize_objects():
    # Create a two qubit quantum graph
    #Retrieve character properties, which are generated by the expectation values 
    # of a qubit
    global qubits
    qubits = QuantumGraph(2)


    ## Initialize character and character position
    global player
    player = Player(14)

    global passage
    passage = Passage(11)



def initialize_game():

    loading.text = "Creating World"
    loading.width = 16
    qisge.update()
    
    #draw_map()
    
    loading.width = 0
    qisge.update()

    
    loading.text = "Generating Character"
    loading.width = 16
    qisge.update()

    #initialize_objects()
    

    loading.width = 0
    
    qisge.update()
    next_level()



def next_level():

    global current_level
    current_level+=1

    draw_map()
    initialize_objects()

    levelScreen = qisge.Text('Level: '+str(current_level), 16,2,font_size=22)
    levelScreen.x = 6
    levelScreen.y = 8
    levelScreen.set_background_color( (168,50,82) )

    qisge.update()

    time.sleep(1)
    levelScreen.width = 0
    qisge.update()


def check_level_condition():
    if ( dx == 0 or dx == 27 or dy == 0 or dy == 15 ):
        print()

    

def restart_level():
    # Decrease health
    player.health-=1

    global current_level
    current_level-=1
    next_level()



def get_image_id(x,y):
    qc = QuantumCircuit(1)


    d = math.sqrt(x**2+y**2)
    f = [ s*math.cos(s*d*math.pi/100) for s in seed]
    tx = (f[0]*x + f[1]*y)*math.pi/7
    ty = (f[2]*x - f[3]*y)*math.pi/7
    tz = (f[4]*(x+y) + f[5]*(x-y))*math.pi/7

    qc.rx(tx,0)
    qc.rz(tz,0)
    qc.ry(ty,0)

    if x==y:
        qc.h(0)

    ket = simulate(qc,get='statevector')
    p = ket[0][0]**2 + ket[0][1]**2

    image_id = int( round(p*(terrain_types-1)) )

    return image_id


def toggle_textbox():
    global loading_visible
    if loading.width == 0:
        loading.width = 6
        loading.height = 5
        loading_visible = True
    else:
        loading.width = 0
        loading_visible = False
    


def next_frame(input):
        
    global pos_x,pos_y
    pressed = False
    gate = ''
    dir_x = 0
    dir_y = 0
    if 0 in input['key_presses']:
        pos_y += 1
        dir_y += 1
        pressed=True
        
    if 1 in input['key_presses']:
        pos_x += 1
        dir_x += 1
        pressed=True
        
    if 2 in input['key_presses']:
        pos_y -= 1
        dir_y -= 1
        pressed=True
        

    if 3 in input['key_presses']:
        pos_x -= 1
        dir_x -= 1
        pressed=True

    if 4 in input['key_presses']:
        toggle_textbox()
        pressed=True



    ##Rebuilds map
    if 8 in input['key_presses']:
        #initialize_game()
        restart_level()
        pressed=True

    if 9 in input['key_presses']:
        pressed=True
        gate = 'X'

    if 10 in input['key_presses']:
        pressed=True
        gate = 'Z'

    if 11 in input['key_presses']:
        pressed=True
        gate = 'H'

    

    if pressed:

        player.update(dir_x,dir_y,gate)
        
        global loading_visible
        if loading_visible:
            loading.text = "HEIGHT: " + str(player.height)
            loading.text += "\nWIDTH: " + str(player.width)
            loading.text += "\nCOLOR: " + str(player.color)
            loading.text += "\n\nApplied gate: " + gate
            loading.text += "\nPlayer:  " + str(player.x) + " " + str(player.y)
            loading.text += "\nPassage  " + str(passage.x) + " " + str(passage.y)

    
    
        # Redraw tiles
        #for dx in range(28):
        #    for dy in range(16):
                #sprite[dx,dy].image_id = get_image_id(pos_x+dx, pos_y+dy)
                #sprite[dx,dy].image_id = sprite[dx,dy].image_id


            
        
        


    ##############
    #
    # Idea: Maybe created 2 qubits in graph, one is the player the other one is 
    # the gate. They should have a relation between them to interact
    #
    ###############