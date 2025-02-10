import pygame
from sys import exit
from random import randint, choice

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("CNN Learning Adventure")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
YELLOW = (255, 255, 0)
PLATFORM_COLOR = (150, 150, 150)

# Fonts
title_font = pygame.font.Font(None, 50)
info_font = pygame.font.Font(None, 36)
note_font = pygame.font.Font(None, 24)

class CNNGame:
    def __init__(self):
        self.stage = 0
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.stage_time = 30  # 30 seconds per stage
        self.stage_timer = 0
        
        # Player properties
        self.player = pygame.Rect(50, 450, 40, 40)
        self.player_velocity = 0
        self.move_speed = 5
        self.jump_power = -15
        self.on_ground = True
        
        # Platforms and obstacles
        self.reset_stage()
        self.obstacles = []
        self.spawn_obstacles()
        
        # Learning content
        self.stages = [
            {
                "title": "Stage 1: Input Layer",
                "task": "Collect blue blocks to learn about CNN input layer",
                "color": BLUE,
                "blocks": [],
                "notes": [
                    "Input Layer: Takes raw image data",
                    "Each pixel becomes a numerical value",
                    "RGB channels are processed separately",
                    "Resolution affects input size"
                ]
            },
            {
                "title": "Stage 2: Convolution Layer",
                "task": "Collect green blocks to learn about convolution",
                "color": GREEN,
                "blocks": [],
                "notes": [
                    "Convolution filters detect features",
                    "Kernels slide across the image",
                    "Different filters find different patterns",
                    "Features like edges are detected first"
                ]
            },
            {
                "title": "Stage 3: Pooling Layer",
                "task": "Collect red blocks to learn about pooling",
                "color": RED,
                "blocks": [],
                "notes": [
                    "Pooling reduces image dimensions",
                    "Max pooling keeps strongest features",
                    "Helps make detection position-invariant",
                    "Reduces computation needed"
                ]
            }
        ]
        
        self.collected_notes = []
        self.show_note = False
        self.note_timer = 0
        self.current_note = ""
        
        self.spawn_learning_blocks()

    def spawn_obstacles(self):
        if self.stage == 0:  # Stage 1: Simple moving obstacles
            self.obstacles = [
                {'rect': pygame.Rect(300, 450, 30, 30),
                 'speed': 3,
                 'direction': 1}
            ]
        elif self.stage == 1:  # Stage 2: More obstacles
            self.obstacles = [
                {'rect': pygame.Rect(300, 450, 30, 30),
                 'speed': 4,
                 'direction': 1},
                {'rect': pygame.Rect(500, 350, 30, 30),
                 'speed': 5,
                 'direction': -1}
            ]
        elif self.stage == 2:  # Stage 3: Fast obstacles
            self.obstacles = [
                {'rect': pygame.Rect(300, 450, 30, 30),
                 'speed': 6,
                 'direction': 1},
                {'rect': pygame.Rect(500, 350, 30, 30),
                 'speed': 6,
                 'direction': -1},
                {'rect': pygame.Rect(400, 250, 30, 30),
                 'speed': 7,
                 'direction': 1}
            ]

    def reset_stage(self):
        # Create platforms
        self.platforms = [
            pygame.Rect(0, 500, 800, 100),    # Ground
            pygame.Rect(200, 400, 100, 20),   # Left platform
            pygame.Rect(400, 300, 100, 20),   # Middle platform
            pygame.Rect(600, 350, 100, 20)    # Right platform
        ]

    def spawn_learning_blocks(self):
        if self.stage < len(self.stages):
            self.stages[self.stage]["blocks"] = []
            block_positions = [
                (250, 350),  # Above left platform
                (450, 250),  # Above middle platform
                (650, 300)   # Above right platform
            ]
            
            for pos in block_positions:
                block = pygame.Rect(pos[0], pos[1], 30, 30)
                self.stages[self.stage]["blocks"].append(block)

    def lose_life(self):
        if not self.invulnerable:
            self.lives -= 1
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            self.reset_player_position()
            if self.lives <= 0:
                self.game_over = True

    def reset_player_position(self):
        self.player.x = 50
        self.player.y = 450
        self.player_velocity = 0
        self.on_ground = True

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if not self.game_over:
            if keys[pygame.K_LEFT]:
                self.player.x -= self.move_speed
            if keys[pygame.K_RIGHT]:
                self.player.x += self.move_speed
            if keys[pygame.K_SPACE] and self.on_ground:
                self.player_velocity = self.jump_power
                self.on_ground = False
        else:
            if keys[pygame.K_r]:
                self.__init__()

        # Keep player in bounds
        self.player.x = max(0, min(self.player.x, 760))

    def update(self):
        if not self.game_over:
            current_time = pygame.time.get_ticks()
            
            # Update stage timer
            if self.stage_timer == 0:
                self.stage_timer = current_time
            elapsed_time = (current_time - self.stage_timer) / 1000
            time_left = max(0, self.stage_time - elapsed_time)
            
            # Time's up
            if time_left == 0:
                self.lose_life()
                self.stage_timer = current_time

            # Update invulnerability
            if self.invulnerable:
                if current_time - self.invulnerable_timer > 2000:
                    self.invulnerable = False

            # Apply gravity
            self.player_velocity += 0.8
            self.player.y += self.player_velocity
            
            # Platform collisions
            self.on_ground = False
            for platform in self.platforms:
                if self.player.colliderect(platform):
                    if self.player_velocity > 0:
                        self.player.bottom = platform.top
                        self.player_velocity = 0
                        self.on_ground = True
                    elif self.player_velocity < 0:
                        self.player.top = platform.bottom
                        self.player_velocity = 0

            # Check if player fell off
            if self.player.top > 600:
                self.lose_life()

            # Update obstacles
            for obstacle in self.obstacles:
                obstacle['rect'].x += obstacle['speed'] * obstacle['direction']
                if obstacle['rect'].right > 800 or obstacle['rect'].left < 0:
                    obstacle['direction'] *= -1
                
                if not self.invulnerable and self.player.colliderect(obstacle['rect']):
                    self.lose_life()

            # Block collisions
            if self.stage < len(self.stages):
                for block in self.stages[self.stage]["blocks"][:]:
                    if self.player.colliderect(block):
                        self.stages[self.stage]["blocks"].remove(block)
                        self.score += 10
                        note = choice(self.stages[self.stage]["notes"])
                        self.show_note = True
                        self.note_timer = current_time
                        self.current_note = note
                        self.collected_notes.append(note)
                        
                        if not self.stages[self.stage]["blocks"]:
                            self.stage += 1
                            self.stage_timer = current_time
                            if self.stage < len(self.stages):
                                self.reset_stage()
                                self.spawn_learning_blocks()
                                self.spawn_obstacles()

            # Update note display timer
            if self.show_note and current_time - self.note_timer > 3000:
                self.show_note = False

    def draw(self):
        screen.fill(BLACK)
        
        # Draw platforms
        for platform in self.platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, platform)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, RED, obstacle['rect'])
        
        # Draw player (flashing if invulnerable)
        if not self.invulnerable or pygame.time.get_ticks() % 200 < 100:
            pygame.draw.rect(screen, YELLOW, self.player)
        
        if self.stage < len(self.stages):
            # Draw blocks
            for block in self.stages[self.stage]["blocks"]:
                pygame.draw.rect(screen, self.stages[self.stage]["color"], block)
            
            # Draw stage info
            title = title_font.render(self.stages[self.stage]["title"], True, WHITE)
            task = info_font.render(self.stages[self.stage]["task"], True, WHITE)
            screen.blit(title, (20, 20))
            screen.blit(task, (20, 70))

            # Draw timer
            time_left = max(0, self.stage_time - (pygame.time.get_ticks() - self.stage_timer) / 1000)
            timer_text = info_font.render(f"Time: {int(time_left)}s", True, WHITE)
            screen.blit(timer_text, (650, 100))

            # Draw current note if active
            if self.show_note:
                note_bg = pygame.Rect(100, 150, 600, 50)
                pygame.draw.rect(screen, WHITE, note_bg)
                note_text = note_font.render(self.current_note, True, BLACK)
                screen.blit(note_text, (110, 165))

        else:
            # Game complete screen
            complete_text = title_font.render("CNN Network Complete!", True, WHITE)
            screen.blit(complete_text, (200, 250))
            
            # Show collected notes
            for i, note in enumerate(self.collected_notes[-5:]):
                note_text = note_font.render(f"• {note}", True, WHITE)
                screen.blit(note_text, (100, 300 + i*30))

        # Draw score and lives
        score_text = info_font.render(f"Score: {self.score}", True, WHITE)
        lives_text = info_font.render(f"Lives: {self.lives}", True, WHITE)
        screen.blit(score_text, (650, 20))
        screen.blit(lives_text, (650, 60))

        # Draw helper text
        helper_text = [
            "Use LEFT/RIGHT arrows to move",
            "Press SPACE to jump",
            "Avoid red obstacles",
            "Collect blocks before time runs out!",
            f"Lives: {self.lives}"
        ]
        
        for i, text in enumerate(helper_text):
            text_surface = note_font.render(text, True, WHITE)
            screen.blit(text_surface, (20, 500 + i * 25))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((800, 600))
            overlay.fill(BLACK)
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("Game Over!", True, WHITE)
            restart_text = info_font.render("Press R to Restart", True, WHITE)
            final_score = info_font.render(f"Final Score: {self.score}", True, WHITE)
            screen.blit(game_over_text, (300, 250))
            screen.blit(restart_text, (300, 300))
            screen.blit(final_score, (300, 350))

def main():
    game = CNNGame()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        game.handle_input()
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()