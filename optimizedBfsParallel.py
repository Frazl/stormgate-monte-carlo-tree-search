import game
import copy
from multiprocessing import Pool, freeze_support, Manager, Lock
import datetime


GOALS = {
        "BuildUnit-Imp": 3,
        "BuildUnit-ImpT": 1,
        "BuildUnit-Gaunt": 1,
        "BuildUnit-Brute": 1,
        "BuildBuilding-Conclave": 1,
        "BuildBuilding-Meat Farm": 1,
        "BuildBuilding-Iron Vault": 1,
    }

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

MAX_DEPTH = 10
MAX_GAME_TIME = 5 * 60

def bfs_parallel(start_node, state):
    frontier = [start_node]
    depth_counter = 0 
    goals_reached = []
    
    while frontier and depth_counter <= MAX_DEPTH:
        next_frontier = []
        start = datetime.datetime.now()
        with Pool() as pool:
            results = pool.map(expand_node, frontier)
            for result in results:
                if isinstance(result, Node):
                    goals_reached.append(result)
                else:
                    next_frontier.extend(result)
        next_frontier.sort(key=sort_node_by_time)
        frontier = next_frontier
        depth_counter += 1
        print("depth", depth_counter, "nodes", len(frontier), "Time Taken", datetime.datetime.now() - start)
        start = datetime.datetime.now()

    goals_reached.sort(key=sort_node_by_time)  # Return None only after checking all possible paths
    if len(goals_reached):
        return goals_reached[0]
    return None

def expand_node(node):
    required_actions_to_goal = find_required_actions(node.state)
    print(len(required_actions_to_goal))
    if len(required_actions_to_goal) == 0:
        return node
    
    neighbors = []
    neighbour_actions = get_neighbors(node, required_actions_to_goal)
    for neighbor_action in neighbour_actions:
        neighbor_node = Node(action=neighbor_action, state=node.state, parent=node)
        neighbors.append(neighbor_node)
        
    future_neighbours = get_possible_future_actions(node, neighbour_actions, required_actions_to_goal, 120)

    return neighbors + future_neighbours

def get_neighbors(node, required_actions_to_goal):
    if node.state['Time'] > MAX_GAME_TIME:
        return []
    actions = game.get_possible_actions(node.state)
    return [action for action in actions if game.get_action_id(action) in required_actions_to_goal]

def get_possible_future_actions(node, currActions, required_actions_to_goal, timeDepth):
    state = copy.deepcopy(node.state)
    actionIds = set(map(game.get_action_id, currActions))
    futureNeighbours = []
    for _ in range(timeDepth):
        # Perform no action and just continue time idling
        state['Time'] += 1
        state = game.handle_production(state)
        actions = (game.get_possible_actions(state))
        valid_actions = [action for action in actions if game.get_action_id(action) in required_actions_to_goal]
        for action in valid_actions:
            actionIdUnderTest = game.get_action_id(action)
            if actionIdUnderTest not in actionIds:
                actionIds.add(actionIdUnderTest)
                futureNeighbours.append(Node(action, state, node))
    return futureNeighbours

def find_required_actions(state):
    required_actions = []
    for actionId, actionCount in GOALS.items():
        cmd = actionId.split("-")
        action = cmd[0]
        object = cmd[1]
        if action == 'BuildUnit':
            if check_unit_count(state, object) != actionCount:
                required_actions.append(actionId)
        elif action == 'BuildBuilding':
            if check_building_count(state, object) != actionCount:
                required_actions.append(actionId)
    return required_actions
        
def check_unit_count(state, unitName):
    return state['Units'].count(unitName)

def check_building_count(state, buildingName):
    return sum([1 for building in state['Buildings'] if building['Name'] == buildingName])

# Change how goals work and how possible actions are chosen based on goals already met

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
    full_path = []
    start_node = Node(action={"Action": "DoNothing", "Payload": {"Name": "StarterNode"}}, state=state) # Start by building an imp
    path = bfs_parallel(start_node, state)
    full_path = full_path + order_solution(path)
    
    for action in full_path:
        print(action)
    
    for item, value in path.state.items():
        print(item, value)
        print("-" * 20)