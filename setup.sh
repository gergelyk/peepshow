python3 -m venv --clear venv
echo "export PEEPSHOW_DEV_MODE=1" >> /venv/bin/activate
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .
