
from pykinect2 import PyKinectV2
from pygame.sysfont import SysFont
from pygame import font
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from pygame.locals import *


import ctypes
import _ctypes
import pygame
import sys
import math 

#referened microsoft documentation for display of skeleton bodies 
# colors for drawing different bodies 
SKELETON_COLORS = [pygame.color.THECOLORS["red"], 
                  pygame.color.THECOLORS["blue"], 
                  pygame.color.THECOLORS["green"], 
                  pygame.color.THECOLORS["orange"], 
                  pygame.color.THECOLORS["purple"], 
                  pygame.color.THECOLORS["yellow"], 
                  pygame.color.THECOLORS["violet"]]

class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()
        pygame.mixer.music.load("edx-all-i-know-official-music-video-youtubemp3free.org.wav")
        pygame.mixer.music.play(-1)

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self.screen_width = 1200
        self.screen_height = 650
        self._screen = pygame.display.set_mode((1200,650), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

        pygame.display.set_caption("Kinect for Windows v2 Body Game")

        # Loop until the user clicks the close button.
        self._done = False

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Kinect runtime object, we want only color and body frames 
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data 
        self._bodies = None
        
        #image of wall
        self.wall = ""

        #dimensions of the wall
        self.wall_size_width = 50
        self.wall_size_height = 50

        #wall starts moving 
        self.wall_coming = ""

        #tuple to keep track of the joints (to be tested against the wall)
        self.joints_tuple = (0, 0)

        #boolean to see if you passed that level
        self.passed_wall = True

        #IS IT ON STARTING SCREEN??
        self.starting_screen_bool = True

        #DIFFICULTY LEVEL
        self.difficulty_level = ""

        #tuple of right hand coordinates
        self.right_hand_coordinates = (0,0)

        #list of wall for easy mode
        self.easy_walls_list = ["wallone.png", 
                                "walltwo.png", 
                                "wallthree.png", 
                                "wallfour.png", 
                                "wallfive.png"]

        #list of walls for two player hard mode
        self.two_player_hard_walls_list = ["twoplayerhardwallone.png", 
                                           "twoplayerhardwalltwo.png", 
                                           "twoplayerhardwallthree.png",
                                           "twoplayerhardwallfour.png",
                                           "twoplayerhardwallfive.png"]

        #EASY MODE- keeps track of which wall appears
        self.wall_count = 0

        #depth 
        self.depth_of_body = 0

        #dictionary to keep track of high score
        self.dict_high_score = {"easy": float("-inf"), "medium": float("-inf"), "hard": float("-inf"), 
                                "twoplayereasy": float("-inf"), "twoplayermedium": float("-inf"), 
                                "twoplayerhard": float("-inf"), "customizedwalls": float("-inf")}

        #score
        self.score = 0

        #the z coordinate of the right hand
        self.right_hand_z_coordinate = 0

        #checks if there is one body
        self.one_body = False

        #timer for flashing lines!
        self.timer = 0 

        #whether is it on the ending screen
        self.ending_screen_bool = False

        #variable for temp storage of difficulty level
        self.temp_difficulty_level = ""

        #list for creating walls
        self.new_list = []
       
        #count for wall created by users
        self.num_wall_creation = 0

        #sees if the user is creating a wall
        self.user_wall_creation = False 

        #creation walls list 
        self.customized_walls_list = []

        #list for drawing customized wall
        self.new_list_two = []

        self.hard_walls_list = ["hardone.png", 
                                "hardtwo.png", 
                                "hardthree.png", 
                                "hardfour.png", 
                                "hardfive.png"]

        self.two_player_easy_walls_list = ["twoplayerhardwalltwo.png", 
                                           "hardfour.png"]
         
###############################################################################################################
    #DRAWS SKELETON OF BODIES
###############################################################################################################
    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):


        joint0State = joints[joint0].TrackingState;
        joint1State = joints[joint1].TrackingState;

        # both joints are not tracked
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked): 
            self.one_body = False
            return

        # both joints are not *really* tracked
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            self.one_body = False
            return

        self.one_body = True 

        # ok, at least one is good 
        start = (jointPoints[joint0].x, jointPoints[joint0].y) 

        if joint0 == PyKinectV2.JointType_SpineMid:
            zcoordinate = joints[getattr(PyKinectV2, "JointType_SpineMid")].Position
            self.depth_of_body = zcoordinate.z

        elif joint0 == PyKinectV2.JointType_HandRight:     
            self.right_hand_coordinates = (jointPoints[joint0].x, jointPoints[joint0].y)           
        end = (jointPoints[joint1].x, jointPoints[joint1].y)

        
        
        try:
            pygame.draw.line(self._frame_surface, color, start, end, 8)
            

            x = int(start[0])
            y = int(start[1])

            if(x > 10 and x < self.screen_width-10):
                if y > 10 and y < self.screen_height-10:
                    self.joints_tuple = (x, y)

        except: # need to catch it due to possible invalid positions (with inf)
            pass

    def draw_body(self, joints, jointPoints, color):
        # Torso
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft);
    
        # Right Arm    

        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight);

        # Left Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft);

        # Right Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight);

        # Left Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft);
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft);

#############################################################################################################
    #DEPTH TESTER
#############################################################################################################
    
    def depth_position(self):
    
      if self.one_body == True:
         
          if self.depth_of_body < 1.7:
            myfont = pygame.font.SysFont(None, 100)
            text = "Move Back"
            ren = myfont.render(text,0, (71, 94, 255) )
            self._frame_surface.blit(ren, (450, 950))
            if self.starting_screen_bool == False and self.ending_screen_bool == False:
                self.score -= 5 
          elif self.depth_of_body > 2.2:
            myfont = pygame.font.SysFont(None, 100)
            text = "Move Forward"
            ren = myfont.render(text,0, (71, 94, 255) )
            self._frame_surface.blit(ren, (450, 950)) 
            if self.starting_screen_bool == False and self.ending_screen_bool == False:
                self.score -= 5
                  


##############################################################################################################
    #WALL CREATION
##############################################################################################################
    def create_wall(self, jointPoints, body):
        if self.user_wall_creation == True:

            myfont = pygame.font.SysFont(None, 100)
            text = "Fist = None"
            ren = myfont.render(text,0, (255,128,0) )
            self._frame_surface.blit(ren, (10, 300))

            myfont = pygame.font.SysFont(None, 100)
            text = "Open = Draw" 
            ren = myfont.render(text,0, (255,128,0) )
            self._frame_surface.blit(ren, (10, 400))

            myfont = pygame.font.SysFont(None, 100)
            text = "Lasso = Save" 
            ren = myfont.render(text,0, (255,128,0) )
            self._frame_surface.blit(ren, (10,500))


            pygame.draw.rect(self._frame_surface, (255, 237, 61), (450, 0,1000, 1000), 10)

            image = pygame.Surface([1000, 1000],pygame.SRCALPHA, 32)
            image = image.convert_alpha()
            self._frame_surface.blit(image, (450, 20))
    
            
            if body.hand_right_state == HandState_Open:
                xcoordhand, ycoordhand = jointPoints[PyKinectV2.JointType_HandRight].x, jointPoints[PyKinectV2.JointType_HandRight].y
                self.new_list.append((int(xcoordhand)-450, int(ycoordhand)-20))
                self.new_list_two.append((int(xcoordhand), int(ycoordhand)))
            for i in range(len(self.new_list)-1):
                pygame.draw.line(image, (255, 237, 61), self.new_list[i], self.new_list[i+1], 100)
                pygame.draw.line(self._frame_surface, (255, 237, 61), self.new_list_two[i], self.new_list_two[i+1], 100)

            if body.hand_right_state == HandState_Lasso:
                self.num_wall_creation += 1
               # image = pygame.transform.scale(image, (650, 650))
                pygame.image.save(image, "wallcreation%d.png" % self.num_wall_creation)
                self.customized_walls_list.append("wallcreation%d.png" % self.num_wall_creation)
                #File is saved
                self.new_list = []
                self.new_list_two = []
                self.user_wall_creation = False
                self.starting_screen_bool = True

                

############################################################################################################
       #CUSTOMIZED WALLS LEVEL
############################################################################################################
    def play_customized_walls(self):
        if self.difficulty_level == "customizedwalls":
            myfont = pygame.font.SysFont(None, 100)
            text = "Score = %d" % self.score
            ren = myfont.render(text,0, (0, 255, 43) )
            self._frame_surface.blit(ren, (1480, 20))

            #passed the level 
            if self.wall_count == len(self.customized_walls_list):
                self.ending_screen_bool = True
                self.starting_screen_bool = False
                self.difficulty_level = ""
                self.temp_difficulty_level = "customizedwalls"
                return

            #blits the wall
            self.wall = pygame.image.load(self.customized_walls_list[self.wall_count])
            if self.wall_coming == "customizedwalls":
                self.wall_size_height +=3
                self.wall_size_width +=3
                wallTest = pygame.transform.scale(self.wall, (self.wall_size_height, self.wall_size_width))
                self._frame_surface.blit(wallTest, (960-self.wall_size_height//2, 
                                                                540-self.wall_size_height//2))
                

                #if the wall is a certain size, then check if the player is touching it
                if self.wall_size_height > 800 and self.wall_size_height < 900:
                    r = int(self._frame_surface.get_at(self.joints_tuple)[0])
                    g = int(self._frame_surface.get_at(self.joints_tuple)[1])
                    b = int(self._frame_surface.get_at(self.joints_tuple)[2])
                    if r > 250and r < 260:
                        if g > 230 and g < 243:
                            if b > 55 and b < 65:
                                #if the player is touching it then they did not pass
                                #the wall, so return out of the function
                                self.score -= 100
                                
                                
                #if the wall size reaches 1000+ then a new wall appears
                if self.wall_size_height >1000:
                    self.score += 1000
                    self.wall_count += 1
                    self.wall_size_height = 50
                    self.wall_size_width = 50


       

    
        
    
       
     
##############################################################################################################
    #lines that go around the wall when it is showtime
##############################################################################################################
    def showtime_lines(self):
        if self.timer % 10 == 0:
            pygame.draw.line(self._frame_surface, (250, 255, 77), (180, 100), (350,250), 30)
            pygame.draw.line(self._frame_surface, (250, 255, 77), (self.screen_width+720-180,100), (self.screen_width+720-350,250), 30)

            pygame.draw.line(self._frame_surface, (250, 255, 77), (150, 400), (325,450), 30)
            pygame.draw.line(self._frame_surface, (250, 255, 77), (self.screen_width+720-150,400), (self.screen_width+720-325,450), 30)

            pygame.draw.line(self._frame_surface, (250, 255, 77), (150, 700), (325,650), 30)
            pygame.draw.line(self._frame_surface, (250, 255, 77), (self.screen_width+720-150,700), (self.screen_width+720-325,650), 30)

            pygame.draw.line(self._frame_surface, (250, 255, 77), (180, 1000), (350,850), 30)
            pygame.draw.line(self._frame_surface, (250, 255, 77), (self.screen_width+720-180,1000), (self.screen_width+720-350,850), 30)


##############################################################################################################
    #STARTING SCREEN!! LEGOOOOO
##############################################################################################################

    def starting_screen(self, right_hand_joints):
        if self.starting_screen_bool == True:
            myfont = pygame.font.SysFont(None, 100)
            text = "Use Right Hand To Select Options"
            ren = myfont.render(text,0, (127, 6, 119) )
            self._frame_surface.blit(ren, (400, 300))

            #easy starting rectangle 
            pygame.draw.rect(self._frame_surface, (250,255,64), Rect((20, 30), (400, 200)))
            my_font = pygame.font.SysFont(None, 80)
            text = "EASY"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (140,100))
            start_screen_rect = pygame.Rect(20, 30, 400, 200)
            if start_screen_rect.collidepoint(self.right_hand_coordinates[0], self.right_hand_coordinates[1]):
                self.starting_screen_bool = False
                self.difficulty_level = "easy"
                self.wall_coming = "easy"
                self.ending_screen_bool = False

             #easy starting rectangle 
            pygame.draw.rect(self._frame_surface, (250,255,64), Rect((20, 400), (400, 200)))
            my_font = pygame.font.SysFont(None, 80)
            text = "HARD"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (140,475))
            start_screen_rect = pygame.Rect(20, 400, 400, 200)
            if start_screen_rect.collidepoint(self.right_hand_coordinates[0], self.right_hand_coordinates[1]):
                self.starting_screen_bool = False
                self.difficulty_level = "hard"
                self.wall_coming = "hard"
                self.ending_screen_bool = False
             
            
            #two player starting rectangle 
            pygame.draw.rect(self._frame_surface, (250,255,64), Rect((1500, 400), (400, 200)))
            my_font = pygame.font.SysFont(None, 80)
            text = "TWO"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (1620,440))
            start_screen_rect = pygame.Rect(1500, 400, 400, 200)
            my_font = pygame.font.SysFont(None, 80)
            text = "PLAYER HARD"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (1500,520))

            if start_screen_rect.collidepoint(self.right_hand_coordinates[0], self.right_hand_coordinates[1]):
                self.starting_screen_bool = False
                self.difficulty_level = "twoplayerhard"
                self.wall_coming = "twoplayerhard"

            #two player easy starting rectangle 
            pygame.draw.rect(self._frame_surface, (250,255,64), Rect((1500, 20), (400, 200)))
            my_font = pygame.font.SysFont(None, 80)
            text = "TWO"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (1620,50))
            start_screen_rect = pygame.Rect(1505, 20, 400, 200)
            my_font = pygame.font.SysFont(None, 80)
            text = "PLAYER EASY"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (1500,130))

            if start_screen_rect.collidepoint(self.right_hand_coordinates[0], self.right_hand_coordinates[1]):
                self.starting_screen_bool = False
                self.difficulty_level = "twoplayereasy"
                self.wall_coming = "twoplayereasy"


            #customize wall
            pygame.draw.rect(self._frame_surface, (250, 255, 64), Rect((20, 800), (400, 200)))
            my_font = pygame.font.SysFont(None, 80)
            text = "CUSTOMIZE"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (50,830))
            my_font = pygame.font.SysFont(None, 80)
            text = "WALL"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (120,910))
            customize_wall_rect = pygame.Rect(20, 800, 400, 200)
            if customize_wall_rect.collidepoint(self.right_hand_coordinates[0], self.right_hand_coordinates[1]):
         
                self.starting_screen_bool = False
                self.difficulty_level = ""
                self.wall_coming = ""
                self.user_wall_creation = True

            #play customized walls 
            pygame.draw.rect(self._frame_surface, (250, 255, 64), Rect((1500, 800), (400, 200)))
            my_font = pygame.font.SysFont(None, 80)
            text = "PLAY"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (1620,800))
            my_font = pygame.font.SysFont(None, 80)
            text = "CUSTOMIZED"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (1520,870))
            my_font = pygame.font.SysFont(None, 80)
            text = "WALLS"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (1600,940))
            start_screen_rect = pygame.Rect(1500, 800, 400, 200)
            if start_screen_rect.collidepoint(self.right_hand_coordinates[0], self.right_hand_coordinates[1]):
                self.starting_screen_bool = False
                self.difficulty_level = "customizedwalls"
                self.wall_coming = "customizedwalls"
                self.user_wall_creation = False

          
                

###############################################################################################################
    #ENDING SCREEN
###############################################################################################################

    def play_ending_screen(self):
        if self.ending_screen_bool == True:
            self.wall_count = 0
            
            #replay
            pygame.draw.rect(self._frame_surface, (250,255,64), Rect((750, 30), (400, 200)))
            my_font = pygame.font.SysFont(None, 80)
            text = "REPLAY"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (770,80))
            replay_rect = pygame.Rect(750, 30, 400, 200)
            if replay_rect.collidepoint(self.right_hand_coordinates[0], self.right_hand_coordinates[1]):
                self.starting_screen_bool = False
                self.difficulty_level = self.temp_difficulty_level
                self.wall_coming = self.temp_difficulty_level
                self.score = 0
                self.ending_screen_bool = False

            #go back to home
            pygame.draw.rect(self._frame_surface, (250,255,64), Rect((750, 800), (400, 200)))
            my_font = pygame.font.SysFont(None, 80)
            text = "HOME PAGE"
            renfont = my_font.render(text,0, (0, 60, 129) )
            self._frame_surface.blit(renfont, (770,880))
            home_page_rect = pygame.Rect(750, 400, 400, 200)
            if home_page_rect.collidepoint(self.right_hand_coordinates[0], self.right_hand_coordinates[1]):
                self.starting_screen_bool = True
                self.difficulty_level = ""
                self.wall_coming = ""
                self.score = 0
                self.ending_screen_bool = False
            
        #somehow, the player exited the inner function, either because
        #they passed all the walls or because they failed
            #prints that they failed
            if self.score < 0:
                myfont = pygame.font.SysFont(None, 80)
                text = "you failed"
                ren = myfont.render(text,0, (0, 255, 43) )
                self._frame_surface.blit(ren, (500, 10))

            #if they passed the level, then the highest score 
            # and the score that they got should print out
            if self.score > self.dict_high_score[self.temp_difficulty_level]:
                self.dict_high_score[self.temp_difficulty_level] = self.score
                myfont = pygame.font.SysFont(None, 80)
                text = "You got the new high score"
                ren = myfont.render(text,0, (0, 255, 43) )
                self._frame_surface.blit(ren, (500, 10))
            myfont = pygame.font.SysFont(None, 150)
            text = "High score = %d" % self.dict_high_score[self.temp_difficulty_level]
            ren = myfont.render(text,0, (51,0,51) )
            self._frame_surface.blit(ren, (500, 400))
            myfont = pygame.font.SysFont(None, 150)
            text = "Your score= %d" % self.score
            ren = myfont.render(text,0, (51,0,51) )
            self._frame_surface.blit(ren, (500, 600))
        
            
################################################################################################################
    #EASY MODE
################################################################################################################
    def play_easy_mode(self):

        if self.difficulty_level == "easy":
       
            myfont = pygame.font.SysFont(None, 100)
            text = "Score = %d" % self.score
            ren = myfont.render(text,0, (0, 255, 43) )
            self._frame_surface.blit(ren, (1480, 20))

            #passed the level 
            if self.wall_count == len(self.easy_walls_list):
                self.ending_screen_bool = True
                self.starting_screen_bool = False
                self.difficulty_level = ""
                self.temp_difficulty_level = "easy"
                return

            #blits the wall
            self.wall = pygame.image.load(self.easy_walls_list[self.wall_count])
            if self.wall_coming == "easy":
                self.wall_size_height +=3
                self.wall_size_width +=3
                wallTest = pygame.transform.scale(self.wall, (self.wall_size_height, self.wall_size_width))
                self._frame_surface.blit(wallTest, (960-self.wall_size_height//2, 
                                                                540-self.wall_size_height//2))
                

                #if the wall is a certain size, then check if the player is touching it
                if self.wall_size_height > 800 and self.wall_size_height < 900:
                    r = int(self._frame_surface.get_at(self.joints_tuple)[0])
                    g = int(self._frame_surface.get_at(self.joints_tuple)[1])
                    b = int(self._frame_surface.get_at(self.joints_tuple)[2])
                    if r > 230 and r < 243:
                        if g > 20 and g < 33:
                            if b > 30 and b < 42:
                                #if the player is touching it then they did not pass
                                #the wall, so return out of the function
                                self.score -= 100
                                
                                
                #if the wall size reaches 1000+ then a new wall appears
                if self.wall_size_height >1000:
                    self.score += 1000
                    self.wall_count += 1
                    self.wall_size_height = 50
                    self.wall_size_width = 50
                    
   

#######################################################################################################
    #HARD MODE
#######################################################################################################
    def play_hard_mode(self):
        if self.difficulty_level == "hard":
         
            myfont = pygame.font.SysFont(None, 100)
            text = "Score = %d" % self.score
            ren = myfont.render(text,0, (0, 255, 43) )
            self._frame_surface.blit(ren, (1480, 20))

            #passed the level 
            if self.wall_count == len(self.easy_walls_list):
                self.ending_screen_bool = True
                self.starting_screen_bool = False
                self.difficulty_level = ""
                self.temp_difficulty_level = "hard"
                return

            #blits the wall
            self.wall = pygame.image.load(self.hard_walls_list[self.wall_count])
            if self.wall_coming == "hard":
                self.wall_size_height +=3
                self.wall_size_width +=3
                wallTest = pygame.transform.scale(self.wall, (self.wall_size_height, self.wall_size_width))
                self._frame_surface.blit(wallTest, (960-self.wall_size_height//2, 
                                                                540-self.wall_size_height//2))
                
                print(self._frame_surface.get_at(self.joints_tuple))

                

                #if the wall is a certain size, then check if the player is touching it
                if self.wall_size_height > 800 and self.wall_size_height < 900:
                    r = int(self._frame_surface.get_at(self.joints_tuple)[0])
                    g = int(self._frame_surface.get_at(self.joints_tuple)[1])
                    b = int(self._frame_surface.get_at(self.joints_tuple)[2])
                    if r > 25 and r < 40:
                        if g > 170 and g < 185:
                            if b > 70 and b < 85:
                                #if the player is touching it then they did not pass
                                #the wall, so return out of the function
                                self.score -= 100
                                
                                
                #if the wall size reaches 1000+ then a new wall appears
                if self.wall_size_height >1000:
                    self.score += 1000
                    self.wall_count += 1
                    self.wall_size_height = 50
                    self.wall_size_width = 50

#######################################################################################################
    #TWO PLAYER EASY MODE
#######################################################################################################
    def play_two_player_easy_mode(self):
        if self.difficulty_level == "twoplayereasy":
        
            myfont = pygame.font.SysFont(None, 100)
            text = "Score = %d" % self.score
            ren = myfont.render(text,0, (0, 255, 43) )
            self._frame_surface.blit(ren, (1480, 20))

            #passed the level 
            if self.wall_count == len(self.easy_walls_list):
                self.ending_screen_bool = True
                self.starting_screen_bool = False
                self.difficulty_level = ""
                self.temp_difficulty_level = "twoplayereasy"
                return

            #blits the wall
            self.wall = pygame.image.load(self.two_player_easy_walls_list[self.wall_count])
            if self.wall_coming == "twoplayereasy":
                self.wall_size_height +=3
                self.wall_size_width +=3
                wallTest = pygame.transform.scale(self.wall, (self.wall_size_height, self.wall_size_width))
                self._frame_surface.blit(wallTest, (960-self.wall_size_height//2, 
                                                                540-self.wall_size_height//2))
                

                #if the wall is a certain size, then check if the player is touching it
                if self.wall_size_height > 800 and self.wall_size_height < 900:
                    r = int(self._frame_surface.get_at(self.joints_tuple)[0])
                    g = int(self._frame_surface.get_at(self.joints_tuple)[1])
                    b = int(self._frame_surface.get_at(self.joints_tuple)[2])
                    if r > 230 and r < 243:
                        if g > 20 and g < 33:
                            if b > 30 and b < 42:
                                #if the player is touching it then they did not pass
                                #the wall, so return out of the function
                                self.score -= 100
                 #if the wall is a certain size, then check if the player is touching it
                if self.wall_size_height > 800 and self.wall_size_height < 900:
                    r = int(self._frame_surface.get_at(self.joints_tuple)[0])
                    g = int(self._frame_surface.get_at(self.joints_tuple)[1])
                    b = int(self._frame_surface.get_at(self.joints_tuple)[2])
                    if r > 25 and r < 40:
                        if g > 170 and g < 185:
                            if b > 70 and b < 85:
                                #if the player is touching it then they did not pass
                                #the wall, so return out of the function
                                self.score -= 100
                                
                #if the wall size reaches 1000+ then a new wall appears
                if self.wall_size_height >1000:
                    self.score += 1000
                    self.wall_count += 1
                    self.wall_size_height = 50
                    self.wall_size_width = 50
        

            

#######################################################################################################
    #TWO PLAYER HARD MODE
#######################################################################################################
    def play_two_player_hard_mode(self):
        if self.difficulty_level == "twoplayerhard":
            myfont = pygame.font.SysFont(None, 100)
            text = "Score = %d" % self.score
            ren = myfont.render(text,0, (0, 255, 43) )
            self._frame_surface.blit(ren, (1480, 20))

            #passed the level 
            if self.wall_count == len(self.easy_walls_list):
                self.ending_screen_bool = True
                self.starting_screen_bool = False
                self.difficulty_level = ""
                self.temp_difficulty_level = "twoplayerhard"
                return

            #blits the wall
            self.wall = pygame.image.load(self.two_player_hard_walls_list[self.wall_count])
            if self.wall_coming == "twoplayerhard":
                self.wall_size_height +=3
                self.wall_size_width +=3
                wallTest = pygame.transform.scale(self.wall, (self.wall_size_height, self.wall_size_width))
                self._frame_surface.blit(wallTest, (960-self.wall_size_height//2, 
                                                                540-self.wall_size_height//2))
                

                #if the wall is a certain size, then check if the player is touching it
                if self.wall_size_height > 800 and self.wall_size_height < 900:
                    r = int(self._frame_surface.get_at(self.joints_tuple)[0])
                    g = int(self._frame_surface.get_at(self.joints_tuple)[1])
                    b = int(self._frame_surface.get_at(self.joints_tuple)[2])
                    if r > 230 and r < 243:
                        if g > 20 and g < 33:
                            if b > 30 and b < 42:
                                #if the player is touching it then they did not pass
                                #the wall, so return out of the function
                                self.score -= 100
                                
                                
                #if the wall size reaches 1000+ then a new wall appears
                if self.wall_size_height >1000:
                    self.score += 1000
                    self.wall_count += 1
                    self.wall_size_height = 50
                    self.wall_size_width = 50

##########################################################################################################
    #run the game
##########################################################################################################
    def keyPressed(self, key):
        name = pygame.key.name(key)
        if str(name) == "e":
            self.difficulty_level = "easy"
            self.wall_coming = "easy"
            self.play_easy_mode()
            self.starting_screen_bool = False
        else:
            self.wall_coming = "twoplayerhard"
            self.difficulty_level = "twoplayerhard"
            self.play_two_player_hard_mode()

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def run(self):
        # -------- Main Program Loop -----------
        while not self._done:
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self._done = True # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE: # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'], 
                                               pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE, 32)
                elif event.type == pygame.KEYDOWN:
                    self.keyPressed(event.key)
                    
            # --- Game logic should go here

            #displaying some sort of text

           
            # --- Getting frames and drawing  
            # --- Woohoo! We've got a color frame! Let's fill out back buffer surface with frame's data 
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None

            # --- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame(): 
                self._bodies = self._kinect.get_last_body_frame()

            # --- draw skeletons to _frame_surface
            if self._bodies is not None: 
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    
                    if not body.is_tracked: 
                        continue 
                    joints = body.joints
                    # convert joint coordinates to color space 
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                    self.draw_body(joints, joint_points, SKELETON_COLORS[i])
                    self.create_wall(joint_points, body)
                   
                
            #runs the diffenrent modes
            self.depth_position()
            
            self.play_ending_screen()

            self.depth_position()

            self.starting_screen(self.joints_tuple)

            self.play_easy_mode()

            self.play_two_player_hard_mode()

            self.play_customized_walls()

            self.play_two_player_easy_mode()

            self.play_hard_mode()
            
            self.timer += 1

            #tells the player to get ready 
            if self.wall_size_height > 700 and self.wall_size_height < 800:
                myfont = pygame.font.SysFont(None, 100)
                text = "GET READY"
                ren = myfont.render(text,0, (255, 0, 127) )
                self._frame_surface.blit(ren, (10, 10))
        
            #ITS SHOWTIME!! now the player must be within the wall boundaries
            if self.wall_size_height > 800 and self.wall_size_width > 800:
                if self.wall_size_height <900 and self.wall_size_width < 900:
                    myfont = pygame.font.SysFont(None, 80)
                    text = "BODY MUST NOT TOUCH WALL!!"
                    ren = myfont.render(text,0, (255, 0, 127) )
                    self._frame_surface.blit(ren, (10, 10))
                    self.showtime_lines()
           

           # myfont = pygame.font.SysFont(None, 80)
            #text = "PLEASEE WORKKK UGHHHHHHH"
            #ren = myfont.render(text, 0, (250,0,0))
            #self._frame_surface.blit(ren, (500, 500))

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height));
            self._screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None
            pygame.display.update() 

            # --- Go ahead and update the screen with what we've drawn.
            #pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        # pygame.mixer.music.stop()
        pygame.quit()


__main__ = "Kinect v2 Body Game"
game = BodyGameRuntime();
game.run();