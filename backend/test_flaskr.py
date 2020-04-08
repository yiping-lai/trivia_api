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
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('postgres:1234@localhost:5432', self.database_name)
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
    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_all_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_delete_question_fail(self):
        res = self.client().delete('/questions/1000')
        self.assertEqual(res.status_code,400)
        data = json.loads(res.data)
        self.assertEqual(data['success'], False)

    def test_create_question(self):
        res = self.client().post('/questions',json={'question':'test question','category':'1','answer':'test answer','difficulty':'1'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        question=Question.query.filter(Question.question=='test question').filter(Question.answer=='test answer').filter(Question.category==1).filter(Question.difficulty==1).all()
        l=len(question)
        for q in question:
            q.delete()
        self.assertEqual(l,1)

    def test_create_incomplete_failure(self):
        res = self.client().post('/questions',json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_search_question(self):
        res = self.client().post('/searchQuestions',json={'searchTerm':'what'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['success'], True)

    def test_search_question_fail(self):
        res = self.client().post('/searchQuestions',json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_category_question(self):
        res = self.client().post('/categories/4/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_category_question_fail(self):
        res = self.client().post('/categories/100/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    def test_quizzes(self):
        res = self.client().post('/quizzes',json={'quiz_category':{'id':'1'}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'],1)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()