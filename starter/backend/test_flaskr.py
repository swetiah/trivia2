import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('caryn', 'caryn','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_paginate_questions(self):
        """Tests question pagination success"""
        res= self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        

    def test_404_request_beyond_valid_page(self):
        """ Tests error if user tries to access nonexistent page """
        res= self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        """ Tests success of loading categories"""
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_question(self):
        """ Tests question delete success """
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 1).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)

    def test_422_if_questions_dose_not_exist(self):
        res= self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_question(self):
        """Tests question creation"""

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['created'])
        self.assertEqual(len(data['questions']))
        

    def test_405_if_question_creation_not_allowed(self):

        res = self.client().post('/questions/50', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_search_question(self):
        """test success fo searchin questions"""

        res = self.client().post('/questions/search', json={'searchTerm': 'Peanut Butter'})
        data = json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']),1)

    def test_404_search_questions(self):
        """test for no search results 404"""
        res = self.client().post('/questions/search', json={'searchTerm': ''})
        data = json.loads(response.data)

       
        self.assertEqual(rese.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_get_category_questions(self):
        """test success of getting questions by categories"""
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)


        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_category_questions(self):
        """test for 404 error with no questions from category"""
        response = self.client().get('/categories/a/questions')
        data = json.loads(response.data)

  
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_quiz(self):
        """test success of playing quiz"""
        quiz = {'previous_questions': [], 'quiz_category': {'type': 'History', 'id': 5}}
        res = self.client().post('/quizzes', json=quiz)
        data = json.loads(res.data)

   
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_get_quiz_fails(self):
        """test 422 error if quiz game fails"""
        res = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

       
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

        




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()