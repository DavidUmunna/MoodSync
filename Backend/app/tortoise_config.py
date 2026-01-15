TORTOISE_ORM = {
    "connections": {
        "default": "postgres://moodsyncAdmin:Halden101@localhost:5432/moodsync"
    },
    "apps": {
        "models": {
            "models": ["app.models.users", "aerich.models"],  # Add your models here
            "default_connection": "default",
        }
    }
}
