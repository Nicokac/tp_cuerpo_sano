# Cuerpo Sano — MVP base (Django)

Mínimo esqueleto para el TP (miembros, membresías, clases, asistencias, pagos).

## Requisitos
- Python 3.12+
- pip

## Puesta en marcha
```bash
python -m venv .venv
source .venv/bin/activate   # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
