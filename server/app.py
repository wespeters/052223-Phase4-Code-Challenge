#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class Restaurants(Resource):
    def get(self):
        Restaurant.serialize_rules = ('-restaurant_pizzas',)
        restaurants = Restaurant.query.all()
        return make_response(jsonify([restaurant.to_dict() for restaurant in restaurants]), 200)

class RestaurantByID(Resource):
    def get(self, id):
        Restaurant.serialize_rules = ('restaurant_pizzas', '-restaurant_pizzas.restaurant',)
        restaurant = Restaurant.query.filter_by(id=id).one_or_none()
        if restaurant is None:
            return make_response({"error": "Restaurant not found"}, 404)
        return make_response(jsonify(restaurant.to_dict()), 200)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).one_or_none()
        if restaurant is None:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return make_response(jsonify([pizza.to_dict() for pizza in pizzas]), 200)

class Restaurant_pizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            restaurant_pizza = RestaurantPizza(price=data['price'], pizza_id=data['pizza_id'], restaurant_id=data['restaurant_id'])
            db.session.add(restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(restaurant_pizza.to_dict()), 201)
        except Exception:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantByID, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(Restaurant_pizzas, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
