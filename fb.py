import pyglet
import random
from nn import *
import numpy as np
import gen
import warnings
warnings.filterwarnings('ignore')

#class for both bottom and top pipes, their movement and recycling
class Pipe:
    def __init__(self, x):
        self.hasPassed = False
        self.y = random.randint(150, 320)
        self.x = x
        self.sprites = pyglet.graphics.Batch()
        self.lower_pipe = pyglet.sprite.Sprite(pyglet.image.load('./pipe.png'), x = x, y = self.y - 320, batch = self.sprites)
        self.upper_pipe = pyglet.sprite.Sprite(pyglet.image.load('./pipe.png'), x = x + 50, y = self.y + 320 + 150, batch = self.sprites)
        self.upper_pipe.rotation = 180
    def update(self, dt):
        self.x = self.lower_pipe.x
        if self.lower_pipe.x <= -50:
            self.lower_pipe.x = pipe_count * pipe_distance - 50
            self.upper_pipe.x = pipe_count * pipe_distance
            new_y = random.randint(150, 320)
            self.lower_pipe.y = new_y - 320
            self.upper_pipe.y = new_y + 320 + 150
            self.y = new_y
            self.hasPassed = False
        else:
            self.lower_pipe.x -= 80 * dt
            self.upper_pipe.x -= 80 * dt

#bird's movement, ai and death
class Bird:

    def __init__(self):
        self.sprite = pyglet.sprite.Sprite(
        img = pyglet.image.Animation([
            pyglet.image.AnimationFrame(pyglet.image.load('./bird-downflap.png'), .15),
            pyglet.image.AnimationFrame(pyglet.image.load('./bird-mid.png'), .15),
            pyglet.image.AnimationFrame(pyglet.image.load('./bird-upflap.png'), .15)]
        ), x = 200, y = 400)
        self.isJumping = False
        self.speed = 0
        self.acceleration = 200
        self.jumpStep = 30
        self.nn = Agent(3, 1)
        self.isStopped = False
    
    def update(self, dt, x):
        if self.sprite.y > -50:
            if self.nn(x) >= 0:
                self.jump()
            if self.jumpStep < 0:
                self.isJumping = False
                self.jumpStep = 15
            if self.isJumping:
                self.acceleration = 200
                self.jumpStep -=1
                self.sprite.rotation = -20
            else:
                self.acceleration = -300
                self.sprite.rotation = 30
            self.sprite.y += self.speed
            self.speed = (self.speed + self.acceleration + 1) * dt
            
    def jump(self):
        if self.acceleration == 0:
            self.isJumping = False
            return
        self.isJumping = True

    def draw(self):
        self.sprite.draw()

    def stop(self, score, dx):
        self.acceleration = 0
        self.sprite.rotation = 0
        self.isJumping = False
        self.nn.score = (score)*200 + dx
        self.sprite.visible = False
        self.isStopped = True


#after how many generations to start over
max_generations = 10
#amount of birds
population_size = 48
num_mutants = population_size // 3
#number of birds from current population taken as parents for a new generation 
num_parents = 4
#number of pipes in the game
pipe_count = 7
#distance between the pipes
pipe_distance = 150

window = pyglet.window.Window(caption='Flappy Bird (AI Edition)', resizable=True, width=1000, height=600)
gui = pyglet.graphics.Batch()
card_border = pyglet.shapes.Rectangle(width=304, height=204, x=678, y = 18, color=(0,0,0))
card = pyglet.shapes.Rectangle(width=300, height=200, x=680, y = 20)
live_birds_label = pyglet.text.Label('Birds left: 0', font_size=24, batch=gui, x = 700, y=176, color=(0,0,0, 255))
score_label = pyglet.text.Label('0', font_size=32, x=500, y=500, batch=gui)
generarion_label = pyglet.text.Label('Generation: 1', font_size=24, x=700, y=142, batch=gui, color=(0,0,0, 255))
max_score = 0
max_score_label = pyglet.text.Label('Max score: 0', font_size=24, x=700, y=40, color=(0,0,0, 255), batch=gui)

population = [Bird() for i in range(population_size)]
parents = []
pipes = [Pipe(600 + i*pipe_distance) for i in range(pipe_count)]
bg = pyglet.image.load('./bg.png')

@window.event
def on_draw():
    window.clear()
    bg.blit(0,0)
    for pipe in pipes:
        pipe.sprites.draw()
    for bird in population:
        bird.draw()
    card_border.draw()
    card.draw()
    gui.draw()

score=0
def update(dt):
    global score, population, parents, score_label, pipes, generarion_label, live_birds_label, max_score, max_score_label
    c_pipe = pipes[score%pipe_count]
    #update pipes
    for pipe in pipes:
        pipe.update(dt)
    #update birds
    for bird in population:
        bird.update(
            dt, 
            np.array([c_pipe.x - 200,
            c_pipe.y - bird.sprite.y,
            150 - (c_pipe.y - bird.sprite.y)], dtype=np.float64)
        )
    #collision check
    for bird in population:
        if not bird.isStopped:
            if (((c_pipe.x >= 150 and c_pipe.x <= 200) and (bird.sprite.y < c_pipe.y or bird.sprite.y + 30 > c_pipe.y + 150))):
                bird.stop(score, c_pipe.x - 200)
                parents.append(bird.nn)
                live_birds_label.text = 'Birds left: ' + str(population_size-len(parents)) + '/' + str(population_size)
            if (bird.sprite.y > 570) or (bird.sprite.y < 0):
                bird.stop(score, c_pipe.x - 200)
                parents.append(bird.nn)
                live_birds_label.text = 'Birds left: ' + str(population_size-len(parents)) + '/' + str(population_size)
    #if a pipe is behind the birds increase the score
    if (c_pipe.x + 50 > 0 and c_pipe.x + 50 < 200) and (c_pipe.hasPassed == False):
                c_pipe.hasPassed = True
                score += 1
                if score > max_score:
                    max_score = score
                    max_score_label.text = 'Max score: ' + str(max_score)
                score_label.text = str(score)
    #reset the game state and prepare new generation
    if (len(parents) == population_size):
        if int(generarion_label.text.split(' ')[-1]) >= 20:
            population = [Bird() for i in range(population_size)]
            generarion_label.text = 'Generation: 1'
        else:
            parents = parents[-1:-(num_parents+1):-1]
            print(len(parents))
            population = [Bird() for i in range(population_size)]
            brains = gen.EVO(population_size, num_parents, num_mutants).step(parents)
            for i in range(16):
                population[i].nn = brains[i]
            generarion_label.text = 'Generation: ' + str(int(generarion_label.text.split(' ')[-1]) + 1)
        parents = []
        pipes = [Pipe(600 + i*pipe_distance) for i in range(pipe_count)]
        score = 0
        score_label.text = str(score)
        

pyglet.clock.schedule_interval(update, 1/60.)
pyglet.app.run()