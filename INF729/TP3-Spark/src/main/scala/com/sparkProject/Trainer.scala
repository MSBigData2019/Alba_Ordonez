package com.sparkProject

import org.apache.spark.{SparkConf}
import org.apache.spark.sql.{SparkSession}
import org.apache.spark.ml.feature.{RegexTokenizer, CountVectorizer, IDF, StopWordsRemover, StringIndexer, OneHotEncoder, VectorAssembler}
import org.apache.spark.ml.Pipeline
import org.apache.spark.ml.classification.LogisticRegression
import org.apache.spark.ml.tuning.{ParamGridBuilder, TrainValidationSplit}
import org.apache.spark.ml.evaluation.MulticlassClassificationEvaluator


object Trainer {

  def main(args: Array[String]): Unit = {

    val conf = new SparkConf().setAll(Map(
      "spark.scheduler.mode" -> "FIFO",
      "spark.speculation" -> "false",
      "spark.reducer.maxSizeInFlight" -> "48m",
      "spark.serializer" -> "org.apache.spark.serializer.KryoSerializer",
      "spark.kryoserializer.buffer.max" -> "1g",
      "spark.shuffle.file.buffer" -> "32k",
      "spark.default.parallelism" -> "12",
      "spark.sql.shuffle.partitions" -> "12",
      "spark.driver.maxResultSize" -> "2g"
    ))

    val spark = SparkSession
      .builder
      .config(conf)
      .appName("TP_spark")
      .getOrCreate()


    /*******************************************************************************
      *
      *       TP 3
      *
      *       - lire le fichier sauvegarder précédemment
      *       - construire les Stages du pipeline, puis les assembler
      *       - trouver les meilleurs hyperparamètres pour l'entraînement du pipeline avec une grid-search
      *       - Sauvegarder le pipeline entraîné
      *
      *       if problems with unimported modules => sbt plugins update
      *
      ********************************************************************************/

    /** 1. Charger le dataframe: prepared_trainingset (parquet) **/

    val dataDir = "/home/alba/KickStarter/TP_ParisTech_2018_2019_starter/TP_ParisTech_2017_2018_starter/data/"

    val df = spark.read.parquet(dataDir + "prepared_trainingset/")
    df.show(50)


    /** 2. Utiliser les données textuelles **/

    // 2.a -> Séparer les textes en mots
    val tokenizer = new RegexTokenizer()
      .setPattern("\\W+")
      .setGaps(true)
      .setInputCol("keywords")
      .setOutputCol("tokens")

    // 2.b -> Retirer les stop words
    val remover = new StopWordsRemover()
      //.setStopWords(stopwords)
      .setInputCol(tokenizer.getOutputCol)
      .setOutputCol("removed")

    // 2.c -> Partie TF de TF-IDF
    val vectorizer = new CountVectorizer()
      .setInputCol(remover.getOutputCol)
      .setOutputCol("vectorized")

    // 2.d -> Partie IDF de TF-IDF
    val idf = new IDF()
      .setInputCol(vectorizer.getOutputCol)
      .setOutputCol("tfidf")

    /** 3. Convertir les catégories en données numériques **/

    // 3.e -> Variable catégorielle "country2" convertie en numérique
    val indexer_country = new StringIndexer()
      .setInputCol("country2")
      .setOutputCol("country_indexed")

    // 3.f -> Variable catégorielle "currency2" convertie en numérique
    val indexer_currency = new StringIndexer()
      .setInputCol("currency2")
      .setOutputCol("currency_indexed")

    // 3.g -> Transformation des 2 variables précédentes en OneHotEncoder
    val encoder_country = new OneHotEncoder()
      .setInputCol("country_indexed")
      .setOutputCol("country_onehot")

    val encoder_currency = new OneHotEncoder()
      .setInputCol("currency_indexed")
      .setOutputCol("currency_onehot")

    /** Mettre les données sous une forme utilisable par Spark.ML **/

    // 4.h -> Assemblage des features
    val vecAssembler = new VectorAssembler()
      .setInputCols(Array("tfidf", "days_campaign", "hours_prepa", "goal", "country_onehot", "currency_onehot"))
      .setOutputCol("features")

    // 4.i -> Définition de la régression logistique
    val lr = new LogisticRegression()
      .setElasticNetParam(0.0)
      .setFitIntercept(true)
      .setFeaturesCol("features")
      .setLabelCol("final_status")
      .setStandardization(true)
      .setPredictionCol("predictions")
      .setRawPredictionCol("raw_predictions")
      .setThresholds(Array(0.7, 0.3))
      .setTol(1.0e-6)
      .setMaxIter(300)

    // 4.j -> Assemblage des stages précédents et création de la pipeline
    val stages = Array(tokenizer, remover, vectorizer, idf, indexer_country, indexer_currency, encoder_country, encoder_currency, vecAssembler, lr)

    val pipeline = new Pipeline().setStages(stages)


    /** 5. Entraînement et tuning du modèle **/

    // 5. k -> Séparation du dataset en training (90%) et test (10%)
    val Array(training, test) = df.randomSplit(Array[Double](0.9, 0.1), 1)

    // 5.l

    // Construction de la grille de recherche des hyper-paramètres du modèle
    val paramGrid = new ParamGridBuilder()
      .addGrid(lr.regParam, Array(10e-2, 10e-4, 10e-6, 10e-8))
      .addGrid(vectorizer.minDF, 55.0 to 95.0 by 20.0)
      .build()

    // Definition de la metric d'evaluation du modèle : F1-score
    val evaluator = new MulticlassClassificationEvaluator().setLabelCol("final_status").setPredictionCol("predictions").setMetricName("f1")

    // Réglage des hyper-paramètres avec TrainValidationSplit
    val trainValidationSplit = new TrainValidationSplit()
      .setEstimator(pipeline)
      .setEvaluator(evaluator)
      .setEstimatorParamMaps(paramGrid)
      .setTrainRatio(0.7)

    // Exécution de TrainValidationSplit sur le dataset training et choix automatique des meilleurs hyper-paramètres
    val model = trainValidationSplit.fit(training)

    // 5.m

    // Prédictions sur le test dataset stockées dans df_WithPredictions
    val df_WithPredictions = model.transform(test)
      .select("features", "final_status", "predictions")

    // Affichage du F1-score obtenu pour le test dataset (arrondi à 2 chiffres après la virgule)
    val F1Score = evaluator.evaluate(df_WithPredictions)

    println("F1-score obtained on test dataset: " + BigDecimal(F1Score).setScale(2, BigDecimal.RoundingMode.HALF_UP).toDouble)

    // 5.n

    // Vue d'emsemble des vrais/faux positifs et des vrais/faux négatifs
    df_WithPredictions.groupBy("final_status", "predictions").count().show()

    // Sauvegarde du modèle
    model.write.overwrite().save(dataDir + "/model")

  }
}