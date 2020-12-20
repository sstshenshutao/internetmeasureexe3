#!/bin/bash
echo "Downloading the data toplist_1m"
# download the dataset
mkdir -p toplist_1m
python downloader.py --url="https://tranco-list.s3.amazonaws.com/tranco_JKYY-1m.csv.zip" --dist_dir="./toplist_1m"
python unzip.py --filename="tranco_JKYY-1m.csv.zip" --dir="./toplist_1m"
