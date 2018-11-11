
Comme demandé, vous trouverez dans ce dossier tout ce qui est nécéssaire pour que vous puissiez compiler le code, à savoir:
   - Fichier build.sbt
   - Dossier src
   - Dossier project/plugins.sbt
   - Fichier build_and_submit.sh
   
Tout ce que j'ai codé se trouve dans l'objet Trainer (se trouvant dans: src/main/scala/com/sparkProject/). 
Comme vous avez déjà les données nécessaires à l'exécution du code, je n'ai pas jugé utile de les inclure dans ce répertoire. Afin que le code puisse tourner, veuillez prendre en compte qu'il faudra changer le path des données à traiter dans la partie du code: ** 1. Charger le dataframe: prepared_trainingset (parquet) **/. 

Je n'ai testé que la régression logistique sur les données de départ.
La précision du modèle a été mesurée avec le F1-score dont la valeur dépend du seed inital utilisé pour séparer les données 
d'entraînement (train) et de test.

Voici ci-dessous, une vue d'ensemble des vrais/faux positifs et des vrais/faux négatifs finalement obtenus avec un seed égal à 1:
------------+-----------+-----+                                                
|final_status|predictions|count|
+------------+-----------+-----+
|           1|        0.0|  988|
|           0|        1.0| 3406|
|           1|        1.0| 2406|
|           0|        0.0| 3943|
+------------+-----------+-----+

Le F1 score associé est de 0.60 (arrondi à 2 chiffres après la virgule).
