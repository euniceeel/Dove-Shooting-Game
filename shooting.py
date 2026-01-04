import pygame
import sys
import random
import os

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("5단계: 점수외 아이템")
clock = pygame.time.Clock()
FPS = 60

# 색상
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# 플레이어 설정
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_speed = 8
player_health = 3

bullet_width, bullet_height = 5, 10
bullet_speed = -10
bullets = []

enemy_width, enemy_height = 50, 50
enemy_speed = 3
enemy_list = []
enemy_timer = 0

items = []
item_timer = 0

score = 0
font = pygame.font.SysFont("Arial", 24)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "images")


def load_image(name):
    path = os.path.join(ASSETS_DIR, name)
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return None


player_img = load_image("player.png")
enemy_img = load_image("enemy.png")
item_img = load_image("item.png")
bullet_img = load_image("bullet.png")


def scale_image_to_max(img, max_w, max_h):
    if img is None:
        return None
    w, h = img.get_size()
    scale = min(1.0, max_w / w, max_h / h)
    if scale < 1.0:
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        return pygame.transform.smoothscale(img, new_size)
    return img


PLAYER_MAX_W, PLAYER_MAX_H = WIDTH // 6, HEIGHT // 6
ENEMY_MAX_W, ENEMY_MAX_H = WIDTH // 8, HEIGHT // 8
BULLET_MAX_W, BULLET_MAX_H = WIDTH // 20, HEIGHT // 20
ITEM_MAX_W, ITEM_MAX_H = WIDTH // 20, HEIGHT // 20

player_img = scale_image_to_max(player_img, PLAYER_MAX_W, PLAYER_MAX_H)
bullet_img = scale_image_to_max(bullet_img, BULLET_MAX_W, BULLET_MAX_H)
enemy_img = scale_image_to_max(enemy_img, ENEMY_MAX_W, ENEMY_MAX_H)
item_img = scale_image_to_max(item_img, ITEM_MAX_W, ITEM_MAX_H)

player_width, player_height = (50, 50) if player_img is None else player_img.get_size()
enemy_width, enemy_height = (50, 50) if enemy_img is None else enemy_img.get_size()
item_width, item_height = (30, 30) if item_img is None else item_img.get_size()
bullet_width, bullet_height = (5, 10) if bullet_img is None else bullet_img.get_size()


def detect_collision(rect1, rect2):
    return rect1.colliderect(rect2)


def create_item():
    return [random.randint(0, WIDTH - 30), 0]


def game_loop():
    global player_x, bullets, enemy_list, enemy_timer, player_health, item_timer, items, score
    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        if keys[pygame.K_SPACE]:
            if len(bullets) < 5:
                bx = player_x + player_width // 2 - bullet_width // 2
                by = player_y
                bullets.append([bx, by])

        player_x = max(0, min(WIDTH - player_width, player_x))
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        if player_img:
            screen.blit(player_img, (player_x, player_y))
        else:
            pygame.draw.rect(screen, BLUE, player_rect)

        # 총알 업데이트
        new_bullets = []
        for b in bullets:
            b[1] += bullet_speed
            # if b[1] > 0:
            if b[1] + bullet_height > 0:
                new_bullets.append(b)

        bullets = new_bullets

        # 총알 그리기
        # for b in bullets:
        #    pygame.draw.rect(screen, YELLOW, (b[0], b[1], bullet_width, bullet_height))

        for b in bullets:
            if bullet_img:
                screen.blit(bullet_img, (b[0], b[1]))
            else:
                pygame.draw.rect(screen, YELLOW, (b[0], b[1], bullet_width, bullet_height))

        if enemy_timer == 0:
            x_pos = random.randint(0, WIDTH - enemy_width)
            enemy_list.append([x_pos, 0])
        enemy_timer = (enemy_timer + 1) % 30

        new_enemy_list = []
        for e in enemy_list:
            new_e = [e[0], e[1] + enemy_speed]
            if new_e[1] < HEIGHT:
                new_enemy_list.append(new_e)
        enemy_list = new_enemy_list

        # draw enemies after movement/update
        for e in enemy_list:
            if enemy_img:
                screen.blit(enemy_img, (e[0], e[1]))
            else:
                pygame.draw.rect(screen, RED, (e[0], e[1], enemy_width, enemy_height))

        # for e in enemy_list[:]:
        #    pygame.draw.rect(screen, RED, (e[0], e[1], enemy_width, enemy_height))

        for e in enemy_list[:]:
            enemy_rect = pygame.Rect(e[0], e[1], enemy_width, enemy_height)
            if detect_collision(player_rect, enemy_rect):
                player_health -= 1
                enemy_list.remove(e)
                if player_health <= 0:
                    running = False

        for b in bullets[:]:
            bullet_rect = pygame.Rect(b[0], b[1], bullet_width, bullet_height)
            for e in enemy_list[:]:
                enemy_rect = pygame.Rect(e[0], e[1], enemy_width, enemy_height)
                if detect_collision(bullet_rect, enemy_rect):
                    bullets.remove(b)
                    enemy_list.remove(e)
                    score += 10
                    break

        if item_timer == 0:
            items.append(create_item())
        item_timer = (item_timer + 1) % 300
        # items = [[i[0], i[1] + 3] for i in items if i[1] < HEIGHT]
        items = [[i[0], i[1] + 3] for i in items if i[1] < HEIGHT - item_height]
        # for i in items:
        #    pygame.draw.rect(screen, GREEN, (i[0], i[1], 30, 30))

        for i in items[:]:
            if item_img:
                screen.blit(item_img, (i[0], i[1]))
            else:
                pygame.draw.rect(screen, GREEN, (i[0], i[1], item_width, item_height))

        # item pickup: restore collision handling so player collects items and gains health
        for it in items[:]:
            item_rect = pygame.Rect(it[0], it[1], item_width, item_height)
            if detect_collision(item_rect, player_rect):
                player_health += 1
                items.remove(it)

        health_text = font.render(f"Health: {player_health}", True, WHITE)
        screen.blit(health_text, (10, 10))

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 40))

        pygame.display.flip()
        clock.tick(FPS)


game_loop()