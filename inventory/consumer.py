import time
from redis_om.model import NotFoundError
from main import redis, Product, format

key = "order_completed"
group = "inventory-group"

try:
    redis.xgroup_create(key, group)
except:
    print("Group already exists")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, None)
        if results != []:
            for result in results:
                obj = result[1][0][1]
                print(obj["product_id"])
                product = Product.get(obj["product_id"])
                print("Product: ")
                product.quantity = product.quantity - int(obj["quantity"])
                product.save()
    except NotFoundError:
        print("Product not found")
    except Exception as e:
        print(str(e))
    time.sleep(1)
