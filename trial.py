import pygame
import sys
import random
from PIL import Image

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 加载音效
jump_sound = [pygame.mixer.Sound('waao.wav'), pygame.mixer.Sound('fenming.wav')] # 加载音效文件



# 设置屏幕尺寸
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 加载玩家图像并缩放
original_player_image = pygame.image.load('player.png')  # 玩家角色的原始图像
player_image = pygame.transform.scale(original_player_image, (50, 50))  # 缩放为 50x50

# 定义颜色
WHITE = (255, 255, 255)
PLATFORM_COLOR = (0, 128, 0)  # 平台的颜色
leftspeed=-1
rightspeed=1


# 玩家类
class Player:
    def __init__(self):
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height-100
        self.speed_y = 0
        self.on_ground = False
        self.speed_x = 3  # 调整水平移动速度为3
        self.music_played = False  # 添加一个标志位来跟踪音乐播放状态

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
        # 更新垂直位置
        self.rect.y += self.speed_y
        self.speed_y += 1  # 重力影响

        # 碰撞检测与平台
        for platform in platforms:
            if self.rect.colliderect(platform.rect):  # 检测与平台的碰撞
                if self.speed_y > 0 and self.rect.bottom >= platform.rect.top and self.rect.bottom<=10+platform.rect.bottom:
                    self.rect.bottom = platform.rect.top  # 置底
                    self.on_ground = True  # 站在平台上
                    self.speed_y = 0  # 重置垂直速度
                    #global point1
                    #point1 +=1

                elif self.speed_y < 0 and self.rect.top <= platform.rect.bottom:
                    self.rect.top = platform.rect.bottom  # 置顶
                    self.speed_y = 0  # 重置垂直速度
                    #global point2
                    #point2+=1

                if self.rect.right > platform.rect.left and self.rect.left < platform.rect.right:
                    if self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.bottom:
                        if self.rect.centerx < platform.rect.centerx:  # 从左侧碰撞
                            self.rect.right = platform.rect.left  # 置于平台左侧
                        else:  # 从右侧碰撞
                            self.rect.left = platform.rect.right  # 置于平台右侧

        # 碰撞检测与地面
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height:
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.on_ground = True
            self.speed_y = 0


# 平台类
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, PLATFORM_COLOR, self.rect)

    def corners(self):
        return [
            (self.rect.left, self.rect.top),         # 左上角
            (self.rect.right, self.rect.top),        # 右上角
            (self.rect.right, self.rect.bottom),     # 右下角
            (self.rect.left, self.rect.bottom)       # 左下角
        ]

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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # 右键
                paused = not paused  # 切换暂停状态

    if not paused:  # 只有在未暂停时更新游戏状态
        # 移动玩家
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(leftspeed)
            rightspeed=1# 使用左箭头向左移动
        if keys[pygame.K_RIGHT]:
            player.move(rightspeed)
            leftspeed=-1# 使用右箭头向右移动

        # 更新玩家位置
        player.update(platforms)  # 传入平台列表进行碰撞检测

    # 绘制
    # 绘制
    # 绘制
    screen.fill(WHITE)
    for platform in platforms:
        platform.draw(screen)  # 绘制平台
        # 显示平台的四个角坐标
        top_left = (platform.rect.left, platform.rect.top)
        top_right = (platform.rect.right, platform.rect.top)
        bottom_left = (platform.rect.left, platform.rect.bottom)
        bottom_right = (platform.rect.right, platform.rect.bottom)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(f'TL: {top_left}, TR: {top_right}, BL: {bottom_left}, BR: {bottom_right}', True,
                                   (0, 0, 0))
        screen.blit(text_surface, (platform.rect.x, platform.rect.y - 20))


    # 显示玩家的坐标和速度
    # 在游戏初始化部分添加字体
    #font = pygame.font.Font(None, 36)  # 创建一个字体对象，字号为36


    # 更新文本
    #text1 = font.render(f'Point1: {point1}', True, (0, 0, 0))  # 渲染point1
    #text2 = font.render(f'Point2: {point2}', True, (0, 0, 0))  # 渲染point2

    # 绘制文本
    #screen.blit(text1, (SCREEN_WIDTH - text1.get_width() - 10, 10))  # 绘制point1在右上角
   # screen.blit(text2, (SCREEN_WIDTH - text2.get_width() - 10, 10 + text1.get_height()))  # 绘制point2在point1下方

    font = pygame.font.Font(None, 24)
    player_info = (f'Bottom: {player.rect.bottom}, Top: {player.rect.top}, '
                   f'X: {player.rect.x}, Y: {player.rect.y}, '
                   f'Speed X: {player.speed_x}, Speed Y: {player.speed_y}')
    player_surface = font.render(player_info, True, (0, 0, 0))
    screen.blit(player_surface, (10, 10))

    screen.blit(player.image, player.rect)  # 绘制玩家

    pygame.display.flip()

    clock.tick(60)
