from tortoise import Tortoise, run_async
from models.users import User
from tortoise_config import TORTOISE_ORM

async def init():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()  # Creates tables if they don't exist yet
    print("✅ Database connected and schemas created!")

    # Example: create a user
    #user = await User.create(first_name="David",last_name="Umunna", email="chimarokeumunna98@gmail.com",password_hash="12345678")
    #print("User created:", user.first_name)
#
    ## Example: fetch users
    #users = await User.all()
    #for u in users:
    #    print(u.first_name, u.email)
#
    #await Tortoise.close_connections()

run_async(init())
