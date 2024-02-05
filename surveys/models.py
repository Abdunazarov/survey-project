from django.db import models


class Survey(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()


class Question(models.Model):
    survey = models.ForeignKey(
        Survey, related_name="questions", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=200)
    question_type = models.CharField(max_length=50)


class Answer(models.Model):
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=200)
    respondents = models.ManyToManyField("Respondent", through="Response")


class Respondent(models.Model):
    session_id = models.CharField(max_length=200)


class Response(models.Model):
    respondent = models.ForeignKey(Respondent, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)


class Condition(models.Model):
    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name="condition",
        null=True,
        blank=True,
    )
    previous_question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="next_question_conditions"
    )
    previous_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def is_met(self, respondent_id):
        return Response.objects.filter(
            respondent_id=respondent_id,
            answer=self.previous_answer,
            answer__question=self.previous_question,
        ).exists()
