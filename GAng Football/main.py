from random import randint
from pygame import *
init()

C_WHITE = (255, 255, 255)
C_RED = (255, 0, 0)
C_GREEN = (0, 255, 0)
C_BLACK = (0, 0, 0)
C_FLOOR = (12, 17, 34)
C_WALLS = (86, 4, 1)

big_font = font.SysFont("Corbel", 72, True)
regular_font = font.SysFont("Corbel", 45, True)

game_over = big_font.render('Твоя команда проиграла', True, C_RED)
win = big_font.render('ГОЛ! Ты выиграл Матч', True, C_GREEN)
pause_text = big_font.render('Пауза', True, C_WHITE)
restart_text = regular_font.render('Нажми R чтобы начать новый матч', True, C_WHITE)

delayer = time.Clock()

mixer.music.load('sounds/ambience.wav') # фоновые звуки леса
mixer.music.set_volume(.7)
mixer.music.play(-1) # -1 - повторять бесконечно

pistol_sounds = [mixer.Sound('sounds/pistol-fire-1.ogg'),mixer.Sound('sounds/pistol-fire-2.ogg')]
shotgun_sounds = [mixer.Sound('sounds/shotgun-fire-1.ogg'), mixer.Sound('sounds/shotgun-fire-2.ogg')]
pistol_reload = mixer.Sound('sounds/reload-pistol.ogg')
shotgun_reload = mixer.Sound('sounds/reload-shotgun.ogg')
imposible_reload = mixer.Sound('sounds/imposible-reload.ogg')

img_file_back = 'images/back.png'
hero_images_pistol = [transform.scale(image.load('images/hero_pistol_walk_1.png'),(80,85)),
                    transform.scale(image.load('images/hero_pistol_walk_2.png'),(80,85)),
                    transform.scale(image.load('images/hero_pistol_normal.png'),(80,85))]
hero_images_shotgun = [transform.scale(image.load('images/hero_shotgun_walk_1.png'),(80,85)),
                    transform.scale(image.load('images/hero_shotgun_walk_2.png'),(80,85)),
                    transform.scale(image.load('images/hero_shotgun_normal.png'),(80,85))]
img_file_enemy = 'images/enemy.png'
img_file_princess = 'images/princess.png'
img_bullet = 'images/bullet.png'

class Princess(sprite.Sprite):
    def __init__(self, **args):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(img_file_princess), (150, 130))
        self.rect = self.image.get_rect()
        self.rect.x = args['x']
        self.rect.y = args['y']
    
class Hero(sprite.Sprite):
    def __init__(self, x_speed=0, y_speed=0, x=20, y=10):
        sprite.Sprite.__init__(self)
        self.image = hero_images_pistol[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.stands_on = False
        
        self.direction = 'right'
        self.gun = 'pistol'
        self.walk = False
        self.counter = 0
        self.pistol_clip = 6
        self.shotgun_clip = 2
    
    def update_direction(self, direction):
        if self.direction != direction:
            self.direction = direction
        
    def gravitate(self):
        self.y_speed += .25
    
    def jump(self, y):
        if self.stands_on:
            self.y_speed = y

    def fire(self):
        global reload_counter, reload_time
        if len(gun_clip) > 0:
            reload_time = False
            reload_counter = 0
            i = 1
            for patron in gun_clip:
                if i == len(gun_clip):
                    gun_clip.remove(patron)
                    if self.gun == 'pistol':
                        self.pistol_clip -= 1
                    elif self.gun == 'shotgun':
                        self.shotgun_clip -= 1
                    break
                i += 1
            if self.gun == 'pistol':
                Bullet(
                    direction = self.direction, 
                    x = self.rect.midright[0] if self.direction == 'right' else self.rect.midleft[0], 
                    y = self.rect.centery - 15, 
                    speed = 15, 
                    range = 600)
                pistol_sounds[randint(0,len(shotgun_sounds) - 1)].play()
            elif self.gun == 'shotgun':
                Bullet(
                    direction = self.direction,
                    x = self.rect.midright[0] - 25 if self.direction == 'right' else self.rect.midleft[0] + 10,
                    y = self.rect.centery - 5,
                    range = 300)
                Bullet(
                    direction = self.direction, 
                    x = self.rect.midright[0] - 25 if self.direction == 'right' else self.rect.midleft[0] + 10,
                    y = self.rect.centery + 5,
                    range = 300)
                Bullet(
                    direction = self.direction,
                    x = self.rect.midright[0] - 25 if self.direction == 'right' else self.rect.midleft[0] + 10,
                    y = self.rect.centery + 15,
                    range = 300)
                shotgun_sounds[randint(0,len(shotgun_sounds) - 1)].play()
        else:
            imposible_reload.play()
    def update(self):
        if self.x_speed != 0:
            if self.direction == 'right':
                self.image = (hero_images_pistol if self.gun == 'pistol' else hero_images_shotgun)[self.walk]
            elif self.direction == 'left':
                self.image = transform.flip((hero_images_pistol if self.gun == 'pistol' else hero_images_shotgun)[self.walk], True, False)
            if self.counter == 0:
                self.counter = 2
                self.walk = not self.walk
            else:
                self.counter -= 1
        else:
            if self.direction == 'right':
                self.image = (hero_images_pistol if self.gun == 'pistol' else hero_images_shotgun)[2]
            else:
                self.image = transform.flip((hero_images_pistol if self.gun == 'pistol' else hero_images_shotgun)[2], True, False)

        self.rect.x += self.x_speed
        # если зашли за стенку, то встанем вплотную к стене
        platforms_touched = sprite.spritecollide(self, barriers, False)
        if self.x_speed > 0: # идем направо, правый край персонажа - вплотную к левому краю стены
            for p in platforms_touched:
                self.rect.right = min(self.rect.right, p.rect.left) # если коснулись сразу нескольких, то правый край - минимальный из возможных
        elif self.x_speed < 0: # идем налево, ставим левый край персонажа вплотную к правому краю стены
            for p in platforms_touched:
                self.rect.left = max(self.rect.left, p.rect.right) # если коснулись нескольких стен, то левый край - максимальный
         
        self.gravitate()
        self.rect.y += self.y_speed
        # если зашли за стенку, то встанем вплотную к стене
        platforms_touched = sprite.spritecollide(self, barriers, False)
        if self.y_speed > 0: # идем вниз
            for p in platforms_touched:
                self.y_speed = 0
                # Проверяем, какая из платформ снизу самая высокая, выравниваемся по ней, запоминаем её как свою опору:
                if p.rect.top < self.rect.bottom:
                    self.rect.bottom = p.rect.top
                    self.stands_on = p
        elif self.y_speed < 0: # идем вверх
            self.stands_on = False # пошли наверх, значит, ни на чем уже не стоим!
            for p in platforms_touched:
                self.y_speed = 0  # при столкновении со стеной вертикальная скорость гасится
                self.rect.top = max(self.rect.top, p.rect.bottom) # выравниваем верхний край по нижним краям стенок, на которые наехали
    
class Wall(sprite.Sprite):
    def __init__(self, **args):
        sprite.Sprite.__init__(self)
        self.image = Surface([args['width'], args['height']])
        if args.get('color') != None:
            self.image.fill(args['color'])
        self.rect = self.image.get_rect()
        self.rect.x = args['x']
        self.rect.y = args['y']
        self.add(barriers, all_sprites)

class Enemy(sprite.Sprite):
    def __init__(self, **args):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(img_file_enemy), (130, 110))
        self.rect = self.image.get_rect()
        self.rect.x = args['x']
        self.rect.y = args['y']
        self.add(enemies, all_sprites)
    
    def update(self):
        self.rect.x += randint(-5, 5)

class Bullet(sprite.Sprite):
    def __init__(self, **args):
        sprite.Sprite.__init__(self)
        self.direction = args['direction']
        self.image = transform.scale(image.load(img_bullet), (50, 40))
        self.rect = self.image.get_rect()
        self.rect.x = args['x']
        self.rect.y = args['y']
        self.range = args['range']
        if args.get('speed'):
            self.speed = args['speed']
        else:
            self.speed = randint(10, 20)
        self.add(bullets, all_sprites)

    def update(self):
        global robin
        if self.direction == 'right':
            self.rect.x += self.speed
        else: 
            self.rect.x -= self.speed
        if self.rect.x < robin.rect.x - self.range or self.rect.x > robin.rect.x + self.range:
            self.kill()

class Patron(sprite.Sprite):
    def __init__(self, **args):
        sprite.Sprite.__init__(self)
        self.image = transform.rotate(transform.scale(image.load(img_bullet), (90, 90)), 90)
        self.rect = self.image.get_rect()
        self.rect.x = args['x']
        self.rect.y = args['y']
        self.add(gun_clip)

def create_walls():
    Wall(x = 50, y = 150, width = 480,  height = 20, color = C_GREEN)
    Wall(x = 700, y = 0, width = 20, height = 100, color = C_GREEN)
    Wall(x = 470, y = 280, width = 250, height = 20, color = C_GREEN)
    Wall(x = -200, y = 380, width = 150, height = 20, color = C_GREEN)
    Wall(x = -200, y = 540, width = 5600, height = 20, color = C_FLOOR)
    Wall(x = 200, y = 310, width = 300, height = 20, color = C_GREEN)
    Wall(x = 800, y = 180, width = 325, height = 20, color = C_GREEN)
    Wall(x = 1111, y = 60, width = 20, height = 1100, color = C_GREEN)
    Wall(x = 3000, y = win_height / 2, width = 20, height = win_height, color = C_BLACK)
    Wall(x = -200, y = win_height / 2, width = 20, height = win_height, color = C_BLACK)
    Wall(x = 5400, y = win_height / 2, width = 20, height = win_height, color = C_BLACK)

def create_enemies():
    Enemy(x = 50, y = 440)
    Enemy(x = 800, y = 440)
    Enemy(x = 500, y = 440)
    Enemy(x = 800, y = 80)

def change_gun(gun):
    reload_time = True
    reload_counter = 0
    for item in gun_clip:
        item.kill()
    robin.gun = gun
    for i in range(robin.pistol_clip if gun == 'pistol' else robin.shotgun_clip):
        gun_clip.add(Patron(x = i * 20 + 20, y = win_height - 40))

def show_text(text, seconds, color):
    temp_color = [0,0,0]
    window.fill(C_BLACK)
    display.update()
    for ap in range(int(seconds * 60 / 4)):
        if temp_color[0] < color[0]:
            temp_color[0] += int(color[0] / (seconds * 60 / 4))
        if temp_color[1] < color[1]:
            temp_color[1] += int(color[1] / (seconds * 60 / 4))
        if temp_color[2] < color[2]:
            temp_color[2] += int(color[2] / (seconds * 60 / 4))
        rtext = font.SysFont("Corbel", 72, True).render(text, True, temp_color, C_BLACK)
        window.blit(rtext, (win_width / 2 - rtext.get_width() / 2, win_height / 2 - rtext.get_height() / 2))
        display.update()
        delayer.tick(60)
    for kek in range(int(60 * seconds / 2)):
        rtext = font.SysFont("Corbel", 72, True).render(text, True, C_WHITE, C_BLACK)
        window.blit(rtext, (win_width / 2 - rtext.get_width() / 2, win_height / 2 - rtext.get_height() / 2))
        display.update()
        delayer.tick(60)
    for ap in range(int(seconds * 60 / 4)):
        if temp_color[0] > 0:
            temp_color[0] -= int(color[0] / (seconds * 60 / 4))
        if temp_color[1] > 0:
            temp_color[1] -= int(color[1] / (seconds * 60 / 4))
        if temp_color[2] > 0:
            temp_color[2] -= int(color[2] / (seconds * 60 / 4))
        rtext = font.SysFont("Corbel", 72, True).render(text, True, temp_color, C_BLACK)
        window.blit(rtext, (win_width / 2 - rtext.get_width() / 2, win_height / 2 - rtext.get_height() / 2))
        display.update()
        delayer.tick(60)

# Запуск игры
display.set_caption("GangGang")
window = display.set_mode((800, 600)) 
win_width = display.Info().current_w  # получаем ширину окна
win_height = display.Info().current_h  # получаем высоту окна

left_bound = win_width / 2 - 50 # границы, за которые персонаж не выходит (начинает ехать фон)
right_bound = win_width / 2 + 50

shift = 50
back = transform.scale(image.load(img_file_back), (win_width, win_height))

all_sprites = sprite.Group()
barriers = sprite.Group()
enemies = sprite.Group()
bullets = sprite.Group()
gun_clip = sprite.Group()

robin = Hero()
all_sprites.add(robin)

change_gun('pistol')
create_walls()
create_enemies()

pr = Princess(x = win_width + 150, y = win_height - 140)
all_sprites.add(pr)


run = True
finished = False
pause = False
reload_time = True
reload_counter = 0

show_text("Level 1", 3, C_WHITE)

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_q:
                run = False
            if e.key == K_r and finished:
                reload_time = True
                reload_counter = 0
                for item in all_sprites:
                    item.kill()
                for item in gun_clip:
                    item.kill()
                create_walls()
                create_enemies()
                shift = 50
                robin = Hero()
                all_sprites.add(robin)
                change_gun('pistol')
                pr = Princess(x = win_width + 500, y = win_height - 140)
                all_sprites.add(pr)
                finished = False
            if e.key == K_ESCAPE and not finished:
                if pause:
                    pause = False
                    mixer.music.unpause()
                elif not pause:
                    pause = True
                    mixer.music.pause()
                    window.blit(pause_text, (win_width / 2 - pause_text.get_width() / 2 , win_height / 2 - pause_text.get_height() / 2))
                    display.update()
            if not pause and not finished:
                if e.key == K_r:
                    if (robin.gun == 'pistol' and len(gun_clip) != 6) or (robin.gun == 'shotgun' and len(gun_clip) != 2):
                        reload_time = True
                    else:
                        imposible_reload.play()
                if e.key == K_1:
                    change_gun('pistol')
                elif e.key == K_2:
                    change_gun('shotgun')
                elif e.key == K_LEFT or e.key == K_a:
                    robin.update_direction('left')
                    robin.x_speed = -5
                elif e.key == K_RIGHT or e.key == K_d:
                    robin.update_direction('right')
                    robin.x_speed = 5
                elif e.key == K_UP or e.key == K_w:
                    robin.jump(-7)
                elif e.key == K_SPACE:
                    robin.fire()
        elif e.type == KEYUP:
            if e.key == K_LEFT:
                robin.x_speed = 0
            elif e.key == K_RIGHT:
                robin.x_speed = 0
    if not pause:
        if not finished:
            all_sprites.update()
            if sprite.spritecollide(robin, enemies, False):
                robin.kill()
            sprite.groupcollide(bullets, enemies, True, True)
            sprite.groupcollide(bullets, barriers, True, False)
            if (robin.rect.x > right_bound and robin.x_speed > 0 or robin.rect.x < left_bound and robin.x_speed < 0): 
                # при выходе влево или вправо переносим изменение в сдвиг экрана
                shift -= robin.x_speed 
                # перемещаем на общий сдвиг все спрайты (и отдельно бомбы, они ж в другом списке):
                for s in all_sprites:
                    s.rect.x -= robin.x_speed # сам robin тоже в этом списке, поэтому его перемещение визуально отменится
            
            if reload_time:
                if reload_counter == 0:
                    if (robin.gun == 'pistol' and len(gun_clip) == 6) or (robin.gun == 'shotgun' and len(gun_clip) == 2):
                        reload_time = False
                    else:
                        if robin.gun == 'pistol':
                            robin.pistol_clip += 1
                            pistol_reload.play()
                        elif robin.gun == 'shotgun':
                            robin.shotgun_clip += 1
                            shotgun_reload.play()
                        reload_counter = 40
                        gun_clip.add(Patron(x = len(gun_clip) * 20 + 20, y = win_height - 40))
                else:
                    reload_counter -= 1
            
            # рисуем фон со сдвигом
            local_shift = shift % win_width
            window.blit(back, (local_shift, 0))
            if local_shift != 0:
                window.blit(back, (local_shift - win_width, 0))
        
            all_sprites.draw(window)
            gun_clip.draw(window)

            if sprite.collide_rect(robin, pr):
                finished = True
                window.fill(C_BLACK)
                window.blit(win, (win_width / 2 - win.get_width() / 2, 250))
                window.blit(restart_text, (win_width / 2 - restart_text.get_width() / 2, 350))

            if robin not in all_sprites or robin.rect.top > win_height:
                finished = True           
                window.fill(C_BLACK)
                window.blit(game_over, (win_width / 2 - game_over.get_width() / 2, 250))
                window.blit(restart_text, (win_width / 2 - restart_text.get_width() / 2, 350))
        display.update()
    delayer.tick(60)