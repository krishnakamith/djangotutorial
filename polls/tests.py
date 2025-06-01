import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertFalse(future_question.was_published_recently())

    def test_was_published_recently_with_past_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        past_question = Question(pub_date = time)
        self.assertFalse(past_question.was_published_recently())

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date = time)
        self.assertTrue(recent_question.was_published_recently())

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days= days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code , 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"],[])

    def test_past_questions(self):
        question = create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"],[question])

    def test_future_questions(self):
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"],[])

    def test_past_and_future_questions(self):
        question = create_question(question_text="Past question", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_two_past_question(self):
        question1 = create_question(question_text="Past question 1", days=-30)
        question2 = create_question(question_text="Past question 2", days=-3)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question2, question1])

class QuestionDetailViewTests(TestCase):
    def test_future_questions(self):
        future_question = create_question(question_text="Future question", days=10)
        response = self.client.get(reverse("polls:detail", args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)
   
    def test_past_questions(self):
        past_question = create_question(question_text="Past question", days=-10)
        response = self.client.get(reverse("polls:detail", args=(past_question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)