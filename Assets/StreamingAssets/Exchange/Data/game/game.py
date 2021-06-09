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
    '../img/dive.png',
    '../img/Smiley.png',
    '../img/player',
    '../img/passage_pointer'])



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

    return False

# determines whether there is a collision with a snack when the player is at a given position
def consumed_snack(new_x,new_y):
    
    global snack_map
    global progessCircuit
    #check if new coordinates are within blocked pixel
    eps = 0.2
    global snacks
    
    # the progess is automatically adjusted by theta dependening on the current level,
    # for every new level you need more snakcs in order to fully rotate to get a 1
    theta = numpy.pi/current_level
    

    for xx,yy in [(eps,eps),(eps,1-eps),(1-eps,eps),(1-eps,1-eps)]:
            tempSnack = snack_map[(int)(new_y+yy)][(int)(new_x+xx)] 
            if tempSnack != -1:
                snacks[tempSnack].sprite.size = 0

                # essentially a progress bar, which manipulates a qubit by theta, theta in that sense is
                # dependent on the level count. SO in order to flip a |0> state into a |1> state you need to rotaet the z bases by pi
                # if you want to do this in a dynamic number of steps, e.g. by a number of snacks to eat.
                # we construct theta as pi/number of snacks avalible and apply a rotation each time  a snack is consumed
                # In the same sense we could also construct a negative theta that rotates  back if you did something that was not intended 
                progessCircuit.rx(theta, 0)
                return True

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



snacks = []

class Snack():

    def __init__(self,id):
        self.x,self.y = get_character_start_position()
        self.sprite = qisge.Sprite(19, self.x, self.y, z=0.9,size = 0.5) 
        self.id = id
        snack_map[self.y][self.x] = id

#number of snacks are level progress
def draw_snacks():

    #draw snacks based on current_level
    global current_level
    global snacks
    global progessCircuit

    #reset progress both qubits will be in state |0>
    progessCircuit = QuantumCircuit(2,2)

    #empty snacks
    snacks = []
    for id in range (0,current_level):
        snacks.append(Snack(id))
        
            
            





#The initial idea was to use the creation of specific characters to get proportional characters but this procedural
# generation can of course be applied to levels and the continous generation of new puzzles and workloads which get more complicated
# once you progress in levels 
class Passage():
    
    # Get changes position at the border of the screen
    # either horizontally alligned or 
    # Maybe include QuantumGraph and manipulate the second qubit and if they allign
    # we can pass through
    def __init__(self,img):

        self.x, self.y, self.orientation, self.side = self.replace_passage()
        
        # Red Square
        self.sprite = qisge.Sprite(11, self.x, self.y, size = 1) 
        self.pointer = qisge.Sprite(21, self.x, self.y, size = 1) 
        self.z = 1
        self.sprite.z = 0.9
        self.pointer.z = 1.0

        global qubits
        
        
        d = math.sqrt(pos_x**2+pos_y**2)
        f = [ s*math.cos(s*d*math.pi/100) for s in seed]
        tx = (f[0]*pos_x + f[1]*pos_y)*math.pi/2
        ty = (f[2]*pos_x - f[3]*pos_y)*math.pi/2
        tz = (f[4]*(pos_x+pos_y) + f[5]*(pos_x-pos_y))*math.pi/2


        global qubits
        qubits.qc.rx(tx,1)
        qubits.qc.rz(tz,1)
        qubits.qc.ry(ty,1)

        

        qubits.update_tomography()

        passage_properties = qubits.get_bloch(1)
        self.height = passage_properties.get('X')**2
        self.width = passage_properties.get('Z')**2
        self.rotation = passage_properties.get('Y')**2

        #0.5 only for display reasons, the calculations are done using the expectation values
        self.pointer.size = self.height + 0.4
        self.pointer.height = self.height + 0.4
        self.pointer.width = self.width + 0.4
        self.pointer.angle = self.rotation*360





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
            if ( (x == 0 and y == 0) or (x == 27 and y == 15) or (x == 27 and y == 0) or (x == 0 and y == 15)):
                valid_pos = False
            else:
                valid_pos = True

        #TODO Check if gate is even accessible

    	
        collision_map[y][x] = False
        return x, y, orientation, side

    def draw_on_map(self):
        self.sprite.z = 0.9




##################################################


class Player():
    def __init__(self,img,speed=0.25):

        self.x, self.y = get_character_start_position()
        self.sprite = qisge.Sprite(img, self.x, self.y,size = 1) 
        self.z = 0
        self.sprite.z = 1
        self.speed = speed 
        self.direction = 1

        

        self.height, self.rotation, self.width,  = self.generate_character()
        
        self.sprite.size = self.height + 0.5
        self.sprite.height= self.height + 0.5
        self.sprite.width = self.width + 0.5
        self.sprite.angle = self.rotation*360

    def reposition_character(self):
        self.x, self.y = get_character_start_position()

    #### Use Quantum Graph and get_bloch to get the expectation values of <X>, <Y>, <Z>
    # Depending on that distribution we create our character sprite Z for HEIGHT, X for WIDTH and  Y for COLOR       
    # Since <X>^2 + <Y>^2 + <Z>^2 <= 1, the character properties are somewhat"proportional" 
    def generate_character(self):
                                                                                                                                                                                                                                                                

        
        d = math.sqrt(self.x**2+self.y**2)
        f = [ s*math.cos(s*d*math.pi/100) for s in seed]
        tx = (f[0]*self.x + f[1]*self.y)*math.pi/7
        ty = (f[2]*self.x - f[3]*self.y)*math.pi/7
        tz = (f[4]*(self.x+self.y) + f[5]*(self.x-self.y))*math.pi/7


        global qubits
        qubits.qc.rx(tx,0)
        qubits.qc.rz(tz,0)
        qubits.qc.ry(ty,0)

        qubits.qc.cz(1,0)


        qubits.update_tomography()

        character_properties = qubits.get_bloch(0)

        return character_properties.get('X')**2,character_properties.get('Y')**2,character_properties.get('Z')**2


    def update_character_proportions(self,gate):

        global  qubits

        #adjust theta the higher the level is
        #to make it more difficult to actually rotate something
        theta = (2*numpy.pi)/8
        if gate == 'X':
            #qubits.qc.x(0)
            qubits.qc.rx(theta,0)
        if gate == 'Z':
            #qubits.qc.z(0)
            qubits.qc.rz(theta,0)
        if gate == 'Y':
            #qubits.qc.z(0)
            qubits.qc.ry(theta,0)
        if gate == 'H':
            qubits.qc.h(0)


        qubits.update_tomography()
        character_properties = qubits.get_bloch(0)

        self.height = character_properties.get('X') **2 
        self.width = character_properties.get('Z') **2 
        self.rotation = character_properties.get('Y') **2

        #Automatically adjusts the size of the character/sprite 
        self.sprite.size = self.height +0.5
        self.sprite.height = self.height +0.5
        self.sprite.width = self.width +0.5
        self.sprite.angle = self.rotation*360


        



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
            img = 20
        if self.direction == 0:
            img = 20

        new_x = self.x+self.speed*pos_x
        new_y = self.y+self.speed*pos_y

        if not collide(new_x,self.y):
            self.x = new_x
        if not collide(self.x,new_y):
            self.y = new_y

        consumed_snack(new_x, new_y)

         ## If character left screen check level conditions reload or next level
        if ( new_x >= Lx-1 or new_x <= 0 or new_y >= Ly-1 or new_y <= 0):
            check_level_condition()


        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.z = 1            

        

        self.sprite.image_id = img
        


    def draw_on_map(self):
        self.sprite.z = 1
        
        
        


seed  = [0.5*random.random() for _ in range(6)]
pos_x = 0
pos_y = 0
sprite = {}

collision_map =  [[False for _ in range(28)] for _ in range(16)] 
snack_map =  [[-1 for _ in range(28)] for _ in range(16)] 


def draw_map():

    
    global collision_map    

    # Draw complete map
    for dx in range(28):
        for dy in range(16):
            
            # artificially place border around screen edge
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
    player = Player(20)

    global passage
    passage = Passage(11)



def initialize_game():

    loading.x = 6
    loading.y = 8
    loading.set_font_color( (0,0,255) )
    loading.set_background_color( (255,255,255) )

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

    #Start with player health = 10
    global health
    health = 10

    global current_level
    current_level = 0
    next_level()


   



def next_level():

    global health
    global current_level
    current_level+=1

    draw_map()
    initialize_objects()
    draw_snacks()
    

    levelScreen = qisge.Text('Level: '+str(current_level) +"\n\nHealth: "+ str(health), 16,2,font_size=22)
    levelScreen.x = 6
    levelScreen.y = 8
    levelScreen.set_background_color( (168,50,82) )

    qisge.update()

    time.sleep(1)
    levelScreen.width = 0
    qisge.update()


def check_level_condition():
    
    #if player state is correct
    #proceed to next level
    if ( valid_state() ):
        next_level()
    
    #else restart level and lose health
    else:
        restart_level()



#Compare the states between character and passage. If alligned within threshold
#return true else false

def valid_state():


    #TODO
    # use CX, CZ or CY in order to toggle  a second qubit to be true 
    # e.g. we can simply use the nature of a quantum bit and use two qbits the first one 
    # is the working one and the second is the state_validation
    # we could now alter the first qbit with operations until it has a expectation value of one
    # to check if the approach was valid and the correct steps have been taken
    # for example we could extend this with using a puzzle game an d finfing clues.
    # each found clue rotates the qubit in a given state. Each round it is checked via cz e.g if everything
    # has been found. This would only flip the second bit (which was prepared in 0 State) if all clues have been found or 
    # number of steps(n) have been taken
    #  each operation than applies pi/n to get the number of steps needed to actally flip the second bit

    # We can always extend this working example to create more levels extend it using a color

    # WIdth is disabled because it has no visual representation and is therefor not needed

    threshold = 0.1
    condition_height =  (passage.height-threshold <= player.height <= passage.height+threshold)
    condition_width = True #(passage.width-threshold <= player.width <= passage.width+threshold)
    condition_rotation =  (passage.rotation-threshold <= player.rotation <= passage.rotation+threshold)

    global progessCircuit
    
    #only flips the second qubit to one if the first qubit is 1
    # The first qubit is only = 1 if every progress has been made
    progessCircuit.cx(0,1)
    progessCircuit.measure(0,0)
    progessCircuit.measure(1,1)
    

    result = simulate(progessCircuit,shots=1,get='memory')[0]
    

    #is only set to '11' if the first qubit is = '_1' that is the case if all snacks have been collected
    # because then the CNOT gate applies a not to the second bit and also turns it to 1 leaving the 
    # 2qubit at '11'
    if ( result == '11' ):
        if ( condition_height and condition_width and condition_rotation ):
            return True

    #To make the game easier we could start by generating the passage first and then rotating 
    # it a few time to generate the player in order to guarantee that the game stays solvable
 
    return False
    


def restart_level():
    # Decrease health
    global health
    health-=1

    global current_level
    current_level-=1
    if ( health <= 0 ):
        game_over()
    else:
        next_level()


def game_over():
    #END GAME

    loading.width = 0

    game_over = qisge.Text('GAME OVER', 16,2,font_size=22)
    game_over.x = 6
    game_over.y = 8
    game_over.set_background_color( (0,0,0) )
    game_over.set_font_color( (255,255,255) )
    qisge.update()
    time.sleep(2)
    restart_timer = 10
    while restart_timer >= 0:
        game_over.text = 'GAME OVER\n\nRestart in: ' + str(restart_timer) + 'sec'
        qisge.update()
        time.sleep(1)
        restart_timer -= 1
    initialize_game()
    

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
        loading.height = 8
        loading.x = 6
        loading.y = 8
        loading.set_font_color( (0,0,255) )

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

    if 12 in input['key_presses']:
        pressed=True
        gate = 'Y'

    

    if pressed:

        player.update(dir_x,dir_y,gate)
        
        if loading_visible:
            loading.text = "Player\nHEIGHT: " + str(player.height)
            loading.text += "\nWIDTH: " + str(player.width)
            loading.text += "\nROTATION: " + str(player.rotation)
            loading.text += "\n\nApplied gate: " + gate
            loading.text += "\nPassage\nHEIGHT: " + str(passage.height)
            loading.text += "\nWIDTH: " + str(passage.width)
            loading.text += "\nROTATION: " + str(passage.rotation)   
            loading.text += "\n\nHealth:  " + str(health) 
                    
        


    ##############
    #
    # Idea: Maybe created 2 qubits in graph, one is the player the other one is 
    # the gate. They should have a relation between them to interact
    #
    ###############
