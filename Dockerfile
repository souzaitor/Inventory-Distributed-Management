FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python","-u","./fabrica.py","-n 1 -p 1 2 3"]
CMD [ "python","-u","./centro_distribuicao.py"]
CMD [ "python","-u","./loja.py","-n 1"]