from django.test import TestCase

from blogs.forms import ArticleForm


class ArticleFormTest(TestCase):
    """記事のフォームのテスト"""
    def test_no_data(self):
        """データがない時のテスト"""
        form_data = {}
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_with_data(self):
        """データがある時のテスト"""
        form_data = {
            'title': 'test title',
            'text': '# test text \n test text',
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data.get('title'), form_data.get('title'))
