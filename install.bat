@echo off

echo Creation du venv...
python -m venv .venv

call .venv\Scripts\activate

echo Mise a jour de pip...
python -m pip install --upgrade pip

echo Installation des dependances...
pip install -r requirements.txt

echo.
echo Installation terminee.
pause
