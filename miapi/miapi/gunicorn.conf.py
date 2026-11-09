bind = '127.0.0.1:8000'  # solo local; Nginx es la puerta de entrada
workers = 3  # (2 x nucleos) + 1. Usa 2 en t3.micro
timeout = 30
accesslog = '-'
errorlog = '-'
loglevel = 'info'
