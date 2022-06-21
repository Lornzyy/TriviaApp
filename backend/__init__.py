from logging import exception
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS=(app)

    QUESTIONS_PER_PAGE = 10

    def paginate_questions(request, selection):

        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions


    # CORS Headers
    @app.after_request
    def after_request(response):
            response.headers.add(
                "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
            )
            response.headers.add(
                "Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS"
            )
            return response


    @app.route("/categories", methods=["GET"])
    def retrieve_categories():

        try:
            categories = Category.query.order_by(Category.id).all()
            current_categories = {category.id: category.type for category in categories}

            if len(current_categories) == 0:
                abort(404)

            return jsonify({
                    "success": True,
                    "categories": current_categories,
                    "total_categories": len(categories)
                })
        except Exception:
            abort(404)
                

    
    @app.route("/questions", methods=["GET"])
    def retrieve_questions():

        try:#get the question in a paginated manner
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)

            if (current_question) == 0:
                abort(404)

            select_category = Category.query.order_by(Category.id).all()
            current_categories = {category.id: category.type for category in select_category}

            question = Question.query.all()

            return jsonify({
                    "success": True,
                    "questions": current_question,
                    "total_questions": len(question),
                    "categories": current_categories,
                })

        except Exception:
            abort(404)


    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == str(question_id)).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)

            return jsonify({
                    "success": True,
                    "deleted": question_id,
                    "total_questions": len(Question.query.all()),
                    "question": current_question,
                    
                })

        except Exception:
            abort(422)



    @app.route("/questions", methods=["POST"])
    def create_question():

        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search_term = body.get("searchTerm", None)        
        

        try:

            if search_term:

                page = request.args.get("page", 1, type=int)
                start = (page - 1) * QUESTIONS_PER_PAGE
                end = start + QUESTIONS_PER_PAGE

                search_query = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

                questions = [question.format() for question in search_query]
                current_questions = questions[start:end]


                if len(questions) == 0:
                    abort(422)

                return jsonify({
                    "success": True,
                    "questions": current_questions,
                    "total_results": len(search_query)
                })

            else:
                if new_question is None or new_answer is None or new_category is None or new_difficulty is None or search_term is None:
                    abort(422)

            question = Question(question = new_question, answer = new_answer, category = new_category, difficulty = new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions= paginate_questions(request, selection)
            question = Question.Query.all()

            return jsonify({
                    "success": True,
                    "created": question.id,
                    "questions": current_questions,
                    "total_questions": len(question)
                })

        except Exception:
            abort(422)




    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_based_on_category(category_id):
        try:


            questions = Question.query.filter(Question.category == str(category_id)).all()

            question = [question.format() for question in questions]

            return jsonify({
                "success": True,
                "questions": question,
                "total_questions": len(questions)
            })

        except Exception:
            abort(404)



    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        
        body = request.get_json()

        category = body.get("quiz_category")
        previous_questions = body.get("previous_questions")

        try:

            if category["id"] == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()


            else:
                questions = Question.query.filter(Question.id.notin_(previous_questions), Question.category == category["id"]).all()

                def random_question():
                    return random.randint(0, len(questions))

            next_que = None

            if len(questions) > 0:
                play = random_question()
                next_que = questions[play].format()


            return jsonify({
                'success': True,
                'question': next_que,
            })
        except Exception:
            abort(404)


    #Error handlers
    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            "success": False,
            "code": 404,
            "message": "resource not found"
            })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
                "success": False,
                "code": 400,
                "message": "bad request"
            })

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "code": 422,
            "message": "unprocessable"
        })
        
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "code": 422,
            "message": "Internal Server Error"
        })






    return app

