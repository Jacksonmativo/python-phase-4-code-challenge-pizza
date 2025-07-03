#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, Pizza, RestaurantPizza

# -----------------------------------------------------------------------------
# App & DB setup
# -----------------------------------------------------------------------------
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DB_URI",
    f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# -----------------------------------------------------------------------------
# Resources
# -----------------------------------------------------------------------------
class Index(Resource):
    def get(self):
        return "<h1>Code challenge</h1>", 200

class Restaurants(Resource):
    def get(self):
        # GET /restaurants
        restaurants = Restaurant.query.all()
        data = [
            {"id": r.id, "name": r.name, "address": r.address}
            for r in restaurants
        ]
        return jsonify(data), 200

class RestaurantById(Resource):
    def get(self, id):
        # GET /restaurants/<id>
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "price": rp.price,
                    "pizza_id": rp.pizza_id,
                    "restaurant_id": rp.restaurant_id,
                    "pizza": {
                        "id": rp.pizza.id,
                        "name": rp.pizza.name,
                        "ingredients": rp.pizza.ingredients
                    }
                }
                for rp in restaurant.restaurant_pizzas
            ]
        }
        return jsonify(data), 200

    def delete(self, id):
        # DELETE /restaurants/<id>
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        db.session.delete(restaurant)
        db.session.commit()
        # 204 No Content
        return "", 204

class Pizzas(Resource):
    def get(self):
        # GET /pizzas
        pizzas = Pizza.query.all()
        data = [
            {"id": p.id, "name": p.name, "ingredients": p.ingredients}
            for p in pizzas
        ]
        return jsonify(data), 200

class RestaurantPizzas(Resource):
    def post(self):
        # POST /restaurant_pizzas
        json_data = request.get_json()
        try:
            rp = RestaurantPizza(
                price=json_data["price"],
                pizza_id=json_data["pizza_id"],
                restaurant_id=json_data["restaurant_id"]
            )
            db.session.add(rp)
            db.session.commit()
        except ValueError:
            # validation error (price out of 1–30)
            db.session.rollback()
            return jsonify({"errors": ["validation errors"]}), 400
        except Exception:
            db.session.rollback()
            return jsonify({"errors": ["validation errors"]}), 400

        data = {
            "id": rp.id,
            "price": rp.price,
            "pizza_id": rp.pizza_id,
            "restaurant_id": rp.restaurant_id,
            "pizza": {
                "id": rp.pizza.id,
                "name": rp.pizza.name,
                "ingredients": rp.pizza.ingredients
            },
            "restaurant": {
                "id": rp.restaurant.id,
                "name": rp.restaurant.name,
                "address": rp.restaurant.address
            }
        }
        return jsonify(data), 201

# -----------------------------------------------------------------------------
# Route Registration
# -----------------------------------------------------------------------------
api.add_resource(Index, '/')
api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

# -----------------------------------------------------------------------------
# Launch
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)
