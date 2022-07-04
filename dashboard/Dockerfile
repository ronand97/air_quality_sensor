FROM python:3.8
WORKDIR /app
COPY dashboard_requirements.txt ./dashboard_requirements.txt
RUN pip install -r dashboard_requirements.txt
EXPOSE 8501
COPY . /app

CMD ["streamlit", "run", "dashboard.py", "--server.port", "8501"]