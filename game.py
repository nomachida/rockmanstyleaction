import pygame
import sys
import json
import math

# 設定ファイルを読み込む
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Pygameを初期化
pygame.init()

# 画面設定
WINDOW_WIDTH = config['features']['graphics']['resolution']['width']
WINDOW_HEIGHT = config['features']['graphics']['resolution']['height']
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(config['game_name'])

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# プレイヤーの設定
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = config['features']['graphics']['sprites']['player']['size'][0]
        self.height = config['features']['graphics']['sprites']['player']['size'][1]
        self.speed = config['features']['physics']['player']['speed']
        self.jump_force = config['features']['physics']['player']['jump_force']
        self.velocity_y = 0
        self.is_jumping = False
        self.health = config['features']['gameplay']['player']['max_health']
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)
        # HPバーを描画
        hp_width = (self.health / config['features']['gameplay']['player']['max_health']) * self.width
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, hp_width, 5))

# 敵の設定
class Enemy:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.width = config['features']['graphics']['sprites']['enemies'][enemy_type]['size'][0]
        self.height = config['features']['graphics']['sprites']['enemies'][enemy_type]['size'][1]
        self.health = config['features']['gameplay']['enemies'][enemy_type]['health']
        self.speed = config['features']['gameplay']['enemies'][enemy_type]['speed'] if enemy_type == 'patrol' else 0
        self.direction = 1
        self.shot_timer = 0
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def update(self):
        if self.type == 'patrol':
            self.x += self.speed * self.direction * 0.016
            if abs(self.x - self.initial_x) > 100:
                self.direction *= -1
        self.rect.x = self.x
        self.rect.y = self.y
        
    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

# プラットフォームの設定
class Platform:
    def __init__(self, x, y, width, height, platform_type='platform'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = platform_type
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)

# ゲームの初期化
player = Player(100, 100)
platforms = []
enemies = []

# プラットフォームを追加
for platform_data in config['features']['stage']['platforms']:
    platform = Platform(
        platform_data['x'],
        platform_data['y'],
        platform_data['width'],
        platform_data['height'],
        platform_data['type']
    )
    platforms.append(platform)

# 敵を追加
for enemy_data in config['features']['stage']['enemies']:
    enemy = Enemy(
        enemy_data['x'],
        enemy_data['y'],
        enemy_data['type']
    )
    enemies.append(enemy)

# ゲームループ
clock = pygame.time.Clock()
running = True

while running:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not player.is_jumping:
                player.velocity_y = -player.jump_force
                player.is_jumping = True
    
    # キー入力処理
    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_LEFT]:
        dx = -player.speed
    if keys[pygame.K_RIGHT]:
        dx = player.speed
    
    # プレイヤーの移動
    player.move(dx * 0.016, player.velocity_y * 0.016)
    
    # 重力の適用
    player.velocity_y += config['features']['physics']['gravity'] * 0.016
    
    # 地面との衝突判定
    for platform in platforms:
        if player.rect.colliderect(platform.rect):
            if player.velocity_y > 0:
                player.rect.bottom = platform.rect.top
                player.y = player.rect.y
                player.velocity_y = 0
                player.is_jumping = False
            elif player.velocity_y < 0:
                player.rect.top = platform.rect.bottom
                player.y = player.rect.y
                player.velocity_y = 0
    
    # 敵の更新
    for enemy in enemies:
        enemy.update()
        if player.rect.colliderect(enemy.rect):
            player.health -= config['features']['gameplay']['enemies'][enemy.type]['damage']
    
    # 画面のクリア
    screen.fill(WHITE)
    
    # オブジェクトの描画
    for platform in platforms:
        platform.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    player.draw(screen)
    
    # 画面の更新
    pygame.display.flip()
    
    # フレームレートの制御
    clock.tick(60)

# ゲームの終了
pygame.quit()
sys.exit()
