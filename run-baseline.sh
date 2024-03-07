#!/bin/zsh
python generate.py \
  --approach baseline \
  --num-chapters 1 \
  --min-num-choices 3 \
  --max-num-choices 3 \
  --min-num-choices-opportunity 2 \
  --max-num-choices-opportunity 2 \
  --enable-image-generation \
  --existing-plot outputs/proposed/1aa8a898-dbcb-11ee-a544-baf3908e4dbe/plot.json