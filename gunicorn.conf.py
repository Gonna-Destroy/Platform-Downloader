
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:80"
reload = True

errorlog = 'error.log'
accesslog = 'access.log'
loglevel = 'debug'