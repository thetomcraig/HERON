set -x
APPNAME=HERON
APPDIR=/home/ubuntu/${APPNAME}

LOGFILE="${APPDIR}/gunicorn.log"
ERRORFILE="${APPDIR}/gunicorn-error.log"
NUM_WORKERS=3
ADDRESS=127.0.0.1:8000

cd ${HOME}
source ./heron_env/bin/activate

cd $APPDIR

exec gunicorn heron.wsgi:application \
-w $NUM_WORKERS --bind=$ADDRESS \
--log-level=debug \
--log-file=$LOGFILE 2>>$LOGFILE  1>>$ERRORFILE &
