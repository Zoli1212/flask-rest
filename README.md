mysql -u myuser -p mydbname -h localhost -P 3307
docker exec -it flask-rest-api_db_1 mysql -u myuser -p mydbname 
mydbname is NOT the password!

show databases;
use <database-name>;
show tables;
select * from <table-name>;
