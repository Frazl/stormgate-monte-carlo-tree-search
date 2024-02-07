import copy
import math
import random
import game


TERMINATE_TIME = 1500

TARGET_LUMINITE = 2000

def is_winner(state):
    # Determine if we have found a path to obtain 2000 luminite
    return state['Luminite'] > TARGET_LUMINITE
    
def is_terminal(state):
    # Determine if we have exceeded the time requirement
    return state['Time'] >= TERMINATE_TIME

def state_heuristic(state, node):
    mod_state = copy.deepcopy(state)
    return ( game.simulate_action(mod_state, node.action)['Luminite'] / TARGET_LUMINITE ) * 10

# game.get_default_state() will get the initial state of a game 
# copy.deepcopy(root_state) could be used to do a deep copy when we wish to mutate the state
# game.get_possible_actions(state) will get possible actions based on the current state 
# game.simulate_action(state, action) will simulate an action on the state and return a new state

class Node:
    def __init__(self, action=None, parent=None):
        self.action = action
        self.parent = parent
        self.children = []
        self.visits = 1   
        self.wins = 0

def mcts(root_state, num_iterations):
    root_node = Node()
    for _ in range(num_iterations):
        node = root_node
        state = copy.deepcopy(root_state)  # Clone the initial game state
        # Selection phase
        while not is_terminal(state) and node.children:
            node = select_child(node, state)
            game.simulate_action(state, node.action)

        # Expansion phase
        if not is_terminal(state) and not node.children:
            possible_actions = game.get_possible_actions(state)
            for action in possible_actions:
                if game.get_action_id(action) not in [game.get_action_id(child.action) for child in node.children]:
                    expand_node(node, action)
        # Simulation phase
        winner = simulate(state)
        # Backpropagation phase
        backpropagate(node, winner)
    # Choose best action based on visit counts
    return root_node

# Expansion phase: Add a new child node
def expand_node(parent, action):
    child = Node(action, parent)
    parent.children.append(child)
    return child

# Simulation phase: Simulate a game from the current state and return the winner
def simulate(state):
    # In this simplified example, we'll randomly choose a winner after a fixed number of steps
    max_steps = 10
    for _ in range(max_steps):
        if is_terminal(state):
            return is_winner(state)
        action = random.choice(game.get_possible_actions(state))
        state = game.simulate_action(state, action)
    return is_winner(state)

# Backpropagation phase: Update visit counts and wins for all nodes along the path to the root
def backpropagate(node, winner):
    while node is not None:
        node.visits += 1
        if winner is not False:  
            node.wins += 1
        node = node.parent

# Choose the best action based on visit counts
def best_child(root_node):
    best_child = None
    best_visits = -1
    for child in root_node.children:
        if child.visits > best_visits:
            best_child = child
            best_visits = child.visits
    return best_child

def select_child(node, state):
    total_visits = sum(child.visits for child in node.children)
    best_child = None
    best_score = -1
    for child in node.children:
        if child.wins == 0:
            exploration_term = state_heuristic(state, child)
        else:
            exploration_term = math.sqrt(2 * math.log(total_visits) / child.visits)
        ucb_score = child.visits + exploration_term
        if ucb_score > best_score:
            best_child = child
            best_score = ucb_score
    return best_child


if __name__ == '__main__':
    root_node = mcts(game.get_default_state(), 500)
    for child in root_node.children:
        print(game.get_action_id(child.action))
    print('-' * 80)
    print(root_node.wins)
    state = game.get_default_state()
    while root_node:
        root_node = best_child(root_node)
        if root_node:
            action_id = game.get_action_id(root_node.action)
            state = game.simulate_action(state, root_node.action)
            if action_id != "Idle--":
                print(game.get_action_id(root_node.action))
    print(state)