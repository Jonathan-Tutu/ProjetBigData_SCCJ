import mysql.connector
import random
import unicodedata
import json
from davinci_api_communication import OpenAI

Openai_instance = OpenAI()

db = mysql.connector.connect(
    host='34.28.129.102',
    user='root',
    password= 'monbeaumotdepasse',
    database='bigdatasql_questions'
)

# Define the cursor
cursor = db.cursor()
def remove_accents(data):
    if isinstance(data, dict):
        return {remove_accents(key): remove_accents(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [remove_accents(element) for element in data]
    elif isinstance(data, str):
        return ''.join(c for c in unicodedata.normalize('NFD', data)
                        if unicodedata.category(c) != 'Mn')
    else:
        return data

def retrieve_mappings():
    difficulteMapping = {}
    themeMapping = {}
    niveauScolaireMapping = {}

    difficulteMapping_query = ("SELECT * FROM quizz_difficulty")
    themeMapping_query = ("SELECT * FROM quizz_thematique")
    niveauScolaireMapping_query = ("SELECT * FROM quizz_niveauscolaire")

  

    cursor.execute(difficulteMapping_query)
    for (id, text) in cursor:
        difficulteMapping[id] = text

    cursor.execute(themeMapping_query)
    for (id, text) in cursor:
        themeMapping[id] = text

    cursor.execute(niveauScolaireMapping_query)
    for (id, text) in cursor:
        niveauScolaireMapping[id] = text

    return difficulteMapping, themeMapping, niveauScolaireMapping

difficulteMapping, themeMapping, niveauScolaireMapping = retrieve_mappings()

def replace_id_with_difficulty(difficulty_id):
    return difficulteMapping.get(difficulty_id, "Unknown Difficulty")

def replace_id_with_school_subject(subject_id):
    return themeMapping.get(subject_id, "Unknown Subject")

def replace_id_with_school_level(level_id):
    return niveauScolaireMapping.get(level_id, "Unknown Level")

def generateNRightFalseQuestions(numberOfQuestions:int, theme, niveauScolaire, difficulte):
    questions = []
    mapped_difficulte = replace_id_with_difficulty(difficulte)
    mapped_theme = replace_id_with_school_subject(theme)
    mapped_niveauScolaire = replace_id_with_school_level(niveauScolaire)

    for _ in range(numberOfQuestions):
        # Generating true/false questions

        rightFalseQuestions = Openai_instance.generate_questions(mapped_theme, mapped_difficulte , mapped_niveauScolaire, "RightFalseQuestions")
        questions.extend(rightFalseQuestions[0])
    
    add_questions_to_db(questions, theme, difficulte, niveauScolaire)

def generateNMultipleChoiceQuestions(numberOfQuestions:int, theme, niveauScolaire, difficulte):
    questions = []
    mapped_difficulte = replace_id_with_difficulty(difficulte)
    mapped_theme = replace_id_with_school_subject(theme)
    mapped_niveauScolaire = replace_id_with_school_level(niveauScolaire)

    for _ in range(numberOfQuestions):
        # Generating multiple choice questions
        multipleChoiceQuestions = Openai_instance.generate_questions(mapped_theme, mapped_difficulte , mapped_niveauScolaire, "MultipleChoiceQuestions")
        questions.extend(multipleChoiceQuestions[0])

    add_questions_to_db(questions, theme, difficulte, niveauScolaire)

def generateNRandomQuestions(numberOfQuestions:int, theme, niveauScolaire, difficulte):
    questions = []
    mapped_difficulte = replace_id_with_difficulty(difficulte)
    mapped_theme = replace_id_with_school_subject(theme)
    mapped_niveauScolaire = replace_id_with_school_level(niveauScolaire)

    random.seed()
    numberOfMultipleChoice = random.randint(0,numberOfQuestions)
    numberOfRightFalse = numberOfQuestions - numberOfMultipleChoice;

    for _ in range(numberOfMultipleChoice):
        print(_)
        # Generating multiple choice questions
        multipleChoiceQuestions = Openai_instance.generate_questions(mapped_theme, mapped_difficulte , mapped_niveauScolaire, "MultipleChoiceQuestions")
        questions.extend(multipleChoiceQuestions[0])

    for _ in range(numberOfRightFalse):
        print(_)
        # Generating true/false questions
        rightFalseQuestions = Openai_instance.generate_questions(mapped_theme, mapped_difficulte , mapped_niveauScolaire, "RightFalseQuestions")
        questions.extend(rightFalseQuestions[0])

    add_questions_to_db(questions, theme, difficulte, niveauScolaire)

def add_questions_to_db(questions, themeId, difficulteId, niveauScolaireId):
    numberOfQuestionToRegenerate = 0

    for question in questions:
        print(question)
        #json normalisation
        question =  remove_accents(question)

        # Unpack the question details
        question_text = question["question"]

        # Check if the question already exists in the Questions table
        check_question_query = "SELECT id FROM quizz_questions WHERE text = %s"
        cursor.execute(check_question_query, (question_text,))
        existing_question = cursor.fetchone()

        if existing_question:
            print("Question already exists. Skipping insertion.")
            numberOfQuestionToRegenerate += 1
            continue  # Skip to the next question

        # Insert the question into the Questions table
        insert_question_query = "INSERT INTO quizz_questions (text, fk_difficulty_id_id, fk_niveauscolaire_id_id, fk_thematique_id_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_question_query, (question_text, difficulteId, niveauScolaireId, themeId))
        question_id = cursor.lastrowid

        # Insert the answers into the Answers table
        for answer in question["reponses"]:
            is_correct = 1 if answer == question["reponse_correcte"] else 0
            insert_answer_query = "INSERT INTO quizz_answers (text, correct, FK_questions_ID) VALUES (%s, %s, %s)"
            cursor.execute(insert_answer_query, (answer, is_correct, question_id))

        db.commit()

    generateNMultipleChoiceQuestions(1, 3, 11, 3)

    generateNRightFalseQuestions(1, 3, 11, 3)