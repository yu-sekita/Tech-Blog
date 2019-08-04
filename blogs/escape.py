import re
from collections import deque


class Phrase:
    """語句を表す

    Attributes:
        is_accepted: エスケープを許容するかどうか(bool)
        text: 語句本体(str)
    """
    def __init__(self, text=''):
        self.is_accepted = False
        self.text = text


class Sentence:
    """文を表す

    Phraseの集まり
    """
    def __init__(self):
        self._phrases = deque()

    @property
    def phrases(self):
        return self._phrases

    def set_phrase(self, phrase):
        if isinstance(phrase, str):
            _phrase = Phrase(phrase)
        elif isinstance(phrase, Phrase):
            _phrase = phrase
        else:
            raise ValueError('phrase must be str or Phrase instance')
        self._phrases.append(_phrase)


def create_sentence(text):
    """textからphraseで区切ったsentenceを作る

    ```で括られている文とそれ以外の文を作成
    """
    sentence = Sentence()
    # phraseは0から
    phrase_count = 0
    current_i = 0

    result_iter = re.finditer('```', text)

    # phraseの間に```を入れるために準備
    quot_phrase = Phrase('```')
    quot_phrase.is_accepted = True
    for result in result_iter:
        result_start_i, result_end_i = result.span()

        phrase = Phrase(text[current_i:result_start_i])
        if phrase_count % 2 == 0:
            # 偶数の場合エスケープ対象
            phrase.is_accepted = False
        else:
            # 奇数の場合エスケープ対象外
            phrase.is_accepted = True
        sentence.set_phrase(phrase)

        phrase_count += 1
        current_i = result_end_i

        # Phraseの間に```を入れる
        sentence.set_phrase(quot_phrase)

    end_phrase = Phrase(text[current_i:])
    end_phrase.is_accepted = False
    sentence.set_phrase(end_phrase)

    return sentence


def replace_trans(text, d):
    """replaceを使って変換を行う関数"""
    for k, v in d.items():
        text = text.replace(k, v)
    return text


def str_trans(text, d):
    """str.translateを使って変換を行う関数

    引数のdのkeyは必ず1文字の場合のみ使える
      ex) d = { '<': '&lt;', '>': '&gt;'}
    """
    if len([k for k in d.keys() if len(k) > 1]) > 0:
        raise ValueError('key mast be one size')

    return text.translate(str.maketrans(d))


class Translater:
    """文字の置換を行うクラス

    Attributes:
        permutation_group: 置換前と置換後を保存するためのdict型変数

    Methods:
        group: permutation_groupを返す
        setgroup: permutation_groupに保存
        translate: permutation_groupに保存されている文字で変換
    """
    def __init__(self):
        """Constructor.置換前と置換後を保存するためのdictを作成

        permutation_group: 置換前がkeyで、置換後がvalue
                 ex) permutation_group = { '&lt;': '<' }
        """
        self._translate = replace_trans
        self._permutation_group = {}

    @property
    def group(self):
        return self._permutation_group

    def setgroup(self, key, value):
        """置換前と置換後を保存する"""
        self._permutation_group.setdefault(key, value)

    def translate(self, text):
        """置換を行う"""
        escaped_text = self._translate(text, self._permutation_group)
        return escaped_text


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

    def unescape_html_filter(self, text):
        """許容されたhtml特殊文字はアンエスケープする

        ```で囲まれたブロックはエスケープ対象外

        Arg:
            text: アンエスケープしてほしい文字列(str)
        Return:
            unescaped_text: ```で囲まれた文以外アンエスケープされたtext(str)
        """
        sentence = create_sentence(text)

        unescaped_text = ''
        for phrase in sentence.phrases:
            if phrase.is_accepted:
                unescaped_text += phrase.text
            else:
                unescaped_text += self.translate(phrase.text)

        return unescaped_text


def escape_html(text):
    """Htmlのタグなどをエスケープする"""
    d = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        '\'': '&#39;'
    }
    return str_trans(text, d)


def escape_html_filter(text):
    """対象のtextのHtml特殊文字をエスケープする

    ```で囲まれたブロックはエスケープ対象外

    Arg:
        text: エスケープしてほしい文字列(str)
    Return:
        escaped_text: ```で囲まれた文以外エスケープされたtext(str)
    """
    sentence = create_sentence(text)

    escaped_text = ''
    for phrase in sentence.phrases:
        if phrase.is_accepted:
            escaped_text += phrase.text
        else:
            escaped_text += escape_html(phrase.text)
    return escaped_text


def _create_escape_filters(*accept_texts):
    """フィルターを作成

    エスケープやアンエスケープ処理を行う関数のリストを返す
    """
    # Html特殊文字をエスケープするフィルター
    yield escape_html_filter

    # 許容されたHtmlタグはアンエスケープするフィルター
    if accept_texts:
        accepter = HtmlAccepter()
        accepter.accepts(*accept_texts)
        yield accepter.unescape_html_filter


def escape_markdown(text, *accept_texts):
    """markdown用のタグをエスケープする関数

    エスケープしないタグがあれば無効とする

    Args:
        text: エスケープ対象文字列
        accept_texts: エスケープしないタグ
    """
    filters = _create_escape_filters(*accept_texts)
    for filter in filters:
        text = filter(text)
    return text
