#!/bin/bash
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)/libs
python3 main.py
