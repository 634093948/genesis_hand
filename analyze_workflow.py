import json

# Read InfiniteTalk workflow
with open(r'E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\user\default\workflows\Infinite Talk test(1).json', 'r', encoding='utf-8') as f:
    infinite_data = json.load(f)

print("="*60)
print("InfiniteTalk Workflow Analysis")
print("="*60)

# Find important nodes
important_types = ['Multi', 'Infinite', 'Audio', 'Sampler', 'I2V', 'Image', 'Load', 'VAE', 'T5']

print(f"\nTotal nodes: {len(infinite_data['nodes'])}")
print("\nImportant nodes:")

for node in infinite_data['nodes']:
    node_type = node['type']
    if any(k in node_type for k in important_types):
        title = node.get('title', 'N/A')
        print(f"  ID {node['id']}: {node_type} - {title}")
        
        # Print widget values for key nodes
        if 'Multi' in node_type or 'Infinite' in node_type or 'Audio' in node_type or 'Sampler' in node_type:
            if 'widgets_values' in node:
                print(f"    Widgets: {node['widgets_values']}")

print("\n" + "="*60)
print("Animate Workflow Analysis")
print("="*60)

# Read Animate workflow
with open(r'E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\user\default\workflows\Animate上好佳工作流（sec）.json', 'r', encoding='utf-8') as f:
    animate_data = json.load(f)

print(f"\nTotal nodes: {len(animate_data['nodes'])}")
print("\nImportant nodes:")

for node in animate_data['nodes']:
    node_type = node['type']
    if any(k in node_type for k in important_types) or 'Animate' in node_type:
        title = node.get('title', 'N/A')
        print(f"  ID {node['id']}: {node_type} - {title}")
        
        if 'Animate' in node_type or 'Sampler' in node_type:
            if 'widgets_values' in node:
                print(f"    Widgets: {node['widgets_values']}")
