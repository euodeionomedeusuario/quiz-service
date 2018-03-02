import math

from flask import redirect, render_template, jsonify, request, session
from bson.objectid import ObjectId

from quiz import app
from quiz import db


#respondendo o quiz
@app.route("/quiz/tests/<test_id>/answers/", methods=["POST"])
def send_answer(test_id):
    answers = request.form.getlist("answers[]")
    values = request.form.getlist("values[]")

    test = db.tests.find_one(
           {
                "_id" : ObjectId(test_id)
           })

    user = db.users.find_one(
           {
                "_id" : ObjectId(session["_id"])
           })

    num_questions = len(test["questions"])
    num_correct_questions = 0

    #analisando se a questão está certa
    for answer, value in zip(answers, values):
        for question in test["questions"]:
            if value == str(question["_id"]):
                question["answer"] = answer

                if question["type"] == "trueOrFalse" or question["type"] == "multipleChoice":
                    if question["correctAnswer"] == question["answer"]:
                        num_correct_questions += 1

    grade = num_correct_questions / num_questions * 10

    #salvando resposta no BD
    db.answers.insert({
        "user": user,
        "test": test,
        "grade": grade
    })

    return "OK"


#atualizando as informações do teste
@app.route("/quiz/tests/<test_id>/", methods=["PUT"])
def update_test(test_id):
    name = request.form.get("name")
    description = request.form.get("description")

    test = db.tests.find_one(
           {
                "_id" : ObjectId(test_id)
           })

    test["name"] = name
    test["description"] = description

    db.tests.update(
    {
        "_id" : ObjectId(test_id)},
        test
    )

    return "OK"


#Compartilhando teste
@app.route("/quiz/tests/<test_id>/classes/", methods=["PUT"])
def share_test(test_id):
    title = request.form.get("title")
    description = request.form.get("description")
    deadline = request.form.get("deadline")
    classe_id = request.form.get("classe")

    classe = db.classes.find_one( {"_id": ObjectId(classe_id)} )

    db.tests.update({"_id" : ObjectId(test_id)},{"$addToSet": {"classes": classe}})

    test = db.tests.find_one( {"_id": ObjectId(test_id)} )

    db.tasks.insert({
        "title": title,
        "description": description,
        "deadline": deadline,
        "class": classe,
        "test": test
    })

    return "OK"

#Criando teste
@app.route("/quiz/tests/", methods=["POST"])
def save_test():
    name = request.form.get("name")
    description = request.form.get("description")
    questions = request.form.getlist("questions[]")
    creator = db.users.find_one(
              {
                "email" : session["email"]
              })

    test = {"name": name, "description": description, "creator": creator, "people": "", "questions": []}

    for question in questions:
        result = db.questions.find_one(
                 {
                    "_id" : ObjectId(question)
                 })
        test["questions"].append(result)

    db.tests.insert_one(test)

    return "OK"


#Retornando todas as questões por tópico
@app.route("/quiz/test/<course>/<topic>/", methods=["POST"])
def create_test(course, topic):
    number = int(request.form.get("number")) #Número de questões
    type = request.form.get("type"); #Tipo de questão
    #Esta pode ser melhorada
    level = [{ "name" : "easy", "percentage" : float(request.form.get("easy")) },
            { "name" : "medium", "percentage" : float(request.form.get("medium")) },
            { "name" : "difficult", "percentage" : float(request.form.get("hard")) }]

    questions = []

    i = 0
    while(i < 3):
        amount = math.floor(level[i]["percentage"] * (number/100))
        if amount != 0:
            result = db.questions.find(
                     {
                        "topic._id" : ObjectId(topic),
                        "level" : level[i]["name"],
                        "type": type
                     }).limit(amount)

            for item in result:
                if item["_id"]:
                    item["_id"] = str(item["_id"])
                    item["topic"]["_id"] = str(item["topic"]["_id"])
                    item["topic"]["course"]["_id"] = str(item["topic"]["course"]["_id"])
                questions.append(item)

        i = i + 1

    return jsonify(questions)


#Retornando um teste pelo ID
@app.route("/quiz/tests/<test_id>/", methods=["GET"])
def get_test_by_id(test_id):
    test = db.tests.find_one(
           {
                "_id" : ObjectId(test_id)
           })

    test["_id"] = str(test["_id"])
    test["creator"]["_id"] = str(test["creator"]["_id"])

    questions = []
    for item in test["questions"]:
        if item["_id"]:
            item["_id"] = str(item["_id"])
            item["topic"]["_id"] = str(item["topic"]["_id"])
            item["topic"]["course"]["_id"] = str(item["topic"]["course"]["_id"])
        questions.append(item)

    test["questions"] = questions

    return render_template("tests/answer.html", test=test)


#Retornando um teste pelo ID
@app.route("/quiz/tests/<test_id>/answers/", methods=["GET"])
def test(test_id):
    test = db.tests.find_one(
           {
                "_id" : ObjectId(test_id)
           })

    test["_id"] = str(test["_id"])
    test["creator"]["_id"] = str(test["creator"]["_id"])

    questions = []
    for item in test["questions"]:
        if item["_id"]:
            item["_id"] = str(item["_id"])
            item["topic"]["_id"] = str(item["topic"]["_id"])
            item["topic"]["course"]["_id"] = str(item["topic"]["course"]["_id"])
        questions.append(item)

    test["questions"] = questions

    answers = db.answers.find(
              {
                "test._id" : ObjectId(test_id)
              })

    return render_template("tests/verify.html", test=test, answers=answers)


@app.route("/quiz/tests/<test_id>/", methods=["DELETE"])
def remove_test(test_id):
    db.tests.remove( {"_id": ObjectId(test_id)} )

    return "OK"
