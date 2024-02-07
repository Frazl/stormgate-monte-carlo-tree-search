import game 

queue = [
    'BuildBuilding-Shrine',
    'BuildUnit-Imp', #9
    'BuildUnit-Imp', #11
    'BuildUnit-Imp', #12
    'BuildUnit-Imp', #13
    'BuildBuilding-Meat Farm', #12
    'BuildBuilding-Iron Vault', #12
    'BuildUnit-Brute', # 24
    'BuildUnit-Brute', # 24
    'BuildBuilding-Meat Farm', #12
    'BuildUnit-Imp', # 24
    'BuildUnit-Imp', # 24
    'BuildUnit-Imp', # 24
    'BuildUnit-Imp', # 24
    'BuildUnit-Imp', # 24
    'BuildUnit-Imp', # 24
    'BuildUnit-Imp', # 24
]


if __name__ == '__main__':
    state = game.get_default_state()
    for i in range(len(queue)):
        action_id = queue[i]
        while state['Time'] < 1000:
            action = game.get_action_if_possible(state, action_id)
            if action:
                state = game.perform_action(state, action)
                print(game.get_pretty_time(state), action_id)
                state['Time'] += 1
                state = game.handle_production(state)
                break
            state['Time'] += 1
            state = game.handle_production(state)
    for item, value in state.items():
        print(item, value)
        print("-" * 20)