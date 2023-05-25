import openai
import json
import re
from prompt import RightFalseQuestion, MultipleChoiceQuestion

class OpenAI():

  def __init__(self):
        openai.api_key = ""

  def generate_questions(self, theme:str, difficulte:str, niveauScolaire:str, type:str) -> list:  
    model_engine = "text-davinci-003"
    questions = []

    success = False
    while not success:
      try:
          # Generate a response based on the type of question
          if type == "MultipleChoiceQuestions":
              prompt = MultipleChoiceQuestion(theme, difficulte, niveauScolaire)
          elif type == "RightFalseQuestions":
              prompt = RightFalseQuestion(theme, difficulte, niveauScolaire)
          else:
              raise ValueError(f"Invalid question type: {type}")

          completion = openai.Completion.create(
              engine=model_engine,
              prompt=prompt,
              max_tokens=3900,
              n=1,
              stop=None,
              temperature=1,
          )

          # Parse the response
          response = completion.choices[0].text
          question_data = json.loads(response)

          # Append the question data to the list
          questions.append(question_data)
          success = True

      except Exception as e:
          print(f"Error: {e}")
 
    return questions, difficulte, theme, niveauScolaire
    

##########################################TEST PURPOSES###########################################################
#my_openai = OpenAI()
#Questions = my_openai.generate_questions(1, "RightFalseQuestion", 5, 3)
#Questions = my_openai.generate_questions("Histoire de France", "MultipleChoiceQuestion", "6ème", "Difficile")

'''
Additionally, it's crucial to validate and review the responses you get from the model. Remember, 
AI is a tool to aid your process and is not infallible. In this case, cross-checking the answers with trusted sources and books is a good practice.
'''