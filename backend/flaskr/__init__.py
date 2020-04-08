import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.expression import func,select

from models import setup_db, Question, Category


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  #CORS(app)
  CORS(app, resources={r"/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  QUESTIONS_PER_PAGE=10
  def paginate_questions(request,selections):
      page=request.args.get('page',1,type=int)
      start=(page-1)*QUESTIONS_PER_PAGE
      end=min(len(selections),start+QUESTIONS_PER_PAGE)
      return selections[start:end]

  '''
  endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def categories():
    data=Category.query.all()
    data_formatted={}
    for d in data:
      data_formatted[d.id]=d.type
    return jsonify({
      'success':True,
      'categories':data_formatted
    })


  '''
  an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def questions_all():
    questions=Question.query.all()
    questions_formatted=[ q.format() for q in questions]
    final_formatted=paginate_questions(request,questions_formatted)

    return jsonify({
      'success':True,
      'questions':final_formatted,
      'total_questions':len(questions),
      'categories':Category.query.count(),
      'current_category':None
    })



  '''
  an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_questions(question_id):
    question=Question.query.get(question_id)
    if question is None:
      abort(400)

    try:
      question.delete()
      return jsonify({
        'success':True,      
      })
    except:
      abort(422)



  '''
  an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def create_questions():  
    body=request.get_json()
    new_question=body.get('question',None)
    new_answer=body.get('answer',None)
    new_difficulty=body.get('difficulty',None)    
    new_category=body.get('category',None)

    if new_question is None or new_answer is None or new_difficulty is None or new_category is None:
      abort(400)

    try:
      new_data=Question(new_question, new_answer, new_category, new_difficulty)
      new_data.insert()
      return jsonify({
        'success':True
      })
    except:
      abort(422)

  '''
  a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/searchQuestions',methods=['POST'])
  def search_questions():
    body=request.get_json()
    search_term=body.get('searchTerm',None)

    if search_term is None or search_term=='':
      abort(400)
    
    try:
      data=Question.query.filter(Question.question.ilike('%'+search_term+'%'))
      data_formatted=[d.format() for d in data]
      return jsonify({
        'success':True,
        'questions':data_formatted,
        'total_questions':len(data_formatted),
        'current_category': None
      })
    except:
      abort(422)



  '''
  a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions',methods=['POST'])
  def questions(category_id):
    data=Question.query.filter(Question.category==category_id).all()
    if len(data)==0:
      abort(400)

    questions_formatted=[ q.format() for q in data]
    return jsonify({
      'success':True,
      'questions':questions_formatted,
      'total_questions':len(data),
      'current_category':category_id
    })


  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def game():
      body=request.get_json()
      category=body.get('quiz_category',None) 
      if category is None:
        abort(400)
     

      try:
        if int(category['id'])==0:
          nxt=Question.query.order_by(func.random()).limit(1).one_or_none()
        else:
          nxt=Question.query.filter(Question.category==int(category['id'])).order_by(func.random()).limit(1).one_or_none()
        return jsonify({
          'success':True,
          'question':nxt.format()
        })
      except:
        abort(405)
      


  '''
  error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404

  @app.errorhandler(400)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400      

  @app.errorhandler(405)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method not allowed"
      }), 405    

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  return app

    