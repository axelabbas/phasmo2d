import pygame

# Constants
CELL_SIZE = 20  # Match your block width scaling
NORTH, SOUTH, EAST, WEST = 0, 1, 2, 3

# Edge structure
class Edge:
    def __init__(self, sx, sy, ex, ey):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey

# Cell structure
class Cell:
    def __init__(self):
        self.exist = False
        self.edge_exist = [False] * 4  # NORTH, SOUTH, EAST, WEST
        self.edge_id = [0] * 4

# Initialize world grid
def create_world(width, height):
    return [[Cell() for _ in range(width)] for _ in range(height)]

# Sample level data (converted to grid coordinates)
level_data = ["0;0", "20;5", "19;5", "18;5", "1;0", "2;0", "3;0", "4;0", "3;2", "1;2", "2;2", "0;2", "4;2", "5;2", "7;0", "5;0", "6;0", "6;2", "7;2", "8;4", "9;4", "11;4", "13;4", "10;4", "12;4", "16;4", "17;4", "18;4", "20;4", "19;4", "30;2", "28;2", "29;2", "27;2", "26;2", "25;2", "23;2", "24;2", "22;4", "21;4", "17;5", "16;5", "10;5", "11;5", "12;5", "13;5", "24;0", "23;0", "25;0", "26;0", "28;0", "27;0", "29;0", "30;0", "10;9", "8;9", "9;10", "14;10", "24;10", "24;13", "22;9", "20;12"]

# Populate world grid
max_x = max(int(cell.split(';')[0]) for cell in level_data) + 2
max_y = max(int(cell.split(';')[1]) for cell in level_data) + 2
world = create_world(max_x, max_y)

for cell in level_data:
    x, y = map(int, cell.split(';'))
    world[y][x].exist = True

# Convert tilemap to polygon edges
vec_edges = []

def convert_tilemap_to_polymap(sx, sy, w, h):
    global vec_edges
    vec_edges.clear()

    # Iterate through region (offset by 1 to avoid boundary checks)
    for x in range(sx + 1, sx + w - 1):
        for y in range(sy + 1, sy + h - 1):
            current_cell = world[y][x]
            if not current_cell.exist:
                continue

            # Check neighbors
            west_cell = world[y][x - 1]
            east_cell = world[y][x + 1]
            north_cell = world[y - 1][x]
            south_cell = world[y + 1][x]

            # WEST EDGE
            if not west_cell.exist:
                if north_cell.edge_exist[WEST]:
                    # Extend northern neighbor's west edge
                    edge = vec_edges[north_cell.edge_id[WEST]]
                    edge.ey += CELL_SIZE
                    current_cell.edge_id[WEST] = north_cell.edge_id[WEST]
                    current_cell.edge_exist[WEST] = True
                else:
                    # Create new west edge
                    edge = Edge(
                        x * CELL_SIZE, y * CELL_SIZE,
                        x * CELL_SIZE, (y + 1) * CELL_SIZE
                    )
                    vec_edges.append(edge)
                    current_cell.edge_id[WEST] = len(vec_edges) - 1
                    current_cell.edge_exist[WEST] = True

            # EAST EDGE
            if not east_cell.exist:
                if north_cell.edge_exist[EAST]:
                    # Extend northern neighbor's east edge
                    edge = vec_edges[north_cell.edge_id[EAST]]
                    edge.ey += CELL_SIZE
                    current_cell.edge_id[EAST] = north_cell.edge_id[EAST]
                    current_cell.edge_exist[EAST] = True
                else:
                    # Create new east edge
                    edge = Edge(
                        (x + 1) * CELL_SIZE, y * CELL_SIZE,
                        (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
                    )
                    vec_edges.append(edge)
                    current_cell.edge_id[EAST] = len(vec_edges) - 1
                    current_cell.edge_exist[EAST] = True

            # NORTH EDGE
            if not north_cell.exist:
                if west_cell.edge_exist[NORTH]:
                    # Extend western neighbor's north edge
                    edge = vec_edges[west_cell.edge_id[NORTH]]
                    edge.ex += CELL_SIZE
                    current_cell.edge_id[NORTH] = west_cell.edge_id[NORTH]
                    current_cell.edge_exist[NORTH] = True
                else:
                    # Create new north edge
                    edge = Edge(
                        x * CELL_SIZE, y * CELL_SIZE,
                        (x + 1) * CELL_SIZE, y * CELL_SIZE
                    )
                    vec_edges.append(edge)
                    current_cell.edge_id[NORTH] = len(vec_edges) - 1
                    current_cell.edge_exist[NORTH] = True

            # SOUTH EDGE
            if not south_cell.exist:
                if west_cell.edge_exist[SOUTH]:
                    # Extend western neighbor's south edge
                    edge = vec_edges[west_cell.edge_id[SOUTH]]
                    edge.ex += CELL_SIZE
                    current_cell.edge_id[SOUTH] = west_cell.edge_id[SOUTH]
                    current_cell.edge_exist[SOUTH] = True
                else:
                    # Create new south edge
                    edge = Edge(
                        x * CELL_SIZE, (y + 1) * CELL_SIZE,
                        (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
                    )
                    vec_edges.append(edge)
                    current_cell.edge_id[SOUTH] = len(vec_edges) - 1
                    current_cell.edge_exist[SOUTH] = True

# Process entire grid
convert_tilemap_to_polymap(0, 0, max_x, max_y)

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Draw edges
def draw_edges():
    for edge in vec_edges:
        pygame.draw.line(
            screen, (255, 255, 255),
            (edge.sx, edge.sy), (edge.ex, edge.ey), 2
        )
        pygame.draw.circle(screen, (255, 0, 0), (edge.sx, edge.sy), 3)
        pygame.draw.circle(screen, (0, 255, 0), (edge.ex, edge.ey), 3)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    draw_edges()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()