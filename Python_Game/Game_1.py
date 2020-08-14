import pygame
import random
import sys
import tkinter as tk
from tkinter import ttk

pygame.init()

# global variables
WIDTH = 800
HEIGHT = 800
BCK_COLOR = (50, 120, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
scorefont = pygame.font.SysFont('monospace', 35)
msgfont = ('Verdana', 10)

agent_pos = (WIDTH / 2, HEIGHT / 1.1)
agent_size = 40
enemy_size = 40
enemies = []
crowd = 10

running = True  # boolean variable, indicates whether to run or stop the pygame screen
track = 0   # integer variable, used for toggeling mouse track
SPEED = 10  # speed of the game
delay = 0.1 # this value manages the frequency of adding new enemies, higher number means higher frequency
score = 0   # this variable tracks the score


screen = pygame.display.set_mode((WIDTH, HEIGHT))   # creates a window using pygame
clock = pygame.time.Clock()
pygame.display.set_caption('Game 1')
pygame.display.flip()

def exit_check(event):
    '''Checks whether the user has presses the 'Escape' key
    or clicked the quit button
    '''
    if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                raise SystemExit
    if event.type == pygame.QUIT:
        return False
    return True

def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("Game over")
    label = ttk.Label(popup, text=msg, font=msgfont)
    label.pack(side="top", fill="x", pady=50)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

def set_difficulty(score, delay):
    '''calculates speed and delay using the current score

    returns: speed and delay 
    '''
    return score / 10 + 10, delay + (score / 50)

def add_enemies(delay, crowd):
    if (len(enemies) < crowd) and (random.random() < delay):
        x_pos = random.randint(0, WIDTH-enemy_size)
        enemies.append((x_pos, 0))

def drow_enemy(enemies):
    for enemy in enemies:
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], enemy_size, enemy_size))

def drop_enemies(enemies, speed, score):
    for i, enemy in enumerate(enemies):
        y_pos = enemy[1]
        if y_pos < HEIGHT:
            y_pos += speed
            enemies[i] = enemy[0], y_pos
        else:
            enemies.pop(i)
            score += 1
    return score

def detect_collision(agent, enemy):
    if (enemy[0] <= agent[0] and (enemy[0]+enemy_size) >= agent[0]) or (enemy[0] >= agent[0] and enemy[0] <= (agent[0]+agent_size)):
        if (enemy[1] <= agent[1] and (enemy[1]+enemy_size) >= agent[1]) or (enemy[1] >= agent[1] and enemy[1] <= (agent[1]+agent_size)):
            return True
    return False

def collision_check(agent_pos, enemies):
    for enemy in enemies:
        if detect_collision(agent_pos, enemy):
            return True
    return False


while running:
    screen.fill(BCK_COLOR)
    for event in pygame.event.get():
        running = exit_check(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            track += 1

        if (track % 2) == 1:
            pygame.mouse.set_visible(False)
            agent_pos = pygame.mouse.get_pos()[0], agent_pos[1]
        else:
            pygame.mouse.set_visible(True)

    if collision_check(agent_pos, enemies):
        running = False
    
    text = 'Score: %d' % score
    label = scorefont.render(text, 1, BLUE)
    screen.blit(label, (WIDTH-250, HEIGHT-40))

    add_enemies(delay, crowd)
    drow_enemy(enemies)
    score = drop_enemies(enemies, SPEED, score)
    SPEED, delay = set_difficulty(score, delay)

    pygame.draw.rect(screen, BLUE, (agent_pos[0], agent_pos[1], agent_size, agent_size))
    clock.tick(30)
    pygame.display.update()
popupmsg('Your score is %d' % score)