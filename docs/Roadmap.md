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
- Fix bug below. Perhaps it requires a new structure for the import window.
- implement a lot of fail-safes:
    - detect problem when choosing columns
        - column doesn't contain correct datatype
    - add warnings for empty data after filtering

- add config options to Transformers
- add flexibility to instit_type filtering
- revamp process description syntax



# Bugs
- ComboBox are created before the available values are available, thus it's impossible to create them with the value from the config already selected