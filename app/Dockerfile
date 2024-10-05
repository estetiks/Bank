FROM  python:3.9

WORKDIR /app


COPY . .

RUN pip3 install flask flask-login flask-sqlalchemy psycopg2-binary bcrypt
EXPOSE 31337


CMD [ "python3", "-m" , "flask", "run"]