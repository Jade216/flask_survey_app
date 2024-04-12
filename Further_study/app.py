from flask import Flask, request, render_template, redirect, session, make_response, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

@app.route('/')
def show_picksurvey_form():
    '''show pick a survey'''
    return render_template('pick_survey.html', surveys = surveys)


@app.route('/', methods = ['POST'])
def pick_survey():
    '''pick a survey'''
    survey_id = request.form['survey_id']

    if request.cookies.get(f'completed_{survey_id}'):
        return render_template('already_done.html')
    
    selected_survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id
    
    return render_template('survey_start.html', selected_survey = selected_survey)
    
@app.route('/begin', methods=['POST'])
def start_survey():
    '''clear the session of responses'''
    session[RESPONSES_KEY] = []
    return redirect('/questions/0')

@app.route('/questions/<int:qid>')
def show_question(qid):
    '''show current question by order'''
    responses = session.get(RESPONSES_KEY)
    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]

    if responses is None:
        return redirect('/')
    if len(responses) == len(survey.questions):
        return redirect('/complete')
    if len(responses) != qid:
        flash(f'Invalid question id: {qid}')
        return redirect(f'/questions/{len(responses)}')
    
    question = survey.questions[qid]

    return render_template(
                           'questions.html',
                           question = question
                           )

@app.route('/answer', methods=['POST'])
def handle_question():
    '''save answers and redirect to next question'''
    choice = request.form['answer']
    text = request.form.get('text', '')

    responses = session[RESPONSES_KEY]
    responses.append({'choice':choice, 'text': text})
    session[RESPONSES_KEY] = responses
    
    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]

    if len(responses) == len(survey.questions):
        return redirect('/complete')
    else:
        return redirect(f'/questions/{len(responses)}')
    
@app.route('/complete')
def complete():
    survey_id = session[CURRENT_SURVEY_KEY]
    selected_survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    html = render_template("completion.html",
                           selected_survey= selected_survey,
                           responses=responses)

    # Set cookie noting this survey is done so they can't re-do it
    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response
