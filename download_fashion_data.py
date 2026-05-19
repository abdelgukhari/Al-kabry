import argparse
import os
import zipfile
from kaggle.api.kaggle_api_extended import KaggleApi

DATASET_SLUG = 'paramaggarwal/fashion-product-images-small'


def download_dataset(destination, force=False):
    os.makedirs(destination, exist_ok=True)

    api = KaggleApi()
    api.authenticate()

    zip_path = os.path.join(destination, 'fashion-product-images-small.zip')
    if os.path.exists(zip_path) and not force:
        print(f'Dataset zip already exists: {zip_path}')
    else:
        print(f'Downloading {DATASET_SLUG} to {destination}...')
        api.dataset_download_files(DATASET_SLUG, path=destination, unzip=False)
        print('Download complete.')

    if os.path.exists(zip_path):
        print('Extracting dataset...')
        with zipfile.ZipFile(zip_path, 'r') as archive:
            archive.extractall(destination)
        print('Extraction complete.')
    else:
        raise FileNotFoundError(f'Could not find downloaded dataset archive at {zip_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download Kaggle fashion-product-images-small dataset.')
    parser.add_argument('--destination', default='data/fashion-product-images-small',
                        help='Destination folder for the dataset download and extraction')
    parser.add_argument('--force', action='store_true', help='Force re-download even if files exist')
    args = parser.parse_args()

    download_dataset(args.destination, force=args.force)
    print('Dataset ready. Use styles.csv with manage.py import_fashion_data.')
