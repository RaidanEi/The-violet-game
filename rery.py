import pygame
import sys
import math
import random

# ======================== ИНИЦИАЛИЗАЦИЯ ========================
pygame.init()
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Пиксельная игра")
clock = pygame.time.Clock()
FPS = 60

# ======================== НАСТРОЙКИ ИЗОБРАЖЕНИЙ ========================
LEVEL_BG_IMAGES = [
    "pole.png",
    "pole2.png",
    "pole3.png",
    "pole4.png",
    "pole.png",
    "pole.png"
]

# Игрок: 90×110
PLAYER_IDLE_IMAGES = ["personag.png", "personag2.png"]
PLAYER_WALK_IMAGES = ["walk1.png", "walk2.png", "walk1.png"]
PLAYER_ATTACK_IMAGES = ["attack1.png", "attack2.png"]
PLAYER_DEATH_IMAGES = ["death1.png", "death2.png"]

# Враги: 90×110
ENEMY_WALK_IMAGES = ["vrag1.png", "vrag2.png", "vrag1.png"]
ENEMY_ATTACK_IMAGES = ["vrag3.png", "vrag2.png"]

# Босс: 140×160
BOSS_WALK_IMAGES = ["boss1.png", "boss2.png", "boss1.png"]
BOSS_ATTACK_IMAGES = ["boss1.png", "boss2.png", "boss1.png"]

# Снаряды: пуля 18×18, стрела 26×12
PLAYER_BULLET_IMAGE = "pula1.png"
ENEMY_ARROW_IMAGE = "pula2.png"

# Портал: 90×110
PORTAL_IMAGES = ["portal1.png", "portal2.png"]
MENU_BG_IMAGE = "menu.png"

WALL_IMAGE = "wall.png"

BG_COLORS = [
    (180, 160, 200),
    (150, 190, 220),
    (140, 140, 140),
    (130, 180, 140),
    (200, 80,  80),
    (180, 100, 100)
]

# ======================== ФУНКЦИИ ЗАГРУЗКИ ========================
def load_image(path, width, height, color=(255,255,255), text=""):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (width, height))
    except:
        surf = pygame.Surface((width, height))
        surf.fill(color)
        if text:
            font = pygame.font.Font(None, 24)
            txt = font.render(text, True, (0,0,0))
            surf.blit(txt, (width//2 - txt.get_width()//2, height//2 - txt.get_height()//2))
        return surf

def load_animation_frames(filenames, width, height, base_color, text_prefix):
    frames = []
    for i, fname in enumerate(filenames):
        color = tuple(min(255, c + i*15) for c in base_color)
        frames.append(load_image(fname, width, height, color, f"{text_prefix}{i+1}"))
    return frames

# ======================== НАСТРОЙКИ ПАРАМЕТРОВ ========================
PLAYER_SPEED = 5
PLAYER_HP = 100
BULLET_SPEED = 12
BULLET_DAMAGE = 25
ENEMY_SPEED = 1.0
ENEMY_HP = 50
ARROW_SPEED = 7
ARROW_DAMAGE = 15
ENEMY_ATTACK_COOLDOWN = 90
BOSS_HP_MULTIPLIER = 3
FINAL_BOSS_HP = 1000
FINAL_BOSS_SPEED = 0.6
FINAL_BOSS_ATTACK_COOLDOWN = 300

# ======================== КЛАССЫ ОБЪЕКТОВ ========================
class Bullet:
    def __init__(self, x, y, target_x, target_y, image):
        self.x = x
        self.y = y
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy) or 1
        self.vx = BULLET_SPEED * dx / dist
        self.vy = BULLET_SPEED * dy / dist
        self.image = image
        self.radius = image.get_width() // 2
        self.damage = BULLET_DAMAGE

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        surface.blit(self.image, (self.x - self.image.get_width()//2, self.y - self.image.get_height()//2))

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

class Arrow:
    def __init__(self, x, y, target_x, target_y, image):
        self.x = x
        self.y = y
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy) or 1
        self.vx = ARROW_SPEED * dx / dist
        self.vy = ARROW_SPEED * dy / dist
        self.image = image
        self.radius = image.get_width() // 2
        self.damage = ARROW_DAMAGE

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        surface.blit(self.image, (self.x - self.image.get_width()//2, self.y - self.image.get_height()//2))

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

class Wall:
    def __init__(self, x, y, w, h, image_path):
        self.rect = pygame.Rect(x, y, w, h)
        self.image = load_image(image_path, w, h, (100, 100, 100), "wall")

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 110  # увеличено
        self.height = 110
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP
        self.state = "idle"
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 8
        self.facing_right = True

        self.images = {
            "idle":   load_animation_frames(PLAYER_IDLE_IMAGES, self.width, self.height, (100,200,100), "idle"),
            "walk":   load_animation_frames(PLAYER_WALK_IMAGES, self.width, self.height, (100,100,200), "walk"),
            "attack": load_animation_frames(PLAYER_ATTACK_IMAGES, self.width, self.height, (200,100,100), "atk"),
            "death":  load_animation_frames(PLAYER_DEATH_IMAGES, self.width, self.height, (100,100,100), "die")
        }
        self.attack_timer = 0
        self.death_timer = 0

    def move(self, dx, dy, walls):
        if self.state in ["death"]:
            return
        new_x = self.x + dx
        rect_x = pygame.Rect(new_x, self.y, self.width, self.height)
        if not any(rect_x.colliderect(w.rect) for w in walls):
            self.x = max(0, min(WIDTH - self.width, new_x))

        new_y = self.y + dy
        rect_y = pygame.Rect(self.x, new_y, self.width, self.height)
        if not any(rect_y.colliderect(w.rect) for w in walls):
            self.y = max(0, min(HEIGHT - self.height, new_y))

        if dx != 0 or dy != 0:
            if self.state != "attack":
                self.state = "walk"
        else:
            if self.state != "attack":
                self.state = "idle"
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

    def attack(self):
        if self.state not in ["death"]:
            self.state = "attack"
            self.attack_timer = 15
            self.anim_index = 0

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.state = "death"
            self.anim_index = 0

    def update(self):
        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            frames = self.images[self.state]
            if frames:
                self.anim_index = (self.anim_index + 1) % len(frames)

        if self.state == "attack":
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.state = "idle"

        if self.state == "death":
            self.death_timer += 1

    def draw(self, surface):
        frames = self.images[self.state]
        if not frames:
            return
        frame = frames[self.anim_index % len(frames)]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (self.x, self.y))

        bar_w = self.width
        bar_h = 6
        fill = (self.hp / self.max_hp) * bar_w
        pygame.draw.rect(surface, (255,0,0), (self.x, self.y - 10, bar_w, bar_h))
        pygame.draw.rect(surface, (0,255,0), (self.x, self.y - 10, fill, bar_h))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_dead(self):
        return self.hp <= 0

class Enemy:
    def __init__(self, x, y, is_boss=False):
        self.x = x
        self.y = y
        self.width = 90    # увеличено
        self.height = 110
        self.hp = ENEMY_HP * (BOSS_HP_MULTIPLIER if is_boss else 1)
        self.max_hp = self.hp
        self.is_boss = is_boss
        self.speed = ENEMY_SPEED * (0.7 if is_boss else 1)
        self.attack_cooldown = ENEMY_ATTACK_COOLDOWN // 2 if is_boss else ENEMY_ATTACK_COOLDOWN
        self.cooldown = random.randint(0, self.attack_cooldown)
        self.preferred_distance = random.randint(200, 350)

        base_color = (255, 100, 100) if not is_boss else (180, 0, 0)
        self.walk_frames = load_animation_frames(ENEMY_WALK_IMAGES, self.width, self.height, base_color, "ewalk")
        self.attack_frames = load_animation_frames(ENEMY_ATTACK_IMAGES, self.width, self.height, (255,50,50), "eatk")

        self.state = "idle"
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 10
        self.attack_timer = 0

    def update(self, player_x, player_y, walls):
        if self.is_dead():
            return False
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)

        move_x, move_y = 0, 0
        if dist < self.preferred_distance - 50:
            if dist > 0:
                move_x = -(dx/dist) * self.speed
                move_y = -(dy/dist) * self.speed
        elif dist > self.preferred_distance + 50:
            if dist > 0:
                move_x = (dx/dist) * self.speed
                move_y = (dy/dist) * self.speed

        new_x = self.x + move_x
        rect_x = pygame.Rect(new_x, self.y, self.width, self.height)
        if not any(rect_x.colliderect(w.rect) for w in walls):
            self.x = max(0, min(WIDTH - self.width, new_x))

        new_y = self.y + move_y
        rect_y = pygame.Rect(self.x, new_y, self.width, self.height)
        if not any(rect_y.colliderect(w.rect) for w in walls):
            self.y = max(0, min(HEIGHT - self.height, new_y))

        moving = (not any(rect_x.colliderect(w.rect) for w in walls) and move_x != 0) or \
                 (not any(rect_y.colliderect(w.rect) for w in walls) and move_y != 0)

        if self.state == "attack":
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.state = "walk" if moving else "idle"
        else:
            self.state = "walk" if moving else "idle"

        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            if self.state == "walk":
                if self.walk_frames:
                    self.anim_index = (self.anim_index + 1) % len(self.walk_frames)
            elif self.state == "attack":
                if self.attack_frames:
                    self.anim_index = (self.anim_index + 1) % len(self.attack_frames)
            else:
                self.anim_index = 0

        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = self.attack_cooldown
            self.state = "attack"
            self.attack_timer = 20
            self.anim_index = 0
            return True
        return False

    def take_damage(self, dmg):
        self.hp -= dmg

    def draw(self, surface):
        if self.state == "attack":
            frames = self.attack_frames
        else:
            frames = self.walk_frames
        if frames:
            frame = frames[self.anim_index % len(frames)]
            surface.blit(frame, (self.x, self.y))

        bar_w = self.width
        bar_h = 6
        fill = (self.hp / self.max_hp) * bar_w
        pygame.draw.rect(surface, (255,0,0), (self.x, self.y - 10, bar_w, bar_h))
        pygame.draw.rect(surface, (0,255,0), (self.x, self.y - 10, fill, bar_h))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_dead(self):
        return self.hp <= 0

class FinalBoss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 200  # увеличено
        self.height = 200
        self.hp = FINAL_BOSS_HP
        self.max_hp = self.hp
        self.speed = FINAL_BOSS_SPEED
        self.attack_cooldown = FINAL_BOSS_ATTACK_COOLDOWN
        self.cooldown = random.randint(0, self.attack_cooldown)
        self.preferred_distance = random.randint(300, 450)

        self.walk_frames = load_animation_frames(BOSS_WALK_IMAGES, self.width, self.height, (180, 0, 0), "bwalk")
        self.attack_frames = load_animation_frames(BOSS_ATTACK_IMAGES, self.width, self.height, (255, 50, 50), "batk")

        self.state = "idle"
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 12
        self.attack_timer = 0
        self.attack_phase = 0

    def update(self, player_x, player_y, walls):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)

        move_x, move_y = 0, 0
        if dist < self.preferred_distance - 70:
            if dist > 0:
                move_x = -(dx/dist) * self.speed
                move_y = -(dy/dist) * self.speed
        elif dist > self.preferred_distance + 70:
            if dist > 0:
                move_x = (dx/dist) * self.speed
                move_y = (dy/dist) * self.speed

        new_x = self.x + move_x
        rect_x = pygame.Rect(new_x, self.y, self.width, self.height)
        if not any(rect_x.colliderect(w.rect) for w in walls):
            self.x = max(0, min(WIDTH - self.width, new_x))

        new_y = self.y + move_y
        rect_y = pygame.Rect(self.x, new_y, self.width, self.height)
        if not any(rect_y.colliderect(w.rect) for w in walls):
            self.y = max(0, min(HEIGHT - self.height, new_y))

        moving = (not any(rect_x.colliderect(w.rect) for w in walls) and move_x != 0) or \
                 (not any(rect_y.colliderect(w.rect) for w in walls) and move_y != 0)

        if self.state == "attack":
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.state = "walk" if moving else "idle"
        else:
            self.state = "walk" if moving else "idle"

        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            if self.state == "walk":
                if self.walk_frames:
                    self.anim_index = (self.anim_index + 1) % len(self.walk_frames)
            elif self.state == "attack":
                if self.attack_frames:
                    self.anim_index = (self.anim_index + 1) % len(self.attack_frames)
            else:
                self.anim_index = 0

        self.cooldown -= 1
        if self.cooldown <= 0:
            self.cooldown = self.attack_cooldown
            self.state = "attack"
            self.attack_timer = 30
            self.anim_index = 0
            self.attack_phase = (self.attack_phase + 1) % 3
            return True
        return False

    def take_damage(self, dmg):
        self.hp -= dmg

    def draw(self, surface):
        if self.state == "attack":
            frames = self.attack_frames
        else:
            frames = self.walk_frames
        if frames:
            frame = frames[self.anim_index % len(frames)]
            surface.blit(frame, (self.x, self.y))

        bar_w = self.width + 20
        bar_h = 8
        fill = (self.hp / self.max_hp) * bar_w
        pygame.draw.rect(surface, (255,0,0), (self.x - 10, self.y - 15, bar_w, bar_h))
        pygame.draw.rect(surface, (0,255,0), (self.x - 10, self.y - 15, fill, bar_h))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_dead(self):
        return self.hp <= 0

class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 150    # увеличено
        self.height = 200
        self.active = False
        self.frames = load_animation_frames(PORTAL_IMAGES, self.width, self.height, (150,0,255), "port")
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 15

    def activate(self):
        self.active = True

    def update(self):
        if self.active:
            self.anim_timer += 1
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                if self.frames:
                    self.anim_index = (self.anim_index + 1) % len(self.frames)

    def draw(self, surface):
        if self.active and self.frames:
            surface.blit(self.frames[self.anim_index], (self.x, self.y))
        elif not self.active and self.frames:
            img = self.frames[0].copy()
            img.set_alpha(80)
            surface.blit(img, (self.x, self.y))

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = (100, 100, 200)
        self.hover_color = (150, 150, 250)
        self.font = pygame.font.Font(None, 36)

    def draw(self, surface, mouse_pos):
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        txt = self.font.render(self.text, True, (255,255,255))
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    return self.action()
        return None

# ======================== ГЕНЕРАЦИЯ УРОВНЕЙ (стены толще) ========================
def create_walls_for_level(level_num):
    walls = []
    # Внешние границы – тонкие (20 px)
    walls.append(Wall(0, 0, 1000, 20, WALL_IMAGE))
    walls.append(Wall(0, 980, 1000, 20, WALL_IMAGE))
    walls.append(Wall(0, 0, 20, 1000, WALL_IMAGE))
    walls.append(Wall(980, 0, 20, 1000, WALL_IMAGE))

    # Внутренние стены – 110 px толщиной
    w = 110
    if level_num == 1:
        walls.append(Wall(150, 150, w, 400, WALL_IMAGE))
        walls.append(Wall(400, 500, 300, w, WALL_IMAGE))
        walls.append(Wall(700, 100, w, 350, WALL_IMAGE))
    elif level_num == 2:
        walls.append(Wall(150, 200, w, 400, WALL_IMAGE))
        walls.append(Wall(350, 400, 300, w, WALL_IMAGE))
        walls.append(Wall(800, 250, w, 400, WALL_IMAGE))
        walls.append(Wall(400, 700, 250, w, WALL_IMAGE))
    elif level_num == 3:
        walls.append(Wall(200, 250, w, 300, WALL_IMAGE))
        walls.append(Wall(500, 150, w, 350, WALL_IMAGE))
        walls.append(Wall(750, 500, 200, w, WALL_IMAGE))
        walls.append(Wall(300, 700, 300, w, WALL_IMAGE))
    elif level_num == 4:
        walls.append(Wall(150, 100, w, 250, WALL_IMAGE))
        walls.append(Wall(400, 350, 200, w, WALL_IMAGE))
        walls.append(Wall(750, 200, w, 350, WALL_IMAGE))
        walls.append(Wall(600, 700, 250, w, WALL_IMAGE))
    elif level_num == 5:
        walls.append(Wall(200, 100, w, 250, WALL_IMAGE))
        walls.append(Wall(450, 300, w, 350, WALL_IMAGE))
        walls.append(Wall(750, 500, w, 300, WALL_IMAGE))
        walls.append(Wall(300, 600, 200, w, WALL_IMAGE))
    elif level_num == 6:
        walls.append(Wall(150, 200, w, 300, WALL_IMAGE))
        walls.append(Wall(400, 400, 200, w, WALL_IMAGE))
        walls.append(Wall(800, 200, w, 400, WALL_IMAGE))
    return walls

def get_safe_position(walls, width, height, min_x=40, max_x=960, min_y=40, max_y=960):
    for _ in range(1000):
        x = random.randint(min_x, max_x - width)
        y = random.randint(min_y, max_y - height)
        rect = pygame.Rect(x, y, width, height)
        if not any(rect.colliderect(w.rect) for w in walls):
            return x, y
    return WIDTH//2 - width//2, HEIGHT//2 - height//2

# ======================== ИГРОВОЙ КЛАСС ========================
class Game:
    def __init__(self):
        self.state = "menu"
        self.level = 1
        self.wins = 0
        self.load_wins()
        self.menu_buttons = []
        self.death_buttons = []
        self.win_buttons = []

        # Размеры снарядов под новый масштаб
        self.bullet_img = load_image(PLAYER_BULLET_IMAGE, 40, 40, (255,255,0), "bullet")
        self.arrow_img = load_image(ENEMY_ARROW_IMAGE, 40, 40, (255,100,100), "arrow")

        self.level_bgs = []
        for i, fname in enumerate(LEVEL_BG_IMAGES):
            self.level_bgs.append(load_image(fname, WIDTH, HEIGHT, BG_COLORS[i], f"level{i+1}"))

        self.final_boss = None
        self.reset_level()

    def load_wins(self):
        try:
            with open("wins.txt", "r") as f:
                self.wins = int(f.read().strip())
        except:
            self.wins = 0

    def save_wins(self):
        with open("wins.txt", "w") as f:
            f.write(str(self.wins))

    def reset_level(self):
        self.walls = create_walls_for_level(self.level)
        # Игрок 90×110
        spawn_x, spawn_y = get_safe_position(self.walls, 90, 110, min_x=30, max_x=880, min_y=30, max_y=880)
        self.player = Player(spawn_x, spawn_y)

        self.bullets = []
        self.arrows = []
        self.enemies = []
        self.final_boss = None

        # Портал 90×110
        portal_x, portal_y = get_safe_position(self.walls, 90, 110, min_x=700, max_x=880, min_y=100, max_y=800)
        self.portal = Portal(portal_x, portal_y)

        if self.level == 6:
            # Босс 140×160
            bx, by = get_safe_position(self.walls, 140, 160, min_x=200, max_x=700, min_y=200, max_y=700)
            self.final_boss = FinalBoss(bx, by)
        elif self.level == 5:
            num_common = 2
            for _ in range(num_common):
                ex, ey = get_safe_position(self.walls, 90, 110)
                self.enemies.append(Enemy(ex, ey))
            bx, by = get_safe_position(self.walls, 90, 110, min_x=400, max_x=800, min_y=200, max_y=600)
            self.enemies.append(Enemy(bx, by, is_boss=True))
        else:
            num_common = 2 + self.level
            for _ in range(num_common):
                ex, ey = get_safe_position(self.walls, 90, 110)
                self.enemies.append(Enemy(ex, ey))

        self.portal.active = False

    def handle_playing(self, events):
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()

        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= PLAYER_SPEED
        if keys[pygame.K_s]: dy += PLAYER_SPEED
        if keys[pygame.K_a]: dx -= PLAYER_SPEED
        if keys[pygame.K_d]: dx += PLAYER_SPEED
        self.player.move(dx, dy, self.walls)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.attack()
                bx = self.player.x + self.player.width//2
                by = self.player.y + self.player.height//2
                self.bullets.append(Bullet(bx, by, mx, my, self.bullet_img))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.portal.active and self.portal.rect().colliderect(self.player.rect()):
                        self.next_level()

        self.player.update()
        if self.player.is_dead() and self.player.state == "death" and self.player.death_timer > 60:
            self.state = "death"

        for enemy in self.enemies:
            if not enemy.is_dead():
                shot = enemy.update(self.player.x + self.player.width//2,
                                    self.player.y + self.player.height//2,
                                    self.walls)
                if shot:
                    ax = enemy.x + enemy.width//2
                    ay = enemy.y + enemy.height//2
                    self.arrows.append(Arrow(ax, ay,
                                            self.player.x + self.player.width//2,
                                            self.player.y + self.player.height//2,
                                            self.arrow_img))

        if self.final_boss and not self.final_boss.is_dead():
            if self.final_boss.update(self.player.x + self.player.width//2,
                                      self.player.y + self.player.height//2,
                                      self.walls):
                ax = self.final_boss.x + self.final_boss.width//2
                ay = self.final_boss.y + self.final_boss.height//2
                num_arrows = 1 if self.final_boss.attack_phase != 2 else 3
                spread = 0.2 if self.final_boss.attack_phase == 1 else 0
                for i in range(num_arrows):
                    angle_offset = -spread + (i * spread * 2 / (num_arrows-1)) if num_arrows > 1 else 0
                    base_angle = math.atan2(self.player.y + self.player.height//2 - ay,
                                            self.player.x + self.player.width//2 - ax)
                    angle = base_angle + angle_offset
                    target_x = ax + math.cos(angle) * 100
                    target_y = ay + math.sin(angle) * 100
                    self.arrows.append(Arrow(ax, ay, target_x, target_y, self.arrow_img))

        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.off_screen():
                self.bullets.remove(bullet)
                continue
            hit_wall = any(wall.rect.collidepoint(bullet.x, bullet.y) for wall in self.walls)
            if hit_wall:
                self.bullets.remove(bullet)
                continue

            hit_enemy = False
            for enemy in self.enemies[:]:
                if not enemy.is_dead() and enemy.rect().collidepoint(bullet.x, bullet.y):
                    enemy.take_damage(bullet.damage)
                    if enemy.is_dead():
                        self.enemies.remove(enemy)
                    hit_enemy = True
                    break
            if hit_enemy:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue

            if self.final_boss and not self.final_boss.is_dead() and self.final_boss.rect().collidepoint(bullet.x, bullet.y):
                self.final_boss.take_damage(bullet.damage)
                if bullet in self.bullets:
                    self.bullets.remove(bullet)

        for arrow in self.arrows[:]:
            arrow.update()
            if arrow.off_screen():
                self.arrows.remove(arrow)
                continue
            hit_wall = any(wall.rect.collidepoint(arrow.x, arrow.y) for wall in self.walls)
            if hit_wall:
                self.arrows.remove(arrow)
                continue
            if self.player.rect().collidepoint(arrow.x, arrow.y):
                self.player.take_damage(arrow.damage)
                if arrow in self.arrows:
                    self.arrows.remove(arrow)

        all_dead = all(e.is_dead() for e in self.enemies)
        if self.final_boss and not self.final_boss.is_dead():
            all_dead = False
        if not self.enemies and not self.final_boss:
            all_dead = True

        self.portal.active = all_dead and (self.final_boss is None or self.final_boss.is_dead())
        self.portal.update()

        if self.portal.active and self.portal.rect().colliderect(self.player.rect().inflate(50, 50)):
            font = pygame.font.Font(None, 36)
            hint = font.render("Нажми Enter", True, (255,255,0))
            screen.blit(hint, (self.portal.x - 20, self.portal.y - 40))

    def next_level(self):
        if self.level < 6:
            self.level += 1
            self.reset_level()
        else:
            self.wins += 1
            self.save_wins()
            self.state = "win"
            self.win_buttons = [
                Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "МЕНЮ", self.go_to_menu)
            ]

    def go_to_menu(self):
        self.state = "menu"
        self.level = 1
        self.reset_level()
        self._create_menu_buttons()

    def _create_menu_buttons(self):
        btn_w = 180
        btn_h = 50
        gap = 20
        total_height = 3 * btn_h + 2 * gap
        start_y = (HEIGHT - total_height) // 2
        x = 80
        self.menu_buttons = [
            Button(x, start_y, btn_w, btn_h, "Играть", self.start_game),
            Button(x, start_y + btn_h + gap, btn_w, btn_h, f"Победы: {self.wins}", None),
            Button(x, start_y + 2*(btn_h + gap), btn_w, btn_h, "Выход", self.exit_game)
        ]

    def revive(self):
        self.state = "playing"
        self.reset_level()

    def draw_playing(self):
        screen.blit(self.level_bgs[self.level-1], (0, 0))
        for wall in self.walls:
            wall.draw(screen)
        self.portal.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)
        if self.final_boss:
            self.final_boss.draw(screen)
        for arrow in self.arrows:
            arrow.draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)
        self.player.draw(screen)

        font = pygame.font.Font(None, 48)
        level_text = font.render(f"Уровень {self.level}", True, (255,255,255))
        screen.blit(level_text, (15, 15))

    def draw_death(self):
        screen.fill((30, 0, 0))
        font_large = pygame.font.Font(None, 90)
        death_text = font_large.render("СМЕРТЬ", True, (255, 0, 0))
        screen.blit(death_text, (WIDTH//2 - death_text.get_width()//2, HEIGHT//2 - 120))
        if not self.death_buttons:
            self.death_buttons = [
                Button(WIDTH//2 - 120, HEIGHT//2, 240, 70, "ВОЗРОДИТСЯ", self.revive)
            ]
        mouse = pygame.mouse.get_pos()
        for btn in self.death_buttons:
            btn.draw(screen, mouse)

    def draw_win(self):
        screen.fill((0, 50, 0))
        font_large = pygame.font.Font(None, 90)
        win_text = font_large.render("ПОБЕДА", True, (255, 215, 0))
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 120))
        for btn in self.win_buttons:
            btn.draw(screen, pygame.mouse.get_pos())

    def draw_menu(self):
        bg = load_image(MENU_BG_IMAGE, WIDTH, HEIGHT, (50, 50, 80), "МЕНЮ")
        screen.blit(bg, (0,0))
        if not self.menu_buttons:
            self._create_menu_buttons()
        mouse = pygame.mouse.get_pos()
        for btn in self.menu_buttons:
            btn.draw(screen, mouse)

        font_title = pygame.font.Font(None, 72)
        title = font_title.render("Violet Storm", True, (255,255,255))
        title_x = WIDTH//2 - title.get_width()//2
        title_y = 60
        screen.blit(title, (title_x, title_y))

    def start_game(self):
        self.state = "playing"
        self.reset_level()

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.exit_game()

        if self.state == "menu":
            for event in events:
                for btn in self.menu_buttons:
                    btn.handle_event(event)
        elif self.state == "playing":
            self.handle_playing(events)
        elif self.state == "death":
            for event in events:
                for btn in self.death_buttons:
                    btn.handle_event(event)
        elif self.state == "win":
            for event in events:
                for btn in self.win_buttons:
                    btn.handle_event(event)
        return events

    def run(self):
        while True:
            self.handle_events()
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.draw_playing()
            elif self.state == "death":
                self.draw_death()
            elif self.state == "win":
                self.draw_win()
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()