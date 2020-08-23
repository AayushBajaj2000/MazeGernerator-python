import pygame
import random

pygame.init()
pygame.display.set_caption("Maze")
icon = pygame.image.load('maze_icon.png')
pygame.display.set_icon(icon)

# --------------------------------------------------------- #

def drawGrid(surface, Grid_object, width):
    for wall in Grid_object.walls:
        start = wall.start
        end = wall.end
        pygame.draw.line(surface, (0, 0, 0), (start[0] * width + center, start[1] * width + center),
                         (end[0] * width + center, end[1] * width + center), 4)


def update(maze):
    pygame.event.get()
    pygame.time.delay(0)
    screen.fill((255, 255, 255))
    drawGrid(screen, maze.mainGrid, width)
    pygame.display.update()
    

def kill():
    pygame.display.quit()
    pygame.quit()
    exit()    

# --------------------------------------------------------- #

def buildRelationships(nodeList):
    for a in nodeList:
        for b in a:
            for w in b.connected_walls:
                if w is not None:
                    w.attached_nodes.append(b)


def createNodeList(n, connected_walls):
    nodeList = []
    for a in range(n):
        nodeList.append([])
        for b in range(n):
            if a == 0:
                top = None
            else:
                top = connected_walls[(a - 1) * ((2 * (n - 1)) + 1) + b + (n - 1)]

            if a == n - 1:
                bottom = None
            else:
                bottom = connected_walls[(a * ((2 * (n - 1)) + 1) + b + (n - 1))]

            if b == 0:
                left = None
            else:
                left = connected_walls[(a * ((2 * (n - 1)) + 1) + b - 1)]

            if b == n - 1:
                right = None
            else:
                right = connected_walls[(a * ((2 * (n - 1)) + 1) + b)]

            nodeList[a].append(Node(top, left, right, bottom))
    return nodeList


def find_path(maze, index, copy, start, visited_nodes, path):
    if start == maze.vertices[maze.n-1][-(index + 1)]:
        maze.finalPath.append(path)

    connected_walls = start.connected_walls_copy

    for wall in connected_walls:
        if wall is not None:
            if ((wall in copy) and (wall not in maze.dualGrid.dual_walls) and (wall not in path)):
                for node in wall.attached_nodes:
                    if node != start and node not in visited_nodes:
                        pat = [wall]
                        vn = [node]
                        find_path(maze, index, copy, node, visited_nodes+vn, path+pat)

# --------------------------------------------------------- #

class Wall:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.weight = random.randint(0, 10)


class DualWall:
    def __init__(self, weight, ref):
        self.start = 0
        self.end = 0        
        self.weight = weight
        self.ref = ref
        self.attached_nodes = []

        if (ref.start[1] == ref.end[1]):
            self.start = (ref.start[0] + 0.5, ref.start[1] - 0.5)
            self.end = (ref.end[0] - 0.5, ref.end[1] + 0.5)
        else:
            self.start = (ref.start[0] - 0.5, ref.start[1] + 0.5)
            self.end = (ref.end[0] + 0.5, ref.end[1] - 0.5)         


class Grid:
    def __init__(self, n):
        self.walls = []
        for y in range(n + 1):
            for x in range(n):
                self.walls.append(Wall((x, y), (x + 1, y)))

            if y < n:
                for x in range(n + 1):
                    self.walls.append(Wall((x, y), (x, y + 1)))


class DualGrid:
    def __init__(self, n, walls):
        self.dual_walls = []
        for a in range(n + 1):
            for b in range(n):
                self.dual_walls.append(DualWall(walls[(a * ((2 * (n + 1)) + 1) + (n + 1) + 1 + b)].weight,
                                            walls[(a * ((2 * (n + 1)) + 1) + (n + 1) + 1 + b)]))

            if a < n:
                for b in range(n + 1):
                    self.dual_walls.append(DualWall(walls[((a + 1) * ((2 * (n + 1)) + 1) + b)].weight,
                                                walls[((a + 1) * ((2 * (n + 1)) + 1) + b)]))


class Node:
    def __init__(self, top, left, right, bottom):
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        self.connected_walls = [self.top, self.left, self.right, self.bottom]
        self.connected_walls_copy = [self.top, self.left, self.right, self.bottom]


class Maze:
    def __init__(self, n):
        self.n = n
        self.mainGrid = Grid(n)
        self.dualGrid = DualGrid(n - 1, self.mainGrid.walls)
        self.vertices = createNodeList(n, self.dualGrid.dual_walls)
        buildRelationships(self.vertices)
        self.finalPath = []

        self.minimuimSpanningTree()

    def minimuimSpanningTree(self):
        # REMOVE RANDOM START AND FINISH
        start_finish_index = random.randint(0, self.n - 1)
        del self.mainGrid.walls[(start_finish_index)]
        del self.mainGrid.walls[(-(start_finish_index + 1))]

        maze_copy = self.dualGrid.dual_walls.copy() # Copy of maze for solution

        # Choose a random node to start from
        currentNode = random.choice(random.choice(self.vertices))

        # List for all visited nodes
        visited_nodes = [currentNode] # Add randomly chosen node to it

        stoppingCondition = False # Stopping condition boolean


        while (not stoppingCondition):
            # Clear and initialize availableWalls list
            availableWalls = []

            # Take current node, and add all connected walls to AW list
            for node in visited_nodes:
                for wall in node.connected_walls:
                    if wall is not None:
                        if wall not in availableWalls:
                            availableWalls.append(wall)

            # The only time there will be no available walls is when the maze is complete, so we test for it and end the loop when we reach this case
            if len(availableWalls) == 0:
                stoppingCondition = True
                continue

            # Initialize and reset lowestWall to search for new lowestWall
            lowestWall = None

            # Loop through all walls in AW list and find one with least weight
            for wall in availableWalls:
                if lowestWall is not None:
                    if wall.weight < lowestWall.weight:
                        lowestWall = wall
                else:
                    lowestWall = wall

            # Check to see if both the nodes atatched to the lowest wall are in visited_nodes
            result = all(node in visited_nodes for node in lowestWall.attached_nodes)

            for node in lowestWall.attached_nodes:
                node.connected_walls.remove(lowestWall)

                if node not in visited_nodes:
                    visited_nodes.append(node)            

            if result == True:
                continue

            self.dualGrid.dual_walls.remove(lowestWall)
            self.mainGrid.walls.remove(lowestWall.ref)

            update(self)

        print("The maze is complete")

        starting_node = self.vertices[0][start_finish_index]

        find_path(self, start_finish_index, maze_copy, starting_node, [starting_node], [])

# --------------------------------------------------------- #

n = 15
sizeX = 1200
sizeY = 1200
width = sizeX/n - 5
running = True
center = (sizeX - width * n) / 2

screen = pygame.display.set_mode((sizeX, sizeY))

maze = Maze(n)

for wall in maze.finalPath[0]:
    start = wall.start
    end = wall.end
    pygame.draw.line(screen, (255, 0, 0), (start[0] * width + center, start[1] * width + center),
                     (end[0] * width + center, end[1] * width + center), 4)    
    pygame.display.update()
    pygame.time.delay(25)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            kill()
