from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

# Custom metadata naming convention for migrations
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy with custom metadata
db = SQLAlchemy(metadata=metadata)


# Restaurant Model
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationships
    restaurant_pizzas = db.relationship(
        "RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan"
    )

    # Serialization Rules
    serialize_rules = ("-restaurant_pizzas",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


# Pizza Model
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationships
    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="pizza")

    # Serialization Rules
    serialize_rules = ("-restaurant_pizzas.pizza",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


# RestaurantPizza (Join Table)
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)

    # Relationships
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    # Serialization Rules
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")

    # Validations
    @validates("price")
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    def __repr__(self):
        return f"<RestaurantPizza price=${self.price}>"