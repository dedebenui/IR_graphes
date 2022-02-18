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

# Todo in order
- [x] finish excel importer
- [x] show message when no available table
- [x] redo access importer to cache stuff like in excel
- [x] implement basic logging
- [] define a plotter abstract class
- [] define a data container system (one set vs many, ...)
- [] define an interface to couple each data set with a plotter
- [] design a configuration system to help implement concrete plotter classes
- [] build the main interface with no functionnality first 
- [] create preview widget


# Bugs
- ComboBox are created before the available values are available, thus it's impossible to create them with the value from the config already selected