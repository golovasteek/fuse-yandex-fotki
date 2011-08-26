#!/usr/bin/python
# auth params to modify
Token = None
UserName = None

# do not modify
ClientId='1141f78aa9854d91be6afbdcb338e76f'

if not Token and not UserName:
	print "This program is testing."
	print "Please visit https://oauth.yandex.ru/authorize?response_type=code&client_id=" + ClientId
	print "and than modify oauth.py with your Token, and UserName"
	exit(1)
