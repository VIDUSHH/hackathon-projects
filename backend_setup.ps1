mkdir backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install fastapi uvicorn pandas prophet python-multipart
pip freeze > requirements.txt
