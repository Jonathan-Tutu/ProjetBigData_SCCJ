
def RightFalseQuestion(theme, difficulte, niveauScolaire): 
    promptRightFalseQuestion = f"""Create a {difficulte} difficulty answerable by Oui/Non random question on {theme} for the {niveauScolaire} level in France. Use this format:
    {{
    "question": "Q",
    "reponses": ["Oui", "Non"],
    "reponse_correcte": "RealAnswer"
    }} Ensure correctness."""

    return promptRightFalseQuestion

def MultipleChoiceQuestion(theme, difficulte, niveauScolaire): 
    promptMultipleChoiceQuestion = f"""Create a {difficulte} difficulty answerable by 4 choices random question on {theme} for the {niveauScolaire} level in France. Use this format:
    {{ #Escape the bracket by using 2 brackets
    "question": "Q",
    "reponses": ["Answer", "Answer", "Answer", "Answer"],   
    "reponse_correcte": "RealAnswer"
    }} Ensure correctness."""

    return promptMultipleChoiceQuestion

