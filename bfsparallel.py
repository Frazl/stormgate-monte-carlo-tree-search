import game
import copy
from multiprocessing import Pool, freeze_support, Manager, Lock
import datetime

class Node:
    def __init__(self, action, state, parent=None):
        self.action = action
        self.state = game.simulate_action(copy.deepcopy(state), action)
        self.parent = parent
    
    def __len__(self):
        i = 1 
        nxt = self.parent
        while nxt:
            i+= 1
            nxt = nxt.parent
        return i

def sort_node_by_time(a):
    return a.state['Time']

MAX_DEPTH = 18
def bfs_parallel(start_node, goal_function):
    frontier = [start_node]
    depth_counter = 0 
    goals = []
    
    while frontier and depth_counter <= MAX_DEPTH:
        next_frontier = []
        start = datetime.datetime.now()
        print("depth", depth_counter, "nodes", len(frontier))
        with Pool(192) as pool:
            results = pool.starmap(expand_node, [(node, goal_function) for node in frontier])
            for result in results:
                if isinstance(result, Node):
                    goals.append(result)
                else:
                    next_frontier.extend(result)
        next_frontier.sort(key=sort_node_by_time)
        frontier = next_frontier
        depth_counter += 1
        print(datetime.datetime.now() - start)
        start = datetime.datetime.now()

    goals.sort(key=sort_node_by_time)  # Return None only after checking all possible paths
    if len(goals):
        return goals[0]
    return None

def expand_node(node, goal_function):
    if goal_function(node):
        return node
    
    neighbors = []
    neighbour_actions = get_neighbors(node)
    for neighbor_action in neighbour_actions:
        neighbor_node = Node(action=neighbor_action, state=node.state, parent=node)
        neighbors.append(neighbor_node)
        
    future_neighbours = get_possible_future_actions(node, neighbour_actions, 120)

    return neighbors + future_neighbours

def get_neighbors(node):
    if node.state['Time'] > 5*60:
        return []
    actions = game.get_possible_actions(node.state)
    valid_actions = filter_valid_actions(actions)
    return valid_actions

def get_possible_future_actions(node, currActions, timeDepth):
    state = copy.deepcopy(node.state)
    actionIds = set(map(game.get_action_id, currActions))
    futureNeighbours = []
    for _ in range(timeDepth):
        # Perform no action and just continue time idling
        state['Time'] += 1
        state = game.handle_production(state)
        actions = filter_valid_actions(game.get_possible_actions(state))
        for action in actions:
            actionIdUnderTest = game.get_action_id(action)
            if actionIdUnderTest not in actionIds:
                actionIds.add(actionIdUnderTest)
                futureNeighbours.append(Node(action, state, node))
    return futureNeighbours
        
        
    

def filter_valid_actions(actions):
    valid_ids = ['BuildUnit-Imp', 'BuildBuilding-Meat Farm', 'BuildBuilding-Shrine']
    return [action for action in actions if game.get_action_id(action) in valid_ids]

def goal_12_imp(node):
    return node.state['Units'].count("Imp") >= 12

def goal_16_imp(node):
    return node.state['Units'].count("Imp") >= 15

def goal_20_imp(node):
    return node.state['Units'].count("Imp") >= 20

def goal_20_imp_2_brutes(node):
    return node.state['Units'].count("Imp") >= 19 and node.state['Units'].count("Brute") >= 1

def goal_24_imp(node):
    return node.state['Units'].count("Imp") >= 24



def order_solution(path):
    path_taken = []
    if path:
        path_taken.append(f"{game.get_pretty_time(path.state)} @ {game.get_action_id(path.action)}")
        while path.parent:
            path_taken.append(f"{game.get_pretty_time(path.parent.state)} @ {game.get_action_id(path.parent.action)}")
            path = path.parent
    else:
        print("No solution found.")
    return path_taken[::-1]

if __name__ == '__main__':
    freeze_support()  # Required for Windows or frozen environments

    # Example usage
    state = game.get_default_state()
    actions = game.get_possible_actions(state)
    [print(game.get_action_id(action)) for action in actions]
    goals = [goal_24_imp]
    full_path = []
    path = Node(action={"Action": "DoNothing", "Payload": {"Name": "StarterNode"}}, state=state)
    for goal in goals:
        start_node = Node(action={"Action": "DoNothing", "Payload": {"Name": "StarterNode"}}, state=path.state) # Start by building an imp
        path = bfs_parallel(start_node, goal)
        print("Hit Goal")
        full_path = full_path + order_solution(path)
    
    for action in full_path:
        print(action)
    
    for item, value in path.state.items():
        print(item, value)
        print("-" * 20)
    
    # imp 10
    # imp 11
    # imp 12
    # imp 13
    # meat 12
    # imp 13
    # shrine 12
    # imp 13
    # imp 14
    # imp 15
    # meat 14
    # imp 15
    # imp 16