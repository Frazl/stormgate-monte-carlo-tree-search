import heapq
import game
import copy

class Node:
    def __init__(self, action, state, g_score=float('inf'), h_score=float('inf'), parent=None):
        self.action = action
        self.state = game.simulate_action(copy.deepcopy(state), action)
        self.g_score = g_score  # Cost from start node to this node
        self.h_score = h_score  # Heuristic estimate of cost from this node to goal node
        self.parent = parent  # Parent node

    def f_score(self):
        return self.g_score + self.h_score  # Total estimated cost of the cheapest path from start to goal
    
    def __lt__(self, other):
        return self.f_score() < other.f_score()

def astar(start_node, goal_function, distance_function):
    open_set = []  # Priority queue of nodes to be evaluated
    start_node.g_score = 0
    heapq.heappush(open_set, (start_node.f_score(), start_node))

    while open_set:
        _, current_node = heapq.heappop(open_set)

        if goal_function(current_node):
            # Reconstruct path
            path = []
            while current_node is not None:
                path.append(current_node.action)
                current_node = current_node.parent
            return path[::-1]  # Reverse the path to get it from start to goal

        # Generate neighboring nodes
        # For each possible action from the current node
        for neighbor_action in get_neighbors(current_node):
            neighbor_node = Node(action=neighbor_action, state=current_node.state, parent=current_node)

            # Compute tentative g_score for the neighbor
            neighbour_distance = distance_function(neighbor_node)
            tentative_g_score = current_node.g_score + neighbour_distance
            
            # If this path to the neighbor is better than any previous one, update the neighbor
            if tentative_g_score < neighbor_node.g_score:
                neighbor_node.g_score = tentative_g_score
                neighbor_node.h_score = distance_function(neighbor_node)
                neighbor_node.parent = current_node

                # Add neighbor to open set if not already present
                if neighbor_node not in [node[1] for node in open_set]:
                    heapq.heappush(open_set, (neighbor_node.f_score(), neighbor_node))

    # If open set is empty but goal was not reached, return failure\
    print("Failure")
    return start_node

# Example function to get neighboring actions
def get_neighbors(node):
    if node.state['Time'] > 60:
        return []
    actions = game.get_possible_actions(node.state)
    actions = list(filter(lambda x: game.get_action_id(x) == 'BuildUnit-Imp' or game.get_action_id(x) == 'BuildBuilding-Meat Farm' or game.get_action_id(x) == 'Idle--' or game.get_action_id(x) == 'BuildBuilding-Spire', actions))
    return actions

def distance_function(node):
    return (1 - (node.state['Units'].count("Imp") + len(node.state['Buildings'])) / 13)

def goal_function(node):
    return node.state['Units'].count("Imp") >= 13 and sum([1 for building in node.state['Buildings'] if building['Name'] == 'Meat Farm']) == 1 and sum([1 for building in node.state['Buildings'] if building['Name'] == 'Spire']) == 2

# Example usage
state = game.get_default_state()
actions = game.get_possible_actions(state)
[print(game.get_action_id(action)) for action in actions]
print("-" * 80)
start_node = Node(action=actions[3], state=state) # Start by building an imp

pathOrNode = astar(start_node, goal_function, distance_function)
if type(pathOrNode) == Node:
    print(pathOrNode)
else:
    # Path
    for path in pathOrNode:
        print(path['Payload']['Name'])