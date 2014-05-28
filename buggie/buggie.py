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

@app.route('/users/<int:userid>/bugs', methods=['GET'])
def get_user_bugs(userid):
    foundbugs = bugstorage.get_user_by_id(userid).bugs
    return json.dumps([bug.marshall_dict() for bug in foundbugs])



############################################################
# Project Interface Routes
############################################################

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = bugstorage.get_projects()
    return json.dumps([project.marshall_dict() for project in projects ])

@app.route('/projects', methods=['POST'])
def create_project():
    try:
        data = json.loads(request.data)
    except ValueError, e:
        app.logger.error(e)
        abort(500)

    try:
        validate_input(data, ['name', 'description'])
    except ValueError:
        app.logger.info("Invalid data passed as post to /projects: %s" % str(data))
        abort(400)

    newproject = bugstorage.create_project(data['name'], data['description'])
    return json.dumps(newproject)
 
@app.route('/projects', methods=['PUT', 'DELETE'])
def invalid_projects_operation():
    app.logger.warn("Attempted %s on /projects" % request.method)


@app.route('/projects/<int:projectid>', methods=['GET'])
def get_project_by_id(projectid):
    foundproject = bugstorage.get_project_by_id(projectid)
    return json.dumps(foundproject.marshall_dict())

@app.route('/projects/<int:projectid>', methods=['PUT'])
def modify_project(projectid):
    try:
        data = json.loads(request.data)
    except ValueError, e:
        app.logger.error(e)
        abort(500)

    try:
        validate_input(data, ['name', 'description'])
    except ValueError:
        app.logger.info("Invalid data passed as put to /projects/%d: %s" % (projectid, str(data)))
        abort(400)

    newproject = bugstorage.modify_project(data['name'], data['description'])
    return json.dumps(newproject)

@app.route('/projects/<int:projectid>', methods=['DELETE'])
def delete_project(projectid):
    bugstorage.delete_project(projectid)
    return "OK"

@app.route('/projects/<int:projectid>', methods=['POST'])
def invalid_projectid_operations(projectid):
    app.logger.warn("Attempted POST on /projects/%d" % projectid)
    abort(405)

@app.route('/projects/<int:projectid>/bugs', methods=['GET'])
def get_project_bugs(projectid):
    foundbugs = bugstorage.get_user_by_id(projectid).bugs
    return json.dumps([bug.marshall_dict() for bug in foundbugs])


############################################################
# Bug Interface Routes
############################################################

@app.route('/bugs')
def get_bugs():
    bugs = bugstorage.get_bugs()
    return json.dumps([bug.marshall_dict() for bug in bugs])

@app.route('/bugs', methods=['POST'])
def create_bug():
    try:
        data = json.loads(request.data)
    except ValueError, e:
        app.logger.error(e)
        abort(500)

    try:
        validate_input(data, ['title', 'summary', 'project_name'])
    except ValueError:
        app.logger.info("Invalid data passed as put to /bugs: %s" %  str(data))
        abort(400)

    if not 'user_name' in data:
        user_name = None
    else:
        user_name = data['user_name']

    newbug_dict = bugstorage.create_bug(data['title'], data['summary'], data['project_name'], user_name)

    return newbug_dict

@app.route('/bugs/<int:bugid>')
def get_bug(bugid):
    try:
        foundbug = bugstorage.get_bug_by_id(bugid)
    except ValueError:
        app.logger.info("Could not find bug with id %d" % bugid)
        abort(404)

    return json.dumps(foundbug.marshall_dict())

@app.route('/bugs/<int:bugid>', methods=['PUT'])
def modify_bug(bugid):
    try:
        data = json.loads(request.data)
    except ValueError, e:
        app.logger.error(e)
        abort(500)

    try:
        validate_input(data, ['title', 'summary', 'project_name', 'state'])
    except ValueError:
        app.logger.info("Invalid data passed as put to /projects/%d: %s" % (bugid, str(data)))
        abort(400)

    if not 'user_name' in data:
        user_name = None
    else:
        user_name = data['user_name']

    newbug_dict = bugstorage.modify_bug(data['title'], data['summary'],
                                        data['project_name'], data['state'],
                                        user_name)
    return newbug_dict

if __name__ == '__main__':
    app.run()
