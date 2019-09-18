#!/bin/bash
if [ $1 = 'start' ]; then
    flag=0
    retries=0
    max_retries=2
    sleep_time=3
    if [ -z "$PERSISTER_PORT" ]
    then
        PERSISTER_PORT=8057
    fi

    while [ $flag -eq 0 ]; do
        if [ $retries -eq $max_retries ]; then
            echo Executed $retries retries, aborting
            exit 1
        fi
        
        #Running gunicorn server
        if exec gunicorn history.subscriber.app:app \
                  --bind 0.0.0.0:$PERSISTER_PORT \
                  --reload -R \
                  --access-logfile - \
                  --log-file - \
                  --env PYTHONUNBUFFERED=1 -k gevent 2>&1 &
        then
            flag=1
        else
            echo "Cannot start application, retrying in $sleep_time seconds..."
            ((retries++))
        fi
        
        #Runnin persister module
        if exec python history/subscriber/persister.py
        then
            flag=1
        else
            echo "Cannot start application, retrying in $sleep_time seconds..."
            ((retries++))
        fi
        sleep $sleep_time        
    done
fi