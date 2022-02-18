# Main elements (non exhaustive)

## Internal
- Config
    - Reads the last config
    - Provides an interface for temporary config changes with the ability to commit them
    - Logically structured (data importation, data transformation, plot options, ...)
- Importer
    - Opens the data base
    - Reads the data
    - Converts it into RawData
- Entries
    - Initialized from RawData
    - Parses the data if necessary (for example dates) and creates a list of Entry obj
    - Guaranties completeness of data
    - Provides a list of unique values for some/all columns
- Process
    - Is made up of :
        - Filter
        - Splitter
        - List of Rules
        - Grouper
    - Takes care of the entire transformation of the data
- Filter
- Splitter
- Rule


## GUI