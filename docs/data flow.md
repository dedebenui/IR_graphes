
# General
    1. An Importer object reads the FinalData and outputs a RowData obj
    2. A Entries object is created from the RowData
    3. For each Process, we get a DataSet
    3. A Plotter takes a DataSet and plots it

# Process
    1. Receives one Entries obj
    2. Applies a filter to it -> one Entreis obj
    3. Applies a Splitter to it -> list of Entries obj
    4. Applies the same set of Rules to each Entries obj -> list of FinalData
    5. Applies the Grouper -> list of DataSet

# Filter
    1. Receives one Entries obj
    2. Outputs one Entries obj

# Splitter
    1. Receives one Entries obj
    2. Outputs a list of uniquely identified Entries obj

# Transformer
    1. Receives one Entries obj
    2. Computes one FinalData obj
    3. Outputs one FinalData obj identified by both the Splitter and the Transformer id

# Grouper
    1. Receives a list of FinalData
    2. Groups it into a list of DataSet based on Splitter id, Transformer id and other criteria
    3. Names each groups
    4. Outputs them as a list of DataSet
