import pygame
import sys
import random
import asyncio
from PIL import Image
GREEN = (0, 128, 0)
YELLOW = (255, 155, 0)
BOARD_SIZE=(5,4)
GRID_SIZE=(155,210)
CARD_SIZE=(145,200)
HEAD_SIZE=(52,210)
FULL_CARDS=BOARD_SIZE[0]*BOARD_SIZE[1]
READ_CARDS=FULL_CARDS-3
SUKIMA=5
BAR_W=100
SIZE = (GRID_SIZE[0]*BOARD_SIZE[0],GRID_SIZE[1]*BOARD_SIZE[1])
FPS=30
SECTION_TIME=10 #sec
SECTION_TIME_SELECT=30 #sec
SECTION_TIME_RESULT=20 #sec
MOVE_TIME=0.1 #SEC
MOVE_FRAME=int(MOVE_TIME*FPS)
CPUAREA_RATE=1.5
CPUAREA_NUM=FULL_CARDS//2
BANDWIDTH=7
INVISIBLE_SIZE=(CARD_SIZE[0]-BANDWIDTH*2,CARD_SIZE[1]-BANDWIDTH*2)
INVISIBLE_TIME=2 #sec, completely invisible
FONT_SIZE_RESULT=74
STARTBTN_POS=[GRID_SIZE[0]*BOARD_SIZE[0]+BAR_W//2, GRID_SIZE[1]*BOARD_SIZE[1]-BAR_W]
STARTBTN_SIZE=[80, 60]
SLIDER_MIN_VALUE = 600# スライダー設定
SLIDER_MAX_VALUE = 1500# スライダー設定
SLIDER_STEP = 100# スライダー設定
SLIDER_WIDTH = 300
SLIDER_HEIGHT = 10
SLIDER_POS = (int(GRID_SIZE[0]*1), int(GRID_SIZE[1]*3)+50)  # スライダーのバーの左上座標
KNOB_RADIUS = 10

#colors=["あお","ぴんく","きー","みどり","おれんじ"]
#colors_kanji=["青札","桃札","黄札","緑札","橙札"]
#colors_eng=["BLUE","PINK","YELLOW","GREEN","ORANGE"]
#colors_code=["#33CCFF","#FF99CC","#FFCC00","#33CC66","#FF9933"]
#colors_code_V85=["#2badd9","#d982ad","#d9ad00","#2bad57","#d9822b"]
#colors_code_S30=["#c2f0ff","#ffe0f0","#fff0b3","#c7ffda","#ffe0c2"]
colors_code_S30_alpha=[(194,240,255),(255,224,240),(255,240,179),(199,255,218),(255,224,194)]
color_char=(250,250,250)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode(SIZE,pygame.RESIZABLE)
pygame.display.set_caption("Goshoku_Hyakunin_Isshu")
clock = pygame.time.Clock()
se_waka=[]
se={}
img = []
head_img = []
background_image = pygame.image.load('pic/noise_image_g.png')  # 画像ファイルのパスを指定
def load_source():
    global se
    global se_waka
    global img
    global head_img
    se["binta01"] = pygame.mixer.Sound("ogg/binta01.ogg")
    se["maru"] = pygame.mixer.Sound("ogg/maru.ogg")
    se["atack"] = pygame.mixer.Sound("ogg/atack.ogg")
    se["ken"] = pygame.mixer.Sound("ogg/ken.ogg")
    se["shouri"] = pygame.mixer.Sound("ogg/sentou-syouri.ogg")
    se["shouri2"] = pygame.mixer.Sound("ogg/sentou-syouri2.ogg")
    se["shouri3"] = pygame.mixer.Sound("ogg/sentou-syouri3.ogg")
    se["shouri4"] = pygame.mixer.Sound("ogg/sentou-syouri4.ogg")
    se["shouri5"] = pygame.mixer.Sound("ogg/sentou-syouri5.ogg")
    se["bgm"] = pygame.mixer.Sound("ogg/harunoumi_s.ogg")
    for c in range(5):
        for i in range(20):
            se_waka.append(pygame.mixer.Sound("ogg/{}_{}.ogg".format(c,i)))
    COMBINED_CARD_PATH = 'pic/cards.png'
    COMBINED_HEAD_PATH = 'pic/heads.png'
    NUM_SETS = 5
    combined_card_img = Image.open(COMBINED_CARD_PATH).convert("RGBA")
    combined_head_img = Image.open(COMBINED_HEAD_PATH).convert("RGBA")
    for set_id in range(NUM_SETS):
        row = []
        head_row = []
        for card_id in range(FULL_CARDS):
            cx = card_id * CARD_SIZE[0]
            cy = set_id * CARD_SIZE[1]
            cropped = combined_card_img.crop((cx, cy, cx + CARD_SIZE[0], cy + CARD_SIZE[1]))
            surface = pil_to_surface(cropped)
            row.append(surface)
            hx = card_id * HEAD_SIZE[0]
            hy = set_id * HEAD_SIZE[1]
            cropped = combined_head_img.crop((hx, hy, hx + HEAD_SIZE[0], hy + HEAD_SIZE[1]))
            surface = pil_to_surface(cropped)
            head_row.append(surface)
        img.append(row)
        head_img.append(head_row)

def pil_to_surface(pil_image):
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    return pygame.image.fromstring(data, size, mode).convert_alpha()

class Karuta:
    def __init__(self):
        random.seed()
        self.board=[]*FULL_CARDS
        b=list(range(FULL_CARDS))
        random.shuffle(b)
        self.board=b
        self.hand=[]*FULL_CARDS
        h=list(range(FULL_CARDS))
        random.shuffle(h)
        self.hand=h
        self.gamesize=(SIZE[0],SIZE[1])
        self.invisible_flag=0
        self.draggingItemIndex=None
        self.drgOffsetX=0
        self.drgOffsetY=0
        self.drgCornerOffsetX=0
        self.drgCornerOffsetY=0
        self.char_flag=False
        self.char_mode_flag=False
        self.cpu_mode_flag=False
        self.cpuscore=0
        self.slider_dragging = False
        self.knob_x=SLIDER_POS[0]
        self.score=0
        self.obtainedcard=0
        self.col=0
        self.cpuframes=[SECTION_TIME*FPS]*READ_CARDS
        self.moveflag=False
        self.move=[0,0,0,0,0] #[pos_x,pos_y,ith,MOVE_FRAME,IS_ME_OR_CPU]
        self.x0=0
        self.y0=0
        self.card_rect=[None]*FULL_CARDS
        self.rotated_img=[None]*FULL_CARDS
        self.title_card_rect=[None]*BOARD_SIZE[0]
        self.wander_mode_flag=False
        ang=[[20,0],[19,6],[16,11],[11,16],[6,19],[0,20],[-7,19],[-12,16],[-17,11],[-20,6],[-20,0],[-20,-7],[-17,-12],[-12,-17],[-7,-20],[-1,-20],[6,-20],[11,-17],[16,-12],[19,-7]]
        random.shuffle(ang)
        self.wander_ang=ang
    def get_posid(self,i):
        for j in range(FULL_CARDS):
            if self.board[j]==i:
                return j
        return 99
    def set_cpuframes(self):
        cpuallframe=(100*READ_CARDS-self.cpuscore)*int(FPS/10)
        cpuarea_cards=0
        for i in range(READ_CARDS):
            if self.hand[i]<CPUAREA_NUM:
                cpuarea_cards+=1
        splitframe=cpuallframe/(CPUAREA_RATE*(READ_CARDS-cpuarea_cards)+cpuarea_cards)
        for i in range(READ_CARDS):
            if self.card_rect[i].center[1]//GRID_SIZE[1] < 2:
                self.cpuframes[i]=int(splitframe)
            else:
                self.cpuframes[i]=int(splitframe*CPUAREA_RATE)
        err=sum(self.cpuframes) - cpuallframe
        if err != 0:
            for i in range(abs(err)):
                self.cpuframes[i%READ_CARDS]+=err/abs(err) #-1 or 1
        tiltfunc=[0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0.0,-0.1,-0.2,-0.3,-0.4,-0.5,-0.6,-0.7,-0.8]
        for i in range(READ_CARDS):
            self.cpuframes[i]+int(tiltfunc[i]*FPS)

    def cpu_atack(self,ith):
        se["atack"].play()
        self.moveflag=True
        x_id, y_id = self.card_rect[self.hand[ith]].center
        x_id //= GRID_SIZE[0]
        y_id //= GRID_SIZE[1]
        self.move=[x_id,y_id,ith,MOVE_FRAME,0]
        self.card_rect[self.hand[ith]] = None

    def draw_board(self,cnt,stage,ith):
        if(cnt<0):
            cnt=0
        screen.fill(GREEN)
        screen.blit(background_image, (self.x0, self.y0), (0, 0, GRID_SIZE[0]*BOARD_SIZE[0], GRID_SIZE[1]*BOARD_SIZE[1]))
        for i in range(FULL_CARDS):
            if self.card_rect[i] is not None and i != self.draggingItemIndex:
                screen.blit(self.rotated_img[i], self.card_rect[i].topleft)
                if self.invisible_flag > 0:
                    self.draw_hidescr(i,cnt,stage)
        if self.draggingItemIndex != None and self.drgCornerOffsetX != 0:
                screen.blit(self.rotated_img[self.draggingItemIndex], (self.drgCornerOffsetX,self.drgCornerOffsetY))
        if self.moveflag:
            if self.move[3]>1:
                temp_pos=(self.x0+self.move[0]*GRID_SIZE[0]+SUKIMA,self.y0+self.move[1]*GRID_SIZE[1]+SUKIMA)
                pos=(temp_pos[0]-(temp_pos[0]-int(GRID_SIZE[0]*BOARD_SIZE[0]/2))/MOVE_FRAME*(MOVE_FRAME-self.move[3]+1),\
                     temp_pos[1]-(temp_pos[1]-SIZE[1]*self.move[4])/MOVE_FRAME*(MOVE_FRAME-self.move[3]+1))
                screen.blit(self.rotated_img[self.hand[self.move[2]]], pos)
                self.move[3]-=1
            elif self.move[3]:
                self.moveflag=False
                self.move=[0,0,0,0,0]
        font_size=24
        score_board_sukima=10
        font = pygame.font.Font(None, font_size)
        text=font.render("SCORE",True, color_char)
        screen.blit(text, (self.x0+BOARD_SIZE[0]*GRID_SIZE[0]+score_board_sukima, self.y0+score_board_sukima))
        text=font.render("{}".format(self.score),True, color_char)
        screen.blit(text, (self.x0+BOARD_SIZE[0]*GRID_SIZE[0]+score_board_sukima, self.y0+font_size+score_board_sukima))
        text=font.render("CARD",True, color_char)
        screen.blit(text, (self.x0+BOARD_SIZE[0]*GRID_SIZE[0]+score_board_sukima, self.y0+font_size*2+score_board_sukima))
        text=font.render("{}".format(self.obtainedcard),True, color_char)
        screen.blit(text, (self.x0+BOARD_SIZE[0]*GRID_SIZE[0]+score_board_sukima, self.y0+font_size*3+score_board_sukima))
        text=font.render("TIME",True, color_char)
        screen.blit(text, (self.x0+BOARD_SIZE[0]*GRID_SIZE[0]+score_board_sukima, self.y0+font_size*5+score_board_sukima))
        if stage==1:
            text=font.render("inf.",True, color_char)
        else:
            text=font.render("{}".format(SECTION_TIME-int(cnt/FPS)),True, color_char)            
        screen.blit(text, (self.x0+BOARD_SIZE[0]*GRID_SIZE[0]+score_board_sukima, self.y0+font_size*6+score_board_sukima))
        if(stage==2 and self.char_flag and self.char_mode_flag and ith < FULL_CARDS):
            start_x = 0
            start_y = 0
            img_w, img_h =head_img[self.col][self.hand[ith]].get_rect().size
            crop_width = img_w
            crop_height = min(cnt*(FPS//10)*2,img_h)
            crop_rect = pygame.Rect(start_x, start_y, crop_width, crop_height)
            cropped_image = head_img[self.col][self.hand[ith]].subsurface(crop_rect)
            crop_center = (self.x0+GRID_SIZE[0]*BOARD_SIZE[0]+BAR_W//2, self.y0+SIZE[1]//2-font_size//2, font_size, font_size)
            display_x = crop_center[0] - crop_width // 2
            display_y = crop_center[1]
            screen.blit(cropped_image, (display_x, display_y))
        if(stage==2 and self.wander_mode_flag):
            for ii in range(FULL_CARDS):
                if self.card_rect[ii] is not None:
                    self.card_rect[ii].x+=self.wander_ang[ii][0]//4
                    self.card_rect[ii].y+=self.wander_ang[ii][1]//4
                    if self.card_rect[ii].left < 0:
                        self.card_rect[ii].left=0
                        self.wander_ang[ii][0]*=-1
                    elif self.card_rect[ii].right > GRID_SIZE[0]*BOARD_SIZE[0]:
                        self.card_rect[ii].right=GRID_SIZE[0]*BOARD_SIZE[0]
                        self.wander_ang[ii][0]*=-1
                    if self.card_rect[ii].top < 0:
                        self.card_rect[ii].top=0
                        self.wander_ang[ii][1]*=-1
                    elif self.card_rect[ii].bottom > GRID_SIZE[1]*BOARD_SIZE[1]:
                        self.card_rect[ii].bottom=GRID_SIZE[1]*BOARD_SIZE[1]
                        self.wander_ang[ii][1]*=-1

    def draw_hidescr(self, card_id, cnt, stage):
        pos=self.card_rect[card_id].center
        if stage==2 and (self.invisible_flag==1 or (self.invisible_flag==2 and pos[1]//GRID_SIZE[1] >=2)):
            if cnt<INVISIBLE_TIME*FPS:
                alpha=255
            else:
                alpha=255-int(255/(SECTION_TIME-INVISIBLE_TIME)*(cnt/FPS-INVISIBLE_TIME))
            #pos=(self.x0+ gridpos[0] * GRID_SIZE[0]+SUKIMA+BANDWIDTH, self.y0+gridpos[1] * GRID_SIZE[1]+SUKIMA+BANDWIDTH)
            hidescr =pygame.Surface(INVISIBLE_SIZE,flags=pygame.SRCALPHA)
            hidescr.fill((colors_code_S30_alpha[self.col][0],colors_code_S30_alpha[self.col][1],colors_code_S30_alpha[self.col][2],alpha))
            #screen.blit(hidescr,pos)
            hidescr_rect=hidescr.get_rect(center=pos)
            screen.blit(hidescr, hidescr_rect.topleft)
    def display_result(self):
        font = pygame.font.Font(None, FONT_SIZE_RESULT)
        if self.cpuscore !=0:
            if self.obtainedcard > READ_CARDS/2:
                se["shouri"].play()
                text = font.render("You win!", True, YELLOW)
            else:
                se["shouri2"].play()
                text = font.render("Try again!", True, YELLOW)
        elif self.score>=1400:
            se["shouri"].play()
            text = font.render("Fantastic!!", True, YELLOW)        
        elif self.score>=1300:
            se["shouri2"].play()
            text = font.render("Congratulations!", True, YELLOW)
        elif self.score>=1200:
            se["shouri3"].play()
            text = font.render("Good Job!", True, YELLOW)
        elif self.score>=1100:
            se["shouri4"].play()
            text = font.render("Finish!", True, YELLOW)
        else:
            se["shouri5"].play()
            text = font.render("Finish...", True, YELLOW)
        text_rect = text.get_rect(center=(SIZE[0] // 2, SIZE[1] // 2))
        text_rect.move_ip(self.x0, self.y0)
        screen.blit(text, text_rect)
        pygame.display.flip()
        self.char_flag=False
    
    def update(self,x,y,ith,thisscore):
        if self.card_rect[self.hand[ith]].collidepoint(x, y):
            se["binta01"].play()
            self.score+=thisscore
            self.moveflag=True
            x_id, y_id = self.card_rect[self.hand[ith]].center
            x_id //= GRID_SIZE[0]
            y_id //= GRID_SIZE[1]
            self.move=[x_id,y_id,ith,MOVE_FRAME,1]
            self.obtainedcard+=1
            self.card_rect[self.hand[ith]] = None
            return True
        else:
            se["ken"].play()
            return False

    def reset_section(self,ith):
        pygame.mixer.stop()
        se_waka[self.col*20+self.hand[ith]].play()
        self.char_flag=True

    def draw_select_board(self):
        screen.fill(GREEN)
        screen.blit(background_image, (self.x0, self.y0), (0, 0, GRID_SIZE[0]*BOARD_SIZE[0], GRID_SIZE[1]*BOARD_SIZE[1]))
        font_size=32
        font = pygame.font.Font(None, font_size)
        card_represent=[5,13,3,4,8]
        for i in range(BOARD_SIZE[0]*1):
            gridpos=(i%BOARD_SIZE[0],1)
            centerpos=(self.x0+gridpos[0]*GRID_SIZE[0]+GRID_SIZE[0]//2, self.y0+gridpos[1]*GRID_SIZE[1]+GRID_SIZE[1]//2)
            self.title_card_rect[i]=img[i][card_represent[i]].get_rect(center=centerpos)
            screen.blit(img[i][card_represent[i]], self.title_card_rect[i].topleft)
        if not self.cpu_mode_flag:
            color_cpu_off, color_cpu_on = 'red', 'gray'
        else:
            color_cpu_off, color_cpu_on = 'gray', 'red'
        if self.invisible_flag==1:
            color_on, color_on2, color_off = 'red', 'gray', 'gray'
        elif self.invisible_flag==2:
            color_on, color_on2, color_off = 'gray', 'red', 'gray'
        else:
            color_on, color_on2, color_off = 'gray', 'gray', 'red'
        if not self.char_mode_flag:
            color_char_off, color_char_on = 'red', 'gray'
        else:
            color_char_off, color_char_on = 'gray', 'red'
        if not self.wander_mode_flag:
            color_wander_off, color_wander_on = 'red', 'gray'
        else:
            color_wander_off, color_wander_on = 'gray', 'red'
        box_size=24
        border_w=1
        small_font = pygame.font.Font(None, box_size)

        cpu_box_x=self.x0+GRID_SIZE[0]*1+box_size
        cpu_box_y=self.y0+int(GRID_SIZE[1]*2.5)+box_size
        self.cpu_rect_off = pygame.Rect(cpu_box_x, cpu_box_y+box_size, box_size, box_size)
        self.cpu_rect_on = pygame.Rect(cpu_box_x, cpu_box_y+int(box_size*2.5), box_size, box_size)
        pygame.draw.rect(screen, color_cpu_off, self.cpu_rect_off)
        pygame.draw.rect(screen, 'gray', self.cpu_rect_off, border_w)
        pygame.draw.rect(screen, color_cpu_on, self.cpu_rect_on)
        pygame.draw.rect(screen, 'gray', self.cpu_rect_on, border_w)
        text = small_font.render("CPU mode", True, 'white')
        text_rect = text.get_rect(midleft=(cpu_box_x, cpu_box_y))
        screen.blit(text, text_rect)
        text = small_font.render("OFF", True, 'white')
        self.text_cpu_rect_off = text.get_rect(midleft=(cpu_box_x+int(box_size*1.5), cpu_box_y+int(box_size*1.5)))
        screen.blit(text, self.text_cpu_rect_off)
        text = small_font.render("ON", True, 'white')
        self.text_cpu_rect_on = text.get_rect(midleft=(cpu_box_x+int(box_size*1.5), cpu_box_y+int(box_size*3)))
        screen.blit(text, self.text_cpu_rect_on)

        char_box_x=self.x0+GRID_SIZE[0]*3+box_size
        char_box_y=self.y0+int(GRID_SIZE[1]*2.5)+box_size
        self.char_rect_off = pygame.Rect(char_box_x, char_box_y+box_size, box_size, box_size)
        self.char_rect_on = pygame.Rect(char_box_x, char_box_y+int(box_size*2.5), box_size, box_size)
        pygame.draw.rect(screen, color_char_off, self.char_rect_off)
        pygame.draw.rect(screen, 'gray', self.char_rect_off, border_w)
        pygame.draw.rect(screen, color_char_on, self.char_rect_on)
        pygame.draw.rect(screen, 'gray', self.char_rect_on, border_w)
        text = small_font.render("readable mode", True, 'white')
        text_rect = text.get_rect(midleft=(char_box_x, char_box_y))
        screen.blit(text, text_rect)
        text = small_font.render("OFF", True, 'white')
        self.text_char_rect_off = text.get_rect(midleft=(char_box_x+int(box_size*1.5), char_box_y+int(box_size*1.5)))
        screen.blit(text, self.text_char_rect_off)
        text = small_font.render("ON", True, 'white')
        self.text_char_rect_on = text.get_rect(midleft=(char_box_x+int(box_size*1.5), char_box_y+int(box_size*3)))
        screen.blit(text, self.text_char_rect_on)

        box_x=self.x0+GRID_SIZE[0]*3+box_size
        box_y=self.y0+GRID_SIZE[1]*3+box_size
        self.inv_rect_off = pygame.Rect(box_x, box_y+box_size, box_size, box_size)
        self.inv_rect_on = pygame.Rect(box_x, box_y+int(box_size*2.5), box_size, box_size)
        self.inv_rect_on2 = pygame.Rect(box_x, box_y+int(box_size*4), box_size, box_size)
        pygame.draw.rect(screen, color_off, self.inv_rect_off)
        pygame.draw.rect(screen, 'gray', self.inv_rect_off, border_w)
        pygame.draw.rect(screen, color_on, self.inv_rect_on)
        pygame.draw.rect(screen, 'gray', self.inv_rect_on, border_w)
        pygame.draw.rect(screen, color_on2, self.inv_rect_on2)
        pygame.draw.rect(screen, 'gray', self.inv_rect_on2, border_w)
        text = small_font.render("invisible mode", True, 'white')
        text_rect = text.get_rect(midleft=(box_x, box_y))
        screen.blit(text, text_rect)
        text = small_font.render("OFF", True, 'white')
        self.text_inv_rect_off = text.get_rect(midleft=(box_x+int(box_size*1.5), box_y+int(box_size*1.5)))
        screen.blit(text, self.text_inv_rect_off)
        text = small_font.render("ON", True, 'white')
        self.text_inv_rect_on = text.get_rect(midleft=(box_x+int(box_size*1.5), box_y+int(box_size*3)))
        screen.blit(text, self.text_inv_rect_on)
        text = small_font.render("ON for my side", True, 'white')
        self.text_inv_rect_on2 = text.get_rect(midleft=(box_x+int(box_size*1.5), box_y+int(box_size*4.5)))
        screen.blit(text, self.text_inv_rect_on2)

        wander_box_x=self.x0+GRID_SIZE[0]*4+box_size
        wander_box_y=self.y0+int(GRID_SIZE[1]*2.5)+box_size
        self.wander_rect_off = pygame.Rect(wander_box_x, wander_box_y+box_size, box_size, box_size)
        self.wander_rect_on = pygame.Rect(wander_box_x, wander_box_y+int(box_size*2.5), box_size, box_size)
        pygame.draw.rect(screen, color_wander_off, self.wander_rect_off)
        pygame.draw.rect(screen, 'gray', self.wander_rect_off, border_w)
        pygame.draw.rect(screen, color_wander_on, self.wander_rect_on)
        pygame.draw.rect(screen, 'gray', self.wander_rect_on, border_w)
        text = small_font.render("wandering mode", True, 'white')
        text_rect = text.get_rect(midleft=(wander_box_x, wander_box_y))
        screen.blit(text, text_rect)
        text = small_font.render("OFF", True, 'white')
        self.text_wander_rect_off = text.get_rect(midleft=(wander_box_x+int(box_size*1.5), wander_box_y+int(box_size*1.5)))
        screen.blit(text, self.text_wander_rect_off)
        text = small_font.render("ON", True, 'white')
        self.text_wander_rect_on = text.get_rect(midleft=(wander_box_x+int(box_size*1.5), wander_box_y+int(box_size*3)))
        screen.blit(text, self.text_wander_rect_on)

        text=font.render("SELECT COLOR",True, color_char)
        text_rect = text.get_rect(center=(int(GRID_SIZE[0]*2.5), int(GRID_SIZE[1]*0.5)))
        text_rect.move_ip(self.x0, self.y0)
        screen.blit(text, text_rect)

    def draw_slider(self, thiscpuscore):
        steps = (thiscpuscore - SLIDER_MIN_VALUE) // SLIDER_STEP
        ratio = steps / ((SLIDER_MAX_VALUE - SLIDER_MIN_VALUE) // SLIDER_STEP)
        self.knob_x= int(SLIDER_POS[0] + ratio * SLIDER_WIDTH)
        pygame.draw.rect(screen, 'gray', (SLIDER_POS[0], SLIDER_POS[1], SLIDER_WIDTH, SLIDER_HEIGHT))
        pygame.draw.circle(screen, 'white', (self.knob_x, SLIDER_POS[1] + SLIDER_HEIGHT // 2), KNOB_RADIUS)
        font = pygame.font.Font(None, 24)
        text = font.render(f"CPU Score: {self.cpuscore}", True, (255, 255, 255))
        screen.blit(text, (SLIDER_POS[0], SLIDER_POS[1] - 20))

    def update_cpuscore(self,this_knob_x):
        relative_x = this_knob_x - SLIDER_POS[0]
        ratio = relative_x / SLIDER_WIDTH
        steps = round(ratio * ((SLIDER_MAX_VALUE - SLIDER_MIN_VALUE) // SLIDER_STEP))
        value = SLIDER_MIN_VALUE + steps * SLIDER_STEP
        value = max(SLIDER_MIN_VALUE, min(SLIDER_MAX_VALUE, value))
        return value
    
    def reset_section_select(self):
        pygame.mixer.stop()
        se["bgm"].play()

    def sizecheck(self):
        w, h = pygame.display.get_surface().get_size()
        self.x0=int((w-self.gamesize[0])/2)
        self.y0=int((h-self.gamesize[1])/2)

    def draw_startbtn(self):
        font = pygame.font.Font(None, 24)
        x, y = STARTBTN_POS[0], STARTBTN_POS[1] # ボタンの中心座標
        w, h = STARTBTN_SIZE[0],STARTBTN_SIZE[1]   # ボタンの幅と高さ
        button_color = 'azure1'
        button_color_edge = 'azure3'
        text_color = 'darkgreen'
        button_rect = pygame.Rect(self.x0+x-w//2+5, self.y0+y-h//2+5, w-10, h-10)
        self.button_rect_edge = pygame.Rect(self.x0 + x - w // 2, self.y0 + y - h // 2, w, h)
        pygame.draw.rect(screen, button_color_edge, self.button_rect_edge)
        pygame.draw.rect(screen, button_color, button_rect)
        text = font.render("START", True, text_color)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

    def card_click_check(self, x, y):
        for i in range(FULL_CARDS):
            if self.card_rect[i].collidepoint(x, y):
                return i
        return 99
    
    def title_card_click_check(self, x, y):
        for c in range(BOARD_SIZE[0]):
            if self.title_card_rect[c].collidepoint(x, y):
                se["maru"].play()
                for i in range(FULL_CARDS):
                    posid=self.get_posid(i)
                    if posid < FULL_CARDS // 2:
                        self.rotated_img[i]=pygame.transform.rotate(img[c][i], 180)
                    else:
                        self.rotated_img[i]=img[c][i]
                    gridpos=(posid%BOARD_SIZE[0],posid//BOARD_SIZE[0])
                    centerpos=(self.x0+gridpos[0]*GRID_SIZE[0]+GRID_SIZE[0]//2, self.y0+gridpos[1]*GRID_SIZE[1]+GRID_SIZE[1]//2)
                    self.card_rect[i]=self.rotated_img[i].get_rect(center=centerpos)
                self.col=c
                return c
        se["ken"].play()
        return 99
def show_loading_screen():
    font = pygame.font.Font(None, 24)
    screen.blit(background_image, (0, 0), (0, 0, SIZE[0], SIZE[1]))
    text = font.render("Goshoku Hyakunin Isshu       Loading...", True, (255, 255, 255))
    screen.blit(text, (SIZE[0] // 2 - text.get_width() // 2, SIZE[1] // 2 - text.get_height() // 2))
    pygame.display.flip()
async def main():
    show_loading_screen()    
    load_source()
    game = Karuta()
    running = True
    cnt=0
    read_cnt=0
    stage=0
    while running:
        game.sizecheck()
        pygame.event.pump()
        if stage==0:
            if cnt%(SECTION_TIME_SELECT*FPS)==0:
                game.reset_section_select()
                cnt = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    px, py = event.pos
                    clicked=game.title_card_click_check(px,py)
                    if clicked in range(BOARD_SIZE[0]):
                        stage = 1
                        cnt = -1
                        game.gamesize=(GRID_SIZE[0]*BOARD_SIZE[0]+BAR_W,GRID_SIZE[1]*BOARD_SIZE[1]) 
                        screen = pygame.display.set_mode(game.gamesize, pygame.RESIZABLE)
                        if game.cpu_mode_flag:
                            game.set_cpuframes()
                    elif game.inv_rect_off.collidepoint(px, py) or game.text_inv_rect_off.collidepoint(px, py):
                        game.invisible_flag=0
                    elif game.inv_rect_on.collidepoint(px, py) or game.text_inv_rect_on.collidepoint(px, py):
                        game.invisible_flag=1
                    elif game.inv_rect_on2.collidepoint(px, py) or game.text_inv_rect_on2.collidepoint(px, py):
                        game.invisible_flag=2
                    elif game.char_rect_off.collidepoint(px, py) or game.text_char_rect_off.collidepoint(px, py):
                        game.char_mode_flag=False
                    elif game.char_rect_on.collidepoint(px, py) or game.text_char_rect_on.collidepoint(px, py):
                        game.char_mode_flag=True
                    elif game.wander_rect_off.collidepoint(px, py) or game.text_wander_rect_off.collidepoint(px, py):
                        game.wander_mode_flag=False
                    elif game.wander_rect_on.collidepoint(px, py) or game.text_wander_rect_on.collidepoint(px, py):
                        game.wander_mode_flag=True
                    elif game.cpu_rect_off.collidepoint(px, py) or game.text_cpu_rect_off.collidepoint(px, py):
                        game.cpu_mode_flag=False
                        game.cpuscore = 0
                    elif game.cpu_rect_on.collidepoint(px, py) or game.text_cpu_rect_on.collidepoint(px, py):
                        game.cpu_mode_flag=True
                        game.cpuscore = 1200
                    elif KNOB_RADIUS >= ((px - game.knob_x) ** 2 + (py - (SLIDER_POS[1] + SLIDER_HEIGHT // 2)) ** 2) ** 0.5:
                        game.slider_dragging = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    game.slider_dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if game.slider_dragging:
                        px, py = event.pos
                        px-=game.x0
                        py-=game.y0
                        this_knob_x = px
                        if px >= SLIDER_POS[0] + SLIDER_WIDTH:
                            this_knob_x=SLIDER_POS[0] + SLIDER_WIDTH
                        elif px <=SLIDER_POS[0]:
                            this_knob_x = SLIDER_POS[0]
                        game.cpuscore = game.update_cpuscore(this_knob_x)
                        steps = (game.cpuscore - SLIDER_MIN_VALUE) // SLIDER_STEP
                        ratio = steps / ((SLIDER_MAX_VALUE - SLIDER_MIN_VALUE) // SLIDER_STEP)
                        game.knob_x= int(SLIDER_POS[0] + ratio * SLIDER_WIDTH)
            game.draw_select_board()
            if game.cpu_mode_flag:
                game.draw_slider(game.cpuscore)

        elif stage==1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    px, py = event.pos
                    clicked=game.card_click_check(px, py)
                    if clicked < FULL_CARDS:
                        game.draggingItemIndex = clicked
                        game.drgCornerOffsetX = game.card_rect[clicked].topleft[0]
                        game.drgCornerOffsetY = game.card_rect[clicked].topleft[1]
                        game.drgOffsetX = px - game.drgCornerOffsetX
                        game.drgOffsetY = py - game.drgCornerOffsetY
                    elif game.button_rect_edge.collidepoint(px, py):
                        cnt = (SECTION_TIME-2)*FPS
                        game.draggingItemIndex=None
                        game.drgOffsetX=0
                        game.drgOffsetY=0
                        game.drgCornerOffsetX=0
                        game.drgCornerOffsetY=0
                        se["maru"].play()
                        stage=2
                elif event.type == pygame.MOUSEMOTION:
                    if game.draggingItemIndex != None:
                        px, py = event.pos
                        game.drgCornerOffsetX=px - game.drgOffsetX
                        game.drgCornerOffsetY=py - game.drgOffsetY
                elif event.type == pygame.MOUSEBUTTONUP:
                    if game.draggingItemIndex != None:
                        px, py = event.pos
                        clicked=game.card_click_check(px, py)
                        #dragcheck
                        if clicked < FULL_CARDS:
                            game.card_rect[game.draggingItemIndex], game.card_rect[clicked] = game.card_rect[clicked], game.card_rect[game.draggingItemIndex] 
                            if (game.card_rect[game.draggingItemIndex][1]//GRID_SIZE[1]-1.5) * (game.card_rect[clicked][1]//GRID_SIZE[1]-1.5) < 0:
                                game.rotated_img[game.draggingItemIndex]=pygame.transform.rotate(game.rotated_img[game.draggingItemIndex], 180)
                                game.rotated_img[clicked]=pygame.transform.rotate(game.rotated_img[clicked], 180)
                        game.draggingItemIndex = None
                        game.drgCornerOffsetX=0
                        game.drgCornerOffsetY=0 
                        game.drgOffsetX=0
                        game.drgOffsetY=0
            if cnt==0:
                pass
            elif cnt==SECTION_TIME*FPS:
                cnt = -1
                #stage=2
            game.draw_board(cnt,stage,99)
            game.draw_startbtn()
        elif stage==2:
            if cnt%(SECTION_TIME*FPS)==0:
                read_cnt += 1
                if read_cnt > READ_CARDS:
                    game.display_result()
                    remaintime=SECTION_TIME_RESULT*FPS*10
                    for i in range(remaintime):
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit()
                        clock.tick(FPS)
                        await asyncio.sleep(0) 
                    pygame.quit()
                    sys.exit()
                else:
                    game.reset_section(read_cnt-1)
                cnt = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    px,py = event.pos
                    if game.card_rect[game.hand[read_cnt-1]] is not None:
                        res=game.update(px,py,read_cnt-1,100-int(100/(SECTION_TIME*FPS)*cnt))
                        if res:
                            cnt=(SECTION_TIME-2)*FPS
            if game.cpuscore!=0 and cnt==game.cpuframes[read_cnt-1] and game.card_rect[game.hand[read_cnt-1]] is not None:
                game.cpu_atack(read_cnt-1)
                cnt=(SECTION_TIME-2)*FPS
            game.draw_board(cnt,stage,read_cnt-1)
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0) 
        cnt += 1
    pygame.quit()
    sys.exit()

#asyncio.run(main())
if __name__ == "__main__": # 二重ループを起こさないように変更
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # In some environments, an event loop might already be running.
        # This handles such cases.
        if "cannot run loop while another loop is running" in str(e):
            loop = asyncio.get_event_loop()
            loop.create_task(main())
        else:
            raise
