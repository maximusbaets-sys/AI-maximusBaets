import pygame


pygame.init()


GRID_SIZE = 8
PLAYER_SIZE = 8
STEP_SIZE = 8
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

player1 = pygame.Rect((200, 400, PLAYER_SIZE, PLAYER_SIZE))
player1_dir = (STEP_SIZE, 0)
next_dir1 = player1_dir

player2 = pygame.Rect((1000, 400, PLAYER_SIZE, PLAYER_SIZE))
player2_dir = (-STEP_SIZE, 0)
next_dir2 = player2_dir

player1_trail = []
player2_trail = []
run = True



while run:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False   
#PLAYER1
    key = pygame.key.get_pressed()
    if key[pygame.K_a] and player1_dir != (STEP_SIZE, 0):
        next_dir1 = (-STEP_SIZE, 0)
    elif key[pygame.K_d] and player1_dir != (-STEP_SIZE, 0):
        next_dir1 = (STEP_SIZE, 0)
    elif key[pygame.K_w] and player1_dir != (0, STEP_SIZE):
        next_dir1 = (0, -STEP_SIZE)
    elif key[pygame.K_s] and player1_dir != (0, -STEP_SIZE):
        next_dir1 = (0, STEP_SIZE)

    if player1.x % GRID_SIZE == 0 and player1.y % GRID_SIZE == 0:
        player1_dir = next_dir1

    player1_trail.append(player1.copy())
    player1.move_ip(player1_dir)


    for segment in player1_trail:
        pygame.draw.rect(screen, (0, 255, 255), segment)
    pygame.draw.rect(screen, (255, 255, 255), player1) 

    #PLAYER2
    key = pygame.key.get_pressed()
    if key[pygame.K_LEFT] and player2_dir != (STEP_SIZE, 0):
        next_dir2 = (-STEP_SIZE, 0)
    elif key[pygame.K_RIGHT] and player2_dir != (-STEP_SIZE, 0):
        next_dir2 = (STEP_SIZE, 0)
    elif key[pygame.K_UP] and player2_dir != (0, STEP_SIZE):
        next_dir2 = (0, -STEP_SIZE)
    elif key[pygame.K_DOWN] and player2_dir != (0, -STEP_SIZE):
        next_dir2 = (0, STEP_SIZE)

    if player2.x % GRID_SIZE == 0 and player2.y % GRID_SIZE == 0:
        player2_dir = next_dir2

    player2_trail.append(player2.copy())
    player2.move_ip(player2_dir)


    for segment in player2_trail:
        pygame.draw.rect(screen, (255, 165, 0), segment)
    pygame.draw.rect(screen, (255, 255, 255), player2) 

    
    #collision
    if player2.left < 0 or player2.right > SCREEN_WIDTH or player2.top < 0 or player2.bottom > SCREEN_HEIGHT:
        run = False   
    if player1.left < 0 or player1.right > SCREEN_WIDTH or player1.top < 0 or player1.bottom > SCREEN_HEIGHT:
        run = False
    #run into yourself
    for segment in player1_trail[:-5]: 
        if player1.colliderect(segment):
            run = False      
    for segment in player2_trail[:-5]: 
        if player2.colliderect(segment):
            run = False
    #Run into other trail
    if player1.collidelist(player2_trail) != -1:
     run = False
    if player2.collidelist(player1_trail) != -1:
     run = False
              
    clock.tick(60)
    pygame.display.update()

pygame.quit()