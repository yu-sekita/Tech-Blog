

class Acceptation:
    """エスケープしない文字列"""
    def __init__(self):
        """Constructor.エスケープしない文字列を保存する辞書を作成

        accepts: エスケープされた文字がkeyで、アンエスケープしたい文字がvalue
            ex) accepts = { '&lt;': '<' }
        """
        self._accepts = {}

    @property
    def accepts(self):
        return self._accepts

    def accept(self, key, value):
        """エスケープしない文字列を保存する"""
        self._accepts.setdefault(key, value)

    def unescape(self, text):
        """エスケープ無効に登録した文字列をアンエスケープする"""
        for escaped_text in self._accepts:
            text = text.replace(escaped_text, self._accepts[escaped_text])
        return text


class AcceptationHtml(Acceptation):
    """エスケープしないHtml"""
    def __init__(self):
        super().__init__()

    def accepts(self, *args):
        """エスケープを無効したいタグを登録"""
        if not isinstance(args, tuple):
            raise ValueError('input string type')

        accept_texts = []
        if len(args) > 1:
            # 可変長引数で渡された場合
            accept_texts += args
        elif isinstance(args[0], str):
            # 引数が1つの場合
            accept_texts.append(args[0])
        elif isinstance(args[0], list):
            # 引数がリストの場合
            accept_texts += args[0]
        else:
            raise ValueError('input string type')

        for accept_text in accept_texts:
            # 開始タグを作成し登録する
            escaped_start_tag = '&lt;' + accept_text + '&gt;'
            unescaped_start_tag = '<' + accept_text + '>'
            self.accept(escaped_start_tag, unescaped_start_tag)
            # 終了タグを作成し登録する
            escaped_end_tag = '&lt;' + '/' + accept_text + '&gt;'
            unescaped_end_tag = '<' + '/' + accept_text + '>'
            self.accept(escaped_end_tag, unescaped_end_tag)

        return self._accepts

    def unescape_html_filter(self, escaped_text):
        """エスケープを無効にしたhtmlタグをアンエスケープする"""
        unescaped_text = self.unescape(escaped_text)
        return unescaped_text


def unescape_html(escaped_text):
    """無害なhtmlをアンエスケープする"""
    acceptation = AcceptationHtml()
    accept_texts = [
        'b', 'blockquote', 'code', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'li', 'ol', 'ol start="42"', 'p', 'pre', 'sub', 'sup', 'strong',
        'strike', 'ul', 'br', 'hr',
    ]

    acceptation.accepts(accept_texts)
    unescaped_text = acceptation.unescape_html_filter(escaped_text)
    return unescaped_text


def escape_tag(un_escaped_text):
    """タグをエスケープ"""
    un_escaped_text = un_escaped_text.replace('<', '&lt;')
    escaped_text = un_escaped_text.replace('>', '&gt;')
    return escaped_text


def escape_script(text):
    """scriptタグをエスケープ"""
    escaped_text = escape_tag(text)
    unescaped_text = unescape_html(escaped_text)
    return unescaped_text
