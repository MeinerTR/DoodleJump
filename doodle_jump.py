import pygame as pg;
from time import time;
from os import urandom;
from random import randint, seed;


#==# some types #==#
class Position:
    def __init__(self, x:int, y:int):
        self.x = x;
        self.y = y;

class Input_device:
    keyboard = 0;
    mouse = 1;

class Color:
    black = (0, 0, 0);
    red = (255, 0, 0);
    green = (0, 255, 0);
    blue = (0, 0, 255);
    white = (255, 255, 255);


#==# window properties #==#
WIDTH, HEIGHT = 350, 400;
BG_COLOR = Color.black;
#==# score properties #==#
FONT_SIZE = 20;
FONT_NAME = "Comic Sans";
FONT_POSITION_X = WIDTH - FONT_SIZE * 3;
FONT_POSITION_Y = HEIGHT - FONT_SIZE * 2;
#==# doodle properties #==#
DOODLE_SIZE = WIDTH / 10;
DOODLE_COLOR = Color.green;
DOODLE_STOP_DISTANCE = HEIGHT / 3;
#==# physics properties #==#
JUMP_POWER = DOODLE_SIZE;
MIN_FALLING_SPEED = 20;
GRAVITY_POWER = DOODLE_SIZE / 26;
TERMINAL_VELOCITY = DOODLE_SIZE / 8;
#==# platform properties #==#
PLATFORM_MOVE_AT_ALTITUDE = DOODLE_STOP_DISTANCE * 2;
PLATFORM_MIN_DISTANCE = DOODLE_SIZE;
PLATFORM_SPAWN_SPEED = 10;
PLATFORM_WIDTH = int(DOODLE_SIZE * 1.5);
PLATFORM_HEIGHT = PLATFORM_WIDTH / 4;
PLATFORM_DISAPPEAR_POS = HEIGHT + PLATFORM_HEIGHT * 5;

class Platform:
    def __init__(self, type:int, pos:Position):
        self.type = type;
        self.pos = pg.Rect(
            pos.x - (PLATFORM_WIDTH / 2),
            pos.y - (PLATFORM_HEIGHT / 2),
            PLATFORM_WIDTH, PLATFORM_HEIGHT);

#==# platform types #==#
class Platforms:# id
    simple      = 0;
    trampoline  = 1;
    cloud       = 2;
    bird        = 3;
    golden      = 4;

LAST_PLATFORM = Platforms.golden;
PLATFORM_TRAMPOLINE_POWER = JUMP_POWER * 2;

#==# color of platforms #==#
PLATFORM_SIMPLE_COLOR = Color.white;
PLATFORM_TRAMPOLINE_COLOR = Color.red;
PLATFORM_CLOUD_COLOR = (200, 200, 200);
PLATFORM_BIRD_COLOR = (0, 200, 0);
PLATFORM_GOLDEN_COLOR = Color.green;
#==# percentage of platforms #==#
PLATFORM_SIMPLE_PERCENTAGE = 90;
PLATFORM_TRAMPOLINE_PERCENTAGE = 70;
PLATFORM_CLOUD_PERCENTAGE = 50;
PLATFORM_BIRD_PERCENTAGE = 30;
PLATFORM_GOLDEN_PERCENTAGE = 20;

PLATFORM_PERCENTAGES = (
    PLATFORM_GOLDEN_PERCENTAGE,
    PLATFORM_BIRD_PERCENTAGE,
    PLATFORM_CLOUD_PERCENTAGE,
    PLATFORM_TRAMPOLINE_PERCENTAGE,
    PLATFORM_SIMPLE_PERCENTAGE
);


class Map:
    def __init__(self):
        self.reset();

    def reset(self):
        self.platforms = [];
        self.seed_type = 0;
        self.velocity = 0;

    def update(self):
        platforms_to_remove = [];
        #==# move platforms by doodle velocity #==#
        for idx, platform in enumerate(self.platforms):
            platform.pos.y += self.velocity; #==# problem here #==#
            if platform.pos.y > PLATFORM_DISAPPEAR_POS:
                platforms_to_remove.append(idx);
        #==# remove unnecessary platforms #==#
        platforms_to_remove.sort(reverse=True);
        for platform in platforms_to_remove:
            self.platforms.pop(platform);

    def spawn_random_platforms(self, count:int, at_startup:bool=False):
        for _ in range(count):
            #==# new seed for better random #==#
            if self.seed_type == 0:
                seed(time() + count);
                self.seed_type = 1;
            else:
                seed(int.from_bytes(urandom(4)) + count);
                self.seed_type = 0;
            #==# spawn platform by percentage #==#
            random_percentage = randint(0, 100);
            platform_index = LAST_PLATFORM;
            height = -randint(
                int(PLATFORM_HEIGHT + PLATFORM_MIN_DISTANCE),
                int(PLATFORM_HEIGHT) * 30);
            if at_startup: height = abs(height);
            for percentage in PLATFORM_PERCENTAGES:
                if random_percentage < percentage:
                    pos = pg.Rect(
                        randint(0, WIDTH - PLATFORM_WIDTH),
                        height, PLATFORM_WIDTH, PLATFORM_HEIGHT);
                    #==# make sure it's not merged with other platform #==#
                    colliding = True;
                    while colliding:
                        #==# new seed for better random #==#
                        if self.seed_type == 0:
                            seed(time() + count);
                            self.seed_type = 1;
                        else:
                            seed(int.from_bytes(urandom(4)) + count);
                            self.seed_type = 0;
                        for platform in self.platforms:
                            if platform.pos.colliderect(pos):
                                pos = pg.Rect(
                                    randint(0, WIDTH - PLATFORM_WIDTH),
                                    height, PLATFORM_WIDTH, PLATFORM_HEIGHT);
                                break;
                        else:
                            colliding = False;
                    #==# append to the list #==#
                    platform = Platform(platform_index, pos);
                    self.platforms.append(platform); break;
                else:
                    platform_index -= 1;

    def draw(self, window:pg.Surface):
        platform_color = Color.white;
        for platform in self.platforms:
            #==# get color #==#
            if platform.type == Platforms.simple:
                platform_color = PLATFORM_SIMPLE_COLOR;
            elif platform.type == Platforms.trampoline:
                platform_color = PLATFORM_TRAMPOLINE_COLOR;
            elif platform.type == Platforms.cloud:
                platform_color = PLATFORM_CLOUD_COLOR;
            elif platform.type == Platforms.bird:
                platform_color = PLATFORM_BIRD_COLOR;
            elif platform.type == Platforms.golden:
                platform_color = PLATFORM_GOLDEN_COLOR;
            #==# draw object #==#
            pg.draw.rect(window, platform_color, platform.pos);

class Doodle:
    def __init__(self):
        self.reset();

    def reset(self):
        self.score = 0;
        self.failed = False;
        self.position = pg.Rect(
            (WIDTH / 2) - (DOODLE_SIZE / 2),
            (HEIGHT / 2) - (DOODLE_SIZE / 2),
            DOODLE_SIZE, DOODLE_SIZE);
        self.altitude = self.position.centery;
        self.vertical_velocity = 0;
        self.pre_vertical_velocity = 0;
        self.horizontal_velocity = 0;
        self.is_falling = False;

    def update(self):
        if self.vertical_velocity < TERMINAL_VELOCITY:
            self.vertical_velocity += GRAVITY_POWER;
        elif self.vertical_velocity > TERMINAL_VELOCITY:
            self.vertical_velocity = TERMINAL_VELOCITY;

        self.altitude += self.vertical_velocity;
        if self.pre_vertical_velocity > self.vertical_velocity:
            if self.altitude > HEIGHT:
                self.failed = True;
            self.is_falling = True;
        self.position.centerx += self.horizontal_velocity;
        self.position.centery = self.altitude;
        self.pre_vertical_velocity = self.vertical_velocity;
    
    def events(self, event:list, device:int=Input_device.mouse):
        if event.type == pg.MOUSEBUTTONDOWN:
            #==# fly for test #==#
            self.vertical_velocity = -JUMP_POWER;
        if device == Input_device.mouse:
            mouse_pos = pg.mouse.get_pos();
            if mouse_pos[0] < self.position.centerx:
                self.horizontal_velocity = -TERMINAL_VELOCITY;
            elif mouse_pos[0] > self.position.centerx:
                self.horizontal_velocity = TERMINAL_VELOCITY;
            if abs(self.horizontal_velocity - mouse_pos[0]) < DOODLE_SIZE:
                self.horizontal_velocity = 0;
        else:
            pressed_key = pg.key.get_pressed();
            if pressed_key[pg.K_a] or pressed_key[pg.K_LEFT]:
                if self.horizontal_velocity < TERMINAL_VELOCITY:
                    self.horizontal_velocity -= GRAVITY_POWER;
                elif self.horizontal_velocity > TERMINAL_VELOCITY:
                    self.horizontal_velocity = TERMINAL_VELOCITY;
            elif pressed_key[pg.K_d] or pressed_key[pg.K_RIGHT]:
                if self.horizontal_velocity < TERMINAL_VELOCITY:
                    self.horizontal_velocity += GRAVITY_POWER;
                elif self.horizontal_velocity > TERMINAL_VELOCITY:
                    self.horizontal_velocity = TERMINAL_VELOCITY;
    
    def is_collided(self, platforms:tuple):
        for platform in platforms:
            if self.position.colliderect(pg.Rect(
                    platform.pos.left,
                    platform.pos.top - self.vertical_velocity,
                    PLATFORM_WIDTH, self.vertical_velocity)):
                return True;
        else:
            return False;

    def draw(self, window:pg.Surface):
        pg.draw.rect(window, DOODLE_COLOR, self.position);


class Game:
    def __init__(self, title:str):
        pg.display.set_caption(title);
        self.reset();

    def reset(self):
        self.game_over = False;
        try: #==# resetting again #==#
            if self.running: pass;
        except AttributeError:
            #==# first time opening #==#
            self.running = False;
            self.text = pg.font.SysFont(FONT_NAME, FONT_SIZE);
            self.input_device = Input_device.mouse;
            self.window = pg.display.set_mode(
                (WIDTH, HEIGHT), pg.DOUBLEBUF);
        
        #==# new objects #==#
        self.doodle = Doodle();
        self.map = Map();
        #==# spawn map in correct position #==#
        self.map.spawn_random_platforms(10);
        self.map.velocity = JUMP_POWER;
        self.map.update();
            
    def run(self, FPS:int):
        self.running = True;
        platform_spawn_timer = 0;
        clock = pg.time.Clock();
        while self.running:
            clock.tick(FPS);
            self.doodle.update();

            if self.doodle.failed:
                self.game_over = True;
                break;
            
            if self.doodle.is_falling:
                if self.doodle.is_collided(self.map.platforms):
                    self.doodle.vertical_velocity = -JUMP_POWER;
            
            if self.doodle.altitude < PLATFORM_MOVE_AT_ALTITUDE:
                if self.doodle.altitude < DOODLE_STOP_DISTANCE:
                    if self.doodle.vertical_velocity > MIN_FALLING_SPEED:
                        self.map.velocity = JUMP_POWER / 2;
                    else:
                        self.map.velocity = TERMINAL_VELOCITY;
                    self.doodle.vertical_velocity = 0;
                if platform_spawn_timer > 100:
                    platform_spawn_timer = 0;
                    self.doodle.score += 1;
                    self.map.spawn_random_platforms(1);
                else:
                    platform_spawn_timer += PLATFORM_SPAWN_SPEED;
                self.map.update();

            self.draw();
            self.events();
        else:
            self.exit("successfully");

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False;
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.running = False;
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == pg.K_TAB:
                    if self.input_device == Input_device.keyboard:
                        self.input_device = Input_device.mouse;
                    else:
                        self.input_device = Input_device.keyboard;
            self.doodle.events(event, self.input_device);
    
    def draw(self):
        self.window.fill(BG_COLOR);
        self.doodle.draw(self.window);
        self.map.draw(self.window);
        score = self.text.render(f"{self.doodle.score}", True, Color.white);
        self.window.blit(score, (FONT_POSITION_X, FONT_POSITION_Y));
        pg.display.update();

    def exit(self, msg:str):
        print(f"doodle exited with message: {msg}!");
        pg.quit();


if __name__ == "__main__":
    pg.init();
    game = Game("DoodleJump");
    game.run(60);
    while game.game_over:
        game.reset();
        game.run(60);
