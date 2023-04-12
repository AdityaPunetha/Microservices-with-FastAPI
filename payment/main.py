from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
from dotenv import load_dotenv
import requests, time, os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


redis = get_redis_connection(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True,
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis


@app.get("/orders/{pk}")
async def get_order(pk: str):
    return Order.get(pk)


@app.post("/orders")
async def create_order(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    product = requests.get("http://localhost:8000/products/%s" % body["id"]).json()

    order = Order(
        product_id=product["id"],
        price=product["price"],
        fee=product["price"] * 0.2,
        total=product["price"] * 1.2,
        quantity=body["quantity"],
        status="pending",
    )
    order.save()

    background_tasks.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()
    redis.xadd("order_completed", order.dict(), "*")
