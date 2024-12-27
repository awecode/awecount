. /home/awex/env/bin/activate
cd /home/awex/app/
pip install -r requirements/prod.txt | grep -v 'Requirement already satisfied' | grep -v 'Cleaning up...'
python manage.py migrate -v 0
sudo /usr/bin/supervisorctl restart awecounting:*
