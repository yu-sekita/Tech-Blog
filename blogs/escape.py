import re
from collections import deque


class Phrase:
    """語句を表す。

    Attributes:
        is_accepted (bool): エスケープを許容するかどうか。
        text (str): 語句本体。
    """
    def __init__(self, text=''):
        self.is_accepted = False
        self.text = text


class Sentence:
    """文を表す。

    Attributes:
        _phrases (deque): Phraseのリスト。
    """
    def __init__(self):
        self._phrases = deque()

    @property
    def phrases(self):
        return self._phrases

    def set_phrase(self, phrase):
        if isinstance(phrase, str):
            self._phrases.append(Phrase(phrase))
        elif isinstance(phrase, Phrase):
            self._phrases.append(phrase)
        else:
            raise ValueError('phrase must be str or Phrase instance')


def create_sentence(text):
    """textからphraseで区切ったsentenceを作る。

    Args:
        text (str): senetence作成前の文字列。

    Returns:
        Sentence: Phraseのリストを保持。

    Examples:
        ```で括られている文とそれ以外の文を作成
        >>> text = '''
        これは文です。
        ```
        ここはエスケープ対象外の文です。
        ```
        ここはエスケープ対象の文です。
        '''
        >>> create_sentence(text)
        Sentence(
            Phrase('これは文です。\\n'),
            Phrase('```\\nここはエスケープ対象外の文です。```\\n'),
            Phrase('ここはエスケープ対象の文です。\\n')
        )
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
    """replaceを使って変換を行う。

    Args:
        text (str): 変換対象文字列。
        d (dict): 変換する文字を定義。

    Returns:
        str: 変換後の文字列。

    Examples:
        >>> text = 'これは<br>エスケープされます。'
        >>> d = {'<': '&lt;', '>': '&gt;'}
        >>> str_trans(text, d)
        'これは&lt;br&gt;エスケープされます。'
    """
    for k, v in d.items():
        text = text.replace(k, v)
    return text


def str_trans(text, d):
    """str.translateを使って変換を行う。

    Args:
        text (str): 変換対象文字列。
        d (dict): 変換する文字を定義。

    Returns:
        str: 変換後の文字列。

    Raises:
        ValueError: dに2以上のサイズのkeyを含む場合。
    """
    one_over_size_in_keys = [k for k in d.keys() if len(k) > 1]
    if len(one_over_size_in_keys) > 0:
        raise ValueError('key mast be one size')

    return text.translate(str.maketrans(d))


class Translater:
    """文字の置換を行う。

    Attributes:
        translate (function): replaceを使って変換する関数。
        permutation_group (dict): 置換前と置換後を定義したグループを保持。

    Methods:
        group: permutation_groupを返す。
        setgroup: permutation_groupに保存。
        translate: permutation_groupに保存されている文字で変換。
    """
    def __init__(self):
        self._translate = replace_trans
        self._permutation_group = {}

    @property
    def group(self):
        return self._permutation_group

    def setgroup(self, key, value):
        """置換前と置換後を保存する。"""
        self._permutation_group.setdefault(key, value)

    def translate(self, text):
        """置換を行う。"""
        escaped_text = self._translate(text, self._permutation_group)
        return escaped_text


class HtmlAccepter(Translater):
    """HTMLタグのアンエスケープを行う。"""
    def __init__(self):
        super().__init__()

    def accepts(self, *args):
        """エスケープを無効したいタグを登録。

        Args:
            args (str, list or tuple): 受け取った引数の数だけタグを生成し、
                                       permutation_groupに保存する。
        """
        accept_texts = self._create_accept_texts(args)
        for accept_text in accept_texts:
            # 開始タグを作成し登録する
            escaped_start_tag = self._create_escaped_tag(accept_text)
            unescaped_start_tag = self._create_tag(accept_text)
            self.setgroup(escaped_start_tag, unescaped_start_tag)
            # 終了タグを作成し登録する
            escaped_end_tag = self._create_escaped_tag('/' + accept_text)
            unescaped_end_tag = self._create_tag('/' + accept_text)
            self.setgroup(escaped_end_tag, unescaped_end_tag)
        return self._permutation_group

    def _create_accept_texts(self, args):
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
        return accept_texts

    def _create_tag(self, tag_name):
        return '<' + tag_name + '>'

    def _create_escaped_tag(self, tag_name):
        return '&lt;' + tag_name + '&gt;'

    def unescape_html_filter(self, text):
        """許容されたhtml特殊文字をアンエスケープする。

        ```で囲まれたブロックはエスケープ対象外

        Args:
            text (str): アンエスケープしてほしい文字列

        Returns:
            str: ```で囲まれた文以外アンエスケープした文字列。
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
    """Htmlのタグなどをエスケープする。

    '&'は初めにエスケープする。
    エスケープ対象文字は全てサイズが1なので、
    str_trans関数を使う。

    Args:
        text (str): エスケープ対象文字列。

    Returns:
        str: エスケープ後文字列。
    """
    d = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        '\'': '&#39;'
    }
    return str_trans(text, d)


def escape_html_filter(text):
    """Html特殊文字をエスケープする。

    ```で囲まれたブロックはエスケープ対象外。

    Args:
        text (str): エスケープしてほしい文字列。

    Returns:
        str: ```で囲まれた文以外エスケープした文字列。
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
    """フィルターを作成。

    エスケープやアンエスケープ処理を行う関数のリストを返す。

    Args:
        accepts_texts (str, list or tuple): エスケープ対象外文字列。

    Yields:
        function: escape_html_filterとunescape_html_filter。
    """
    # Html特殊文字をエスケープするフィルター
    yield escape_html_filter

    # 許容されたHtmlタグはアンエスケープするフィルター
    if accept_texts:
        accepter = HtmlAccepter()
        accepter.accepts(*accept_texts)
        yield accepter.unescape_html_filter


def escape_markdown(text, *accept_texts):
    """markdown用のタグをエスケープ。

    エスケープしないタグがあれば無効とする。

    Args:
        text (str): エスケープ対象文字列。
        accept_texts (str, list or tuple): エスケープしないタグ。

    Returns:
        str: エスケープ後文字列。
    """
    filters = _create_escape_filters(*accept_texts)
    for filter in filters:
        text = filter(text)
    return text
