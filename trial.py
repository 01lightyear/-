import pygame
import sys
import random
import math
# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 加载音效
jump_sound = [pygame.mixer.Sound('waao.wav'), pygame.mixer.Sound('bing.wav')]  # 加载音效文件
game_over_sound = pygame.mixer.Sound('gameover.wav')  # 加载游戏结束的音效

# 设置屏幕尺寸
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 加载玩家和怪物图像
original_player_image = pygame.image.load('player.png')  # 玩家角色的原始图像
player_image = pygame.transform.scale(original_player_image, (50, 50))  # 缩放为 50x50

monster_image = pygame.image.load('monster_none.png')  # 怪物角色图像
monster_image = pygame.transform.scale(monster_image, (100, 125))  # 缩放怪物图像为 50x50

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
        self.speed_x = 3  # 调整水平移动速度为3
        self.alive_time = 0.0  # 玩家存活时间

    def jump(self):
        if self.on_ground:
            self.speed_y = -14  # 调整跳跃力度为-14
            self.on_ground = False
            random.choice(jump_sound).play()

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
    def __init__(self,monster_image,speed=1.2,hp=100):
        self.image = monster_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH - self.rect.width
        self.rect.y = 0
        self.speed = speed
        self.hp=hp

    def update(self, player):
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
# 平台类
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, PLATFORM_COLOR, self.rect)

# 创建平台列表
platforms = [
    Platform(100, 550, 600, 10),
    Platform(150, 450, 100, 10),
    Platform(300, 350, 200, 10),
    Platform(500, 250, 150, 10),
    Platform(200, 150, 400, 10)
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
        "[1]: easy",
        "[2]: hard",
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
# 倒计时相关
start_ticks = pygame.time.get_ticks()  # 获取游戏开始时间
countdown = 5.0  # 倒计时5秒
game_over = False  # 游戏是否结束
show_alive_time = False  # 是否显示存活时间

monster = None  # 初始化怪物为 None
while True:
    if not game_over:
        # 倒计时处理
        seconds = (pygame.time.get_ticks() - start_ticks) / 1000.0  # 获取过去的秒数
        countdown_display = max(0, int(countdown - int(seconds)))  # 倒计时剩余时间

        if countdown_display == 0 and monster is None:  # 倒计时结束后生成怪物
            monster = Monster(monster_image)
            show_alive_time = True  # 倒计时结束后开始显示存活时间
        if show_alive_time == True and countdown_display==0:
            player.alive_time=seconds


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_LCTRL or event.key== pygame.K_RCTRL:
                show_player_info = not show_player_info
            if event.key == pygame.K_DOWN :
                player.speed_y = max(player.speed_y - 3, 0)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # 右键
            paused = not paused  # 切换暂停状态

    if not paused and not game_over:
        # 移动玩家
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1)
        if keys[pygame.K_RIGHT]:
            player.move(1)

        # 更新玩家位置
        player.update(platforms)

        # 更新怪物位置
        if monster:
            monster.update(player)

        # 碰撞检测：玩家与怪物
        if monster and player.rect.colliderect(monster.rect):
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
        screen.blit(monster.image, monster.rect)

    # 显示玩家存活时间
    if show_alive_time:  # 仅在倒计时结束后显示存活时间
        alive_time_surface = font.render(f'Time: {player.alive_time-countdown:.2f}s', True, (0, 0, 0))
        screen.blit(alive_time_surface, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 40))

    # 游戏结束显示
    if game_over:
        game_over_font = pygame.font.Font(None, 100)
        game_over_surface = game_over_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
    if show_player_info:
        player_info = f'Player: ({int(player.rect.x)}, {int(player.rect.y)}) speed: {player.speed_x}, {player.speed_y}'
        font_surface = font.render(player_info, True, (0, 0, 0))
        screen.blit(font_surface, (10, 10))

        for platform in platforms:
            corner_info = (f'platform: TL({platform.rect.topleft}), TR({platform.rect.topright}), '
                           f'BL({platform.rect.bottomleft}), BR({platform.rect.bottomright})')
            corner_surface = font.render(corner_info, True, (0, 0, 0))
            screen.blit(corner_surface, (10, 40 + platforms.index(platform) * 30))

        if monster:
            monster_info = f'Monster: ({int(monster.rect.x)}, {int(monster.rect.y)}) speed: {monster.speed}'
            monster_surface = font.render(monster_info, True, (0, 0, 0))
            screen.blit(monster_surface, (SCREEN_WIDTH - 250, 10))
    pygame.display.flip()
    clock.tick(60)
