from tortoise import fields, models
import uuid
import bcrypt

class User(models.Model):
    user_id = fields.UUIDField(pk=True,default=uuid.uuid4)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100,unique=True)
    password_hash=fields.CharField(max_length=128),
    createdAt=fields.DatetimeField(auto_now_add=True)
    updatedAt = fields.DatetimeField(auto_now=True)

class Meta:
    table=User

  # Automatically hash before saving
    async def save(self, *args, **kwargs):
        # Only hash if it's not already hashed
        if not self.password_hash.startswith("$2b$"):
            self.password_hash = bcrypt.hash(self.password_hash)
        await super().save(*args, **kwargs)

    # Verify password
    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)


#async def run():
#    await Tortoise.init(
#        db_url="postgres://username:password@localhost:5432/mydatabase",
#        modules={"models": ["__main__"]}
#    )
#    await Tortoise.generate_schemas()
#    await User.create(name="Chima", email="chima@example.com")
#    user = await User.get(name="Chima")
#    print(user.email)
#    await Tortoise.close_connections()
#
#run_async(run())
