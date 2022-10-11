import os
from flask import Flask, request, jsonify, abort,Response
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',methods=["GET"])
def get_drinks():
    try:
        drinks_data = Drink.query.all()
        if drinks_data is None:
            abort(404)
        print(drinks_data)
        drinks = [i.short() for i in drinks_data]

        return jsonify({
            "success": True,
            "drinks": drinks
            })
    except:
        abort(422)
        
       

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    try:
        drinks_data = Drink.query.all()
        if drinks_data is None:
            abort(404)
        
        drinks = [i.long() for i in drinks_data]

        return jsonify({
            "success": True,
            "drinks": drinks
            })
    except:
        abort(422)
        

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def post_drinks(jwt):
    try:
        
        drink_data = request.get_json()

        if request.method != "POST" and drink_data is None:
            abort(405)
       
        drink_recipe= json.dumps(drink_data.get('recipe'))
        print(drink_recipe)
    
        drink = Drink(title=drink_data.get('title'),recipe=f'[{drink_recipe}]')
        x = drink.recipe
       
        drink.insert()


        return jsonify({
            "success" : True,
            "drinks" : drink.long()
        })
    except:
        abort(422)



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def edit_drink(jwt,drink_id):
    try:
        data = request.get_json()
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)
        recipe = json.dumps(data.get('recipe'))
        drink.title = data.get('title')
        drink.recipe = recipe
        drink.update()

        return jsonify({
            "success": True, 
            "drinks": [drink.long()]
        })
    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drinkj(jwt,drink_id):
    try:
        
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)
        drink.delete()

        return jsonify({
            "success": True, 
            "delete": drink_id
        })
    except:
        abort(422)

# Error Handling


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, 
                "error": 422, 
                "message": "unprocessable"}), 422
                
'''if endpoint is not found i.e the url is incorrect/does not exist'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, 
                    "error": 400, 
                    "message": "bad request"}), 400
                    
                    

'''if user uses inappropiate method to endpoint e.g. makes a POST request to GET endpoint.'''
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"success": False, 
                    "error": 405, 
                    "message": "method not allowed"}),405


'''for when there is an issue with our server'''
@app.errorhandler(500)
def internal_server(error):
    return jsonify({"success": False, 
                    "error": 500, 
                    "message": "internal server error"}),500



'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404
    )

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return (
        jsonify({"success": False, "error": error.error}),
        error.status_code
    )
