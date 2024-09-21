import pygame
import neat
import random
import os
import pickle

pygame.init()


WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

FPS = 60

WHITE = (255,255,255)
BLACK = (0,0,0)

PADDLE_WIDTH, PADDLE_HEIGHT = 20,100
BALL_RADIUS = 7

SCORE_FONT = pygame.font.SysFont("Verdana", 40)
WIN_FONT = pygame.font.SysFont("Verdana", 60)
HIT_FONT = pygame.font.SysFont("Verdana", 40)
WINNING_SCORE = 10

left_hits = 0
right_hits = 0


class GameInformation:
	def __init__(self, left_hits, right_hits, left_score, right_score):
		self.left_hits = left_hits
		self.right_hits = right_hits
		self.left_score = left_score
		self.right_score = right_score

class Ball:
	MAX_VEL = 5
	COLOR = WHITE
	def __init__(self, x, y, radius):
		self.x = self.original_x = x
		self.y = self.original_y = y
		self.radius = radius
		self.x_vel = random.choice([-self.MAX_VEL, self.MAX_VEL])
		self.y_vel = random.uniform(-1,1)

	def draw(self, win):
		pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

	def move(self):
		self.x += self.x_vel
		self.y += self.y_vel

	def reset(self):
		if self.x < 0:
			self.x_vel = self.MAX_VEL
		elif self.x + self.radius > WIDTH:
			self.x_vel = self.MAX_VEL * -1
		self.x = self.original_x
		self.y = self.original_y
		self.y_vel = random.uniform(-1,1)
		

class Paddle:
	COLOR = WHITE
	VELOCITY = 4
	def __init__(self, x, y, width, height):
		self.x = self.original_x = x
		self.y = self.original_y = y
		self.width = width
		self.height = height

	def draw(self, win):
		pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

	def move(self, up = True):
		if up:
			self.y -= self.VELOCITY
		else:
			self.y += self.VELOCITY

	def reset(self):
		self.x = self.original_x
		self.y = self.original_y


def draw(win, paddles, ball, left_score, right_score, right_hits):
	win.fill(BLACK)

	left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
	right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
	right_hits_text = HIT_FONT.render(f"{right_hits}", 1, WHITE)


	win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()/2, 20))
	win.blit(right_score_text, (WIDTH * (3/4) - right_score_text.get_width()/2, 20))
	if right_hits != -1:
		win.blit(right_hits_text, (WIDTH//2, 10))

	for paddle in paddles:
		paddle.draw(win)


	for i in range(10, HEIGHT, HEIGHT//20):
		if i % 2 == 1:
			continue
		pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))

	ball.draw(win)

	pygame.display.update()

def handle_paddle_movement(keys, left_paddle):
	if keys[pygame.K_w] and left_paddle.y - left_paddle.VELOCITY >= 0:
		left_paddle.move(up = True)
	if keys[pygame.K_s] and left_paddle.y + left_paddle.VELOCITY + left_paddle.height <= HEIGHT:
		left_paddle.move(up = False)

def handle_collisions(ball, left_paddle, right_paddle):
	if ball.y + ball.radius >= HEIGHT:
		ball.y_vel *= -1
	elif ball.y - ball.radius <= 0:
		ball.y_vel *= -1

	if ball.x_vel < 0:
		if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
			if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
				ball.x_vel *= -1
				global left_hits
				left_hits+=1
				middle_y = left_paddle.y + left_paddle.height / 2
				difference_in_y = middle_y - ball.y

				reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
				y_vel = difference_in_y / reduction_factor
				ball.y_vel = y_vel * -1
				if ball.y_vel < 0:
					ball.y_vel -= 1
				elif ball.y_vel > 0:
					ball.y_vel += 1

				if ball.x_vel < 0:
					ball.x_vel -= 0.7
				elif ball.x_vel > 0:
					ball.x_vel += 0.7
	else:
		if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
			if ball.x + ball.radius >= right_paddle.x:
				ball.x_vel *= -1
				global right_hits
				right_hits+=1
				middle_y = right_paddle.y + right_paddle.height / 2
				difference_in_y = middle_y - ball.y

				reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
				y_vel = difference_in_y / reduction_factor
				ball.y_vel = y_vel * -1

				if ball.y_vel < 0:
					ball.y_vel -= 1
				elif ball.y_vel > 0:
					ball.y_vel += 1

				if ball.x_vel < 0:
					ball.x_vel -= 1
				elif ball.x_vel > 0:
					ball.x_vel += 1



def main(genome1, genome2, config):
	global right_hits
	global left_hits
	right_hits = 0
	left_hits = 0
	def calculate_fitness(genome1, genome2, game_info):
		
		genome1.fitness += game_info.left_hits
		genome2.fitness += game_info.right_hits


	running = True
	clock = pygame.time.Clock()

	net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
	net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

	left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
	right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
	ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS)

	left_score = 0
	right_score = 0
	

	while running:
		clock.tick(100000)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				pygame.quit()
				quit()
				break
		draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score, right_hits)
		gameInformation = GameInformation(left_hits, right_hits, left_score, right_score)
		game_info = gameInformation

		if game_info.left_score >= 1 or game_info.right_score >= 1 or game_info.left_hits > 50:
			calculate_fitness(genome1, genome2, game_info)
			break

		output1 = net1.activate((left_paddle.y, ball.y, abs(left_paddle.x - ball.x)))
		decision1 = output1.index(max(output1))
		output2 = net2.activate((right_paddle.y, ball.y, abs(right_paddle.x - ball.x)))
		decision2 = output2.index(max(output2))
		

		if decision1 == 0:
			pass
		elif decision1 == 1 and left_paddle.y - left_paddle.VELOCITY >= 0:
			left_paddle.move(up = True)
		else:
			if left_paddle.y + left_paddle.VELOCITY + left_paddle.height <= HEIGHT:
				left_paddle.move(up = False)

		if decision2 == 0:
			pass
		elif decision2 == 1 and right_paddle.y - right_paddle.VELOCITY >= 0:
			right_paddle.move(up = True)
		else:
			if right_paddle.y + right_paddle.VELOCITY + right_paddle.height <= HEIGHT:
				right_paddle.move(up = False)

		



		ball.move()
		handle_collisions(ball, left_paddle, right_paddle)

		if ball.x < 0:
			right_score+=1
			genome2.fitness += 1
			genome1.fitness -= 1
			ball.reset()
		elif ball.x > WIDTH:
			left_score+=1
			genome1.fitness += 1
			genome2.fitness -= 1
			ball.reset()

		won = False


		

		

		
		

	


def eval_genomes(genomes, config):
	for i, (genome_id1, genome1) in enumerate(genomes):
		if i == len(genomes) - 1:
			break
		genome1.fitness = 0
		for genome_id2, genome2 in genomes[i+1:]:
			genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
			main(genome1, genome2, config)


def run_neat(config):
	#To load AI from a certain generation:
	#p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-16")
	p = neat.Population(config)
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	p.add_reporter(neat.Checkpointer(1))

	winner = p.run(eval_genomes, 100)
	with open("best.pickle", "wb") as f:
		pickle.dump(winner, f)

def test_ai(config):
	#To train AI
	#with open("best.pickle", "rb") as f:
	with open("ToughAI.pickle", "rb") as f:
		winner = pickle.load(f)
		
		playAgainstAI(winner)




def playAgainstAI(genome):
	
	running = True
	clock = pygame.time.Clock()

	net = neat.nn.FeedForwardNetwork.create(genome, config)
	

	left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
	right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
	ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS)

	left_score = 0
	right_score = 0
	

	while running:
		clock.tick(60)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				pygame.quit()
				quit()
				break
		draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score, -1)

		
		output = net.activate((right_paddle.y, ball.y, abs(right_paddle.x - ball.x)))
		decision = output.index(max(output))
		


		if decision == 0:
			pass
		elif decision == 1 and right_paddle.y - right_paddle.VELOCITY >= 0:
			right_paddle.move(up = True)
		else:
			if right_paddle.y + right_paddle.VELOCITY + right_paddle.height <= HEIGHT:
				right_paddle.move(up = False)



		keys = pygame.key.get_pressed()

		handle_paddle_movement(keys, left_paddle)

		ball.move()
		handle_collisions(ball, left_paddle, right_paddle)

		if ball.x < 0:
			right_score+=1
			ball.reset()
		elif ball.x > WIDTH:
			left_score+=1
			ball.reset()

		won = False

		if left_score >= WINNING_SCORE:
			won = True
			win_text = WIN_FONT.render("WIN", 1, WHITE)
			WIN.blit(win_text, (WIDTH//4 - win_text.get_width()//2, HEIGHT//2 - win_text.get_height()//2))
			pygame.display.update()
			pygame.time.delay(5000)
		elif right_score >= WINNING_SCORE:
			won = True
			win_text = WIN_FONT.render("WIN", 1, WHITE)
			WIN.blit(win_text, (WIDTH * (3/4) - win_text.get_width()//2, HEIGHT//2 - win_text.get_height()//2))
			pygame.display.update()
			pygame.time.delay(5000)
		if won:
			ball.reset()
			left_paddle.reset()
			right_paddle.reset()
			left_score = 0
			right_score = 0




if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, "config-feedforward.txt")
	
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

	#To train AI
	#run_neat(config)
	test_ai(config)