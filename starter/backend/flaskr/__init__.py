import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json
from models import setup_db, Question, Category

db = SQLAlchemy()

QUESTIONS_PER_PAGE = 10


# paginating questions
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # Set up CORS with '*' for origins
    CORS(app, resources={'/': {'origins': '*'}})

    # CORS headers to set access control
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # -------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------

    @app.route('/categories')
    def get_categories():

        # get all categories 
        categories = Category.query.all()
        #add categories of formmated
        categories_formmated = {}
        for category in categories:
            categories_formmated[category.id] = category.type

        #  if  categories = 0
        if (len(categories_formmated) == 0):
            abort(404)

        # return data
        return jsonify({
            'success': True,
            'categories': categories_formmated
        })
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

    @app.route('/questions')
    def get_questions():
        # get questions 
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        # if  questions =0
        if (len(current_questions) == 0):
            abort(404)

        try:
            # get categories
            categories = Category.query.all()
            # add to formmated
            categories_formmated = {}
            for category in categories:
                categories_formmated[category.id] = category.type

            # return  data
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total_questions,
                'categories': categories_formmated
            })
        except:

            abort(422)


    # -----------------------------------------------------------
    # -----------------------------------------------------------

    #delete questions

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            # get one question by id
            question = Question.query.filter_by(id=id).one_or_none()

            # if question=0
            if question is None:
                abort(404)

            # delete function
            question.delete()

            return jsonify({
                'success': True,
                'deleted': id
            })
        except:
            #  if there's a problem deleting the question
            abort(422)

    # -----------------------------------------------------------
    # -----------------------------------------------------------
     # Create question with POST /method
    @app.route('/questions', methods=['POST'])
    def create_question():
        #  body and data from user 
        body = request.get_json()
        new_question = body.get('question','')
        new_answer = body.get('answer','')
        new_difficulty = body.get('difficulty','')
        new_category = body.get('category','')
        try:
            # insert new question into database
            question = Question(question=new_question, answer=new_answer,difficulty=new_difficulty, category=new_category)
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            #return data

            return jsonify({
                'success': True,
                'created': question.id,
                'question_created': question.question,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    # -----------------------------------------------------------
    # -----------------------------------------------------------

    # Searching for  questions

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        # Get user searshing
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        try:
            if search_term:
                selection = Question.query.filter(Question.question.ilike (f'%{search_term}%')).all()

            # paginate 
            paginated = paginate_questions(request, selection)

            #return data

            return jsonify({
                'success': True,
                'questions':  paginated,
                'total_questions': len(selection),
                'current_category': None
            })
        except:
            abort(404)

    # -----------------------------------------------------------
    # -----------------------------------------------------------

    # GET questions based on category

    @app.route('/categories/<int:id>/questions')
    def get_category_questions(id):
        # Get  one category by id
        category = Category.query.filter_by(id=id).one_or_none()
        try:
            # get questions/category
            selection = Question.query.filter_by(category=category.id).all()

            # paginate 
            paginated = paginate_questions(request, selection)

            #return data
            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all()),
                'current_category': category.type
            })
        except:
            abort(400)

# -----------------------------------------------------------
# -----------------------------------------------------------
# play

    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', None)

        try:
            if quiz_category:
                if quiz_category['id'] == 0:
                    available = Question.query.all()
                else:
                    available= Question.query.filter_by(category=quiz_category['id']).all()

            selection =  [question.format() for question in available if question.id not in previous_questions]

            #select random questions from available questions

            output = random.choice(selection)

            #Returns JSON object with random available questions which are not among previous used questions

            return jsonify({
                'success': True,
                'question':output
            })
        except:
            abort(422)

# -----------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

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

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app