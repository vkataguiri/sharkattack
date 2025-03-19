import pgzrun
import random

# Window resolution
WIDTH = 800
HEIGHT = 600

# Actors attributes
PLAYER_SPEED = 5
MIN_SHARK_SPEED = 3
MAX_SHARK_SPEED = 7
INITIAL_SPAWN_RATE = 60
MIN_SPAWN_RATE = 20
BACKGROUND_SPEED = 2

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
game_state = MENU

shark_spawn_rate = INITIAL_SPAWN_RATE
difficulty_mod = 0
time_survived = 0

bg1 = Actor("sea.jpg")
bg2 = Actor("sea.jpg")
bg1.pos = (WIDTH // 2, HEIGHT // 2)
bg2.pos = (WIDTH // 2 + WIDTH, HEIGHT // 2)
player = Actor("boat.png")

sharks = []

buttons = [
    {"text": "Play", "rect": Rect(270, 200, 250, 50), "action": "start_game", "type": "menu"},
    {"text": "Quit", "rect": Rect(270, 300, 250, 50), "action": "quit_game", "type": "menu"},
    {"text": "Sound: ON", "rect": Rect(500, 500, 250, 50), "action": "switch_sounds", "type": "menu"},
    {"text": "Try again?", "rect": Rect(270, 280, 250, 50), "action": "start_game", "type": "game_over"},
    {"text": "Quit Game", "rect": Rect(270, 360, 250, 50), "action": "quit_game", "type": "game_over"},
]

# Shark animation
shark_anim_frames = ["shark001.png", "shark002.png"]
shark_anim_index = 0
shark_anim_delay = 0.2
shark_anim_timer = 0

# Explosion animation
explosion = Actor("explosion001.png")
exp_anim_frames = [
    "explosion001.png", "explosion002.png", "explosion003.png", "explosion004.png", "explosion005.png", "explosion006.png",
    "explosion007.png", "explosion008.png", "explosion009.png", "explosion010.png",
]
exp_anim_index = 0
exp_anim_delay = 0.05
exp_anim_timer = 0
explosion_playing = False

sound_volume = 0.1
sounds_enabled = True
playing_music = False

diff_scheduled = False
can_move = False

def draw_menu():
    # Title
    screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (34, 176, 212)) # Background
    screen.draw.text("Shark Attack", (260, 100), fontsize=60, color=(255, 255, 255))

    # Buttons
    for button in buttons:
        if button["type"] == "menu":
            screen.draw.filled_rect(button["rect"], (34, 212, 70))
            if button["action"] == "switch_sounds":
                if sounds_enabled:
                    button["text"] = "Sounds: ON"
                else:
                    button["text"] = "Sounds: OFF"
                screen.draw.text(button["text"], (button["rect"].center[0] - 75, button["rect"].center[1] - 12), fontsize=40, color=(255, 255, 255))
            else:
                screen.draw.text(button["text"], (button["rect"].center[0] - 26, button["rect"].center[1] - 12), fontsize=40, color=(255, 255, 255))

def draw_game():
    bg1.draw()
    bg2.draw()
    player.draw()
    if explosion_playing: explosion.draw()
    screen.draw.text('Time survived: ' + str(round(time_survived)), (15, 10), color=(255, 255, 255), fontsize=30)
    for shark in sharks:
        shark["actor"].draw()

def draw_game_over():
    screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0))  # Background
    screen.draw.text('Game Over!', (280, 180), color=(255, 255, 255), fontsize=60)
    screen.draw.text("You've managed to stay {} seconds alive.".format(round(time_survived)), (150, 230), color=(173, 173, 173), fontsize=35)
    for button in buttons:
        if button["type"] == "game_over":
            screen.draw.filled_rect(button["rect"], (34, 212, 70))
            screen.draw.text(button["text"], (button["rect"].center[0] - 65, button["rect"].center[1] - 12), fontsize=40, color=(255, 255, 255))

def draw():
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()
    elif game_state == GAME_OVER:
        draw_game_over()

def update():
    global time_survived, difficulty_mod, diff_scheduled, shark_anim_delay, shark_anim_timer, playing_music, explosion_playing, game_state, exp_anim_index, exp_anim_timer, can_move
    if game_state == MENU:
        play_music("menumusic.wav", sound_volume)

    if game_state == PLAYING and can_move:
        play_music("gamemusic.wav", sound_volume)

        # Infinite background effect
        bg1.x -= BACKGROUND_SPEED
        bg2.x -= BACKGROUND_SPEED

        if bg1.right <= 0:
            bg1.left = WIDTH
        if bg2.right <= 0:
            bg2.left = WIDTH

        # Difficulty manager
        if not diff_scheduled:
            diff_scheduled = True
            clock.schedule_interval(increase_difficulty, 1)

        # Prevent player from going off screen
        if player.bottom >= HEIGHT:
            player.bottom = HEIGHT
        if player.top <= 0:
            player.top = 0
        if player.left <= 0:
            player.left = 0

        # Handle player movement
        player_movement()

        # Spawn sharks on a random position and a random interval
        if random.randint(0, shark_spawn_rate) == 0:
            shark_spawn()

        # Handle shark position
        shark_controller()

        # Handle player collision
        check_collision()

        time_survived += 1 / 60

        # Update shark animation
        shark_anim_timer += 1 / 60
        if shark_anim_timer >= shark_anim_delay:
            shark_anim_timer = 0
            update_shark_animation()

    # Update explosion animation when Game Over
    if explosion_playing:
        exp_anim_timer += 1 / 60
        if exp_anim_timer >= exp_anim_delay:
            exp_anim_timer = 0
            exp_anim_index += 1
            if exp_anim_index >= len(exp_anim_frames):
                explosion_playing = False
                game_state = GAME_OVER
                music.stop()
                playing_music = False
            else:
                explosion.image = exp_anim_frames[exp_anim_index]

def update_shark_animation():
    for shark in sharks:
        shark["frame_index"] = (shark["frame_index"] + 1) % len(shark_anim_frames)
        shark["actor"].image = shark_anim_frames[shark["frame_index"]]

def play_music(song, volume):
    global playing_music
    if sounds_enabled and not playing_music:
        music.set_volume(volume)
        music.play(song)
        playing_music = True

# Check if player clicked the button
def on_mouse_down(pos):
    global game_state
    if game_state == MENU:
        iterate_buttons("menu", pos)
    elif game_state == GAME_OVER:
        iterate_buttons("game_over", pos)

def iterate_buttons(type, pos):
    for button in buttons:
        if button["rect"].collidepoint(pos) and button["type"] == type:
            handle_button_click(button["action"])

def handle_button_click(action):
    global game_state, sharks, player, time_survived, shark_spawn_rate, diff_scheduled, sounds_enabled, playing_music, can_move
    if sounds_enabled:
        sounds.button_click.play()
    if action == "start_game":
        can_move = True
        # Take explosion off screen
        explosion.pos = WIDTH + 100, HEIGHT + 100
        music.stop()
        playing_music = False
        shark_spawn_rate = INITIAL_SPAWN_RATE
        clock.unschedule(increase_difficulty)
        diff_scheduled = False
        sharks = []
        player.pos = 400, 300
        time_survived = 0
        game_state = PLAYING
    elif action == "switch_sounds":
        if playing_music:
            playing_music = False
            music.stop()
        sounds_enabled = not sounds_enabled
    elif action == "quit_game":
        quit()

def shark_controller():
    for shark in sharks:
        shark["actor"].x -= shark["speed"]

        # Remove shark if it's out of screen
        if shark["actor"].x < -50:
            sharks.remove(shark)

def check_collision():
    global game_state, playing_music, exp_anim_index, explosion_playing, can_move
    shark_actors = []
    for shark in sharks:
        shark_actors.append(shark["actor"])
    if player.collidelist(shark_actors) != -1: # Player collided with a shark
        can_move = False
        # Play explosion animation
        if sounds_enabled: sounds.explosion.play()
        explosion.pos = player.pos
        explosion_playing = True
        exp_anim_index = 0
        explosion.image = exp_anim_frames[exp_anim_index]

def shark_spawn():
    shark = {
        "speed": random.randint(MIN_SHARK_SPEED, MAX_SHARK_SPEED),
        "actor": Actor(shark_anim_frames[0]),
        "frame_index": 0
    }

    shark["actor"].x = 850
    shark["actor"].angle = 0
    shark["actor"].y = random.randint(0, 600)

    sharks.append(shark)

def player_movement():
    if keyboard.W:
        player.y -= PLAYER_SPEED
    if keyboard.S:
        player.y += PLAYER_SPEED
    if keyboard.A:
        player.x -= PLAYER_SPEED
    if keyboard.D:
        player.x += PLAYER_SPEED

def increase_difficulty():
    global shark_spawn_rate
    if shark_spawn_rate > MIN_SPAWN_RATE:
        shark_spawn_rate -= 1

sounds.button_click.set_volume(sound_volume)
sounds.explosion.set_volume(sound_volume)

pgzrun.go()