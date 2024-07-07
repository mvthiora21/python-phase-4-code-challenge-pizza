from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

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

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants])

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            return jsonify(restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas')))
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas])

class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(jsonify({
                'id': new_restaurant_pizza.id,
                'price': new_restaurant_pizza.price,
                'pizza_id': new_restaurant_pizza.pizza_id,
                'restaurant_id': new_restaurant_pizza.restaurant_id,
                'pizza': new_restaurant_pizza.pizza.to_dict(),
                'restaurant': new_restaurant_pizza.restaurant.to_dict()
            }), 201)
        except ValueError as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)
        except KeyError as e:
            return make_response(jsonify({"errors": [f"KeyError: Missing required key '{e.args[0]}'"]})), 400

api.add_resource(RestaurantsResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzasResource, '/pizzas')
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)