# EMS app

Le but de cette application est de créer des graphiques représentant l'évolution du COVID-19 dans les EMS du canton de Fribourg.

# Objectifs

- Prendre le relais des graphes de monitoring
- Être facile à utiliser et à configurer
    - Mémoire des derniers réglages
    - Simplement cliquer sur un bouton devrait suffir pour une utilisation normale quotidienne
    - Le dossier contenant les nouveaux graphiques s'ouvre à la fin du processus
    - Créer des graphiques personnalisés devrait être facile également
- Fonctionnalités essentielles
    - Accéder directement à EMIR afin d'avoir des données à jour et d'éviter les étapes intermédiaires
    - Pouvoir combiner districts / dates / institutions afin de :
        - Sommer ces composants sur un graphique (p. ex. total par district)
        - Filtrer (p. ex. créer un graphique uniquement pour une institution en particulier)
        - Distribuer (créer un graphique par district / institution / ...)
- Autres fonctionnalités désirées.
    - Personnalisation des noms de fichiers
    - Être flexible sur le look des graphiques
        - Pouvoir changer les couleurs / marges / tailles de police / ...
        - Options de combiner différentes données sur un même graphe, sur plusieurs graphe dans le même document ou dans plusieurs documents
    - Proposer différents formats d'images

# Scénarios
1. Utilisation quotidienne
    - Ouvrir l'application
    - Cliquer sur un bouton du genre "générer les graphes par défaut"
    - Une barre de progression apparaît pendant la génération des graphes
    - Une fois fini, un nouveau dossier contenant les derniers graphes s'ouvre
2. Cas particulier : un Ems, une période donnée
    - Ouvrir l'application
    - Choisir l'EMS
    - Choisir la date de début et de fin
    - Cliquer sur "Générer"
    - ...


# Interrogations

- est-ce qu'on va régulièrement leur demander leurs taux d'absentéisme ?
- est-ce que la définition de flambée risque de changer ?
- est-ce que le format de base de donnée risque de changer ?




