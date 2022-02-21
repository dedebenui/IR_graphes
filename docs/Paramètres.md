# Comment entrer des paramètres

Ce fichier est au format Toml : https://fr.wikipedia.org/wiki/TOML

Ne spécifier qu'un seul paramètre par ligne. Chaque paramètre est décrit ci-dessous avec le format `nom : type`. Pour spécifier un paramètre, il faut écrire son nom suivit d'un ` = ` suivi de la valeur désirée.

Si le type est `str`, ça veut dire que le paramètre est un bout de texte et doit être écrit entre guillemets doubles. Exemple pour le paramètre `col_date_start : str` 
```
col_date_start = "Date de test"
```

Si le type est `list[_type_]`, cela veut dire que la valeur du paramètre est une liste de valeurs de type `_type_` écrites à l'intérieur de crochets `[ ]` et séparées par des virgules.
Exemple pour le paramètre `date_formats : list[str]`
```
date_formats = ["%x", "%d.%m.%Y", "%d/%m/%Y"]
```

# data
db_path : str
    chemin vers la source de données (fichier .accdb, .xlsx, ...)

table_name : str
    nom de la table (Microsoft Access) ou du tableau (Excel)

excel_start_year : 1900 ou 1904
    date zéro selon Excel. L'option se trouve dans options -> options avancées -> Lors du calcul de ce classeur -> Utiliser le calendrier depuis 1904. Si cette case est cochée pour le fichier désiré, alors, la valeur de ce paramètre doit être 1904, sinon elle doit être 1900.

col_date_start : str
    nom de la colonne contenant la date de début

col_date_end : str
    nom de la colonne contenant la date de fin

col_role : str
    nom de la colonne contenant le role de la personne

col_institution : str
    nom de la colonne contenant le nom de l'institution

col_location : str
    nom de la colonne contenant la localité de l'institution

date_formats : list[str]
    formats de dates à essayer si jamais les données ne sont pas déjà des dates. Les formats disponibles se trouvent sur https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    Par exemple. "%d.%m.%Y" veut dire que programme va essayer d'interpréter le texte "02.09.2021" comme "2 septembre 2021". 