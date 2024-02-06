def get_buildings():
    with open('buildings.csv', 'r') as f:
        lines = f.readlines()
        keys = lines[0].strip().split("\t")
        data = lines[1:]
        buildings = []
        for i in range(len(data)):
            d = {}
            row = data[i].strip().split("\t")
            for j in range(len(row)):
                try:
                    d[keys[j]] = float(row[j])
                except:
                    d[keys[j]] = row[j]
            buildings.append(d)
        return buildings

def get_buildings_map():
    b = get_buildings()
    d = {}
    for building in b:
        d[building['Name']] = building
    return d
        

def get_example():
    return {'Name': 'Shrine', 'Luminite': '200', 'Therium': '0', 'Build Time': '80', 'Walk Time': '15', 'Unit Supply Time': '15', 'Supply': '0', 'Unlocks': 'Imp,Meat Farm,Iron Vault,Conclave'}
