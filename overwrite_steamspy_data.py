import shutil

import steamspypi

IMPORTED_DATA_FNAME = "steamspy.json"


def main():
    dst = steamspypi.get_data_folder() + steamspypi.get_cached_database_filename()
    shutil.copyfile(IMPORTED_DATA_FNAME, dst)


if __name__ == "__main__":
    main()
