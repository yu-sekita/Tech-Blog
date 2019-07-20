

class Translater:
    """文字の置換を行うクラス

    Attributes:
        permutation_group: 置換前と置換後を保存するためのdict型変数

    Methods:
        group: permutation_groupを返す
        setgroup: permutation_groupに保存
        translate: permutation_groupに保存されている文字を変換
    """
    def __init__(self):
        """Constructor.置換前と置換後を保存するためのdictを作成

        permutation_group: 置換前がkeyで、置換後がvalue
                 ex) permutation_group = { '&lt;': '<' }
        """
        self._permutation_group = {}

    @property
    def group(self):
        return self._permutation_group

    def setgroup(self, key, value):
        """置換前と置換後を保存する"""
        self._permutation_group.setdefault(key, value)

    def translate(self, text):
        """置換を行う"""
        for escaped_text, accepted_text in self._permutation_group.items():
            text = text.replace(escaped_text, accepted_text)
        return text


class HtmlAccepter(Translater):
    """HTMLタグのアンエスケープを行うクラス"""
    def __init__(self):
        super().__init__()

    def accepts(self, *args):
        """エスケープを無効したいタグを登録

        引数にstr, list, tupleを受け取って、
        その数だけタグを生成し、permutation_groupに保存する
        """
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
            self.setgroup(escaped_start_tag, unescaped_start_tag)
            # 終了タグを作成し登録する
            escaped_end_tag = '&lt;' + '/' + accept_text + '&gt;'
            unescaped_end_tag = '<' + '/' + accept_text + '>'
            self.setgroup(escaped_end_tag, unescaped_end_tag)

        return self._permutation_group

    def unescape_html_filter(self, escaped_text):
        """エスケープを無効にしたhtmlタグをアンエスケープする"""
        unescaped_text = self.translate(escaped_text)
        return unescaped_text


def escape_tag(un_escaped_text, *accept_texts):
    """タグをエスケープする関数

    エスケープしないタグがあれば無効とする

    Args:
        accept_texts: エスケープしないタグ
    """
    escaped_text = un_escaped_text.translate(str.maketrans({
        '<': '&lt;',
        '>': '&gt;'
    }))
    if accept_texts:
        accepter = HtmlAccepter()
        accepter.accepts(*accept_texts)
        escaped_text = accepter.unescape_html_filter(escaped_text)
    return escaped_text
