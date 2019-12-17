from collections import deque

from django.test import TestCase


class PhraseTest(TestCase):
    """語句を表すクラスのテスト"""
    def test_instance(self):
        """正常にインスタンス化されることの確認"""
        from blogs.escape import Phrase

        phrase = Phrase()
        self.assertTrue(phrase is not None)
        self.assertTrue(isinstance(phrase, Phrase))

    def test_init(self):
        """コンストラクタが正常に動作することの確認"""
        from blogs.escape import Phrase

        phrase = Phrase('test text')
        self.assertFalse(phrase.is_accepted)
        self.assertEqual(phrase.text, 'test text')

    def test_str(self):
        """__str__が正常に動作することの確認"""
        from blogs.escape import Phrase

        phrase = Phrase('test __str__')
        print(phrase)
        self.assertEqual(str(phrase), 'Phrase(test __str__)')


class SentenceTest(TestCase):
    """文を表すクラスのテスト"""
    def test_instance(self):
        """正常にインスタンス化されることの確認"""
        from blogs.escape import Sentence

        sentence = Sentence()
        self.assertTrue(sentence is not None)
        self.assertTrue(isinstance(sentence, Sentence))

    def test_set_phrase(self):
        """phraseが正常に設定されることの確認"""
        from blogs.escape import Phrase, Sentence

        sentence = Sentence()
        phrase1 = Phrase('phrase1')
        sentence.set_phrase(phrase1)
        phrase2 = Phrase('phrase2')
        phrase2.is_accepted = True
        sentence.set_phrase(phrase2)

        phrases = sentence.phrases
        self.assertFalse(phrases[0].is_accepted)
        self.assertTrue(phrases[1].is_accepted)

    def test_str_phrase(self):
        """引数にstr型を渡した場合の確認"""
        from blogs.escape import Sentence

        sentence = Sentence()
        sentence.set_phrase('phrase str')

        phrases = sentence.phrases
        self.assertFalse(phrases[0].is_accepted)
        self.assertEqual(phrases[0].text, 'phrase str')

    def test_arg_error(self):
        """引数にint型を渡した場合の確認"""
        from blogs.escape import Sentence

        sentence = Sentence()
        with self.assertRaises(ValueError) as error:
            sentence.set_phrase(10)
        error_message = 'phrase must be str or Phrase instance'
        self.assertEqual(error.exception.args[0], error_message)

    def test_str(self):
        """__str__が正常に設定されることの確認"""
        from blogs.escape import Phrase, Sentence

        sentence = Sentence()
        phrase1 = Phrase('phrase1')
        sentence.set_phrase(phrase1)
        phrase2 = Phrase('phrase2')
        sentence.set_phrase(phrase2)

        result_str = 'Sentence(deque([Phrase(phrase1), Phrase(phrase2)]))'
        self.assertEqual(str(sentence), result_str)


class CreateSentenceTest(TestCase):
    """textからphraseで区切ったsentenceを作る関数のテスト"""
    def setUp(self):
        self.test_text = '''
        Here is Sentence1.
        ```
            Here is Sentence2.
            In the quot block.
        ```
        Here is Sentence3.
        '''

        self.test_text2 = '''
        Here is Sentence1.
        ```
            Here is Sentence2.
            In the quot block.
        ```
        Here is Sentence3.
        ```
            Here is Sentence4.
            In the quot block.
        ```
        Here is Sentence5.
        ```
            Here is Sentence6.
            In the quot block.
        ```
        Here is Sentence7.
        '''

        self.confirm_texts = deque()

        self.confirm_texts.append('```')
        confirm_text1 = '''
            Here is Sentence2.
            In the quot block.
        '''
        self.confirm_texts.append(confirm_text1)
        self.confirm_texts.append('```')

        self.confirm_texts.append('```')
        confirm_text2 = '''
            Here is Sentence4.
            In the quot block.
        '''
        self.confirm_texts.append(confirm_text2)
        self.confirm_texts.append('```')

        self.confirm_texts.append('```')
        confirm_text3 = '''
            Here is Sentence6.
            In the quot block.
        '''
        self.confirm_texts.append(confirm_text3)
        self.confirm_texts.append('```')

    def test_count(self):
        """sentenceが期待通りの個数作られることの確認"""
        from blogs.escape import create_sentence

        sentence = create_sentence(self.test_text)
        self.assertEqual(len(sentence.phrases), 5)

    def test_accept(self):
        """phraseのacceptが期待通りに設定されていることの確認"""
        from blogs.escape import create_sentence

        phrases = create_sentence(self.test_text).phrases
        self.assertFalse(phrases[0].is_accepted)
        self.assertTrue(phrases[1].is_accepted)
        self.assertTrue(phrases[2].is_accepted)
        self.assertTrue(phrases[3].is_accepted)
        self.assertFalse(phrases[4].is_accepted)

    def test_some_accepte_phrases(self):
        """トリプルクォートが複数ある場合に
        期待通りにsentenceが作られることの確認
        """
        from blogs.escape import create_sentence

        phrases = create_sentence(self.test_text2).phrases
        for phrase in phrases:
            if phrase.is_accepted:
                self.assertEqual(phrase.text, self.confirm_texts.popleft())


class ReplaceTransTest(TestCase):
    """変換関数のテスト"""
    def test_no_change(self):
        """変換対象がない場合"""
        from blogs.escape import replace_trans

        d = {'<': '&lt;', '>': '&gt;'}
        text = 'これはテストです、&lt;と&gt;は変換されません。'
        result = replace_trans(text, d)
        self.assertEqual(result, text)

    def test_with_change_data(self):
        """変換対象がある場合"""
        from blogs.escape import replace_trans

        d = {'<': '&lt;', '>': '&gt;'}
        text = 'これはテストです、<と>は変換されます。'
        result_text = 'これはテストです、&lt;と&gt;は変換されます。'
        result = replace_trans(text, d)
        self.assertEqual(result, result_text)

    def test_with_continuity_data(self):
        """変換対象が続けてある場合"""
        from blogs.escape import replace_trans

        d = {'<': '&lt;', '>': '&gt;'}
        text = 'これはテストです、<<<<は全て変換されます。'
        result_text = 'これはテストです、&lt;&lt;&lt;&lt;は全て変換されます。'
        result = replace_trans(text, d)
        self.assertEqual(result, result_text)


class StrTransTest(TestCase):
    """str.translateを使って変換を行うクラスのテスト"""
    def test_no_change(self):
        """変換対象がない場合"""
        from blogs.escape import str_trans

        d = {'<': '&lt;', '>': '&gt;'}
        text = 'これはテストです、&lt;と&gt;は変換されません。'
        result = str_trans(text, d)
        self.assertEqual(result, text)

    def test_with_change_data(self):
        """変換対象がある場合"""
        from blogs.escape import str_trans

        d = {'<': '&lt;', '>': '&gt;'}
        text = 'これはテストです、<と>は変換されます。'
        result_text = 'これはテストです、&lt;と&gt;は変換されます。'
        result = str_trans(text, d)
        self.assertEqual(result, result_text)

    def test_with_continuity_data(self):
        """変換対象が続けてある場合"""
        from blogs.escape import str_trans

        d = {'<': '&lt;', '>': '&gt;'}
        text = 'これはテストです、<<<<は全て変換されます。'
        result_text = 'これはテストです、&lt;&lt;&lt;&lt;は全て変換されます。'
        result = str_trans(text, d)
        self.assertEqual(result, result_text)

    def test_key_is_not_one_length(self):
        """dのkeyのサイズが2以上"""
        from blogs.escape import str_trans

        d = {'&lt;': '<', '&gt;': '>'}
        text = 'これはテストです、&lt;と&gt;はアンエスケープされません'

        with self.assertRaises(ValueError) as error:
            str_trans(text, d)
        error_message = 'key mast be one size'
        self.assertEquals(error.exception.args[0], error_message)

    def test_correct_key_and_incorrect(self):
        """dのkeyのサイズが2以上と1がある場合"""
        from blogs.escape import str_trans

        d = {'&lt;': '<', '>': '&gt;'}
        text = 'これはテストです、&lt;と>は変換されません'

        with self.assertRaises(ValueError) as error:
            str_trans(text, d)
        error_message = 'key mast be one size'
        self.assertEquals(error.exception.args[0], error_message)


class TranslaterTest(TestCase):
    """文字の置換を行うクラスのテスト"""
    def test_setgroup(self):
        """エスケープしない文字列を保存するメソッドのテスト"""
        from blogs.escape import Translater
        translater = Translater()

        translater.setgroup('&lt;', '<')
        confirm_result = {'&lt;': '<'}
        self.assertEquals(translater.group, confirm_result)

    def test_translate(self):
        """置換群に登録した文字列を置換するメソッドのテスト"""
        from blogs.escape import Translater
        translater = Translater()

        test_text = '''以下がアンエスケープされることをテストします。
        &lt;br>
        '''
        translater.setgroup('&lt;', '<')
        result_text = translater.translate(test_text)
        confirm_text = test_text.replace('&lt;', '<')
        self.assertEquals(result_text, confirm_text)


class HtmlAccepterTest(TestCase):
    """アンエスケープしたいHtmlのテスト"""
    def test_accepts_no_text(self):
        """str型でない引数を渡した場合"""
        from blogs.escape import HtmlAccepter
        acceptation = HtmlAccepter()

        text = 100
        with self.assertRaises(ValueError) as error:
            acceptation.accepts(text)
        error_message = 'input string type'
        self.assertEquals(error.exception.args[0], error_message)

    def test_accepts_one_data(self):
        """1つの引数を渡した場合"""
        from blogs.escape import HtmlAccepter
        acceptation = HtmlAccepter()

        text = 'br'
        result = acceptation.accepts(text)
        confirm_result = {
            '&lt;br&gt;': '<br>',
            '&lt;/br&gt;': '</br>',
        }
        self.assertEquals(result, confirm_result)

    def test_accepts_list_data(self):
        """listの引数を渡した場合"""
        from blogs.escape import HtmlAccepter
        acceptation = HtmlAccepter()

        text = ['br', 'li', 'a']
        result = acceptation.accepts(text)
        confirm_result = {
            '&lt;br&gt;': '<br>',
            '&lt;/br&gt;': '</br>',
            '&lt;li&gt;': '<li>',
            '&lt;/li&gt;': '</li>',
            '&lt;a&gt;': '<a>',
            '&lt;/a&gt;': '</a>',
        }
        self.assertEquals(result, confirm_result)

    def test_accepts_args_data(self):
        """引数を可変長で渡した場合"""
        from blogs.escape import HtmlAccepter
        acceptation = HtmlAccepter()

        text = ['br', 'li', 'a']
        confirm_result = {
            '&lt;br&gt;': '<br>',
            '&lt;/br&gt;': '</br>',
            '&lt;li&gt;': '<li>',
            '&lt;/li&gt;': '</li>',
            '&lt;a&gt;': '<a>',
            '&lt;/a&gt;': '</a>',
        }
        result = acceptation.accepts(*text)
        self.assertEquals(result, confirm_result)

    def test_unescape_filter(self):
        """エスケープを無効にした文字列をアンエスケープするテスト"""
        from blogs.escape import HtmlAccepter
        from blogs.escape import escape_html
        acceptation = HtmlAccepter()

        test_text = '''これはテストになります。<br>
        以下の無害なhtmlはエスケープしません。
        <ul>
            <li>br</li>
            <li>ul</li>
            <li>li</li>
        </ul>
        以下のようなjavascriptにはエスケープしてもらいます。
        <script>alert('test xss')</script>
        '''

        # タグをエスケープする
        test_text = escape_html(test_text)

        # 無害なhtmlをアンエスケープする
        acceptation.accepts('br', 'ul', 'li')
        result = acceptation.unescape_html_filter(test_text)

        confirm_result = '''これはテストになります。<br>
        以下の無害なhtmlはエスケープしません。
        <ul>
            <li>br</li>
            <li>ul</li>
            <li>li</li>
        </ul>
        以下のようなjavascriptにはエスケープしてもらいます。
        &lt;script&gt;alert(&#39;test xss&#39;)&lt;/script&gt;
        '''

        self.assertEquals(result, confirm_result)

    def test_unescape_filter_with_qout(self):
        """トリプルクォートで囲まれた文以外で
        エスケープを無効にした文字列をアンエスケープするテスト
        """
        from blogs.escape import HtmlAccepter
        acceptation = HtmlAccepter()

        test_text = '''
        Here is Sentence1.&lt;br&gt;
        Not accepte escapeing block.
        But br will unescape.
        ```
            Here is Sentence2.
            In the quot block.&lt;br&gt;
            Accepted escaping block.
        ```
        Here is Sentence3.&lt;br&gt;
        &lt;li&gt; will escape.
        Not accepte escapeing block.
        But li will unescape.
        '''
        confirm_text = '''
        Here is Sentence1.<br>
        Not accepte escapeing block.
        But br will unescape.
        ```
            Here is Sentence2.
            In the quot block.&lt;br&gt;
            Accepted escaping block.
        ```
        Here is Sentence3.<br>
        <li> will escape.
        Not accepte escapeing block.
        But li will unescape.
        '''

        # 無害なhtmlをアンエスケープする
        acceptation.accepts('br', 'ul', 'li')
        result = acceptation.unescape_html_filter(test_text)

        self.assertEquals(result, confirm_text)


class EscapeHtmlTest(TestCase):
    """Htmlのタグなどをエスケープする関数のテスト"""
    def test_no_escape(self):
        """エスケープする文字がない場合のテスト"""
        from blogs.escape import escape_html

        test_text = '''エスケープする文字がない場合のテストです。'''
        result_text = escape_html(test_text)
        self.assertEquals(result_text, test_text)

    def test_one_escape(self):
        """エスケープする文字が1つある場合のテスト"""
        from blogs.escape import escape_html

        test_text = '''以下の文字のうちタグの左がエスケープされます。
        テスト <br
        test
        '''
        result_text = escape_html(test_text)
        confirm_text = '''以下の文字のうちタグの左がエスケープされます。
        テスト &lt;br
        test
        '''
        self.assertEquals(result_text, confirm_text)

    def test_some_escape(self):
        """エスケープする文字が2つ以上ある場合のテスト"""
        from blogs.escape import escape_html

        test_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        &これは最初にエスケープされます。
        テスト <br>
        "ダブルクォート"や
        'シングルクォート'もエスケープされます。
        <ul>
            <li>test1</li>
        </ul>
        &これは最初にエスケープされます。
        '''
        result_text = escape_html(test_text)
        confirm_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        &amp;これは最初にエスケープされます。
        テスト &lt;br&gt;
        &quot;ダブルクォート&quot;や
        &#39;シングルクォート&#39;もエスケープされます。
        &lt;ul&gt;
            &lt;li&gt;test1&lt;/li&gt;
        &lt;/ul&gt;
        &amp;これは最初にエスケープされます。
        '''
        self.assertEquals(result_text, confirm_text)


class EscapeHtmlFilterTest(TestCase):
    """対象のtextのHtml特殊文字をエスケープする関数のテスト"""
    def setUp(self):
        self.test_text = '''
        Here is Sentence1.<br>
        Not accepte escapeing block.
        ```
            Here is Sentence2.
            In the quot block.<br>
            Accepted escaping block.
        ```
        Here is Sentence3.<br>
        Not accepte escapeing block.
        '''
        self.confirm_text = '''
        Here is Sentence1.&lt;br&gt;
        Not accepte escapeing block.
        ```
            Here is Sentence2.
            In the quot block.<br>
            Accepted escaping block.
        ```
        Here is Sentence3.&lt;br&gt;
        Not accepte escapeing block.
        '''

    def test_without_escape(self):
        """エスケープするテキストがない場合のテスト"""
        from blogs.escape import escape_html_filter

        text = '''This is test.
        ```python
        This text is not escaped.
        ```
        '''
        result = escape_html_filter(text)
        self.assertEqual(result, text)

    def test_with_escape(self):
        """エスケープするテキストがある場合のテスト"""
        from blogs.escape import escape_html_filter

        result = escape_html_filter(self.test_text)
        self.assertEqual(result, self.confirm_text)


class EscapeMarkdownTest(TestCase):
    """markdown用のタグをエスケープする関数のテスト"""
    def test_no_escape(self):
        """エスケープする文字がない場合のテスト"""
        from blogs.escape import escape_markdown

        test_text = '''エスケープする文字がない場合のテストです。'''
        result_text = escape_markdown(test_text)
        self.assertEquals(result_text, test_text)

    def test_one_escape(self):
        """エスケープする文字が1つある場合のテスト"""
        from blogs.escape import escape_markdown

        test_text = '''以下の文字のうちタグの左がエスケープされます。
        テスト <br
        test
        '''
        result_text = escape_markdown(test_text)
        confirm_text = '''以下の文字のうちタグの左がエスケープされます。
        テスト &lt;br
        test
        '''
        self.assertEquals(result_text, confirm_text)

    def test_some_escape(self):
        """エスケープする文字が2つ以上ある場合のテスト"""
        from blogs.escape import escape_markdown

        test_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト <br>
        <ul>
            <li>test1</li>
        </ul>
        '''
        result_text = escape_markdown(test_text)
        confirm_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト &lt;br&gt;
        &lt;ul&gt;
            &lt;li&gt;test1&lt;/li&gt;
        &lt;/ul&gt;
        '''
        self.assertEquals(result_text, confirm_text)

    def test_with_accete_text(self):
        """エスケープしないタグを文字列で渡した場合のテスト"""
        from blogs.escape import escape_markdown
        test_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト <br>
        <ul>
            <li>test1</li>
        </ul>
        '''
        confirm_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト &lt;br&gt;
        <ul>
            &lt;li&gt;test1&lt;/li&gt;
        </ul>
        '''
        accept_texts = 'ul'
        result_text = escape_markdown(test_text, accept_texts)
        self.assertEquals(result_text, confirm_text)

    def test_with_accete_list(self):
        """エスケープしないタグをリストで渡した場合のテスト"""
        from blogs.escape import escape_markdown
        test_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト <br>
        <ul>
            <li>test1</li>
        </ul>
        '''
        confirm_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト <br>
        <ul>
            &lt;li&gt;test1&lt;/li&gt;
        </ul>
        '''
        accept_texts = ['br', 'ul']
        result_text = escape_markdown(test_text, accept_texts)
        self.assertEquals(result_text, confirm_text)

    def test_with_accete_args(self):
        """エスケープしないタグを可変長引数で渡した場合のテスト"""
        from blogs.escape import escape_markdown
        test_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト <br>
        <ul>
            <li>test1</li>
        </ul>
        '''
        confirm_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト <br>
        <ul>
            &lt;li&gt;test1&lt;/li&gt;
        </ul>
        '''
        accept_texts = ['br', 'ul']
        result_text = escape_markdown(test_text, *accept_texts)
        self.assertEquals(result_text, confirm_text)

    def test_with_quot_block(self):
        """トリプルクォートで囲まれた部分以外エスケープされることのテスト"""
        from blogs.escape import escape_markdown

        test_text = '''
        Here is Sentence1.<br>
        Not accepte escapeing block.
        But br is accepted.
        ```
            Here is Sentence2.
            In the quot block.<br>
            Accepted escaping block.
        ```
        Here is Sentence3.<br>
        <li> will escape.
        Not accepte escapeing block.
        '''
        confirm_text = '''
        Here is Sentence1.<br>
        Not accepte escapeing block.
        But br is accepted.
        ```
            Here is Sentence2.
            In the quot block.<br>
            Accepted escaping block.
        ```
        Here is Sentence3.<br>
        &lt;li&gt; will escape.
        Not accepte escapeing block.
        '''
        accept_texts = ['br']
        result_text = escape_markdown(test_text, *accept_texts)
        self.assertEquals(result_text, confirm_text)
