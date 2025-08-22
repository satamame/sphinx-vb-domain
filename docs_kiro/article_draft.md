# タイトル

Excel マクロのドキュメントを Sphinx で書く

# はじめに

業務で Excel マクロを開発していると、ドキュメント作成が課題になることがあります。  
設計書などのドキュメントが Excel で書かれているのをよく見ますが、私は Sphinx で書きたいです。

そこで、Visual Basic のコードから Sphinx のドキュメントを自動生成する Sphinx 拡張機能「[sphinx-vb-domain](https://github.com/satamame/sphinx-vb-domain)」を開発しました。

# Sphinx と autodoc について

[Sphinx](https://www.sphinx-doc.org/) は、Python プロジェクトのドキュメント作成でよく使われるツールです。reStructuredText や Markdown で書いたドキュメントを、HTML や PDF など様々な形式に変換できます。

特に便利なのが autodoc 機能です。これは、Python のソースコードから docstring を抽出して、自動的に API リファレンスを生成する機能です。例えば、以下のような Python コードがあるとします：

```python
def get_user_name(user_id: int) -> str:
    """ユーザー名を取得する関数

    Parameters
    ----------
    user_id : int
        ユーザー ID

    Returns
    -------
    str
        ユーザー名
    """
    # 実装
```

autodoc を使えば、この docstring から以下のような reStructuredText が自動生成されます：

```restructuredtext
.. py:function:: get_user_name(user_id: int) -> str

   ユーザー名を取得する関数

   :param user_id: ユーザー ID
   :type user_id: int
   :returns: ユーザー名
   :rtype: str
```

コードを変更したら Sphinx でドキュメントをビルドするだけで良いので、コードとドキュメントの乖離を防げるのが大きなメリットです。

# VB で autodoc したい

## 業務での状況
私は業務でマクロ有効 Excel ブックを開発しており、ドキュメントは Sphinx で作成しています。マクロにはドキュメントコメントを書いているので、これを活用してドキュメントを自動生成したいです。

```vb
''' <summary>
''' ユーザー名を取得する関数
''' </summary>
''' <param name="userId">ユーザー ID</param>
''' <returns>ユーザー名</returns>
Private Function getUserName(ByVal userId As Integer) As String
    ' 実装
End Function
```

マクロはバージョン管理のために .bas ファイルに抽出しているので、Sphinx から参照することは可能です。

```{note}
Excel ブックから VBA コードを .bas ファイルに抽出するには、[exxm](https://github.com/satamame/exxm) というツールを使用しています。これにより、マクロのバージョン管理と Sphinx での参照が可能になります。
```

## Sphinx は VB に対応していない

Sphinx は公式には Visual Basic に対応していません。標準で提供されているのは Python、C/C++、JavaScript などの言語ドメインのみです。

また、OSS として公開されている Sphinx 拡張機能を調べても、VB や VBA に対応したものは見つかりませんでした。そのため、VB のコードから autodoc のようなドキュメント自動生成を行うには、独自の拡張機能を開発する必要がありました。

# VB 対応に必要な要素

Sphinx で VB の autodoc を実現するには、以下の要素が必要でした：

## 1. VB 専用のディレクティブ
Sphinx の Python 用ディレクティブ（`.. py:function::` など）は VB の構文に対応していません。VB の関数シグネチャを適切に表現できるディレクティブが必要です。

## 2. VB ソースコードの解析機能
.bas ファイルから VB の関数定義やコメントを抽出し、Sphinx のドキュメント形式に変換する機能が必要です。

## 3. 日本語対応
VBA では日本語の関数名やコメントが使われることが多いため、適切な日本語対応が必要です。

## 4. クロスリファレンス機能
他のページから関数リファレンスへのリンクを作れるように、関数ごとにターゲットラベルを付与する必要があります。

# sphinx-vb-domain の機能

sphinx-vb-domain では、上記の「必要な要素」を機能として実装しました。

## 1. VB 専用のディレクティブ

VB の関数シグネチャを適切に表現できる `vb:function` ディレクティブを実装しました。以下のように記述して Sphinx でビルドできます：

```restructuredtext
.. vb:function:: Private Function getUserName(ByVal userId As Integer) As String
   :module: Sheet1

   ユーザー名を取得する関数

   :param userId: ユーザー ID
   :type userId: Integer
   :returns: ユーザー名
   :rtype: String
```

シグネチャ部分が VB の構文（`Private Function`、`ByVal`、`As String` など）に対応していることがこの機能のポイントです。

## 2. VB ソースコードの解析機能（Autodoc）

.bas ファイルから VB の関数定義やドキュメントコメントを自動抽出し、上記のディレクティブを自動生成する機能を実装しました。

```python
# conf.py
vb_autodoc_paths = [
    ('../../macros',  # VB ソースディレクトリ
     'modules',       # 生成する reST ファイル名
     'マクロ仕様',     # ページタイトル
     notes),          # 補足説明の辞書
]
```

この設定により、.bas ファイルから直接ドキュメントを自動生成できるようになりました。  
`notes` パラメータを使用すると、生成されるドキュメント内の特定の関数に補足説明を追加できます。

autodoc を有効にしてドキュメントを生成するには、以下のコマンドを実行します：

```bash
sphinx-build -D vb_autodoc=1 source build
```

## 3. 日本語対応

VBA でよく使われる日本語の関数名やコメントに対応しました。  
autodoc でクロスリファレンス用のターゲットラベルを生成する際は、無効な文字列を含む関数名はハッシュエンコードされます。

## 4. クロスリファレンス機能

他のページから関数リファレンスへのリンクを作るための、ターゲットラベルが生成されるようにしました。以下のように他のページから関数を参照できます：

**reStructuredText の場合:**
```restructuredtext
:vb:function:`Sheet1.getUserName`
```

**MyST (Markdown) の場合:**
```markdown
{vb:function}`Sheet1.getUserName`
```

複数のページに同じ名前の関数がある場合も、モジュール名やファイル名を含めたラベル生成により正確にリンクできます。

# 技術的なポイント

## アーキテクチャ
全体の処理フローは以下のようになります：
```
Excel ブック → exxm → .bas ファイル → sphinx-vb-domain → Sphinx ドキュメント
```

Excel ブックから exxm ツールで VBA コードを .bas ファイルに抽出し、バージョン管理する運用としておきます。  
sphinx-vb-domain がそれを解析して Sphinx ドキュメントを生成します。この自動化により、Excel ブックの更新からドキュメント生成まで一貫した処理が可能になります。

## 主要コンポーネント
sphinx-vb-domain は以下の主要コンポーネントで構成されています：

`VBDomain` は Sphinx のカスタムドメイン実装の中核で、Visual Basic 専用のディレクティブやロールを定義します。`VBFunction` は関数ディレクティブの具体的な処理を担当し、VBA の関数シグネチャを解析して Sphinx の標準的な関数ドキュメント形式に変換します。

`vb_autodoc` は .bas ファイルからドキュメントを自動生成する機能を提供し、`utils` はテンプレートからのノート生成など補助的な機能を担います。

## 技術的な工夫点

### 1. クロスリファレンス対応
複数のページに同じ名前の関数が存在する場合を考慮して、ターゲットラベルの一意性を確保できるよう、以下の設定オプションを提供しています：

```python
# conf.py
# 基本設定：モジュール名.関数名 の形式でラベル生成
vb_add_function_labels = True  # デフォルト: True

# ファイル名も含める：ファイル名-モジュール名.関数名 の形式
vb_add_docname_to_labels = True  # デフォルト: False

# ファイル名とモジュール名の区切り文字を変更
vb_docname_label_delimiter = '__'  # デフォルト: '-'

# 日本語など無効な文字を含む関数名をハッシュエンコード
vb_encode_invalid_labels = True  # デフォルト: True
```

これらの設定により、プロジェクトの構成に応じてターゲットラベルをカスタマイズでき、異なるファイルに同名の関数があっても正確にリンクできます。

### 2. notes による補足説明
autodoc で生成されるドキュメントに補足説明を追加するため、辞書形式の `notes` を使って、辞書のキーにより挿入箇所を示すようにしました：

```python
# conf.py
notes = {
    '__page__': 'このページはマクロの仕様書です。',           # ページ全体への説明
    'Sheet1': 'Sheet1 モジュールの関数一覧です。',           # モジュールへの説明
    'Sheet1.getUserName': 'この関数は重要な処理を行います。', # 特定の関数への説明
}

vb_autodoc_paths = [
    ('../../macros', 'modules', 'マクロ仕様', notes),
]
```

キーの命名規則により、ページ全体（`__page__`）、特定のモジュール（`モジュール名`）、特定の関数（`モジュール名.関数名`）のそれぞれに対して、適切な場所に説明を挿入できます。  
また、reStructuredText テンプレートから notes 辞書を生成する `notes_from_template()` 関数も提供しています：

```python
from sphinx_vb_domain.utils import notes_from_template

notes = notes_from_template('notes.rst')
vb_autodoc_paths = [
    ('../../macros', 'modules', 'マクロ仕様', notes),
]
```

# 開発で苦労した点

## Sphinx の内部仕様の理解
最も苦労したのは、Sphinx がどのようにディレクティブを分解してレンダリングしているのか、カスタム処理を入れるために何をオーバーライドすれば良いのかを理解することでした。

Sphinx の拡張機能開発に関する資料は限られており、特にカスタムドメインの作成については手探りで進める必要がありました。正直なところ、いまだに完全には理解できていない部分もあります。

## 複雑な要件への対応
実用的なツールにするためには、単純な機能実装だけでは不十分でした。複数のページに同じ名前の関数がある場合のターゲット ID の一意性確保など、意外と考えることが多かったです。  
また、多数の設定オプションを用意したことで、それらの相互作用を考慮する必要がありました。しかし、この柔軟性があることで、様々なプロジェクト構成に対応できるようになっています。

# 業務での活用効果
実際に導入した結果、以下の効果が得られました：

- **素早いリファレンス**: VBA エディタを開かずに、設計書だけでマクロの全体像を把握できるようになった。
- **情報共有の効率化**: チーム内でのマクロ仕様の共有が簡単になった。
- **新メンバー教育**: 各シートでどのマクロを使っているかが一目瞭然になり、教育時間が短縮された。
- **保守性向上**: コードとドキュメントの自動同期により、保守作業が不要になった。

# まとめ

sphinx-vb-domain の開発により、「Sphinx でドキュメントを書きたいけれど、業務では VBA を使わざるを得ない」という課題を解決できました。  
同じような境遇の方々の助けになればと思っています。

# リンク
- [sphinx-vb-domain (GitHub)](https://github.com/satamame/sphinx-vb-domain)
- [sphinx-vb-domain (PyPI)](https://pypi.org/project/sphinx-vb-domain/)
