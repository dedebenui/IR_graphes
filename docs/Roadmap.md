# Distinct functionalities
- import raw data and convert it to a standard format
- perform transformations on the data
    - filtering
        - 
    - grouping
    - ...
- provide a preview of a plot
- export plots in png or pdfs
- be configurable

# TODO
- fix grouping by transformer
- create an actual testing data set
- create tests for each stage
- design output interface
- implement output interface
- implement exception hook
- write documentation for process description
- add secondary column for data import

- add config options to Transformers

# idées
afficher la date du jour
Titre descriptif
ajouter descriptif des périodes touchées (texte penché)

# Bugs
- ComboBox are created before the available values are available, thus it's impossible to create them with the value from the config already selected