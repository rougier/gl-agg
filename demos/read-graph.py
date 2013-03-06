nodes = {}
def get_id(node):
    name = node['name']
    if name not in nodes.keys():
        nodes[name] = len(nodes)
    return nodes[name]
def connect(parent, links):
    parent_id  = get_id(parent)
    if 'children' in parent.keys():
        for child in parent['children']:
            child_id = get_id(child)
            links.append( (parent_id,child_id) )
            links.extend( connect(child, []) )
    return links

root = eval(open('graph.json').read())
print connect(root, [])
