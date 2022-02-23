from matplotlib import pyplot as plt
from emsapp.config import Config, DataConfig
from emsapp.data.loading import DataLoaderFactory, load_data
from emsapp.data.process import current_processes
from emsapp.plotting.plotter import Plotter


Config().data = DataConfig(
    **{
        "db_path": R"Z:\04_MONITORING_EMS\EMIR Synthèse\220131_EMS_Synthèse.xlsx",
        "table_name": "ems",
        "excel_start_year": 1900,
        "col_date_start": "Date_debut",
        "col_date_end": "Date_fin",
        "col_role": "role",
        "col_institution": "instit_nom",
        "col_institution_type": "instit_type",
        "col_location": "instit_loc",
        "date_formats": ["%x", "%d.%m.%Y", "%d/%m/%Y"],
    }
)


def main():
    loader = DataLoaderFactory.create(Config().data.db_path)
    entries = load_data(loader)
    for name, process in current_processes().items():
        print(name)
        processed = process(entries)
        for dataset in processed[:3]:
            print(dataset.title)
            plotter = Plotter()
            plotter.plot(dataset)
            plt.show()
            plt.close()


if __name__ == "__main__":
    main()
