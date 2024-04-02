#!/bin/zsh
python main.py batch-generation \
  --num-chapters 3 \
  --min-num-choices 2 \
  --max-num-choices 3 \
  --min-num-choices-opportunity 1 \
  --max-num-choices-opportunity 2 \
  --enable-image-generation
  --themes "adventure"
  --themes "high-fantasy"
  --themes "science fiction"
  --n-stories 50