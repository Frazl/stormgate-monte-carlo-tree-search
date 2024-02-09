import game 

queue = [
    'BuildUnit-Imp', #10
    'BuildBuilding-Iron Vault', #9
    'BuildBuilding-Conclave', #8
    'BuildUnit-ImpT', #
    'BuildUnit-Imp', #10
    'BuildUnit-Imp', #11
    'BuildBuilding-Meat Farm', #10
    'BuildUnit-Gaunt', # 24
    'BuildUnit-Brute', # 24
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
    print(state['Units'].count("Imp"), "Imps")