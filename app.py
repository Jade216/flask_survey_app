from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as sa_survey

RESPONSES_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

@app.route('/')
def show_survey_startpage():
    '''show survey title&instructions to start'''
    return render_template('start_survey.html', sa_survey = sa_survey)

@app.route('/start', methods = ['POST'])
def start_survey():
    '''clear the session of responses'''
    session[RESPONSES_KEY] = []
    return redirect('/questions/0')

@app.route('/questions/<int:qid>')
def show_questions(qid):
    '''show current question by order'''
    responses = session.get(RESPONSES_KEY)

    if responses is None:
        return redirect('/')
    
    if len(responses) == len(sa_survey.questions):
        return redirect('/complete')
    
    if len(responses) != qid:
        flash(f'Invalid question id: {qid}')
        return redirect(f'/questions/{len(responses)}')
    
    question = sa_survey.questions[qid]
    
    return render_template('/question.html', question = question)

@app.route('/answer', methods=['POST'])
def answer_question():
    '''save responses and redirect to next question'''
    choice = request.form['answer']

    responses = session.get(RESPONSES_KEY)
    responses.append(choice)
    session[RESPONSES_KEY] = responses

    if len(responses) == len(sa_survey.questions):
        return redirect('/complete')
    else:
        return redirect(f'/questions/{len(responses)}')


@app.route('/complete')
def complete():
    return render_template('completion.html')