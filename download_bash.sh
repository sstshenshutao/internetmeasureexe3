#!/bin/bash
echo "Downloading the data toplist_1m"
# download the dataset
mkdir -p toplist_1m
python downloader.py --url="https://tranco-list.s3.amazonaws.com/tranco_JKYY-1m.csv.zip" --dist_dir="./toplist_1m"
python unzip.py --filename="tranco_JKYY-1m.csv.zip" --dir="./toplist_1m"

# download bgpdata
python downloader.py --url="http://archive.routeviews.org/route-views.amsix/bgpdata/2020.12/RIBS/rib.20201215.1200.bz2" --dist_dir="./as_csv"
