TORTOISE_ORM = {
    "connections": {
        "default": "postgres://postgres:password@localhost:5432/moodsync"
    },
    "apps": {
        "models": {
            "models": ["app.models.users", "aerich.models"],  # Add your models here
            "default_connection": "default",
        }
    }
}
