import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_questions(self):
        """
        was_published_recently() returns False for questions whose pub_date is older than 1 day
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        q = Question(pub_date=time)
        self.assertIs(q.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for question whose pub_date is within the last day
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        q = Question(pub_date=time)
        self.assertIs(q.was_published_recently(), True)


def create_question(text, days):
    """
    Create a question with given
    :param text: question text
    :param days: offset to now (positive - future, negative - questions created in the past)
    :return: a Question object
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=text, pub_date=time)


class QuestionIndexViewTest(TestCase):

    def test_no_question(self):
        """
        if no questions exist an appropriate message is displayed
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions from the past are displayed on the index page
        """
        create_question(text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question>'])

    def test_future_question(self):
        """
        Questions with 'pub_date' in the future aren't displayed on the index page
        """
        create_question(text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        When both past and future questions exist, display only the part from the past
        """
        create_question(text="Past question", days=-30)
        create_question(text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question>'])

    def test_two_past_questions(self):
        """
        Index page can display multiple questions
        """
        create_question(text="Past question 1", days=-30)
        create_question(text="Past question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
                                 ['<Question: Past question 2>', '<Question: Past question 1>'])


class QuestionDetailViewTest(TestCase):

    def test_future_question(self):
        """
        Detail view of question with pub_date in the future returns 404 not found
        """
        future_question = create_question("Future question", 30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        Detail view of question with pub_date in the past displays question's text
        """
        past_question = create_question("Past question", -30)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
