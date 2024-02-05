from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Survey, Question, Answer, Respondent, Response
from django.db import connection


def index(request):
    surveys = Survey.objects.all()
    return render(request, "surveys/index.html", {"surveys": surveys})


def survey_detail(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    respondent, _ = Respondent.objects.get_or_create(
        session_id=request.session.session_key
    )

    questions_to_display = [
        question
        for question in survey.questions.all()
        if not getattr(question, "condition", None)
        or question.condition.is_met(respondent.id)
    ]

    return render(
        request,
        "surveys/detail.html",
        {"survey": survey, "questions": questions_to_display},
    )


def submit_survey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    respondent, _ = Respondent.objects.get_or_create(
        session_id=request.session.session_key
    )

    for question in survey.questions.all():
        answer_id = request.POST.get(f"question{question.id}")
        if answer_id:
            answer = get_object_or_404(Answer, pk=answer_id)
            Response.objects.create(respondent=respondent, answer=answer)

    return HttpResponseRedirect(reverse("survey_result", args=(survey.id,)))


def get_survey_statistics(survey_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                q.id,
                COUNT(r.id) as response_count,
                COUNT(DISTINCT r.respondent_id) as respondent_count
            FROM surveys_question q
            LEFT JOIN surveys_answer a ON a.question_id = q.id
            LEFT JOIN surveys_response r ON r.answer_id = a.id
            WHERE q.survey_id = %s
            GROUP BY q.id
            ORDER BY response_count DESC
        """,
            [survey_id],
        )
        result = cursor.fetchall()
    return result


def survey_result(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    total_respondents, questions_data, question_answers_data = get_survey_details(
        survey_id
    )

    return render(
        request,
        "surveys/result.html",
        {
            "survey": survey,
            "total_respondents": total_respondents,
            "questions_data": questions_data,
            "question_answers_data": question_answers_data,
        },
    )


def get_survey_details(survey_id):
    with connection.cursor() as cursor:
        total_respondents = get_total_respondents(cursor, survey_id)
        questions_data = get_questions_data(cursor, survey_id)
        question_answers_data = get_question_answers_data(cursor, questions_data)
    return total_respondents, questions_data, question_answers_data


def get_total_respondents(cursor, survey_id):
    cursor.execute(
        """
        SELECT COUNT(DISTINCT respondent_id)
        FROM surveys_response
        WHERE answer_id IN (
            SELECT id
            FROM surveys_answer
            WHERE question_id IN (
                SELECT id
                FROM surveys_question
                WHERE survey_id = %s
            )
        )
    """,
        [survey_id],
    )
    return cursor.fetchone()[0]


def get_questions_data(cursor, survey_id):
    cursor.execute(
        """
        SELECT q.id, q.text, COUNT(DISTINCT r.respondent_id) as respondent_count
        FROM surveys_question q
        LEFT JOIN surveys_answer a ON q.id = a.question_id
        LEFT JOIN surveys_response r ON a.id = r.answer_id
        WHERE q.survey_id = %s
        GROUP BY q.id, q.text
        ORDER BY respondent_count DESC, q.id
    """,
        [survey_id],
    )
    return cursor.fetchall()


def get_question_answers_data(cursor, questions_data):
    question_answers_data = {}
    for question_id, _, _ in questions_data:
        cursor.execute(
            """
            SELECT a.text, COUNT(r.id) as response_count
            FROM surveys_answer a
            LEFT JOIN surveys_response r ON a.id = r.answer_id
            WHERE a.question_id = %s
            GROUP BY a.text
        """,
            [question_id],
        )
        question_answers_data[question_id] = cursor.fetchall()
    return question_answers_data
