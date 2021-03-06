# Import Python libraries
import copy
import pygame
import random
import pyperclip as pc
import csv
import time

pygame.init()

WIDTH = 800
SIMWIDTH = WIDTH - 300
HEIGHT = 500
FPS = 60
CELLSIZE = 4

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("test GoL")

font = pygame.font.Font('freesansbold.ttf', 17)
font2 = pygame.font.Font('freesansbold.ttf', 32)

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)


class Analyzer:
    def __init__(self, cells, tempCells):
        self.cells = cells
        self.tempCells = tempCells

    def analyze(self, cells, tempCells):
        self.update(cells, tempCells)

        x = round(self.average(), 3)

        return x, round(self.connect(),3) - x, round(self.chaos(), 3)

    def update(self, cells, tempCells):
        self.cells = cells
        self.tempCells = tempCells

    def average(self):
        num = 0

        for i in range(0, len(self.cells) - 1):

            for j in range(0, len(self.cells[0]) - 1):
                num += self.cells[i][j]

        return (num / (len(self.cells) * len(self.cells[0])))*100

    def connect(self):
        num = 0
        count = 0

        for x in range(0, len(self.cells) - 1):

            for y in range(0, len(self.cells[0]) - 1):
                if(self.cells[x][y] == 1):
                    count += 1
                    num += (self.cells[x-1][y+1] + self.cells[x][y+1] + self.cells[x+1][y+1] + self.cells[x-1][y] + self.cells[x+1][y] + self.cells[x-1][y-1] + self.cells[x][y-1] + self.cells[x+1][y-1])/8

        return (num / count)*100

    def chaos(self):
        num = 0

        for x in range(0, len(self.cells) - 1):

            for y in range(0, len(self.cells[0]) - 1):
                if self.cells[x][y] != self.tempCells[x][y]:
                    num += 1

        return (num / (len(self.cells) * len(self.cells[0])))*100


class UserInterface:
    def __init__(self, rule_set):
        self.x = WIDTH-300
        self.color1 = (150, 150, 150)
        self.color2 = (100, 100, 100)

        self.genX, self.genY = WIDTH-290, 10
        self.statusX, self.statusY = WIDTH - 290, 40
        self.ruleX, self.ruleY = WIDTH - 290, 70
        self.pauseX, self.pauseY = 0, 0
        self.button_clearX, self.button_clearY = WIDTH - 285, 160
        self.button_new_seedX, self.button_new_seedY = WIDTH - 285, 200
        self.button_copyX, self.button_copyY = WIDTH - 285, 240
        self.enterX, self.enterY = WIDTH - 285, 280

        self.ruleset = rule_set

        self.clear = False
        self.random = False
        self.deadGen = 0
        self.checkDead = True
        self.copy = False
        self.button_clear_hover = False

    # draws all the buttons and stuff
    def draw(self, step, paused, dead):
        pygame.draw.rect(WIN, self.color1, (self.x, 0, 300, HEIGHT))
        # pygame.draw.rect(WIN, self.color2, (self.x, 0, 5, HEIGHT))
        pygame.draw.rect(WIN, self.color2, (self.button_clearX-5, self.button_clearY-5, 90, 30))
        pygame.draw.rect(WIN, self.color2, (self.button_new_seedX - 5, self.button_new_seedY - 5, 90, 30))
        pygame.draw.rect(WIN, self.color2, (self.button_copyX - 5, self.button_copyY - 5, 90, 30))

        generation = font.render("generation: " + str(step), True, (0, 0, 0))
        rule = font.render("Ruleset: " + str(self.ruleset), True, (0, 0, 0))
        button_clear = font.render("Clear", True, (0, 0, 0))
        button_new_seed = font.render("New Seed", True, (0, 0, 0))
        button_copy = font.render("Copy", True, (0, 0, 0))
        enter = font.render("Enter ruleset: ", True, (0, 0, 0))

        if dead:
            if self.checkDead:
                self.deadGen = step
                self.checkDead = False
            status = font.render("Status: Dead (gen "+str(self.deadGen)+")", True, (0, 0, 0))
        else:
            self.checkDead = True
            status = font.render("Status: Alive", True, (0, 0, 0))

        if paused:
            pause = font2.render("Paused", True, (75, 75, 200))
        else:
            pause = font2.render("", True, (75, 75, 200))

        WIN.blit(generation, (self.genX, self.genY))
        WIN.blit(status, (self.statusX, self.statusY))
        WIN.blit(rule, (self.ruleX, self.ruleY))
        WIN.blit(pause, (self.pauseX, self.pauseY))
        WIN.blit(button_clear, (self.button_clearX, self.button_clearY))
        WIN.blit(button_new_seed, (self.button_new_seedX, self.button_new_seedY))
        WIN.blit(button_copy, (self.button_copyX, self.button_copyY))
        WIN.blit(enter, (self.enterX, self.enterY))
        # [0, 0, 1, 1, 0, 0, 2, 0, 1]

    # checks to see if a button has been clicked
    def button_press(self, x, y, click2):
        if (x > self.button_clearX-5) and (x < self.button_clearX+50):
            if (y > self.button_clearY-5) and (y < self.button_clearX+25):
                self.clear = True

        if (x > self.button_new_seedX-5) and (x < self.button_new_seedX+85) and click2:
            if (y > self.button_new_seedY-5) and (y < self.button_new_seedY+25):
                self.random = True

        if (x > self.button_copyX-5) and (x < self.button_copyX+85):
            if (y > self.button_copyY-5) and (y < self.button_copyY+25):
                self.copy = True


# Handles rule set compilation
class RuleSets:
    def __init__(self):
        self.ruleset = []

    def getRule(self, num):
        return self.ruleset[num]


# InputBox Class, makes InputBox objects which can be used as input
class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.textsave = ''
        self.hasText = False
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    # checks whether a inputbox has been clicked
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False

            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.textsave = self.text
                    self.hasText = True
                    self.text = ''

                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]

                else:
                    self.text += event.unicode
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    # draws textbox to screen
    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)


# draws cells on the screen
def draw_cells(cells):
    color = (250, 250, 250)
    for i in range(len(cells)):
        for j in range(len(cells[0])):
            if cells[i][j] == 1:
                x = i * CELLSIZE
                y = j * CELLSIZE
                pygame.draw.rect(WIN, color, (x, y, CELLSIZE, CELLSIZE))


# draws the grid on top of the screen and cells
def draw_grid():
    color = (0, 0, 0)

    for i in range(HEIGHT // CELLSIZE):
        pygame.draw.line(WIN, color, (0, i * CELLSIZE), (SIMWIDTH, i * CELLSIZE))
    for i in range(SIMWIDTH // CELLSIZE):
        pygame.draw.line(WIN, color, (i * CELLSIZE, 0), (i * CELLSIZE, HEIGHT))


# adds a cell to the screen if the user clicks, removes on right click
def add_cell(x, y, cells, click, right_click):
    try:
        if click and x <= SIMWIDTH:
            cells[x // CELLSIZE][y // CELLSIZE] = 1
        elif right_click and x <= SIMWIDTH:
            cells[x // CELLSIZE][y // CELLSIZE] = 0
    except IndexError:
        pass

    return cells


# counts the amount of alive neighbours a cell has
def count_alive(cells, x, y):
    return cells[x-1][y+1] + cells[x][y+1] + cells[x+1][y+1] + cells[x-1][y]\
           + cells[x+1][y] + cells[x-1][y-1] + cells[x][y-1] + cells[x+1][y-1]


# each cell checks its neighbours and then updates its status according to the rule set
def update_cells(cells, rule_set, dead):
    new_cells = copy.deepcopy(cells)
    checked = False

    for i in range(0, len(cells) - 1):

        for j in range(0, len(cells[0]) - 1):

            alive = count_alive(cells, i, j)
            num = rule_set[alive]

            if int(num) == 1:
                new_cells[i][j] = 0
                if not checked and (cells[i][j] != 0):
                    dead = False
                    checked = True

            elif rule_set[alive] == 2:
                new_cells[i][j] = 1

                if not checked and (cells[i][j] != 1):
                    dead = False
                    checked = True

    if not checked:
        dead = True

    return new_cells, dead

    # [1, 1, 0, 2, 1, 1, 1, 1, 1]


# main update loop, checks for UI interactions, displays data and cells
def update(x, y, cells, click, right_click, paused, ui, step, dead, click2, input_box1, rule_counter, rules):
    rule_set = rules.getRule(rule_counter)

    if click or right_click:
        cells = add_cell(x, y, cells, click, right_click)
        ui.button_press(x, y, click2)

    if ui.clear:
        cells = [[0 for j in range(0, (HEIGHT // CELLSIZE))] for i in range(0, (SIMWIDTH // CELLSIZE))]
        ui.clear = False

    if ui.random:
        paused = True

        cells = [[0 for j in range(0, (HEIGHT // CELLSIZE))] for i in range(0, (SIMWIDTH // CELLSIZE))]
        rule_set = []
        for i in range(9):
            rule_set.append(random.randint(0, 2))
        ui.ruleset = rule_counter
        ui.random = False
        step = 0
        dead = True

    if input_box1.hasText:

        if len(input_box1.textsave) > 7:
            paused = True
            rule_set = []
            cells = [[0 for j in range(0, (HEIGHT // CELLSIZE))] for i in range(0, (SIMWIDTH // CELLSIZE))]

            for char in input_box1.textsave:
                rule_set.append(int(char))

            input_box1.textsave = ''
            ui.ruleset = rule_counter
            step = 0
            dead = True

        input_box1.hasText = False
        input_box1.textsave = ''

    if ui.copy:
        pc.copy(str(rule_set))
        ui.copy = False

    if not paused:
        cells, dead = update_cells(cells, rule_set, dead)
        step += 1

    WIN.fill((0, 0, 0))
    draw_cells(cells)

    draw_grid()

    ui.draw(step, paused, dead)

    if dead:
        step = 0

    return cells, step, dead, rule_set, paused


# generates all rule sets recursively
def generateAllRules(n, arr, i, rules):
    if i == n:
        rule = [int(i) for i in arr]
        rules.ruleset.append(rule)
        return

    arr[i] = 0
    generateAllRules(n, arr, i + 1, rules)
    arr[i] = 1
    generateAllRules(n, arr, i + 1, rules)
    arr[i] = 2
    generateAllRules(n, arr, i + 1, rules)


# writes data to CAdata.csv
def writeFile(data):
    with open('CAdata.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


# main pygame loop, checks for user inputs and interactions as well as initialization
def main():
    clock = pygame.time.Clock()
    previous = time.time() * 1000

    run = True
    click = False
    right_click = False
    paused = True
    step = 0
    dead = False
    waiting = False
    counter = 0

    cells = [[random.randint(0, 1) for j in range(0, (HEIGHT // CELLSIZE))] for i in range(0, SIMWIDTH // CELLSIZE)]

    input_box1 = InputBox(WIDTH - 285, 300, 140, 32)
    input_boxes = [input_box1]

    n = 9
    arr = [None] * n
    rules = RuleSets()
    generateAllRules(n, arr, 0, rules)

    rule_counter = 3179
    rule_set = []

    ui = UserInterface(rule_set)

    solve = Analyzer(cells, tempCells=None)

    data = [["RuleSet", "Average Value", "Connectedness", "Chaos"]]

    while run:
        current = time.time() * 1000
        elapsed = current - previous
        previous = current
        delay = 1000.0 / FPS - elapsed
        delay = max(int(delay), 0)

        x, y = pygame.mouse.get_pos()
        pressed = pygame.key.get_pressed()
        click2 = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # checks for right and left input
            if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and event.button == 3:
                if right_click:
                    right_click = False
                else:
                    right_click = True
            if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and event.button == 1:
                if click:
                    click = False
                else:
                    click = True

            # handles left and right click interactions
            if (event.type == pygame.MOUSEBUTTONDOWN) and event.button == 1:
                if not waiting:
                    click2 = True
                    waiting = True
            if (event.type == pygame.MOUSEBUTTONUP) and event.button == 1:
                waiting = False

            # handles space bar interactions
            if event.type == pygame.KEYUP:
                if pressed[pygame.K_SPACE]:
                    if not paused:
                        paused = True
                    else:
                        paused = False

            # calls for box interactions if the user is clicking
            for box in input_boxes:
                box.handle_event(event)

        # updates boxes
        for box in input_boxes:
            box.update()

        # main update function
        cells, step, dead, rule_set, paused = update(x, y, cells, click, right_click,
                                                     paused, ui, step, dead, click2, input_box1, rule_counter, rules)

        pygame.display.flip()
        pygame.time.delay(delay)

        # draws boxes
        for box in input_boxes:
            box.draw(WIN)

        if counter == 24:
            tempCells = copy.deepcopy(cells)

        if counter == 25:
            average, connect, chaos = solve.analyze(cells, tempCells)

            data.append([rule_counter, average, connect, chaos])

            counter = 0
            rule_counter +=1

            cells = [[random.randint(0, 1) for j in range(0, (HEIGHT // CELLSIZE))]
                     for i in range(0, (SIMWIDTH // CELLSIZE))]

            writeFile(data)

        if not paused:
            counter += 1

    pygame.quit()


if __name__ == '__main__':
    main()
