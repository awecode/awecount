. ../env/bin/activate
cd ../app/
pip install -r requirements/prod.txt | grep -v 'Requirement already satisfied' | grep -v 'Cleaning up...'
./manage.py migrate -v 0
circusctl restart awecount
./manage.py qcluster &