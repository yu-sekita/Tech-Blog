from django.test import TestCase


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
            result = acceptation.accepts(text)
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
        from blogs.escape import escape_tag
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
        test_text = escape_tag(test_text)

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
        &lt;script&gt;alert('test xss')&lt;/script&gt;
        '''

        self.assertEquals(result, confirm_result)


class EscapeTagTest(TestCase):
    """タグをエスケープする関数のテスト"""
    def test_no_escape(self):
        """エスケープする文字がない場合のテスト"""
        from blogs.escape import escape_tag

        test_text = '''エスケープする文字がない場合のテストです。'''
        result_text = escape_tag(test_text)
        self.assertEquals(result_text, test_text)

    def test_one_escape(self):
        """エスケープする文字が1つある場合のテスト"""
        from blogs.escape import escape_tag

        test_text = '''以下の文字のうちタグの左がエスケープされます。
        テスト <br
        test
        '''
        result_text = escape_tag(test_text)
        confirm_text = '''以下の文字のうちタグの左がエスケープされます。
        テスト &lt;br
        test
        '''
        self.assertEquals(result_text, confirm_text)

    def test_some_escape(self):
        """エスケープする文字が2つ以上ある場合のテスト"""
        from blogs.escape import escape_tag

        test_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト <br>
        <ul>
            <li>test1</li>
        </ul>
        '''
        result_text = escape_tag(test_text)
        confirm_text = '''以下の文字のうちタグになるものを全てエスケープされます。
        テスト &lt;br&gt;
        &lt;ul&gt;
            &lt;li&gt;test1&lt;/li&gt;
        &lt;/ul&gt;
        '''
        self.assertEquals(result_text, confirm_text)

    def test_with_accete_text(self):
        """エスケープしないタグを文字列で渡した場合のテスト"""
        from blogs.escape import escape_tag
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
        result_text = escape_tag(test_text, accept_texts)
        self.assertEquals(result_text, confirm_text)

    def test_with_accete_list(self):
        """エスケープしないタグをリストで渡した場合のテスト"""
        from blogs.escape import escape_tag
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
        result_text = escape_tag(test_text, accept_texts)
        self.assertEquals(result_text, confirm_text)

    def test_with_accete_args(self):
        """エスケープしないタグを可変長引数で渡した場合のテスト"""
        from blogs.escape import escape_tag
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
        result_text = escape_tag(test_text, *accept_texts)
        self.assertEquals(result_text, confirm_text)
