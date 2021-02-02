#! /bin/bash
echo "kill uwsgi........"
if [ ! -f "pids/uwsgi.pid" ]; then
    echo "please run the uwsgi server first or kill handly!"
    exit 0
fi
uwsgi_pid=$(cat pids/uwsgi.pid)
echo "uwsgi pid is $uwsgi_pid"
kill -9 $uwsgi_pid
echo "kill success..."
