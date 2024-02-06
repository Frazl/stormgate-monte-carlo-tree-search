def get_units():
    with open('./units.csv', 'r') as f:
        lines = f.readlines()
        keys = lines[0].strip().split("\t")
        data = lines[1:]
        units = []
        for i in range(len(data)):
            d = {}
            row = data[i].strip().split("\t")
            for j in range(len(row)):
                try:
                    d[keys[j]] = float(row[j])
                except:
                    d[keys[j]] = row[j]
            units.append(d)
    return units

def get_units_map():
    u = get_units()
    d = {}
    for unit in u:
        d[unit['Name']] = unit
    return d
        
    

def get_example():
    return {'Requires': 'Shrine', 'Unit': 'Imp', 'Health': '80', 'White Health': '20', 'Damage': '8', 'Range': '0.8', 'Attack Speed': '1.5', 'Armor': '0', 'Move Speed': '3.5', 'Supply': '1', 'Luminite': '50', 'Therium': '0', 'DPS': '5.333333333'}