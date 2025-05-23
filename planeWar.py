import pygame
import random
import os
import pathlib

FPS = 30
WIDTH = 500
HEIGHT = 600
BLACK = (0,0,0)

folder = pathlib.Path(__file__).parent.resolve()

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('飞机大战')
clock = pygame.time.Clock()

background_img = pygame.image.load(os.path.join(folder,"img","background.png")).convert()
player_img = pygame.image.load(os.path.join(folder,"img","player.png")).convert()
player_mini_img = pygame.transform.scale(player_img,(25,20))
player_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mini_img)
bullet_img = pygame.image.load(os.path.join(folder,"img","bullet.png")).convert()
rock_images = []
for i in range(7):
    rock_images.append(pygame.image.load(os.path.join(folder,"img",f"rock{i}.png")).convert())
expl_anim = {}
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join(folder,"img",f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img,(75,75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img,(30,30)))
    player_expl_img = pygame.image.load(os.path.join(folder,"img",f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join(folder,"img","shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join(folder,"img","gun.png")).convert()

shoot_sound = pygame.mixer.Sound(os.path.join(folder,"sound","shoot.wav"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join(folder,"sound","expl0.wav")),
    pygame.mixer.Sound(os.path.join(folder,"sound","expl1.wav"))
]
die_sound = pygame.mixer.Sound(os.path.join(folder,"sound","rumble.ogg"))
shield_sound = pygame.mixer.Sound(os.path.join(folder,"sound","pow0.wav"))
gun_sound = pygame.mixer.Sound(os.path.join(folder,"sound","pow1.wav"))

pygame.mixer.music.load(os.path.join(folder,"sound","background.ogg"))

font_name = os.path.join(folder,'font.ttf')

def draw_lives(surf,lives,img,x,y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x+30*i
        img_rect.y = y
        surf.blit(img,img_rect)

def draw_text(surface,text,size,x,y):
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text,True,(255,255,255))
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surface.blit(text_surface,text_rect)   

def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock) 

def draw_health(surf,hp,x,y):
    if hp<0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,(255,255,255),outline_rect,2)
    pygame.draw.rect(surf,(0,255,0),fill_rect)

def draw_init():
    screen.blit(background_img,(0,0))
    draw_text(screen,'飞机大战',62,WIDTH/2,HEIGHT/4)
    draw_text(screen,'AD键移动，右键发射子弹',22,WIDTH/2,HEIGHT/2)
    draw_text(screen,'按任意键开始',18,WIDTH/2,HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img,(50,40))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 23
        #pygame.draw.circle(self.image,(255,0,0),self.rect.center,self.radius)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT-20
        self.speedx = 8

        self.health = 100
        self.lives = 3
        self.hidden = False
        self.gun = 1
    def update(self):
        now = pygame.time.get_ticks()
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            self.rect.x -= self.speedx
        if key[pygame.K_RIGHT] or key[pygame.K_d]:
            self.rect.x +=  self.speedx
        if self.rect.right>WIDTH:
            self.rect.right = WIDTH
        if self.rect.left<0:
            self.rect.left = 0
        if self.hidden and now-self.hide_time>1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT-20
        if self.gun>1 and now-self.gun_time>5000:
            self.gun = 1
    def shoot(self):
        if not self.hidden:
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx,self.rect.centery)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            else:
                bullet1 = Bullet(self.rect.left,self.rect.centery)
                bullet2 = Bullet(self.rect.right,self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2,HEIGHT+500)
    def gunup(self):
        self.gun +=  1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_origin = random.choice(rock_images)
        self.image_origin.set_colorkey(BLACK)
        self.image = self.image_origin.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width/2.2
        #pygame.draw.circle(self.image,(0,255,0),self.rect.center,self.radius)
        self.rect.x = random.randrange(0,WIDTH-self.rect.width)
        self.rect.y = random.randrange(-180,-40)
        self.speedy = random.randrange(2,10)
        self.speedx = random.randrange(-3,2)

        self.total_degree = 0
        self.rot_degree = random.randrange(-3,3)

    def rotate(self):
        self.total_degree +=  self.rot_degree
        self.total_degree %= 360
        self.image = pygame.transform.rotate(self.image_origin,self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y +=  self.speedy
        self.rect.x +=  self.speedx
        if self.rect.top>HEIGHT or self.rect.left>WIDTH or self.rect.right<0:
            self.rect.x = random.randrange(0,WIDTH-self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(2,10)
            self.speedx = random.randrange(-3,2)
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedy = -10

    def update(self):
        self.rect.y +=  self.speedy
        if self.rect.bottom<0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
    def update(self):
        now = pygame.time.get_ticks()
        if now-self.last_update>50:
            self.last_update = now
            self.frame +=  1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self,center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        if self.type == 'shield':
            shield_sound.play()
        elif self.type == 'gun':
            gun_sound.play()

        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y +=  self.speedy
        if self.rect.top>HEIGHT:
            self.kill()

show_init = True
running = True
while running:
    if show_init:
        score = 0
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            new_rock()

        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.3)
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button
            if button == 3:
                player.shoot()
    all_sprites.update()

    hits_rockAndBullet = pygame.sprite.groupcollide(rocks,bullets,True,True)
    for hit in hits_rockAndBullet:
        new_rock()
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center,'lg')
        all_sprites.add(expl)
        score +=  int(hit.radius)
        if random.random()>0.7:
            power = Power(hit.rect.center)
            all_sprites.add(power)
            powers.add(power)
    hits_playerAndRocks = pygame.sprite.spritecollide(player,rocks,True,pygame.sprite.collide_circle)
    for hit in hits_playerAndRocks:
        player.health -= hit.radius
        new_rock()
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        if player.health <= 0:
            d_expl = Explosion(player.rect.center,'player')
            all_sprites.add(d_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
        if player.lives == 0:
            show_init = True
    hits_playerAndPower = pygame.sprite.spritecollide(player,powers,True)
    for hit in hits_playerAndPower:
        if hit.type == 'shield':
            player.health +=  20
            if player.health >= 100:
                player.health = 100
        elif hit.type == 'gun':
            player.gunup()

    screen.fill(BLACK)
    screen.blit(background_img,(0,0))
    all_sprites.draw(screen)
    draw_text(screen,'分数：'+str(score),18,WIDTH/2,0)
    draw_health(screen,player.health,10,30)
    draw_lives(screen,player.lives,player_mini_img,WIDTH-100,15)
    pygame.display.update()

pygame.quit()