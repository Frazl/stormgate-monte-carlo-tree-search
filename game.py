import building 
import unit 
import random
from collections import defaultdict

def get_default_state():
    default_unlocked = {
        "Shrine": True,
        "Imp": True,
        "Iron Vault": True,
        "Conclave": True,
        "Meat Farm": True,
    }
    state = {
        "Time": 0,
        "Units": ["Imp"] * 9,
        "Buildings": [{"Name": "Shrine", "Workers": 9, "TheriumWorkers": 0, "UnitSupply": 1, "NextUnitProgress": 0}],
        "Queue": [],
        "SupplyCapacity": 15,
        "Luminite": 100,
        "Therium": 0,
        "Unlocked": defaultdict(lambda: False, default_unlocked)
    }
    return state
    

def main():
    state = get_default_state()
    steps = 60
    for _ in range(steps):
        state = tick(state)
    return state

def get_action_id(action):
    return action['Action'] + '-' + action['Payload']['Name']

def get_possible_actions(state):
    builds = get_possible_buildings(state)        
    units = get_possible_units(state)
    nothing = [{"Action": "Idle", "Payload": {"Name": "-"}}]
    return builds + units + nothing

def get_possible_buildings(state):
    all_buildings = building.get_buildings()
    possible_buildings = []
    for b in all_buildings:
        if state['Unlocked'][b['Name']]:
            if resources_exist(state, b):
                possible_buildings.append({
                    "Action": 'BuildBuilding',
                    "Payload": b
                })
    return possible_buildings

def get_possible_units(state):
    all_units = unit.get_units()
    possible_units = []
    
    for u in all_units:
        if state['Unlocked'][u['Name']]:
            # Add check to see if we have unit supply 
            source_buildings = [b for b in state['Buildings'] if b['Name'] == u['Requires']]
            if (sum([1 for b in source_buildings if b['UnitSupply']])):
                if resources_exist(state, u) and supply_exists(state, u):
                    possible_units.append({
                        "Action": 'BuildUnit',
                        "Payload": u
                    })
    return possible_units

def perform_action(state, choice):
    if choice['Action'] == 'DoNothing':
        return state
    elif choice['Action'] == 'BuildBuilding':
        shrinesWithWorkers = [b for b in state['Buildings'] if (b['Name'] == 'Shrine' or b['Name'] == 'Greater Shrine') and b['Workers'] > 0]
        random.choice(shrinesWithWorkers)['Workers'] -= 1
        toBuild = choice['Payload']
        state['Queue'].append({"Type": choice['Action'], "Name": toBuild['Name'], 'timeRequired': toBuild['Walk Time'] + toBuild['Build Time'], "Progress": 0})
        state['Luminite'] -= toBuild['Luminite']
        state['Therium'] -= toBuild['Therium']
        pass
    elif choice['Action'] == 'BuildUnit':
        u = choice['Payload']
        if u['Name'] == 'Imp':
            # increment workers in a random shrine
            shrinesWithNonMaxWorkers = [b for b in state['Buildings'] if (b['Name'] == 'Shrine' or b['Name'] == 'Greater Shrine') and b['Workers'] < 12]
            if len(shrinesWithNonMaxWorkers):
                shrine = random.choice(shrinesWithNonMaxWorkers)
                shrine['Workers'] += 1
                shrine['UnitSupply'] -= 1
        if u['Name'] == 'ImpT':
            # increment workers in a random shrine
            shrinesWithNonMaxWorkers = [b for b in state['Buildings'] if (b['Name'] == 'Shrine' or b['Name'] == 'Greater Shrine') and b['Workers'] < 12 and b['UnitSupply'] > 0]
            if len(shrinesWithNonMaxWorkers):
                shrine = random.choice(shrinesWithNonMaxWorkers)
                shrine['TheriumWorkers'] += 1
                shrine['UnitSupply'] -= 1
                
        state['Units'].append(u['Name'])
        state['Luminite'] -= u['Luminite']
        state['Therium'] -= u['Therium']
    elif choice['Action'] == 'PerformCamp':
        pass
    return state

def isShrineMax(b):
    return (b['Name'] == 'Shrine' or b['Name'] == 'Greater Shrine') and b['NextUnitProgress'] >= 15

def handle_production(state):
    # Handle Resources
    shrines = [b for b in state['Buildings'] if b['Name'] == 'Shrine' or b['Name'] == 'Greater Shrine']
    for shrine in shrines:
        state['Luminite'] += shrine['Workers']
        state['Therium'] += shrine['TheriumWorkers'] * 0.8
    # Handle Construction of Buildings 
    for construction in state['Queue']:
        construction['Progress'] += 1
        if construction['Progress'] == construction['timeRequired']:
            state = buildings_builder(state, construction['Name'])
    state['Queue'] = [item for item in state['Queue'] if item['timeRequired'] != item['Progress']]
    # Handle UnitProgress in buildings 
    factories = [b for b in state['Buildings'] if b.get('NextUnitProgress', None) != None]
    for factory in factories:
        if factory['UnitSupply'] < 3:
            factory['NextUnitProgress'] += 1
            if factory['NextUnitProgress'] == 35 or isShrineMax(factory):
                factory['UnitSupply'] += 1
                factory['NextUnitProgress'] = 0
    # Handle Meat Farm felhogs and supply 
    felhoggeries = [b for b in state['Buildings'] if b['Name'] == 'Meat Farm']
    for meatFarm in felhoggeries:
        if meatFarm['Felhogs'] < 3:
            meatFarm['FelhogsProgress'] += 1
            if meatFarm['FelhogsProgress'] == 20:
                meatFarm['FelhogsProgress'] = 0
                meatFarm['Felhogs'] += 1
                state['SupplyCapacity'] += 2
    return state
        
def buildings_builder(state, buildingName):
    if buildingName == 'Shrine' or buildingName == 'Greater Shrine':
        # Handle Shrine
        state['Buildings'].append({"Name": buildingName, "Workers": 0, "TheriumWorkers": 0, "UnitSupply": 1, "NextUnitProgress": 0})
    elif buildingName == 'Meat Farm':
        # handle special meat farm
        state['Buildings'].append({"Name": buildingName, "Felhogs": 0, "FelhogsProgress": 0})
        state['SupplyCapacity'] += 10
    else:
        state['Buildings'].append({"Name": buildingName, "UnitSupply": 1, "NextUnitProgress": 0})
        # handle unit production building
        
    return state

def _print_actions(time, actions):
    for action in actions:
        print(time, action['Action'], action['Payload']['Name'])

def tick(state):
    possible_actions = get_possible_actions(state)
    choice = random.choice(possible_actions)
    _print_actions(state['Time'], possible_actions)
    _print_actions(state['Time'], [choice])
    state = perform_action(state, choice)
    state['Time'] += 1
    state = handle_production(state) # Handles building buildings in progress, updating currency collected by workers etc.
    return state

def simulate_action(state, action):
    state = perform_action(state, action)
    state['Time'] += 1
    state = handle_production(state) # Handles building buildings in progress, updating currency collected by workers etc.
    return state
    

# Helpers 

def resources_exist(state, buildingOrUnit):
    return state['Luminite'] >= buildingOrUnit['Luminite'] and state['Therium'] >= buildingOrUnit['Therium']

def supply_exists(state, unit):
    # Check if a unit would exceed supply
    return state['SupplyCapacity'] >= unit['Supply'] + get_supply_used(state)

def get_supply_used(state): 
    units = unit.get_units_map()
    supply = 0
    for u in state['Units']:
        supply += units[u]['Supply']
    return supply

if __name__ == '__main__':
    final_state = main()
    import json 
    print(json.dumps(final_state))