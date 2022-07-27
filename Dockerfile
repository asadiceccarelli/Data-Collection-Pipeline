# FROM python:3.8-slim-buster

# COPY . . 

# RUN pip install -r requirements.txt

# CMD ["python", "project/scraper.py"]

x=i.strip() for i in open("requirements.txt").readlines()
print(x)