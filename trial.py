import cv2
import pygame
import numpy as np
import sys
import math
import threading
import random
# 初始化 Pygame
pygame.init()
pygame.mixer.init()
# 加载音效
jump_sound = pygame.mixer.Sound('file\\dash.wav')  # 加载音效文件
game_over_sound = pygame.mixer.Sound('file\\gameover.wav')  # 加载游戏结束的音效
bullet_sound = pygame.mixer.Sound('file2\\waao.wav')# 加载子弹发射音效
bullet_sound.set_volume(0.3)
activate_sound = pygame.mixer.Sound('file2\\activate.wav')
bullet_huge_sound = pygame.mixer.Sound('file2\\si!.wav')
bullet_huge_sound.set_volume(1.6)
bullet_waao_sound = pygame.mixer.Sound('file2\\cao.wav')
bullet_waao_sound.set_volume(2)
# 设置屏幕尺寸
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# 加载图像
original_player_image = pygame.image.load('file\\player.png')  # 玩家角色的原始图像
player_image = pygame.transform.scale(original_player_image, (50, 50))  # 缩放为 50x50
bullet_image = pygame.image.load('file\\bullet.png')
bullet_image = pygame.transform.scale(bullet_image,(16,10))
bullet_huge_image = pygame.image.load('file\\bullet.png')
bullet_huge_image = pygame.transform.scale(bullet_huge_image,(96,60))
#monster_image = pygame.image.load('file\\monster_none.png')  # 怪物角色图像
#monster_image = pygame.transform.scale(monster_image, (100, 125))  # 缩放怪物图像为 50x50
angry_image = pygame.image.load('file\\angry_mother.png')
angry_image = pygame.transform.scale(angry_image,(130,163))
bullet_waao_image = pygame.image.load('file\\waao.png')
bullet_waao_image = pygame.transform.scale(bullet_waao_image,(150,176))
# 定义颜色
WHITE = (255, 255, 255)
PLATFORM_COLOR = (0, 128, 0)  # 平台的颜色
monster_list = [] #初始化怪物列表
# 玩家类
class Player:
    def __init__(self):
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 100
        self.speed_y = 0
        self.on_ground = False
        self.speed_x = 3.5  # 调整水平移动速度为3.5
        self.alive_time = 0.0  # 玩家存活时间
        self.skill_active = False
        self.speed_jump = -14
        self.skill_duration = 3  # 技能持续时间3秒
        self.cooldown_time = 20.0  # 冷却时间20秒
        self.cooldown_timer = 0.0  # 冷却计时器
        self.active_timer = 0  # 技能效果计时器
        self.font_cd = pygame.font.Font(None, 36)  # 冷却字体设置
        self.strengthen_active = True
    def activate_skill(self):
        if not self.skill_active and self.cooldown_timer <= 0:
            self.speed_x = 4.5  # 提升水平移动速度
            self.speed_jump = -17
            self.skill_active = True
            self.active_timer = self.skill_duration  # 开始计时
            self.cooldown_timer = self.cooldown_time  # 重置冷却计时
            activate_sound.play()
    def jump(self):
        if self.on_ground:
            self.speed_y = self.speed_jump  # 调整跳跃力度
            self.on_ground = False
            jump_sound.play()
    def move(self, direction):
        self.rect.x += direction * self.speed_x
        # 边界检查
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width
    def update(self, platforms):
        self.rect.y += self.speed_y
        self.speed_y += 1  # 重力影响
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.speed_y > 0 and self.rect.bottom >= platform.rect.top and self.rect.bottom <= 10 + platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.speed_y = 0
                elif self.speed_y < 0 and self.rect.top <= platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.speed_y = 0
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height:
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.on_ground = True
            self.speed_y = 0
        # 更新冷却计时和技能持续时间
        if self.skill_active:
            self.active_timer -= 1 / 60  # 每帧减少技能持续时间
            if self.active_timer <= 0:
                self.skill_active = False
                self.speed_x = 3.5  # 恢复原始水平移动速度
                self.speed_jump= -14  # 恢复原始跳跃力度
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1 / 60  # 每帧减少冷却时间
        # 显示冷却时间
    def draw(self, screen):
        # 显示冷却时间
        if self.cooldown_timer > 0:
            cooldown_text = self.font_cd.render(f"Cooldown: {self.cooldown_timer:.2f}s", True, (128, 0, 128))
            screen.blit(cooldown_text, (10, SCREEN_HEIGHT - 30))  # 在左下角显示冷却时间
# 怪物类
class Monster:
    def __init__(self,monster_image,speed=1.2,hp=200,slowspeed=0.9):
        self.image = monster_image
        self.original_hp=hp
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH - self.rect.width
        self.rect.y = 0
        self.original_speed = speed
        self.speed = speed
        self.hp=hp
        self.slowspeed=slowspeed
        self.colliderate=False
        self.attached = False
    def update(self, player):
        if self.hp>0:
            # 计算怪物与玩家之间的距离
            dx = player.rect.x - self.rect.x
            dy = player.rect.y - self.rect.y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:  # 确保不除以零
                # 计算单位向量
                direction_x = dx / distance
                direction_y = dy / distance
                # 更新怪物的位置
                self.rect.x += direction_x * self.speed
                self.rect.y += direction_y * self.speed
            self.colliderate = False
            # 边界检查
            if self.rect.x < 0:
                self.rect.x = 0
            if self.rect.x > SCREEN_WIDTH - self.rect.width:
                self.rect.x = SCREEN_WIDTH - self.rect.width
            for platform in platforms:
                if self.rect.colliderect(platform.rect) and not (isinstance(self,Monster_dog) and self.rect.width>120) :
                    self.speed=self.slowspeed
                    self.colliderate = True
            if self.colliderate == False:
                self.speed = self.original_speed
class Monster_dog(Monster):
    def __init__(self,monster_image,speed=1.3,hp=650):
        super().__init__(monster_image, hp=hp)
        self.timer = 0  # 用于跟踪时间
        self.scale_timer = 0  # 用于跟踪放大时间
        self.is_scaled = False  # 记录当前是否放大
        self.scale_duration = 2  # 放大持续时间
        self.total_duration = 5  # 总周期时间
        self.scale_start_time = 0  # 放大开始的时刻
    def update(self, player):
        self.timer += 1 / 60
        if self.is_scaled:
            self.scale_timer += 1 / 60  # 更新放大计时器
            if self.scale_timer >= self.scale_duration:  # 两秒后恢复原大小
                self.is_scaled = False
                center = self.rect.center
                self.image = pygame.transform.scale(self.image,
                                                     (self.image.get_width() // 2, self.image.get_height() // 2))
                self.rect = self.image.get_rect(center=center)  # 保持中心不变
        if self.timer >= self.total_duration:
            self.timer = 0  # 重置总计时器
            self.scale_start_time = random.uniform(0, 3)  # 随机决定放大开始的时刻
            self.scale_timer = 0  # 重置放大计时器
        # 判断是否在放大阶段
        if self.timer >= self.scale_start_time and not self.is_scaled and self.timer < self.scale_start_time + self.scale_duration:
            self.is_scaled = True  # 开始放大
            center = self.rect.center
            self.image = pygame.transform.scale(self.image,
                                                 (self.image.get_width() * 2, self.image.get_height() * 2))
            self.rect = self.image.get_rect(center=center)   # 保持中心不变
        super().update(player)
class Monster_mother(Monster):
    def __init__(self, monster_image, angry_image=angry_image,speed=1.3, hp=650):
        self.angry_image = angry_image
        super().__init__(monster_image, speed, hp)
        self.original_size = (self.rect.width, self.rect.height)
        self.is_invisible = False
        self.invisibility_timer = 0
        self.stop_tracking_timer = 0
        self.is_stopped = False
        self.half = False #血量是否过半
    def update(self, player):
        if self.hp > 0:
            if self.hp <= self.original_hp / 2 and not self.half:
                self.half = True
                self.speed*=1.3
                self.original_speed*=1.3
                self.slowspeed*=1.3
                self.is_stopped = True
                self.stop_tracking_timer = pygame.time.get_ticks() + 3000
            if self.is_stopped:
                if pygame.time.get_ticks() >= self.stop_tracking_timer:
                    self.is_stopped = False
                    self.image = self.angry_image
                    self.rect=self.image.get_rect()
                    self.rect.x = random.choice([0,SCREEN_WIDTH-self.rect.width])
                    self.rect.y = random.choice([0,SCREEN_HEIGHT-self.rect.height])
            # 开始隐形效果
            if not self.is_stopped and not self.is_invisible and self.image==self.angry_image:
                if pygame.time.get_ticks() % 5000 < 100:  # 每隔5秒隐形3秒
                    self.is_invisible = True
                    self.invisibility_timer = pygame.time.get_ticks() + 3000
            if self.is_invisible:
                if pygame.time.get_ticks() >= self.invisibility_timer:
                    self.is_invisible = False
            if not self.is_stopped:
                super().update(player)
class Monster_chestnut(Monster):
    def __init__(self,monster_image,speed=1.3,hp=650,slowspeed=0.9):
        super().__init__(monster_image,speed,hp,slowspeed)
        self.activate_timer=0.0
        self.activate_cycle = 10000 #释放周期 10s
    def update(self,player,monster_list = monster_list):
        if pygame.time.get_ticks()>self.activate_timer:
            self.activate_timer = pygame.time.get_ticks() + self.activate_cycle
            small_monster=Monster(pygame.transform.scale(pygame.image.load('file\\monster_chestnut.png'), (30, 30)),speed=1.7,hp=10,slowspeed = 1.25)
            small_monster.rect.x = random.choice([SCREEN_WIDTH - small_monster.rect.width,0])
            small_monster.rect.y = random.choice([SCREEN_HEIGHT-small_monster.rect.height,0])
            monster_list.append(small_monster)
        super().update(player)
# 平台类
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
    def draw(self, surface):
        pygame.draw.rect(surface, PLATFORM_COLOR, self.rect)
class Bullet:
    def __init__(self, x, y, target_x, target_y,bullet_image,bullet_sound=bullet_sound,penetrate=False,hit=10,speed=15):
        self.hit = hit
        self.speed = 15  # 子弹的移动速度
        self.image = bullet_image  # 子弹图像
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        # 计算子弹的移动方向（单位向量）
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        self.direction_x = dx / distance
        self.direction_y = dy / distance
        self.fire = True  # 标记子弹为发射状态
        bullet_sound.play()
        self.penetrate = penetrate
    def update(self, monster_list, platforms):
        # 更新子弹的位置，沿着计算的方向移动
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed
        # 检测子弹是否碰到怪物
        for monster in monster_list:
            if self.rect.colliderect(monster.rect):
                if isinstance(monster,Monster_mother):
                    if not monster.is_invisible:
                        monster.hp -= self.hit
                        return False
                else:
                    monster.hp-= self.hit
                    return False  # 子弹失效
        # 检测子弹是否碰到平台
        if not self.penetrate:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    return False  # 子弹失效
        # 检查子弹是否超出屏幕
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
            return False  # 子弹失效
        return True  # 子弹有效
class Bullet_waao(Bullet):
    def __init__(self, x, y, target_x, target_y,bullet_image,bullet_sound,penetrate=True,hit=40,speed=20):
        super().__init__(x, y, target_x, target_y,bullet_image,bullet_sound,penetrate,hit,speed)
    def update(self, monster_list,platforms):
        # 更新子弹的位置，沿着计算的方向移动
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed
        for monster in monster_list:
            if self.rect.colliderect(monster.rect):
                if not isinstance(monster,Monster_mother) or isinstance(monster,Monster_mother) and not monster.is_invisible:
                    if monster.attached == False:
                        monster.hp -= self.hit
                        monster.attached = True
                    if monster:#击退怪物
                        monster.rect.x += self.direction_x * (self.speed+monster.speed)
                        monster.rect.y += self.direction_y * (self.speed+monster.speed)
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
            monster.attached = False
            return False  # 子弹失效
        return True  # 子弹有效
# 创建平台列表
platforms = [
    Platform(100, 520, 600, 10),
    Platform(200, 450, 150, 10),
    Platform(400, 375, 200, 10),
    Platform(600, 300, 150, 10),
    Platform(800, 210, 200, 10),
    Platform(300, 150, 150, 10),
    Platform(500, 220, 100, 10),
    Platform(700, 120, 200, 10),
    Platform(400, 60, 210, 10),
    Platform(800,360,150,10),
    Platform(220,350,70,10),
    Platform(800,500,120,10),
    Platform(1000,440,150,10),
    Platform(90 ,240,140,10),
    Platform(980,300,100,10)
]
# 创建玩家
player = Player()
# 字体设置
font = pygame.font.Font(None, 36)
# 游戏主循环
clock = pygame.time.Clock()
paused = False  # 初始化暂停状态
show_player_info = False  # 默认为隐藏
choose=False
bullet_list=[]
#选择难度和敌人
while not choose:
    screen.fill(WHITE)  # 填充背景颜色
    lines = [
        "Choose which one you want to encounter:",
        "[1]: MOTHER",
        "[2]: DOG",
        "[3]: GOD"
    ]
    for i, line in enumerate(lines):
        choose_char_surface = font.render(line, True, (0, 0, 0))
        screen.blit(choose_char_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50 + i * 40))
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_Monster = 1
                    choose=True
                elif event.key == pygame.K_2:
                    selected_Monster = 2
                    choose = True
                elif event.key == pygame.K_3:
                    selected_Monster = 3
                    choose = True
    pygame.display.flip()  # 更新屏幕
    clock.tick(60)  # 控制帧率
choose=False
while not choose:
    screen.fill(WHITE)  # 填充背景颜色
    lines = [
        "Choose your game difficulty:",
        "[1]: Easy",
        "[2]: Hard",
        "[3]: ",
    ]
    for i, line in enumerate(lines):
        if line == "[3]: ":  # 检查是否是"[3]: N"
            choose_char_surface = font.render(line, True, (0, 0, 0))  # 默认黑色
            screen.blit(choose_char_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50 + i * 40))

            nightmare_surface = font.render("NIGHTMARE", True, (255, 0, 0))  # 红色
            screen.blit(nightmare_surface,
                        (SCREEN_WIDTH // 2 - 200 + font.size(line)[0], SCREEN_HEIGHT // 2 - 50 + i * 40))  # 直接跟在后面
        else:
            choose_char_surface = font.render(line, True, (0, 0, 0))  # 默认黑色
            screen.blit(choose_char_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50 + i * 40))
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_difficulty = 1
                    choose=True
                elif event.key == pygame.K_2:
                    selected_difficulty = 2
                    choose = True
                elif event.key == pygame.K_3:
                    selected_difficulty = 3
                    choose = True
    pygame.display.flip()  # 更新屏幕
    clock.tick(60)  # 控制帧率
if selected_Monster ==1:
    monster_image = pygame.image.load('file\\monster_none.png')  # 怪物角色图像
    monster_image = pygame.transform.scale(monster_image, (100, 125))  # 缩放怪物图像为 50x50
elif selected_Monster==2:
    monster_image = pygame.image.load('file\\monster_dog.png')  # 怪物角色图像
    monster_image = pygame.transform.scale(monster_image, (120, 120))  # 缩放怪物图像为 50x50
elif selected_Monster==3:
    monster_image = pygame.image.load('file\\monster_chestnut.png')  # 怪物角色图像
    monster_image = pygame.transform.scale(monster_image, (80, 80))  # 缩放怪物图像为 50x50
start_ticks = pygame.time.get_ticks()  # 获取游戏开始时间
countdown = 5.0  # 倒计时5秒
game_over = False  # 游戏是否结束
game_win = False
show_alive_time = False  # 是否显示存活时间
monster = None  # 初始化怪物为 None
call_for_fire = False
call_for_fire_count=0.0
win_countdown_count=0.0
bullet_waao = None
def monster_choose(m,n):
    if n == 1:
        return Monster(monster_image)
    if n == 2:
        return Monster(monster_image,speed=1.25,hp=450)
    if (m,n)==(3,3):
        return Monster_chestnut(monster_image)
    if(m,n) == (2,3):
        return Monster_dog(monster_image)
    if (m,n) == (1,3):
        return Monster_mother(monster_image)
pygame.key.stop_text_input()
while True:
    if not game_over:
        # 倒计时处理
        seconds = (pygame.time.get_ticks() - start_ticks) / 1000.0  # 获取过去的秒数
        countdown_display = max(0, int(countdown - int(seconds)))  # 倒计时剩余时间
        if countdown_display == 0 and monster is None:  # 倒计时结束后生成怪物
            monster = monster_choose(selected_Monster,selected_difficulty)
            monster_list.append(monster)
            show_alive_time = True  # 倒计时结束后开始显示存活时间
        if not monster is None:
            if monster.hp <= 0:
                game_win = True
        if show_alive_time == True and countdown_display==0:
            player.alive_time=seconds
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.jump()
            if event.key == pygame.K_LCTRL or event.key== pygame.K_RCTRL:
                show_player_info = not show_player_info
            if event.key == pygame.K_s :
                player.speed_y = max(player.speed_y - 3, 0)
            if event.key == pygame.K_q :
                player.activate_skill()
            if event.key == pygame.K_p :
                paused = not paused  # 切换暂停状态
        if event.type == pygame.MOUSEBUTTONDOWN :  # 右键
            if event.button == 1:  # 左键点击
                if not call_for_fire: #开火间隔控制为0.4秒每发
                    call_for_fire = True
                    mouse_x, mouse_y = event.pos  # 获取鼠标点击位置
                    if not player.skill_active:
                        bulletnew = Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y,bullet_image)  # 从玩家中心位置发射子弹
                        bullet_list.append(bulletnew)  # 添加到子弹列表
                    if player.skill_active:
                        bulletnew = Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y,bullet_huge_image,bullet_huge_sound,True,20)  # 从玩家中心位置发射子弹
                        bullet_list.append(bulletnew)  # 添加到子弹列表
                    call_for_fire_count = pygame.time.get_ticks()
            if event.button == 3:  #右键
                if player.strengthen_active:
                    player.strengthen_active = False
                    mouse_x, mouse_y = event.pos
                    bullet_waao = Bullet_waao(player.rect.centerx, player.rect.centery, mouse_x, mouse_y,bullet_waao_image,bullet_waao_sound)
                    bullet_list.append(bullet_waao)
    if not paused and not game_over and not game_win:
        if call_for_fire_count <= -400+pygame.time.get_ticks(): #判断开火冷却是否结束
            call_for_fire = False
        # 移动玩家
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.move(-1)
        if keys[pygame.K_d]:
            player.move(1)
        if not bullet_list == []:
            # 更新子弹
            for bullet in bullet_list[:]:
                if not bullet.update(monster_list, platforms):  # 更新子弹并检查是否有效
                    bullet_list.remove(bullet)  # 移除失效子弹
        # 更新玩家位置
        player.update(platforms)
        # 更新怪物位置
        if monster:
            for current_monster in monster_list[:]:
                current_monster.update(player)
                if current_monster.hp<=0:
                    monster_list.remove(current_monster)
        # 碰撞检测：玩家与怪物
        if monster and monster.hp>0:
            for current_monster in monster_list:
                if player.rect.colliderect(current_monster.rect):
                    game_over = True
                    pygame.mixer.Sound.play(game_over_sound)  # 播放游戏结束音效
    # 绘制
    screen.fill(WHITE)
    for platform in platforms:
        platform.draw(screen)
    # 绘制玩家
    screen.blit(player.image, player.rect)
    # 倒计时显示
    font_size = 100  # 修改字体大小
    font_color = (255, 0, 0)
    font_instruction_size = 40
    if countdown_display > 0:
        # 显示提示文本
        font = pygame.font.Font(None, font_instruction_size)
        instructions_text = "Use WASD to control your player, press left and right to fire, use Q to activate"
        instructions_surface = font.render(instructions_text, True, font_color)
        # 设置显示位置，可以根据需要调整坐标 (x, y)
        screen.blit(instructions_surface, (SCREEN_WIDTH // 2 - instructions_surface.get_width() // 2, 100))
        font = pygame.font.Font(None, font_size)
        countdown_surface = font.render(f'{countdown_display}', True, font_color)
        screen.blit(countdown_surface, (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 20))
    font = pygame.font.Font(None, 36)
    # 绘制怪物
    if monster:
        for monster_ in monster_list:
            if not isinstance(monster_,Monster_mother):
                screen.blit(monster_.image, monster_.rect)
            else:
                if not monster_.is_invisible:  # 仅在怪物可见时绘制
                    screen.blit(monster_.image, monster_.rect)
        # 显示怪物的 HP
        if not (isinstance(monster,Monster_mother) and monster.is_invisible):
            hp_font = pygame.font.Font(None, 36)
            hp_surface = hp_font.render(f'HP: {monster.hp}', True, (255, 0, 0))  # 红色字体
            hp_position = (monster.rect.x, monster.rect.y + monster.rect.height)  # 在怪物下方显示 HP
            screen.blit(hp_surface, hp_position)
    # 绘制子弹
    if not bullet_list==[]:
        for bullet in bullet_list:
            screen.blit(bullet.image, bullet.rect)
    # 显示玩家存活时间
    if show_alive_time:  # 仅在倒计时结束后显示存活时间
        alive_time_surface = font.render(f'Time: {player.alive_time-countdown:.2f}s', True, (0, 0, 0))
        screen.blit(alive_time_surface, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40))
    player.draw(screen)
    # 游戏结束显示
    if game_over:
        game_over_font = pygame.font.Font(None, 100)
        game_over_surface = game_over_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
    if game_win:
        game_win_font = pygame.font.Font(None, 100)
        game_win_surface = game_win_font.render("YOU WIN!!!", True, (255, 0, 0))
        screen.blit(game_win_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
        if win_countdown_count==0:
            win_countdown_count=pygame.time.get_ticks()
    if show_player_info:
        info_font = pygame.font.Font(None,20)
        player_info = f'Player: ({int(player.rect.x)}, {int(player.rect.y)}) speed: {player.speed_x}, {player.speed_y}'
        font_surface = info_font.render(player_info, True, (0, 0, 0))
        screen.blit(font_surface, (10, 10))
        for platform in platforms:
            corner_info = (f'TL({platform.rect.topleft}), TR({platform.rect.topright}), '
                           f'BL({platform.rect.bottomleft}), BR({platform.rect.bottomright})')
            corner_surface = info_font.render(corner_info, True, (0, 0, 0))
            text_position = (
            platform.rect.centerx - corner_surface.get_width() // 2, platform.rect.top - corner_surface.get_height())
            screen.blit(corner_surface, text_position)
        if monster:
            monster_info = f'Monster: ({int(monster.rect.x)}, {int(monster.rect.y)}) speed: {monster.speed}'
            monster_surface = info_font.render(monster_info, True, (0, 0, 0))
            screen.blit(monster_surface, (SCREEN_WIDTH - 250, 10))
    if game_win and win_countdown_count <= -1500+pygame.time.get_ticks(): #胜利后1.5秒进入胜利cg
        break
    pygame.display.flip()
    clock.tick(60)
pygame.init()
# 打开视频文件
if selected_difficulty == 1:
    video_path = "one.mp4"
elif selected_difficulty ==2:
    video_path = "two.mp4"
else:
    video_path = "three.mp4"
cap = cv2.VideoCapture(video_path)
def play_audio(audio_file):
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
# 获取视频的宽度和高度
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))-500
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))-300
# 设置 Pygame 显示窗口
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
# 创建一个线程来播放音频
audio_thread = threading.Thread(target=play_audio, args=("file2\\fuck.mp3",))
audio_thread.start()  # 开始播放音频
# 视频播放主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.mixer.music.stop()
    # 读取视频帧
    ret, frame = cap.read()
    if not pygame.mixer.music.get_busy():
        break
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    # 将 BGR 转换为 RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 顺时针旋转 90 度
    frame = np.rot90(frame, k=-1)  # 旋转
    # 水平翻转帧
    frame = np.flip(frame, axis=1)
    # 创建 Pygame 表面
    frame_surface = pygame.surfarray.make_surface(frame)
    # 绘制帧到屏幕
    screen.blit(frame_surface, (0, 0))
    pygame.display.flip()
    # 控制帧率
    clock.tick(30)
# 等待音频线程结束
audio_thread.join()
# 释放视频捕获对象
cap.release()
pygame.quit()
