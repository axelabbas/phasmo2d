

# Constants
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

class Shadow:
    def __init__(self):
        self.edges = []
        self.world: dict[tuple, Cell] = {}  # Store world as a dictionary (x, y) -> Cell
    def create_world(self, width, height):
        return [[Cell() for _ in range(width)] for _ in range(height)]

    def loadMap(self, level_data):
        max_x = max(int(cell.split(';')[0]) for cell in level_data) + 2
        max_y = max(int(cell.split(';')[1]) for cell in level_data) + 2
        self.world = self.create_world(max_x, max_y)

        for cell in level_data:
            x, y = map(int, cell.split(';'))
            self.world[y][x].exist = True
        return (max_x, max_y)
    def convert_tilemap_to_polymap(self, sx, sy, w, h, CELL_SIZE):
        self.edges.clear()
        # Iterate through region (offset by 1 to avoid boundary checks)
        for x in range(sx, sx + w):
            for y in range(sy, sy + h):
                if y >= len(self.world) or x >= len(self.world[0]):
                    continue
                current_cell = self.world[y][x]
                if not current_cell.exist:
                    continue

                # Check neighbors
                west_cell = self.world[y][x - 1] if x > 0 else None
                east_cell = self.world[y][x + 1] if x < len(self.world[0]) - 1 else None
                north_cell =self.world[y - 1][x] if y > 0 else None
                south_cell =self.world[y + 1][x] if y < len(self.world) - 1 else None

                # WEST EDGE
                if west_cell is None or not west_cell.exist:
                    if north_cell and north_cell.edge_exist[WEST]:
                        # Extend northern neighbor's west edge
                        edge = self.edges[north_cell.edge_id[WEST]]
                        edge.ey += CELL_SIZE
                        current_cell.edge_id[WEST] = north_cell.edge_id[WEST]
                        current_cell.edge_exist[WEST] = True
                    else:
                        # Create new west edge
                        edge = Edge(
                            x * CELL_SIZE, y * CELL_SIZE,
                            x * CELL_SIZE, (y + 1) * CELL_SIZE
                        )
                        self.edges.append(edge)
                        current_cell.edge_id[WEST] = len(self.edges) - 1
                        current_cell.edge_exist[WEST] = True

                # EAST EDGE
                if east_cell is None or not east_cell.exist:
                    if north_cell and north_cell.edge_exist[EAST]:
                        # Extend northern neighbor's east edge
                        edge = self.edges[north_cell.edge_id[EAST]]
                        edge.ey += CELL_SIZE
                        current_cell.edge_id[EAST] = north_cell.edge_id[EAST]
                        current_cell.edge_exist[EAST] = True
                    else:
                        # Create new east edge
                        edge = Edge(
                            (x + 1) * CELL_SIZE, y * CELL_SIZE,
                            (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
                        )
                        self.edges.append(edge)
                        current_cell.edge_id[EAST] = len(self.edges) - 1
                        current_cell.edge_exist[EAST] = True

                # NORTH EDGE
                if north_cell is None or not north_cell.exist:
                    if west_cell and west_cell.edge_exist[NORTH]:
                        # Extend western neighbor's north edge
                        edge = self.edges[west_cell.edge_id[NORTH]]
                        edge.ex += CELL_SIZE
                        current_cell.edge_id[NORTH] = west_cell.edge_id[NORTH]
                        current_cell.edge_exist[NORTH] = True
                    else:
                        # Create new north edge
                        edge = Edge(
                            x * CELL_SIZE, y * CELL_SIZE,
                            (x + 1) * CELL_SIZE, y * CELL_SIZE
                        )
                        self.edges.append(edge)
                        current_cell.edge_id[NORTH] = len(self.edges) - 1
                        current_cell.edge_exist[NORTH] = True

                # SOUTH EDGE
                if south_cell is None or not south_cell.exist:
                    if west_cell and west_cell.edge_exist[SOUTH]:
                        # Extend western neighbor's south edge
                        edge = self.edges[west_cell.edge_id[SOUTH]]
                        edge.ex += CELL_SIZE
                        current_cell.edge_id[SOUTH] = west_cell.edge_id[SOUTH]
                        current_cell.edge_exist[SOUTH] = True
                    else:
                        # Create new south edge
                        edge = Edge(
                            x * CELL_SIZE, (y + 1) * CELL_SIZE,
                            (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE
                        )
                        self.edges.append(edge)
                        current_cell.edge_id[SOUTH] = len(self.edges) - 1
                        current_cell.edge_exist[SOUTH] = True
