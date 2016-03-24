import pygame
import math
from random import random
from utils.vec2d import vec2d

class Creep(pygame.sprite.Sprite):

    def __init__(self, 
            color, 
            radius, 
            pos_init, 
            dir_init, 
            speed, 
            reward, 
            TYPE,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            life):

        pygame.sprite.Sprite.__init__(self)
        
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.TYPE = TYPE
        self.jitter_speed = 0.003
        self.speed = speed
        self.reward = reward
        self.life = life
        self.radius = radius
        self.pos = vec2d(pos_init)

        self.direction = vec2d(dir_init)
        self.direction.normalize() #normalized
        
        image = pygame.Surface((radius*2, radius*2))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0,0,0))
 
        pygame.draw.circle(
                image,
                color,
                (radius, radius),
                radius,
                0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dt):
        jitter_x, jitter_y = 0, 0
        if self.pos.x-self.radius > self.SCREEN_WIDTH-1 or self.pos.x <= self.radius*3:
            self.direction.x *= -1
            jitter_x = self.jitter_speed*self.direction.x*random()

        if self.pos.y-self.radius > self.SCREEN_HEIGHT-1 or self.pos.y <= self.radius*3:
            self.direction.y *= -1
            jitter_y = self.jitter_speed*self.direction.y*random()

        displacement = vec2d((
                self.direction.x * self.speed * dt,
                self.direction.y * self.speed * dt))

        self.pos += displacement

        self.rect.center = ((
                self.pos.x - self.image.get_size()[0],
                self.pos.y - self.image.get_size()[1]))


class Wall(pygame.sprite.Sprite):

    def __init__(self, pos, w, h):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos)
        self.w = w
        self.h = h
        
        image = pygame.Surface([w, h])
        image.fill( (10, 10, 10) )
        self.image = image.convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.center = pos

    def draw(self, screen):
        pygame.draw.rect(screen, (10, 10, 10), [self.pos.x, self.pos.y, self.w, self.h], 0)

class Player(pygame.sprite.Sprite):

    def __init__(self, 
            radius, 
            color, 
            speed, 
            pos_init,
            SCREEN_WIDTH,
            SCREEN_HEIGHT):

        pygame.sprite.Sprite.__init__(self)
        
        self.bounce_force = 0.0 #decays

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
 
        self.pos = vec2d(pos_init)
        self.vel = vec2d((0,0))

        image = pygame.Surface([radius*2, radius*2])
        image.set_colorkey((0,0,0))

        pygame.draw.circle(
                image,
                color,
                (radius, radius),
                radius,
                0
        )
        
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect()
        self.radius = radius

    def update(self, dx, dy, dt):
        self.vel.x += dx
        self.vel.y += dy

        self.vel.x = self.vel.x*0.9
        self.vel.y = self.vel.y*0.9

        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        if self.pos.x < self.radius:
            self.pos.x = self.radius
            self.vel.x *= self.bounce_force

        if self.pos.x > self.SCREEN_WIDTH-(self.radius):
            self.pos.x = self.SCREEN_WIDTH-(self.radius)
            self.vel.x *= self.bounce_force

        if self.pos.y < self.radius:
            self.pos.y = self.radius
            self.vel.x *= self.bounce_force

        if self.pos.y > self.SCREEN_HEIGHT-(self.radius):
            self.pos.y = self.SCREEN_HEIGHT-(self.radius)
            self.vel.y *= self.bounce_force

        self.rect.center = (self.pos.x, self.pos.y)     
