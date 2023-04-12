from redis_om import HashModel
from main import redis, Product


print(list(Product.all_pks()))
print(Product.get("01GXQT2S36NZ3R9T6ZMZP4X2WK"))
