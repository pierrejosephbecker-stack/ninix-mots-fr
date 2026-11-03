# ninix-mots-fr

Liste de mots français utilisée par le jeu « Course aux mots » de l'app Ninix (version de liste `fr-gl7.7-1`).

- **Fichier** : [`Ninix/Resources/Games/mots-fr.txt`](Ninix/Resources/Games/mots-fr.txt)
- **Contenu** : 161 978 mots de 3 à 9 lettres
- **Format** :
  - majuscules A à Z, sans accent ;
  - un mot par ligne, `\n` après chaque mot ;
  - trié par octets ;
  - UTF-8 sans BOM.
- **Empreinte SHA-256** : `fcc692540f149610a1ac4088c5c54680592ba3b143402da325da4afd886afc4d`

## Source

« Lexique des formes fléchies du français », Grammalecte / Dicollecte, version 7.7 (https://grammalecte.net), sous licence Mozilla Public License 2.0.

Fichier d'origine : https://www.grammalecte.net/dic/lexique-grammalecte-fr-v7.7.zip. Le texte qu'il contient (`lexique-grammalecte-fr-v7.7.txt`) a pour SHA-256 `dc1fa3740e6353bccdcb435ea8f1c8a65287726026abd53dd232d5d494548eff`.

## Modifications

La liste est fabriquée par [`tools/build_word_list.py`](tools/build_word_list.py), qui :

1. retire les noms propres, prénoms et patronymes, les sigles, symboles et unités, et les formes marquées `cc` ou `abty` ;
2. retire les formes qui commencent par une majuscule ou contiennent autre chose qu'une lettre ;
3. remplace Œ par OE et Æ par AE, enlève les accents et la cédille, puis met tout en majuscules ;
4. garde les mots de 3 à 9 lettres, sans doublon ;
5. retire 129 mots d'une liste noire relue à la main, [`tools/word_list_blacklist.txt`](tools/word_list_blacklist.txt) : sigles, onomatopées répétitives, noms de lettres grecques, préfixes et éléments étrangers de locutions.

Pour refabriquer ou vérifier la liste (Python 3.9 ou plus, sans dépendance) :

```sh
python3 tools/build_word_list.py --check
```

## Licence

Mozilla Public License 2.0 (voir [`LICENSE`](LICENSE)). L'avis de licence de la liste est dans [`Ninix/Resources/Games/mots-fr-LICENCE.txt`](Ninix/Resources/Games/mots-fr-LICENCE.txt).
