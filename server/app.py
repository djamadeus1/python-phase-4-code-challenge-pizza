#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

# Configure the database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET /restaurants
class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        response = [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
            for restaurant in restaurants
        ]
        return make_response(response, 200)

# GET and DELETE /restaurants/<int:id>
class RestaurantById(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)

        response = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "pizza_id": rp.pizza_id,
                    "price": rp.price
                }
                for rp in restaurant.restaurant_pizzas
            ]
        }
        return make_response(response, 200)

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)

        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)

# GET /pizzas
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        response = [
            {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            }
            for pizza in pizzas
        ]
        return make_response(response, 200)

# POST /restaurant_pizzas
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        # Validate presence of required fields
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        if not all([price, pizza_id, restaurant_id]):
            return make_response({"errors": ["validation errors"]}, 400)

        # Validate price range
        try:
            price = int(price)
            if not (1 <= price <= 30):
                raise ValueError
        except (TypeError, ValueError):
            return make_response({"errors": ["validation errors"]}, 400)

        # Check if pizza and restaurant exist
        pizza = db.session.get(Pizza, pizza_id)
        restaurant = db.session.get(Restaurant, restaurant_id)
        if not pizza or not restaurant:
            return make_response({"errors": ["validation errors"]}, 400)

        # Create the RestaurantPizza record
        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response = {
            "id": new_restaurant_pizza.id,
            "price": new_restaurant_pizza.price,
            "pizza_id": new_restaurant_pizza.pizza_id,
            "restaurant_id": new_restaurant_pizza.restaurant_id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
        }
        return make_response(response, 201)

# Add Resources to the API
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
