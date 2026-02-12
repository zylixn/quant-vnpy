from vnpy.trader.constant import Interval

# 查看Interval的所有属性
print("Interval的所有属性:")
for attr in dir(Interval):
    if not attr.startswith('_'):
        print(f"- {attr}")

# 尝试获取Interval的所有值
print("\nInterval的所有值:")
try:
    for value in Interval:
        print(f"- {value}")
except Exception as e:
    print(f"获取Interval值失败: {e}")
