#!/bin/bash

# Array of DOIs
dois=(
    "10.1002/ajmg.a.61316"
    "10.1002/ajmg.a.62965"
    "10.1002/ajmg.a.32596"
    "10.1002/ajmg.a.32612"
    "10.1002/ajmg.a.32597"
    "10.1002/ajmg.a.32602"
    "10.1002/ajmg.a.32600"
)

# Download each PDF
for doi in "${dois[@]}"; do
    filename=$(echo $doi | sed 's/\//_/g').pdf
    url="https://onlinelibrary.wiley.com/doi/pdfdirect/${doi}"
    echo "Downloading: $url"
    curl -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
         -o "$filename" "$url"
    sleep 2
done
