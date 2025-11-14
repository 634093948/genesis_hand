#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 I2V 生成按钮
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("测试 I2V 生成按钮")
print("=" * 80)

# 检查关键变量是否定义
print("\n1. 检查导入...")
try:
    from genesis.apps import wanvideo_gradio_app
    print("✅ 成功导入 wanvideo_gradio_app")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

print("\n2. 启动应用...")
print("请在浏览器中:")
print("  1. 选择 InfiniteTalk 模式")
print("  2. 上传一张图片")
print("  3. 点击 '🧪 Test Click' 按钮测试")
print("  4. 如果测试按钮有反应，再点击 '🎬 Generate Video'")
print("  5. 观察浏览器控制台是否有错误")
print("\n" + "=" * 80)
print("按 Ctrl+C 停止应用")
print("=" * 80 + "\n")

# 启动应用
try:
    wanvideo_gradio_app.main()
except KeyboardInterrupt:
    print("\n\n应用已停止")
except Exception as e:
    print(f"\n❌ 应用启动失败: {e}")
    import traceback
    traceback.print_exc()
