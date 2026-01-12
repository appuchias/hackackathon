wsgi_app = "hackackathon.wsgi"

daemon = True
pidfile = "gunicorn.pid"

workers = 2
threads = 2

bind = "127.0.0.1:8000"

accesslog = "log/gunicorn-access.log"
errorlog = "log/gunicorn-error.log"
# access_log_format = '%(h)s %(l)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
access_log_format = (
    '%({x-forwarded-for}i)s %(l)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
)
capture_output = True


def when_ready(server):
    print("Gunicorn listo")


def on_exit(server):
    print("Gunicorn apagado")
