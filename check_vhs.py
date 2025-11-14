import json

# 读取工作流
with open(r'E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\user\default\workflows\Infinite Talk test(1).json', encoding='utf-8') as f:
    data = json.load(f)

# 找到 VHS_VideoCombine 节点
vhs_node = [n for n in data['nodes'] if n['type'] == 'VHS_VideoCombine'][0]

print("=" * 60)
print("VHS_VideoCombine 节点详情")
print("=" * 60)

print("\n输入连接:")
for inp in vhs_node['inputs']:
    name = inp['name']
    link = inp.get('link')
    print(f"  {name}: link={link}")

print("\n参数值:")
print(json.dumps(vhs_node['widgets_values'], indent=2, ensure_ascii=False))

# 找到音频输入的来源
print("\n=" * 60)
print("追踪音频输入")
print("=" * 60)

# 找到连接到 audio 输入的 link
audio_input = [i for i in vhs_node['inputs'] if i['name'] == 'audio'][0]
audio_link_id = audio_input.get('link')

if audio_link_id:
    # 找到这个 link 的来源
    for link in data['links']:
        if link[0] == audio_link_id:
            source_node_id = link[1]
            source_output_idx = link[2]
            
            # 找到源节点
            source_node = [n for n in data['nodes'] if n['id'] == source_node_id][0]
            print(f"\n音频来源节点:")
            print(f"  ID: {source_node['id']}")
            print(f"  类型: {source_node['type']}")
            print(f"  输出索引: {source_output_idx}")
            
            if source_node['type'] == 'MultiTalkWav2VecEmbeds':
                print(f"\n  ✅ 音频来自 MultiTalkWav2VecEmbeds 节点!")
                print(f"  这个节点的输出:")
                for i, out in enumerate(source_node['outputs']):
                    print(f"    [{i}] {out['name']}: {out['type']}")
            break
else:
    print("\n⚠️ 没有连接音频输入")
