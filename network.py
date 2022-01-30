from numpy import infty


class Network:
    """Define a network of roads."""

    def __init__(self):
        """Initiate the network as a list of roads."""
        self.roads = []
        self.adj = []
        self.in_roads = []
        self.out_roads = []
        self.paths = []

    def add_roads(self, roads):
        """Adds roads to the network."""
        for road in roads:
            self.roads.append(road)

    def calibrate(self):
        """Calibrate the network by finding the connections and paths."""
        self.make_connections()
        self.incoming()
        self.outgoing()
        self.find_paths()

    def make_connections(self):
        """
        Find the connections between the roads and store them in an
        adjacency matrix.
        """
        # Find the children and parents of every road.
        for road in self.roads:
            for road_2 in self.roads:
                if road.end == road_2.start:
                    road.children.append(road_2)
                    road_2.parents.append(road)

        # Make the adjacency matrix and fill it.
        self.adj = [[0 for _ in range(0,len(self.roads))] for _ in range(0,len(self.roads))]
        for road in self.roads:
            for child in road.children:
                self.adj[self.roads.index(road)][self.roads.index(child)] = 1


    def incoming(self):
        """
        Check which roads have no parent, and are thus places where a car can
        spawn.
        """
        # Check if a column of the adj matrix is all zeros.
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
        # Ceck if a row of the adj matrix is all zeros.
        for i in range(len(self.adj)):
            if self.adj[i] == [0] * len(self.adj):
                self.out_roads.append(self.roads[i])

    def find_paths(self):
        """
        Find the shortest paths from any incoming road to any outgoing road.
        Do this with a Dijkstra's algorithm. See the wikipedia pseudocode
        for more comments.
        """
        # Loop over every start and end to get every possible path between them.
        for start in self.in_roads:
            for end in self.out_roads:

                # Set the distance to every road to infinity, except for start.
                dist = [infty] * len(self.roads)
                dist[self.roads.index(start)] = 0

                # Set array for the previous road in the shortest path.
                prev = [None] * len(self.roads)

                # Roads to check.
                Q = [road for road in self.roads]

                while len(Q) > 0:
                    # Set u as the road with the shortest distance that is
                    # not checked yet.
                    Q_dist = [dist[self.roads.index(x)] for x in Q]
                    u = Q[Q_dist.index(min(Q_dist))]
                    Q.remove(u)

                    # Stop if the end is reached.
                    if u == end:
                        break

                    for child in u.children:
                        # Only check the children which weren't checked before.
                        if child in Q:
                            u_index = self.roads.index(u)
                            c_index = self.roads.index(child)

                            # Change the distance and previous if the distance
                            # from u is smaller then from previous.
                            alt = dist[u_index] + u.length
                            if alt < dist[c_index]:
                                dist[c_index] = alt
                                prev[c_index] = u

                # Work backwards from the end to find the path.
                S = []
                u = end
                # Only do this if the end was reachable.
                if prev[self.roads.index(u)] or u == start:
                    while u:
                        S.insert(0, u)
                        u = prev[self.roads.index(u)]

                self.paths.append(S)

        # Sort the paths by length to make differentiating easier.
        self.paths.sort(key=len)
