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
bullet_sound = pygame.mixer.Sound('waao.wav')# 加载子弹发射音效
bullet_sound.set_volume(0.3)
# 设置屏幕尺寸
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 加载图像
original_player_image = pygame.image.load('file\\player.png')  # 玩家角色的原始图像
player_image = pygame.transform.scale(original_player_image, (50, 50))  # 缩放为 50x50
bullet_image = pygame.image.load('file\\bullet.png')
bullet_image = pygame.transform.scale(bullet_image,(16,10))
#monster_image = pygame.image.load('file\\monster_none.png')  # 怪物角色图像
#monster_image = pygame.transform.scale(monster_image, (100, 125))  # 缩放怪物图像为 50x50
angry_image = pygame.image.load('file\\angry_mother.png')
angry_image = pygame.transform.scale(angry_image,(130,163))
# 定义颜色
WHITE = (255, 255, 255)
PLATFORM_COLOR = (0, 128, 0)  # 平台的颜色

# 玩家类
class Player:
    def __init__(self):
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 100
        self.speed_y = 0
        self.on_ground = False
        self.speed_x = 3.5  # 调整水平移动速度为3
        self.alive_time = 0.0  # 玩家存活时间

    def jump(self):
        if self.on_ground:
            self.speed_y = -14  # 调整跳跃力度为-14
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

# 怪物类
class Monster:
    def __init__(self,monster_image,speed=1.2,hp=200,slowspeed=0.8):
        self.image = monster_image
        self.original_hp=hp
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH - self.rect.width
        self.rect.y = 0
        self.speed = speed
        self.hp=hp
        self.slowspeed=slowspeed
    def update(self, player):
        if self.hp>0:
            print(self.hp)
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
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    self.speed=self.slowspeed
class Monster_mother(Monster):
    def __init__(self, monster_image, angry_image=angry_image,speed=1.2, hp=400):
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
                    print(self.rect.x,self.rect.y)
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
# 平台类
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, PLATFORM_COLOR, self.rect)
class Bullet:
    def __init__(self, x, y, target_x, target_y, hit=10):
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
    def update(self, monster, platforms):
        # 更新子弹的位置，沿着计算的方向移动
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed

        # 检测子弹是否碰到怪物
        if monster and self.rect.colliderect(monster.rect):
            if isinstance(monster,Monster_mother):
                if not monster.is_invisible:
                    monster.hp -= self.hit
                    return False
            else:
                monster.hp-= self.hit
                return False  # 子弹失效

        # 检测子弹是否碰到平台
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                return False  # 子弹失效
        # 检查子弹是否超出屏幕
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
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
    Platform(90,350,180,10),
    Platform(800,500,120,10),
    Platform(1000,440,150,10)
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
print(monster_image)
start_ticks = pygame.time.get_ticks()  # 获取游戏开始时间
countdown = 5.0  # 倒计时5秒
game_over = False  # 游戏是否结束
game_win = False
show_alive_time = False  # 是否显示存活时间
monster = None  # 初始化怪物为 None
call_for_fire = False
call_for_fire_count=0.0
win_countdown_count=0.0
def monster_choose(m,n):
    if (m,n) == (1,1):
        return Monster(monster_image)
    if (m,n) == (2,1):
        return Monster(monster_image)
    if(m,n) == (3,1):
        return Monster(monster_image)
    if (m,n) == (1,3):
        return Monster_mother(monster_image)
while True:
    if not game_over:
        # 倒计时处理
        seconds = (pygame.time.get_ticks() - start_ticks) / 1000.0  # 获取过去的秒数
        countdown_display = max(0, int(countdown - int(seconds)))  # 倒计时剩余时间

        if countdown_display == 0 and monster is None:  # 倒计时结束后生成怪物
            monster = monster_choose(selected_Monster,selected_difficulty)
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
            if event.key == pygame.K_UP:
                player.jump()
            if event.key == pygame.K_LCTRL or event.key== pygame.K_RCTRL:
                show_player_info = not show_player_info
            if event.key == pygame.K_DOWN :
                player.speed_y = max(player.speed_y - 3, 0)
        if event.type == pygame.MOUSEBUTTONDOWN :  # 右键
            if event.button == 3:
                paused = not paused  # 切换暂停状态
            if event.button == 1:  # 左键点击
                if not call_for_fire: #开火间隔控制为0.8秒每发
                    call_for_fire = True
                    mouse_x, mouse_y = event.pos  # 获取鼠标点击位置
                    bulletnew = Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y)  # 从玩家中心位置发射子弹
                    bullet_list.append(bulletnew)  # 添加到子弹列表
                    call_for_fire_count = pygame.time.get_ticks()
    if not paused and not game_over and not game_win:
        if call_for_fire_count <= -400+pygame.time.get_ticks(): #判断开火冷却是否结束
            call_for_fire = False
        # 移动玩家
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1)
        if keys[pygame.K_RIGHT]:
            player.move(1)
        if not bullet_list == []:
            # 更新子弹
            for bullet in bullet_list[:]:
                if not bullet.update(monster, platforms):  # 更新子弹并检查是否有效
                    bullet_list.remove(bullet)  # 移除失效子弹

        # 更新玩家位置
        player.update(platforms)

        # 更新怪物位置
        if monster:
            monster.update(player)

        # 碰撞检测：玩家与怪物
        if monster and player.rect.colliderect(monster.rect) and monster.hp>0:
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
    font = pygame.font.Font(None, font_size)
    if countdown_display > 0:
        countdown_surface = font.render(f'{countdown_display}', True, font_color)
        screen.blit(countdown_surface, (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 20))
    font = pygame.font.Font(None, 36)
    # 绘制怪物
    if monster:
        if not isinstance(monster,Monster_mother):
            screen.blit(monster.image, monster.rect)
        else:
            if not monster.is_invisible:  # 仅在怪物可见时绘制
                screen.blit(monster.image, monster.rect)
    # 绘制子弹
    if not bullet_list==[]:
        for bullet in bullet_list:
            screen.blit(bullet.image, bullet.rect)
    # 显示玩家存活时间
    if show_alive_time:  # 仅在倒计时结束后显示存活时间
        alive_time_surface = font.render(f'Time: {player.alive_time-countdown:.2f}s', True, (0, 0, 0))
        screen.blit(alive_time_surface, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40))

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
    if game_win and win_countdown_count <= -2500+pygame.time.get_ticks():
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
audio_thread = threading.Thread(target=play_audio, args=("file\\fuck.mp3",))
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
    if not ret:
        break  # 如果没有帧可读，退出循环
    # 将 BGR 转换为 RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 顺时针旋转 90 度
    frame = np.rot90(frame, k=-1)  # 旋转
    # 水平翻转帧（可选，根据需要）
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
