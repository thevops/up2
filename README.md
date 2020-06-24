# up2
Simple service for static hosting



up2 init
	- server generates subdomain (sqlite)
	- server creates vhost
	- client saves subdomain, email and token in file .XXXXX

up2 deploy
	- client zips directory
	- client sends zip file to server
	- server unzip file and put it in subdomain directory
	- server reload WWW

up2 delete
	- server remove subdomain directory and vhost
	- server reload WWW



server:
	- docker
	- nginx (SSL LE), uwsgi
	- python, flask, sqlite

client:
	- python, requests




# test

## init

http --form POST http://127.0.0.1:5000/init domain=costam



## deploy

http --form POST http://127.0.0.1:5000/deploy token=11086cad8bc9819cfb2c419cec7a3dac domain=costam file@timer_debata.zip


## delete 

http --form POST http://127.0.0.1:5000/delete token=398d2d1d04ee0e16186482d7ceddc418 domain=miecio
