# buggie.py - trivial api for a bug tracking system
#
#Copyright (C) 2014 Tim Flink
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.


from flask import Flask, request, abort
from flask.ext.sqlalchemy import SQLAlchemy
import json


class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../buggie.db'



app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app)

from . import bugstorage
bugstorage.init_db()

def validate_input(data, requirements):
    for requirement in requirements:
        if requirement not in data:
            raise ValueError("Required parameter %s not found in data!" % requirement)


############################################################
# User Interface Routes
############################################################

@app.route('/users', methods=['GET'])
def get_users():
    users = bugstorage.get_users()
    return json.dumps([user.marshall_dict() for user in users ])

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = json.loads(request.data)
    except ValueError, e:
        app.logger.error(e)
        abort(500)

    try:
        validate_input(data, ['username', 'email', 'timezone'])
    except ValueError:
        app.logger.info("Invalid data passed as post to /users: %s" % str(data))

    newuser = bugstorage.create_user(data['username'],
                                     data['email'],
                                     data['timezone'])
    return json.dumps(newuser)
 
@app.route('/users', methods=['PUT', 'DELETE'])
def invalid_users_operation():
    app.logger.warn("Attempted %s on /users" % request.method)


@app.route('/users/<int:userid>', methods=['GET'])
def get_user_by_id(userid):
    founduser = bugstorage.get_user_by_id(userid)
    return json.dumps(founduser.marshall_dict())

@app.route('/users/<int:userid>', methods=['PUT'])
def modify_user(userid):
    try:
        data = json.loads(request.data)
    except ValueError, e:
        app.logger.error(e)
        abort(500)

    try:
        validate_input(data, ['username', 'email', 'timezone'])
    except ValueError:
        app.logger.info("Invalid data passed as put to /users/%d: %s" % (userid, str(data)))
        abort(400)

    newuser = bugstorage.modify_user(userid,
                                     data['username'],
                                     data['email'],
                                     data['timezone'])
    return json.dumps(newuser)

@app.route('/users/<int:userid>', methods=['DELETE'])
def delete_user(userid):
    bugstorage.delete_user(userid)
    return "OK"

@app.route('/users/<int:userid>', methods=['POST'])
def invalid_userid_operations(userid):
    app.logger.warn("Attempted POST on /users/%d" % userid)
    abort(405)



############################################################
# Project Interface Routes
############################################################

@app.route('/projects', methods=['GET'])
def get_projects():
    pass

@app.route('/projects', methods=['POST'])
def create_project():
    pass


############################################################
# Bug Interface Routes
############################################################


if __name__ == '__main__':
    app.run()
