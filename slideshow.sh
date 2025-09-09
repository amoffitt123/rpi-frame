#!/bin/bash

export DISPLAY=:0

if ! command -v mogrify &>/dev/null; then
	echo "ImageMagick not found."
	 exit 1
fi

UPLOAD_DIR="/home/anderson/picture-frame/uploads"
PROCESSED_DIR="/home/anderson/picture-frame/processed"

mkdir -p "$PROCESSED_DIR"

cd "$UPLOAD_DIR" || exit

for img in *.jpg *.jpeg *.png *.JPG *.JPEG *.PNG; do
	if [[ -f "$img"  ]]; then
		if [[ ! -f "$PROCESSED_DIR/$img" ]]; then
			echo "processing $img..."
			mogrify -auto-orient -rotate 90 "$img" 
			mv "$img" "$PROCESSED_DIR/$img"
		else
			echo "Skipping already processed"
		fi
	fi
done


feh --fullscreen --slideshow-delay 5 --hide-pointer --randomize "$PROCESSED_DIR"

sleep 3

export DISPLAY=:0
conky -c ~/.conkyrc &
