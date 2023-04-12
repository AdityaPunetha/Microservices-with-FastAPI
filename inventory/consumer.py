import time
from main import redis, Product

key = "order_completed"
group = "inventory-group"

try:
    redis.xgroup_create(key, group, mkstream=True)
except:
    print("Group already exists")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, None)
        if results != []:
            for result in results:
                obj = result[1][0][1]
                print("Product: ")
                product = Product.get(obj["product_id"])
                print("Product: ")
                product.quantity = product.quantity - int(obj["quantity"])
                product.save()
    except Exception as e:
        print(str(e))
    time.sleep(1)
