class Network:
    """
    Defines a network of roads.
    """
    def __init__(self):
        """
        Initiates the network as just a list of roads.
        """
        self.roads = []
        self.adj = []
        self.in_roads = []
        self.out_roads = []
        self.paths = []

    def add_roads(self, roads):
        """
        Adds roads to the network.
        """
        for road in roads:
            self.roads.append(road)

        # Make the connections, and find the routes the cars can take.
        self.make_connections()
        self.incoming()
        self.outgoing()
        self.find_paths()

    def make_connections(self):
        """
        Creates connections between the roads and stores them in an
        adjacency matrix.
        """
        # Find the children of every road
        for road in self.roads:
            for road_2 in self.roads:
                if road.end == road_2.start:
                    road.children.append(road_2)

        # Make the adjacency matrix and fill it
        self.adj = [[0 for y in range(0,len(self.roads))] for x in range(0,len(self.roads))]
        for road in self.roads:
            for child in road.children:
                self.adj[self.roads.index(road)][self.roads.index(child)] = 1


    def incoming(self):
        """
        Check which roads have no parent, and are thus places where a car can
        spawn.
        """
        # We check if a column of the adj matrix is all zeros
        for j in range(len(self.adj)):
            incoming = 0
            for i in range(len(self.adj)):
                incoming += self.adj[i][j]

            if incoming == 0:
                self.in_roads.append(self.roads[j])

    def outgoing(self):
        """
        Check which roads have no parent, and are thus places where a car can
        end.
        """
        # We check if a row of the adj matrix is all zeros
        for i in range(len(self.adj)):
            if self.adj[i] == [0] * len(self.adj):
                self.out_roads.append(self.roads[i])

    def find_paths(self):
        """
        Finds the shortest paths from any incoming road to any outgoing road.
        This is done with a BFS. See the wikipedia pseudocode.
        """
        for start in self.in_roads:
            for end in self.out_roads:
                # Because we want the whole path, put the paths in the queue
                # instead of only the last element.
                Q = [[start]]
                explored = [start]
                found = False
                while len(Q) > 0:
                    p = Q.pop(0)

                    if p[-1] == end:
                        self.paths.append(p)
                        found = True

                    # If a shortest path is found, do not add longer paths
                    if found == True:
                        continue

                    for child in p[-1].children:
                        if child not in explored:
                            explored.append(child)
                            # Add the extended path to the queue
                            Q.append(p + [child])