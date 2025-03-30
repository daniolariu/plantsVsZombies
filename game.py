import pygame
import random

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH = 130 * 9  # 9 columns * 130 pixels = 1170 pixels
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Superseed vs Crypto")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load background image (adjust path as needed)
background = pygame.image.load("assets/grass.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Define planting spots with adjusted coordinates
PLANTING_SPOTS = []
for row in range(5):
    for col in range(9):
        x = 130 * col  + 75  # Center of each 130px column
        y = 200 + row * 78  # Start lower (200) with 70px vertical spacing
        PLANTING_SPOTS.append((x, y))

# Function to create and resize sprite
def create_sprite(color, size, target_size=40):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (size // 2, size // 2), size // 2)
    return pygame.transform.scale(surface, (target_size, target_size))

# Plant sprites
plant_sprites = {
    "SeedShooter": pygame.transform.scale(pygame.image.load("assets/superseed.png").convert_alpha(), (45, 45)),
    "NutWall": create_sprite((139, 69, 19), 40),
    "VineBlaster": create_sprite((0, 100, 0), 40)
}

# Enemy sprites
enemy_sprites = {
    "BitcoinBot": [create_sprite((255, 215, 0), 40), create_sprite((255, 215, 0), 35)],
    "EthereumGhoul": [create_sprite((128, 128, 128), 40), create_sprite((128, 128, 128), 35)],
    "NFTZombie": [create_sprite((255, 0, 255), 40), create_sprite((255, 0, 255), 35)]
}

# Bullet and Superseed airdrop sprites
bullet_sprite = create_sprite((255, 255, 0), 10, 10)
superseed_sprite = pygame.transform.scale(pygame.image.load("assets/sun.png").convert_alpha(), (28,28))

# Plant class
class Plant:
    def __init__(self, x, y, plant_type):
        self.x = x
        self.y = y
        self.type = plant_type
        self.health = 100
        self.animation_frame = 0
        self.animation_timer = 0
        self.plant_stats = {
            "SeedShooter": {"cost": 50, "damage": 20, "cooldown": 60},
            "NutWall": {"cost": 75, "damage": 0, "cooldown": 0},
            "VineBlaster": {"cost": 100, "damage": 40, "cooldown": 90}
        }
        self.cooldown_timer = 0

    def draw(self):
        screen.blit(plant_sprites[self.type], (self.x - 20, self.y - 20))

    def update(self, bullets):
        self.animation_timer += 1
        if self.animation_timer >= 15:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        elif self.type != "NutWall" and self.cooldown_timer == 0:
            bullets.append(Bullet(self.x, self.y, self.plant_stats[self.type]["damage"]))
            self.cooldown_timer = self.plant_stats[self.type]["cooldown"]

# Bullet class
class Bullet:
    def __init__(self, x, y, damage):
        self.x = x
        self.y = y - 5
        self.speed = 5
        self.damage = damage

    def update(self):
        self.x += self.speed

    def draw(self):
        screen.blit(bullet_sprite, (self.x, self.y))

# Crypto Enemy class
class CryptoEnemy:
    def __init__(self):
        self.row = random.randint(0, 4)
        self.x = WIDTH
        self.y = PLANTING_SPOTS[self.row * 9][1]  # Align with row
        self.type = random.choice(["BitcoinBot", "EthereumGhoul", "NFTZombie"])
        self.speed = random.randint(1, 3)
        self.health = 100 if self.type == "BitcoinBot" else 150 if self.type == "EthereumGhoul" else 80
        self.animation_frame = 0
        self.animation_timer = 0

    def draw(self):
        screen.blit(enemy_sprites[self.type][self.animation_frame], (self.x - 20, self.y - 20))

    def update(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
        self.x -= self.speed

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

# Superseed Airdrop class
class SuperseedAirdrop:
    def __init__(self):
        spot = random.choice(PLANTING_SPOTS)
        self.x = spot[0]
        self.y = spot[1]
        self.value = random.randint(25, 75)

    def draw(self):
        screen.blit(superseed_sprite, (self.x - 10, self.y - 10))

# Game variables
superseeds = 200
plants = []
enemies = []
bullets = []
airdrops = []
spawn_timer = 0
airdrop_timer = 0
font = pygame.font.Font(None, 36)

ui_panel = pygame.Surface((WIDTH, 100))
ui_panel.fill((50, 50, 50))

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if event.button == 1 and y > 100:
                nearest_spot = min(PLANTING_SPOTS, key=lambda spot: ((spot[0] - x) ** 2 + (spot[1] - y) ** 2) ** 0.5)
                if ((nearest_spot[0] - x) ** 2 + (nearest_spot[1] - y) ** 2) ** 0.5 < 40:
                    for airdrop in airdrops[:]:
                        if airdrop.x == nearest_spot[0] and airdrop.y == nearest_spot[1]:
                            superseeds += airdrop.value
                            airdrops.remove(airdrop)
                            break
                    else:
                        if not any(p.x == nearest_spot[0] and p.y == nearest_spot[1] for p in plants):
                            if superseeds >= 50 and pygame.key.get_mods() & pygame.KMOD_SHIFT and superseeds >= 75:
                                plants.append(Plant(nearest_spot[0], nearest_spot[1], "NutWall"))
                                superseeds -= 75
                            elif superseeds >= 100 and pygame.key.get_mods() & pygame.KMOD_CTRL:
                                plants.append(Plant(nearest_spot[0], nearest_spot[1], "VineBlaster"))
                                superseeds -= 100
                            elif superseeds >= 50:
                                plants.append(Plant(nearest_spot[0], nearest_spot[1], "SeedShooter"))
                                superseeds -= 50

    # Spawn enemies
    spawn_timer += 1
    if spawn_timer >= 120:
        enemies.append(CryptoEnemy())
        spawn_timer = 0

    # Spawn Superseed airdrops
    airdrop_timer += 1
    if airdrop_timer >= 300 and len(airdrops) < 3:
        airdrops.append(SuperseedAirdrop())
        airdrop_timer = 0

    # Update game objects
    for plant in plants[:]:
        plant.update(bullets)

    for bullet in bullets[:]:
        bullet.update()
        if bullet.x > WIDTH:
            bullets.remove(bullet)

    for enemy in enemies[:]:
        enemy.update()
        if enemy.x < 0:
            enemies.remove(enemy)
            continue
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 10, 10)
            enemy_rect = pygame.Rect(enemy.x - 20, enemy.y - 20, 40, 40)
            if bullet_rect.colliderect(enemy_rect):
                if enemy.take_damage(bullet.damage):
                    enemies.remove(enemy)
                bullets.remove(bullet)
                break

    # Draw everything
    screen.blit(background, (0, 0))
    screen.blit(ui_panel, (0, 0))

    seeds_text = font.render(f"Superseeds: {superseeds}", True, WHITE)
    screen.blit(seeds_text, (10, 10))

    for i, (plant_type, sprite) in enumerate(plant_sprites.items()):
        screen.blit(sprite, (150 + i * 50, 30))
        cost_text = font.render(str(Plant(0, 0, plant_type).plant_stats[plant_type]["cost"]), True, WHITE)
        screen.blit(cost_text, (155 + i * 50, 70))

    instructions = font.render("Click plants above, then lawn to place; Click airdrops to collect", True, WHITE)
    screen.blit(instructions, (10, 80))

    for plant in plants:
        plant.draw()
    for bullet in bullets:
        bullet.draw()
    for enemy in enemies:
        enemy.draw()
    for airdrop in airdrops:
        airdrop.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()