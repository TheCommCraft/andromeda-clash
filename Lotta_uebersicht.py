import pygame
import sys
import random
import math

# Pygame initialisieren
pygame.init()

# Konstanten definieren
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Farben definieren (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Spielfenster erstellen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Grundlagen")

# Clock-Objekt für FPS-Kontrolle
clock = pygame.time.Clock()

# Schriftarten
font_small = pygame.font.SysFont("Arial", 24)
font_big = pygame.font.SysFont("Arial", 48)

# Sound laden
try:
    pygame.mixer.init()
    collision_sound = pygame.mixer.Sound("collision.wav")  # Platzhalter - eigene Datei verwenden
    background_music = pygame.mixer.Sound("background.wav")  # Platzhalter - eigene Datei verwenden
    # background_music.play(-1)  # Endlosschleife (-1)
except:
    print("Sound konnte nicht geladen werden - wird übersprungen")

# Bilder laden
try:
    player_img = pygame.image.load("player.png")  # Platzhalter - eigene Datei verwenden
    # player_img = pygame.transform.scale(player_img, (50, 50))  # Größe anpassen
except:
    # Wenn kein Bild vorhanden, erstellen wir ein einfaches Rechteck
    player_img = pygame.Surface((50, 50))
    player_img.fill(GREEN)


# Spieler-Klasse
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.score = 0
        
    def update(self):
        # Bewegung mit Tasten
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
            
        # Bildschirmgrenzen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


# Gegner-Klasse
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(20, 40)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.size)
        self.speed_x = random.randint(-3, 3)
        self.speed_y = random.randint(-3, 3)
        
        # Sicherstellen, dass die Gegner sich bewegen
        if self.speed_x == 0:
            self.speed_x = 1
        if self.speed_y == 0:
            self.speed_y = 1
            
    def update(self):
        # Bewegung
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Bildschirmgrenzen abprallen
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x *= -1
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.speed_y *= -1


# Sammelbares Objekt
class Collectible(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 15)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - 15)


# Button-Klasse für Menüs
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_surface = font_small.render(text, True, BLACK)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        surface.blit(self.text_surface, self.text_rect)
        
    def is_hovered(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False


# Spiel initialisieren
def initialize_game():
    # Sprite-Gruppen erstellen
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()
    
    # Spieler erstellen
    player = Player()
    all_sprites.add(player)
    
    # Gegner erstellen
    for i in range(5):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
    
    # Sammelobjekte erstellen
    for i in range(10):
        collectible = Collectible()
        all_sprites.add(collectible)
        collectibles.add(collectible)
    
    return all_sprites, enemies, collectibles, player


# Hauptmenü
def main_menu():
    title_text = font_big.render("Pygame Grundlagen", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    
    start_button = Button(SCREEN_WIDTH // 2 - 100, 250, 200, 50, "Spielen", GREEN, BLUE)
    quit_button = Button(SCREEN_WIDTH // 2 - 100, 350, 200, 50, "Beenden", RED, BLUE)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button.is_hovered(mouse_pos):
                    game_loop()
                elif quit_button.is_hovered(mouse_pos):
                    pygame.quit()
                    sys.exit()
                    
        mouse_pos = pygame.mouse.get_pos()
        start_button.is_hovered(mouse_pos)
        quit_button.is_hovered(mouse_pos)
                    
        screen.fill(BLACK)
        screen.blit(title_text, title_rect)
        start_button.draw(screen)
        quit_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)


# Game Over Bildschirm
def game_over(score):
    game_over_text = font_big.render("Game Over", True, RED)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    
    score_text = font_small.render(f"Punktzahl: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
    
    restart_button = Button(SCREEN_WIDTH // 2 - 100, 300, 200, 50, "Neustart", GREEN, BLUE)
    menu_button = Button(SCREEN_WIDTH // 2 - 100, 400, 200, 50, "Hauptmenü", YELLOW, BLUE)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button.is_hovered(mouse_pos):
                    game_loop()
                elif menu_button.is_hovered(mouse_pos):
                    main_menu()
        
        mouse_pos = pygame.mouse.get_pos()
        restart_button.is_hovered(mouse_pos)
        menu_button.is_hovered(mouse_pos)
        
        screen.fill(BLACK)
        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_text, score_rect)
        restart_button.draw(screen)
        menu_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)


# Hauptspiel-Schleife
def game_loop():
    all_sprites, enemies, collectibles, player = initialize_game()
    game_active = True
    
    # Timer für das Spiel (60 Sekunden)
    game_time = 60 * FPS  # 60 Sekunden in Frames
    
    while game_active:
        # Zeitlimit reduzieren
        game_time -= 1
        if game_time <= 0:
            game_over(player.score)
        
        # Events verarbeiten
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # ESC-Taste für Pause/Menü
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
        
        # Spiellogik
        all_sprites.update()
        
        # Kollisionserkennung: Spieler mit Gegnern
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            try:
                collision_sound.play()
            except:
                pass
            game_over(player.score)
        
        # Kollisionserkennung: Spieler mit Sammelobjekten
        collectible_hits = pygame.sprite.spritecollide(player, collectibles, True)
        for hit in collectible_hits:
            player.score += 1
            try:
                collision_sound.play()
            except:
                pass
            # Neues Sammelobjekt erstellen
            if len(collectibles) < 10:
                new_collectible = Collectible()
                all_sprites.add(new_collectible)
                collectibles.add(new_collectible)
        
        # Bildschirm zeichnen
        screen.fill(BLACK)
        
        # Hintergrund (Beispiel für eine einfache Animation)
        current_time = pygame.time.get_ticks()
        for i in range(20):
            size = 5 + math.sin(current_time / 500 + i) * 3
            pos_x = (SCREEN_WIDTH // 20) * i + 20
            pos_y = 50 + math.sin(current_time / 1000 + i * 0.5) * 30
            pygame.draw.circle(screen, BLUE, (int(pos_x), int(pos_y)), int(size))
        
        # Alle Sprites zeichnen
        all_sprites.draw(screen)
        
        # UI-Elemente
        score_text = font_small.render(f"Punktzahl: {player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        time_left = game_time // FPS
        time_text = font_small.render(f"Zeit: {time_left}s", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 120, 10))
        
        # Fortschrittsbalken für die Zeit
        time_bar_length = 200
        time_bar_height = 20
        time_percentage = game_time / (60 * FPS)
        current_bar_length = time_bar_length * time_percentage
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - time_bar_length - 10, 40, time_bar_length, time_bar_height), 2)
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - time_bar_length - 10, 40, current_bar_length, time_bar_height))
        
        pygame.display.flip()
        clock.tick(FPS)


# Spiel starten
if __name__ == "__main__":
    main_menu()
    