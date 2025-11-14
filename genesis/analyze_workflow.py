import json

# Load workflow
workflow_path = r"E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\user\default\workflows\Infinite Talk test(1).json"
with open(workflow_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find relevant nodes
print("=== InfiniteTalk Workflow Analysis ===\n")

# Find all node types
node_types = {}
for node in data['nodes']:
    node_type = node.get('type', '')
    if node_type not in node_types:
        node_types[node_type] = []
    node_types[node_type].append(node['id'])

# Print InfiniteTalk related nodes
keywords = ['multitalk', 'wav2vec', 'sampler', 'infinitetalk', 'model', 'vae', 'encode', 'decode']
print("=== Relevant Nodes ===")
for node_type, ids in sorted(node_types.items()):
    if any(kw in node_type.lower() for kw in keywords):
        print(f"{node_type}: {ids}")

print("\n=== Detailed Node Info ===\n")
for node in data['nodes']:
    node_type = node.get('type', '')
    if any(keyword in node_type.lower() for keyword in ['multitalk', 'wav2vec', 'sampler']):
        print(f"ID {node['id']}: {node_type}")
        if 'widgets_values' in node:
            print(f"  Widgets: {node['widgets_values']}")
        if 'inputs' in node:
            print(f"  Inputs: {[inp.get('name', inp.get('label', '?')) for inp in node['inputs']]}")
        print()

# Find connections
print("\n=== Node Connections ===")
links = {link[0]: link for link in data.get('links', [])}
for node in data['nodes']:
    node_type = node.get('type', '')
    if 'WanVideoSampler' in node_type or 'MultiTalk' in node_type:
        print(f"\n{node_type} (ID {node['id']}):")
        if 'inputs' in node:
            for inp in node['inputs']:
                if inp.get('link'):
                    link = links.get(inp['link'])
                    if link:
                        print(f"  <- {inp.get('name')}: from node {link[1]}")
        if 'outputs' in node:
            for out in node['outputs']:
                if out.get('links'):
                    for link_id in out['links']:
                        link = links.get(link_id)
                        if link:
                            print(f"  -> {out.get('name')}: to node {link[3]}")

print("\n\n=== WanVideo Related Nodes ===")
for n in data['nodes']:
    if 'WanVideo' in n['type']:
        print(f"\nNode ID: {n['id']}")
        print(f"Type: {n['type']}")
        if 'widgets_values' in n:
            print(f"Widgets: {n['widgets_values'][:5] if len(n['widgets_values']) > 5 else n['widgets_values']}")
