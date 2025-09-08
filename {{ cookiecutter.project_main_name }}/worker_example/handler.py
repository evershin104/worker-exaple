from time import sleep

from faststream.rabbit import RabbitBroker
from faststream import FastStream, ContextRepo, Logger
from worker_example.settings import RabbitBrokerConfig
from worker_example.schema import Payload
from worker_example.middlewares import LoggingMiddleware


broker = RabbitBroker(
    middlewares=[LoggingMiddleware,]
)

app = FastStream(broker)

# faststream run worker_example.handler:app --reload --env .env


@app.on_startup
async def setup(context: ContextRepo, env: str = ".env"):
    """ Load settings from .env """
    settings = RabbitBrokerConfig(_env_file=env)
    context.set_global("settings", settings)
    await broker.connect(settings.rabbitmq_url)


@app.after_startup
async def log_startup(logger: Logger):
    # from uuid import uuid4
    # await broker.publish({"task_id": uuid4(), "triggered_by": uuid4()}, "example_worker_queue")
    logger.info("Worker started")


@broker.subscriber("example_worker_queue", retry=3)
async def handle_example_queue(message: Payload) -> None:
    print(f"Processing task: {message.task_id}")

