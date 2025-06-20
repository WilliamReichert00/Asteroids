import pygame, math, time, random
from pygame.locals import (
    KEYDOWN,
    KEYUP,
    MOUSEBUTTONDOWN,
    K_ESCAPE,
    K_SPACE,
    K_r,
    K_LEFT,
    K_RIGHT,
    K_UP,
    K_DOWN,
    K_a,
    K_d,
    K_w,
    K_s)

# Program Constants ---------------------------------------------------------------------------------------------------- Program Constants
# width and height of pygame window
WIDTH = 2500
HEIGHT = 1400
# pi used in rotation and sphere calculations
PI = math.pi

# Pygame initializations ----------------------------------------------------------------------------------------------- Pygame initializations
pygame.init()
pygame.mixer.init()
pygame.font.init()
pygame.display.set_caption("Asteroids!")
game_over = pygame.mixer.Sound("assets/GOver.wav")
hit = pygame.mixer.Sound("assets/Hit.wav")
blast = pygame.mixer.Sound("assets/Pip.wav")

track0 = pygame.mixer.Sound("assets/All is cool.wav")
track1 = pygame.mixer.Sound("assets/Blood pumping.wav")
track2 = pygame.mixer.Sound("assets/Warming up.wav")
track3 = pygame.mixer.Sound("assets/Too warm.wav")
track4 = pygame.mixer.Sound("assets/Getting hot.wav")
track5 = pygame.mixer.Sound("assets/Something is coming.wav")
track6 = pygame.mixer.Sound("assets/Something is here.wav")

# use for any object drawn to the screen
all_sprites = pygame.sprite.Group()
# used for entity handling
all_players = []
all_asteroids = []
all_lasers = []

# pygame screen definition
screen = pygame.display.set_mode([WIDTH, HEIGHT])
screen.fill((0, 0, 0))


# color functions
def random_color(min=0, max=255):
    r = random.randint(min, max)
    g = random.randint(min, max)
    b = random.randint(min, max)
    return [r, g, b]


def color_shift(color, shift_max=25):
    new_color = []
    for value in color:
        new_value = value
        shift = random.randint(-shift_max, shift_max)
        new_value += shift
        if new_value > 255:
            new_value = 255
        elif new_value < 0:
            new_value = 0
        new_color.append(new_value)

    return new_color


class Text(pygame.sprite.Sprite):
    def __init__(self, size, text="Hello World", color=(255, 255, 255), x=WIDTH / 2, y=HEIGHT / 2):
        super(Text, self).__init__()
        self.color = color
        self.x = x
        self.y = y
        self.size = size
        self.message = text
        self.font = pygame.font.Font(pygame.font.get_default_font(), size)
        self.text = self.font.render(self.message.__str__(), True, self.color)
        self.rect = self.text.get_rect()
        self.rect.center = (self.x, self.y)
        all_sprites.add(self)

    # updates the text object
    def update(self):
        return

    # updates the text to new text
    def update_text(self, text):
        self.message = text
        self.text = self.font.render(self.message.__str__(), True, (255, 255, 255), (0, 0, 0))
        self.rect = self.text.get_rect()
        self.rect.center = (self.x, self.y)

    # removes the text from the sprite list
    def destroy(self):
        all_sprites.remove(self)

    # draws the asteroid to the screen
    def draw(self, screen):
        screen.blit(self.text, self.rect)


class Asteroid(pygame.sprite.Sprite):
    score = 0
    score_text = Text(size=20, text=("Score: " + str(score)), x=100, y=60)

    def __init__(self, width, color=(255, 255, 255), x=WIDTH / 2, y=HEIGHT / 2):
        super(Asteroid, self).__init__()
        self.xVelocity = random.randint(-2, 2)
        self.yVelocity = random.randint(-2, 2)
        self.aVelocity = random.randint(1, 4) * random.choice([-1, 1])
        self.color = color
        self.width = width
        self.x = x
        self.y = y
        self.angle = 0
        Asteroid.score += 1
        Asteroid.score_text.update_text("Score: " + str(Asteroid.score))

        angles = [0]
        while len(angles) <= math.log2(width) + 2:
            angles.append(random.randint(angles[0],
                                         360) / 360)  # append a random number between 0 and 1 which is used to determine the point's position on a circle
            angles.sort()

        points = []
        # convert angle into coordinates
        for angle in angles:
            pair = [self.width / 2 * math.cos(angle * 2 * PI) + self.width / 2,
                    self.width / 2 * math.sin(angle * 2 * PI) + self.width / 2]
            # set the current value to the new point values
            points.append(pair)

        self.original_surf = pygame.Surface((self.width, self.width), pygame.SRCALPHA, 32)
        self.original_surf = self.original_surf.convert_alpha()
        pygame.draw.polygon(surface=self.original_surf, color=self.color, points=points, width=1)
        self.surf = self.original_surf
        self.rect = self.surf.get_rect(center=(self.x, self.y))
        all_sprites.add(self)
        all_asteroids.append(self)

    # moves the sprite and surface to the given coordinates on the screen
    def goto(self, xy):
        self.x = xy[0]
        self.y = xy[1]
        self.rect = self.surf.get_rect(center=(self.x, self.y))

    # updates the asteroid's position each frame
    def update(self):
        x = (self.x + self.xVelocity) % WIDTH
        # if x > WIDTH:
        #     x = 0
        # elif x < 0:
        #     x = WIDTH - 1
        y = (self.y + self.yVelocity) % HEIGHT
        # if y > HEIGHT:
        #     y = 0
        # elif y < 0:
        #     y = HEIGHT - 1
        self.angle += self.aVelocity
        self.angle = self.angle % 360
        self.surf = pygame.transform.rotate(self.original_surf, self.angle)
        self.rect = self.surf.get_rect(center=self.rect.center)
        self.goto([x, y])

    # when asteroid is destroyed, it splits into two smaller asteroids if it is large enough
    def destroy(self):
        if hit.get_num_channels() <= 3:
            hit.play()
        if self.width >= 64:
            Asteroid(self.width / 2, color=color_shift(self.color), x=self.x, y=self.y)
            Asteroid(self.width / 2, color=color_shift(self.color), x=self.x, y=self.y)
        Asteroid.score += int(self.width)
        Asteroid.score_text.update_text("Score: " + str(Asteroid.score))
        for each in range(int(math.log(self.width, 2))):
            Particle(color=color_shift(self.color), x=self.x, y=self.y)
        all_sprites.remove(self)
        all_asteroids.remove(self)

    # remove asteroid without splitting or emitting particles
    def destroyX(self):
        all_sprites.remove(self)
        all_asteroids.remove(self)

    # draws the asteroid to the screen
    def draw(self, screen):
        screen.blit(self.surf, self.rect)

    # refreshes class variables
    def restart(self=0):
        Asteroid.score = 0
        Asteroid.score_text = Text(size=20, text=("Score: " + str(Asteroid.score)), x=100, y=60)


class Player(pygame.sprite.Sprite):

    def __init__(self, width=25, color=(255, 255, 255), x=WIDTH / 2, y=HEIGHT / 2):
        super(Player, self).__init__()
        self.xVelocity = 0
        self.yVelocity = 0
        self.aVelocity = 0
        self.color = color
        self.width = width
        self.x = x
        self.y = y
        self.lives = 3
        self.lives_text = Text(size=20, text=("Lives: " + str(self.lives)), x=WIDTH - 100, y=35)
        self.bullets = 2
        self.bullets_text = Text(size=20, text=("Bullets: " + str(self.lives)), x=WIDTH - 100, y=60)
        self.coolDown = 0
        self.iFrames = 0
        self.draw_frame = True
        self.angle = 0
        self.original_surf = pygame.Surface((self.width, self.width), pygame.SRCALPHA, 32)
        self.original_surf = self.original_surf.convert_alpha()
        pygame.draw.polygon(surface=self.original_surf, color=self.color,
                            points=[(0, 0), (self.width / 2, self.width), (self.width, 0),
                                    (self.width / 2, self.width / 2)], width=1)
        self.surf = self.original_surf
        self.rect = self.original_surf.get_rect(center=(self.x, self.y))
        all_sprites.add(self)
        all_players.append(self)

    # moves the sprite and surface to the given coordinates on the screen
    def goto(self, xy):
        self.x = xy[0]
        self.y = xy[1]
        self.rect = self.surf.get_rect(center=(self.x, self.y))

    # updates the player's position each frame
    def update(self):

        x = self.x
        y = self.y

        if self.coolDown > 0:
            self.coolDown -= 1

        if self.iFrames > 0:
            self.iFrames -= 1
            if self.iFrames % 5 == 0:
                self.draw_frame = not self.draw_frame

        if self.xVelocity != 0:
            x = (self.x + self.xVelocity) % WIDTH

            self.xVelocity *= .9
            if math.fabs(self.xVelocity) < .1:
                self.xVelocity = 0

        if self.yVelocity != 0:
            y = (self.y + self.yVelocity) % HEIGHT

            self.yVelocity *= .9
            if math.fabs(self.yVelocity) < .1:
                self.yVelocity = 0

        if self.aVelocity != 0:
            self.angle += self.aVelocity
            self.angle = self.angle % 360
            self.surf = pygame.transform.rotate(self.original_surf, self.angle)
            self.rect = self.surf.get_rect(center=self.rect.center)

            self.aVelocity *= .9
            if math.fabs(self.aVelocity) < 1:
                self.aVelocity = 0

        self.bullets_text.update_text("Bullets: " + str(self.bullets - len(all_lasers)))
        self.lives_text.update_text("Lives: " + str(self.lives))

        self.goto([x, y])

    # remove from lists when destroyed
    def destroy(self):
        if self.iFrames <= 0:
            hit.play()
            self.lives -= 1
            for each in range(int(math.log(self.width, 2))):
                Particle(color=color_shift(self.color), x=self.x, y=self.y)
            self.x = WIDTH / 2
            self.y = HEIGHT / 2
            self.xVelocity = 0
            self.yVelocity = 0
            self.aVelocity = 0
            self.iFrames = 120
        if self.lives <= 0:
            all_players.remove(self)
            all_sprites.remove(self)
            self.lives_text.destroy()
            self.bullets_text.destroy()

    # increase the player's forward velocity
    def forward(self):
        self.xVelocity += 1.125 * math.sin(self.angle / 180 * PI)
        self.yVelocity += 1.125 * math.cos(self.angle / 180 * PI)

    # increase the player's angular velocity
    def turn(self, angle):
        self.aVelocity += angle

    # shoots a small projectile in the same direction as the player
    def shoot(self):
        if len(all_lasers) < self.bullets and self.coolDown <= 0:
            blast.play()
            self.coolDown = 3
            Laser(self.angle, x=self.x, y=self.y)

    # increases the number of bullets available to the player
    def increase_bullets(self, num=1):
        self.bullets += num

    # increases the number of lives the player has
    def increase_lives(self, num=1):
        self.lives += num

    # draws the player to the screen
    def draw(self, screen):
        if self.draw_frame:
            screen.blit(self.surf, self.rect)


class Laser(pygame.sprite.Sprite):
    def __init__(self, angle, width=25, color=(255, 255, 255), x=WIDTH / 2, y=HEIGHT / 2):
        super(Laser, self).__init__()
        self.xVelocity = 11 * math.sin(angle / 180 * PI)
        self.yVelocity = 11 * math.cos(angle / 180 * PI)
        self.color = color
        self.width = width
        self.x = x
        self.y = y
        self.timer = 0
        self.surf = pygame.Surface((self.width, self.width), pygame.SRCALPHA, 32)
        self.original_surf = self.surf.convert_alpha()
        pygame.draw.line(self.surf, self.color, (self.width / 2, self.width), (self.width / 2, 0), 4)
        self.rect = self.surf.get_rect(center=(self.x, self.y))
        self.surf = pygame.transform.rotate(self.surf, angle)
        self.rect = self.surf.get_rect(center=self.rect.center)

        all_sprites.add(self)
        all_lasers.append(self)

    # moves the sprite and surface to the given coordinates on the screen
    def goto(self, xy):
        self.x = xy[0]
        self.y = xy[1]
        self.rect = self.surf.get_rect(center=(self.x, self.y))

    # updates the asteroid's position each frame
    def update(self):
        self.timer += 1
        x = (self.x + self.xVelocity) % WIDTH
        y = (self.y + self.yVelocity) % HEIGHT
        self.goto([x, y])
        if self.timer >= 90:
            self.destroy()

    # when laser hits the end of the screen or an asteroid, it is destroyed
    def destroy(self):
        Particle(color=self.color, x=self.x, y=self.y)
        all_sprites.remove(self)
        all_lasers.remove(self)

    # draws the asteroid to the screen
    def draw(self, screen):
        screen.blit(self.surf, self.rect)


class Particle(pygame.sprite.Sprite):
    def __init__(self, width=(5 * WIDTH // HEIGHT), color=(255, 255, 255), x=WIDTH / 2, y=HEIGHT / 2):
        super(Particle, self).__init__()
        self.xVelocity = random.random() * 4 - 2
        self.yVelocity = random.random() * 4 - 2
        self.aVelocity = random.random() * 45 - 22.5
        self.color = color
        self.width = width
        self.x = x
        self.y = y
        self.angle = 0

        angles = []
        while len(angles) < 3:
            angles.append(
                random.random())  # append a random number between 0 and 1 which is used to determine the point's position on a circle
            angles.sort()

        points = []
        # convert angle into coordinates
        for angle in angles:
            pair = [self.width / 2 * math.cos(angle * 2 * PI) + self.width / 2,
                    self.width / 2 * math.sin(angle * 2 * PI) + self.width / 2]
            # set the current value to the new point values
            points.append(pair)

        self.original_surf = pygame.Surface((self.width, self.width), pygame.SRCALPHA, 32)
        self.original_surf = self.original_surf.convert_alpha()
        pygame.draw.polygon(surface=self.original_surf, color=self.color, points=points, width=1)
        self.surf = self.original_surf
        self.rect = self.original_surf.get_rect(center=(self.x, self.y))
        all_sprites.add(self)

    # moves the sprite and surface to the given coordinates on the screen
    def goto(self, xy):
        self.x = xy[0]
        self.y = xy[1]
        self.rect = self.surf.get_rect(center=(self.x, self.y))

    # updates the sprite's position each frame
    def update(self):

        x = self.x
        y = self.y

        if self.xVelocity != 0:
            x = self.x + self.xVelocity
            self.xVelocity *= .9
            if math.fabs(self.xVelocity) < .1:
                self.xVelocity = 0

        if self.yVelocity != 0:
            y = self.y + self.yVelocity
            self.yVelocity *= .9
            if math.fabs(self.yVelocity) < .1:
                self.yVelocity = 0

        if self.aVelocity != 0:
            self.angle += self.aVelocity
            self.angle = self.angle % 360
            self.surf = pygame.transform.rotate(self.original_surf, self.angle)
            self.rect = self.surf.get_rect(center=self.rect.center)
            self.aVelocity *= .9
            if math.fabs(self.aVelocity) < 1:
                self.aVelocity = 0

        self.goto([x, y])
        if self.xVelocity + self.yVelocity + self.aVelocity == 0:
            self.destroy()

    # remove from lists when destroyed
    def destroy(self):
        all_sprites.remove(self)

    # increase the player's forward velocity
    def forward(self):
        self.xVelocity += 1.125 * math.sin(self.angle / 180 * PI)
        self.yVelocity += 1.125 * math.cos(self.angle / 180 * PI)

    # increase the player's angular velocity
    def turn(self, angle):
        self.aVelocity += angle

    # shoots a small projectile in the same direction as the player
    def shoot(self):
        if len(all_lasers) < self.bullets:
            Laser(self.angle, x=self.x, y=self.y)

    # increases the number of bullets available to the player
    def increase_bullets(self, num=1):
        self.bullets += num

    # increases the number of lives the player has
    def increase_lives(self, num=1):
        self.lives += num

    # draws the player to the screen
    def draw(self, screen):
        screen.blit(self.surf, self.rect)


class Album():
    def __init__(self, songs):
        self.song_list = songs
        self.number_of_songs = len(songs)
        self.current_song = 0

    def is_playing(self):
        if self.song_list[self.current_song].get_num_channels() >= 1:
            return True

    def next(self):
        self.current_song = self.current_song + 1 % self.number_of_songs

    def previous(self):
        self.current_song = self.current_song - 1 % self.number_of_songs

    def shuffle(self):
        self.current_song = random.randint(0,self.number_of_songs)

    def play(self, song_id=-1):
        if song_id > -1 and song_id <= self.number_of_songs:
            self.song_list[song_id].play()
            self.current_song = song_id
        else:
            self.song_list[self.current_song].play()


# Game Functions
def restart():
    for player in all_players:
        player.destroy()
    for asteroid in all_asteroids:
        asteroid.destroyX()
    for laser in all_lasers:
        laser.destroy()
    for sprite in all_sprites:
        all_sprites.remove(sprite)
    all_players.clear()
    all_asteroids.clear()
    all_lasers.clear()
    Asteroid.restart()


def start():
    # keypress variables
    wasdControls = [False, False, False, False]  # 0 - w, 1 - s, 2 - a, 3 - d
    arrowControls = [False, False, False, False]  # 0 - up, 1 - down, 2 - left, 3 - right

    # game variables
    level = 1
    level_text = Text(size=20, text=('Level: ' + str(level)), x=100, y=35)

    player = Player(25)
    soundtrack = Album([track0, track1, track2, track3, track4, track5, track6])

    # Initialize loop conditions + variables ------------------------------------------------------------------------------- Initialize loop conditions + variables
    loop = True
    menu = True
    menu_text1 = Text(60, "ASTEROIDS!", y=HEIGHT / 2 - 75)
    menu_text2 = Text(50, "Use ARROWS to play, SPACE to pause, R to restart, ESC to quit")
    menu_text3 = Text(50, "Press any key to start", y=HEIGHT / 2 + 75)
    while menu:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    menu = False
                    loop = False
                else:
                    menu = False
                    menu_text1.destroy()
                    menu_text2.destroy()
                    menu_text3.destroy()
        screen.fill((0, 0, 0))
        menu_text1.draw(screen)
        menu_text2.draw(screen)
        menu_text3.draw(screen)
        # apply screen changes
        pygame.display.flip()
        # regulate frame rate
        time.sleep(1 / 60)

    while loop:

        # determine music track
        if not soundtrack.is_playing():
            if level > 15:
                soundtrack.shuffle()
                soundtrack.play()
            elif level > 12:
                soundtrack.play(6)
            elif level > 10:
                soundtrack.play(5)
            elif level > 9:
                soundtrack.play(4)
            elif level > 7:
                soundtrack.play(3)
            elif level > 5:
                soundtrack.play(2)
            elif level > 2:
                soundtrack.play(1)
            else:
                soundtrack.play(0)

        # reinitialize surfaces
        screen.fill((0, 0, 0))

        if player.lives <= 0:
            game_over.play()
            menu_text = Text(50, "You DIED! Your score was " + str(Asteroid.score) + ". Press R to restart")
            while True:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            return False
                        elif event.key == K_r:
                            menu_text.destroy()
                            return True
                menu_text.draw(screen)
                # apply screen changes
                pygame.display.flip()
                # regulate frame rate
                time.sleep(1 / 60)

        if 2 + 2 * level > len(all_asteroids) and random.random() <= 0.01:
            size = 5 + random.randint(0, int(math.log(level, 2)))
            if random.choice([True, False]):
                Asteroid(2 ** size, color=random_color(min=50), x=random.choice([0, WIDTH]), y=random.random() * HEIGHT)
            else:
                Asteroid(2 ** size, color=random_color(min=50), x=random.random() * WIDTH, y=random.choice([0, HEIGHT]))

        # redraw sprites
        for entity in all_sprites:
            entity.update()
            entity.draw(screen)

        # handle collision
        for asteroid in all_asteroids:
            for player in all_players:
                if (player.x - asteroid.x) ** 2 + (player.y - asteroid.y) ** 2 <= (asteroid.width / 2) ** 2:
                    player.destroy()
            for laser in all_lasers:
                if (laser.x - asteroid.x) ** 2 + (laser.y - asteroid.y) ** 2 <= (asteroid.width / 2) ** 2:
                    asteroid.destroy()
                    laser.destroy()
                    break

        # get event data
        mouse_data = pygame.mouse.get_pos()

        # check event data
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    loop = False
                elif event.key == K_UP:
                    arrowControls[0] = True
                elif event.key == K_DOWN:
                    arrowControls[1] = True
                elif event.key == K_LEFT:
                    arrowControls[2] = True
                elif event.key == K_RIGHT:
                    arrowControls[3] = True
                elif event.key == K_w:
                    wasdControls[0] = True
                elif event.key == K_s:
                    wasdControls[1] = True
                elif event.key == K_a:
                    wasdControls[2] = True
                elif event.key == K_d:
                    wasdControls[3] = True
                elif event.key == K_SPACE:
                    paused = True
                    pause_text = Text(50, "PAUSED")
                    while paused:
                        for event in pygame.event.get():
                            if event.type == KEYDOWN:
                                if event.key == K_ESCAPE:
                                    loop = False
                                elif event.key == K_SPACE:
                                    paused = False
                                    pause_text.destroy()
                                elif event.key == K_r:
                                    return True
                                elif event.key == K_UP:
                                    arrowControls[0] = True
                                elif event.key == K_DOWN:
                                    arrowControls[1] = True
                                elif event.key == K_LEFT:
                                    arrowControls[2] = True
                                elif event.key == K_RIGHT:
                                    arrowControls[3] = True
                                elif event.key == K_w:
                                    wasdControls[0] = True
                                elif event.key == K_s:
                                    wasdControls[1] = True
                                elif event.key == K_a:
                                    wasdControls[2] = True
                                elif event.key == K_d:
                                    wasdControls[3] = True

                            if event.type == KEYUP:
                                if event.key == K_UP:
                                    arrowControls[0] = False
                                elif event.key == K_DOWN:
                                    arrowControls[1] = False
                                elif event.key == K_LEFT:
                                    arrowControls[2] = False
                                elif event.key == K_RIGHT:
                                    arrowControls[3] = False
                                elif event.key == K_w:
                                    wasdControls[0] = False
                                elif event.key == K_s:
                                    wasdControls[1] = False
                                elif event.key == K_a:
                                    wasdControls[2] = False
                                elif event.key == K_d:
                                    wasdControls[3] = False

                        pause_text.draw(screen)
                        # apply screen changes
                        pygame.display.flip()
                        # regulate frame rate
                        time.sleep(1 / 60)
                elif event.key == K_r:
                    return True

            if event.type == KEYUP:
                if event.key == K_UP:
                    arrowControls[0] = False
                elif event.key == K_DOWN:
                    arrowControls[1] = False
                elif event.key == K_LEFT:
                    arrowControls[2] = False
                elif event.key == K_RIGHT:
                    arrowControls[3] = False
                elif event.key == K_w:
                    wasdControls[0] = False
                elif event.key == K_s:
                    wasdControls[1] = False
                elif event.key == K_a:
                    wasdControls[2] = False
                elif event.key == K_d:
                    wasdControls[3] = False

            if event.type == MOUSEBUTTONDOWN:
                for asteroid in all_asteroids:
                    if asteroid.width / 2 + asteroid.x > mouse_data[0] > asteroid.x - asteroid.width / 2:
                        if asteroid.width / 2 + asteroid.y > mouse_data[1] > asteroid.y - asteroid.width / 2:
                            asteroid.destroy()
                            break
                for asteroid in all_players:
                    if asteroid.width / 2 + asteroid.x > mouse_data[0] > asteroid.x - asteroid.width / 2:
                        if asteroid.width / 2 + asteroid.y > mouse_data[1] > asteroid.y - asteroid.width / 2:
                            asteroid.destroy()
                            break

        if arrowControls[0]:
            player.forward()
        if arrowControls[1]:
            player.shoot()
        if arrowControls[2]:
            player.turn(2)
        if arrowControls[3]:
            player.turn(-2)

        # Level increases when all asteroids are destroyed
        if Asteroid.score >= 32 * 1.75 ** level:
            level += 1
            level_text.update_text("Level: " + str(level))

            # player upgrades at certain level milestones
            if (level % 2 == 0):
                player.increase_bullets()
            if (level % 8 == 0):
                player.increase_lives()

        # apply screen changes
        pygame.display.flip()

        # regulate frame rate
        time.sleep(1 / 60)
    return None


# Default start
while start():
    print("Player Finished")
    restart()
