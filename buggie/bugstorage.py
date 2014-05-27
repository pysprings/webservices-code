# bugstorage.py - convenience methods for hiding database interactions
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


from sqlalchemy.exc import OperationalError

from .buggie import db, app

""" This code is mostly conveninece methods for buggie.py so that a database
could be used without worrying about much of the added complexity while focusing
on the web service interface

If you're reading this, don't take this method of encapsulating database access
as the right way of doing things. It works for a teaching tool but that's about
as far as some of this goes. You have been warned :)"""


valid_states = ['OPEN', 'RESOLVED', 'INVALID']

############################################################
# user storage utility methods
############################################################

def create_user(username, email, timezone):
    newuser = User(username, email, timezone)
    db.session.add(newuser)
    db.session.commit()

    return newuser.marshall_dict()

def get_users():
    return User.query.all()

def get_user_by_id(userid):
    founduser = User.query.filter_by(id=userid).first()

    if not founduser:
        raise ValueError("There is no user with id %d" % userid)
    return founduser

def get_user_by_name(username):
    founduser = User.query.filter_by(username=username).first()

    if not founduser:
        raise ValueError("There is no user with name %s" % username)
    return founduser

def modify_user(userid, username, email, timezone):
    #founduser = get_user_by_id(userid)
    founduser = User.query.filter_by(id=userid).first()

    founduser.username = username
    founduser.email = email
    founduser.timezone = timezone

    app.logger.error("userid modification: %d" % founduser.id)
    db.session.commit()

    return founduser.marshall_dict()

def deactivate_user(userid):
    founduser = get_user_by_id(userid)
    founduser.active = False
    db.session.add(founduser)
    db.session.commit()

    return founduser.marshall_dict()

############################################################
# project storage utility methods
############################################################

def create_project(name, description):
    newproject = Project(name, description)
    db.session.add(newproject)
    db.session.commit()

    return newproject.marshall_dict()

def get_projects():
    return Project.query.all()

def get_project_by_id(projectid):
    foundproject = Project.query.get(projectid)

    if not foundproject:
        raise ValueError("There is no project with id %d" % projectid)
    return foundproject

def get_project_by_name(name):
    foundproject = Project.query.filter_by(name = name).first()

    if not foundproject:
        raise ValueError("There is no project with name %s" % name)
    return foundproject

def modify_project(projectid, name, description):
    foundproject = get_project_by_id(projectid)
    foundproject.name = name
    foundproject.description = description
    db.session.add(foundproject)
    db.session.commit()

    return foundproject.marshall_dict()

def deactivate_project(projectid):
    foundproject = get_project_by_id(projectid)
    foundproject.active = False
    db.session.add(foundproject)
    db.session.commit()

############################################################
# bug storage utility methods
############################################################

def create_bug(title, summary, project_name, assignedto_name=None):
    if assignedto_name is not None:
        assignedto = get_user_by_name(assignedto_name)
    else:
        assignedto = None

    project = get_project_by_name(project_name)
    newbug = Bug(title, summary, project, assignedto)
    db.session.add(newbug)
    db.session.commit()

    return newbug.marshall_dict()

def get_bugs():
    return Bug.query.all()

def get_bug_by_id(bugid):
    foundbug = Bug.query.get(bugid)

    if not foundbug:
        raise ValueError("No bug found with id %d" % bugid)

    return foundbug

def modify_bug(bugid, title, summary, project_name, state, assignedto_name=None):
    foundbug = get_bug_by_id(bugid)

    if state not in valid_states:
        raise ValueError("Bug state must be one of %s. Received %s" % (', '.join(valid_states), state))

    if assignedto_name is not None:
        assignedto = get_user_by_name(assignedto_name)
    else:
        assignedto = None

    project = get_project_by_name(project_name)

    foundbug.title = title
    foundbug.summary = summary
    foundbug.project = project
    foundbug.assignedto = assignedto

    db.session.add(foundbug)
    db.session.commit()

    return foundbug.marshall_dict()



############################################################
# database models
############################################################

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    email = db.Column(db.Text)
    timezone = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    def __init__(self, username, email, timezone=0):
        self.username = username
        self.email = email
        self.timezone = timezone
        self.active = True

    def __repr__(self):
        activestring = 'active' if self.active else 'inactive'

        return "<user({0},{1},{2}>".format(self,id, self.userid, activestring)

    def marshall_dict(self):
        return { 'id': self.id,
                 'username': self.username,
                 'email': self.email,
                 'timezone': self.timezone,
                 'active': self.active
               }

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean)

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.active = True

    def __repr__(self):
        activestring = 'active' if self.active else 'inactive'

        return "<project({0},{1},{2}>".format(self,id, self.name, activestring)

    def marshall_dict(self):
        return { 'id': self.id,
                 'description': self.description,
                 'active': self.active
               }

class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    summary = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship('Project', backref=db.backref('bugs', lazy='dynamic'))
    assignedto_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    assignedto = db.relationship('User', backref=db.backref('bugs', lazy='dynamic'))
    state = db.Column(db.String(16))

    def __init__(self, title, summary, project, assignedto=None ):
        self.title = title
        self.summary = summary
        self.project = project
        self.assignedto = assignedto
        self.state = 'OPEN'

    def __repr__(self):
        return "<bug({0},{1},{2}".format(self.id, self.title, self.project.name)

    def marshall_dict(self):
        return { 'id': self.id,
                 'title': self.title,
                 'summary': self.summary,
                 'project': self.project.id,
                 'assignedto': self.assignedto.id,
               }

############################################################
# General Storage Utils
############################################################

def init_db():
    # this is a hacky way to determine whether or not the database is already
    # initialized and has data
    try:
        User.query.get(1)
    except OperationalError:
        pass
    else:
        return

    db.create_all()
    create_user('joebob', 'joebob@nowor.ky', -6)
    create_project('worlddomination', 'dominate the world')
    create_bug('start world domination', 'The path to world domination starts with a single step. Take that first step.', 'worlddomination', 'joebob')
