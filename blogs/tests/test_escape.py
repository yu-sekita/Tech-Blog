from django.test import TestCase


class AccepterTest(TestCase):
    """アンエスケープしたい文字列のテスト"""
    def test_accept(self):
        """エスケープしない文字列を保存するメソッドのテスト"""
        from blogs.escape import Accepter
        accepter = Accepter()

        accepter.accept('&lt;', '<')
        confirm_result = {'&lt;': '<'}
        self.assertEquals(accepter.accepted_texts, confirm_result)

    def test_unescape(self):
        """エスケープ無効に登録した文字列をアンエスケープするメソッドのテスト"""
        from blogs.escape import Accepter
        accepter = Accepter()

        test_text = '''以下がアンエスケープされることをテストします。
        &lt;br>
        '''
        accepter.accept('&lt;', '<')
        result_text = accepter.unescape(test_text)
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


class UnescapeHtmlTest(TestCase):
    """無害なhtmlをアンエスケープする関数のテスト"""
    def setUp(self):
        self.test_text = '''以下のhtmlタグがアンエスケープされることをテストします。
        &lt;b&gt;, &lt;blockquote&gt;, &lt;code&gt;, &lt;em&gt;, &lt;h1&gt;,
        &lt;h2&gt;, &lt;h3&gt;, &lt;h4&gt;, &lt;h5&gt;, &lt;h6&gt;,
        &lt;li&gt;, &lt;ol&gt;, &lt;ol start="42"&gt;, &lt;p&gt;, &lt;pre&gt;,
        &lt;sub&gt;, &lt;sup&gt;, &lt;strong&gt;,
        &lt;strike&gt;, &lt;ul&gt;, &lt;br&gt;, &lt;hr&gt;

        '''

        self.confirm_text = '''以下のhtmlタグがアンエスケープされることをテストします。
        <b>, <blockquote>, <code>, <em>, <h1>,
        <h2>, <h3>, <h4>, <h5>, <h6>,
        <li>, <ol>, <ol start="42">, <p>, <pre>,
        <sub>, <sup>, <strong>,
        <strike>, <ul>, <br>, <hr>

        '''

    def test_unescape_html(self):
        """アンエスケープされることの確認"""
        from blogs.escape import unescape_html

        result_text = unescape_html(self.test_text)
        self.assertEquals(result_text, self.confirm_text)

    def test_escape_html(self):
        """scriptタグはエスケープされていることの確認"""
        from blogs.escape import unescape_html

        self.test_text += '''\n <script>\nalert('test xss')\n</script>'''
        self.confirm_text += '''\n <script>\nalert('test xss')\n</script>'''

        result_text = unescape_html(self.test_text)
        self.assertEquals(result_text, self.confirm_text)


class EscapeScript(TestCase):
    """scriptタグをエスケープする関数のテスト"""
    def setUp(self):
        self.test_text = '''以下のhtmlタグがアンエスケープされることをテストします。
        <b>, <blockquote>, <code>, <em>, <h1>,
        <h2>, <h3>, <h4>, <h5>, <h6>,
        <li>, <ol>, <ol start="42">, <p>, <pre>,
        <sub>, <sup>, <strong>,
        <strike>, <ul>, <br>, <hr>

        <script> alert('test xss') </script>

        '''

        self.confirm_text = '''以下のhtmlタグがアンエスケープされることをテストします。
        <b>, <blockquote>, <code>, <em>, <h1>,
        <h2>, <h3>, <h4>, <h5>, <h6>,
        <li>, <ol>, <ol start="42">, <p>, <pre>,
        <sub>, <sup>, <strong>,
        <strike>, <ul>, <br>, <hr>

        &lt;script&gt; alert('test xss') &lt;/script&gt;

        '''

    def test_escape_script(self):
        """scriptタグのみエスケープされるテスト"""
        from blogs.escape import escape_script

        result_text = escape_script(self.test_text)
        self.assertEquals(result_text, self.confirm_text)
