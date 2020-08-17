import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# DONE uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN

# db_drop_and_create_all()

# ROUTES
##########################

# @DONE implement endpoint
#   GET /drinks
#       it should be a public endpoint
#       it should contain only the drink.short() data representation
#           returns status code 200 and json
#               {"success": True, "drinks": drinks}
#           where drinks is the list of drinks
#       or appropriate status code indicating reason for failure


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        get_drinks = Drink.query.all()
        drinks = [drink.short() for drink in get_drinks]

        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200

    except BaseException:
        abort(404)

# @DONE implement endpoint
#   GET /drinks-detail
#       it should require the 'get:drinks-detail' permission
#       it should contain the drink.long() data representation
#           returns status code 200 and json
#               {"success": True, "drinks": drinks}
#           where drinks is the list of drinks
#       or appropriate status code indicating reason for failure


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(token):
    try:
        get_drinks = Drink.query.all()
        drinks = [drink.long() for drink in get_drinks]

        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200

    except BaseException:
        abort(404)

# @DONE implement endpoint
#   POST /drinks
#       it should create a new row in the drinks table
#       it should require the 'post:drinks' permission
#       it should contain the drink.long() data representation
#           returns status code 200 and json
#               {"success": True, "drinks": drink}
#           where drink an array containing only the newly created drink
#       or appropriate status code indicating reason for failure


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(token):
    form = request.get_json()
    drink_title = form.get('title')
    drink_recipe = json.dumps(form.get('recipe'))

    try:
        drink = Drink(
            title=drink_title,
            recipe=drink_recipe
        )

        drink.insert()

        return jsonify({
            "success": True,
            "drinks": drink.long()
        }), 200

    except BaseException:
        abort(422)

# @DONE implement endpoint
#   PATCH /drinks/<id>
#       where <id> is the existing model id
#       it should respond with a 404 error if <id> is not found
#       it should update the corresponding row for <id>
#       it should require the 'patch:drinks' permission
#       it should contain the drink.long() data representation
#           returns status code 200 and json
#               {"success": True, "drinks": drink}
#           where drink an array containing only the updated drink
#       or appropriate status code indicating reason for failure


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, id):
    form = request.get_json()
    drink_title = form.get('title')
    drink_recipe = json.dumps(form.get('recipe'))

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        drink = Drink(
            title=drink_title,
            recipe=drink_recipe
        )

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200

    except BaseException:
        abort(422)

# @DONE implement endpoint
#   DELETE /drinks/<id>
#       where <id> is the existing model id
#       it should respond with a 404 error if <id> is not found
#       it should delete the corresponding row for <id>
#       it should require the 'delete:drinks' permission
#           returns status code 200 and json
#               {"success": True, "delete": id}
#           where id is the id of the deleted record
#       or appropriate status code indicating reason for failure


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        }), 200

    except BaseException:
        abort(404)


# Error Handling

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

# @DONE implement error handler for AuthError
#   error handler should conform to general task above


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
