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

import time
import math
import random

map_height = 28
map_width = 16

Lx,Ly = 28,16 # screen size in tiles
Mx,My = 10,10 # mountain size in screens
P = 0.9 # cutoff between background and foreground rocks


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

# determines whether there is a collision with the map when the player is at a given position
def collide(x,y):
    not_collision = True
        
    return not not_collision

class Player():
    def __init__(self,img,speed=0.25,j=4,j_frames=12):

        self.sprite = qisge.Sprite(img) 
        self.x = 0
        self.y = 0
        self.z = 0
        self.speed = speed
        self.j = j
        self.j_frames = j_frames
        self.impulse = 0
        self.direction = 1

        self.height, self.width, self.color = self.generate_character()


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
            qubits.qc.x(0)
        if gate == 'Z':
            qubits.qc.z(0)
        if gate == 'H':
            qubits.qc.h(0)

        qubits.update_tomography()
        character_properties = qubits.get_bloch(0)

        self.height = character_properties.get('X')
        self.width = character_properties.get('Z')
        self.color = character_properties.get('Y')



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
        


seed  = [0.5*random.random() for _ in range(6)]
pos_x = 0
pos_y = 0
sprite = {}



def initialize_game():
    
    loading.text = "Creating World"
    loading.width = 16
    qisge.update()


    

    # Draw complete map
    for dx in range(28):
        for dy in range(16):
            image_id = get_image_id(pos_x+dx, pos_y+dy)
            sprite[dx,dy] = qisge.Sprite(image_id, x=dx,y=dy)
        


    loading.width = 0
    input = qisge.update()

    loading.text = "Generating Character"
    loading.width = 16
    input = qisge.update()

    # Create a two qubit quantum graph
    #Retrieve character properties, which are generated by the expectation values 
    # of a qubit
    global qubits
    qubits = QuantumGraph(2)



    ## Initialize character and character position
    global player
    player = Player(14)
    player.x = 7
    player.y = 7
    player.z = 1



    loading.width = 0
    qisge.update()





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


    if pressed:

        player.update(dir_x,dir_y,gate)
        
        global loading_visible
        if loading_visible:
            loading.text = "HEIGHT: " + str(player.height)
            loading.text += "\nWIDTH: " + str(player.width)
            loading.text += "\nCOLOR: " + str(player.color)
            loading.text += "\n\nApplied gate: " + gate


    

        # Redraw tiles
        #for dx in range(28):
        #    for dy in range(16):
                #sprite[dx,dy].image_id = get_image_id(pos_x+dx, pos_y+dy)
                #sprite[dx,dy].image_id = sprite[dx,dy].image_id


            
        
        


    ##############
    #
    # Idea: Maybe created 2 qubits in graph, one is the playery the other one is 
    # the gate. They should have a relation between them to interact
    #
    ###############