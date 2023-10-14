cat unit.json | curl -X PUT --data-binary @- --unix-socket /var/run/unit/control.sock http://localhost/config/
