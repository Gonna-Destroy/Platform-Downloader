progresses = {}

def get_element(element):
    return progresses.get(element)

def update_element(data, element):
    progresses[element] = data

def get_all():
    data = ''
    for (key, value) in progresses.items():
        data += f'{key}: {value}'
    return data

def delete_all():
    progresses.clear()

def delete_item(title):
    progresses.pop(title)