#!/bin/bash
# Activa el entorno virtual y lanza la app Streamlit
dirname=$(dirname "$0")
source "$dirname/.venv/bin/activate"
streamlit run tesing.py 