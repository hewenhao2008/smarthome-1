# -*- coding: utf-8 -*-
import logging
import tornado.escape
import tornado.options
import tornado.web
import tornado.gen
import tornado.websocket
import tornado.httpclient
import time
import os.path
import uuid
import json
from mdns_util import MDNS

def fetch_image(url, callback=None):
	logging.info("fetch image url=%s", url)
	def on_fetch(response):
		if response.error:
			logging.error("fetch image error %s", response.error)
		else:
			logging.info("fetch image url=%s success.", url)
			if callback is not None:
				callback(response.body)
			#print dir(response)
			#logging.info("image %s",response.body[0:100])
	tornado.httpclient.AsyncHTTPClient().fetch(url, on_fetch)

def send_image_by_airplay(host, port, image):
	logging.info("airplay send image to %s:%s", host, port)

	def stop_airplay():
		logging.info("stop airplay on %s:%s", host, port)
		def on_sended(response):
			if response.error:
				logging.error("stop airplay error %s", response.error)
			else:
				logging.info("stop airplay over %s",response)
		headers = {
			#PUT /photo HTTP/1.1
			'X-Apple-AssetKey': 'F92F9B91-954E-4D63-BB9A-EEC771ADE6E8',
			'Content-Length': 0,
			'User-Agent': 'MediaControl/1.0',
			'X-Apple-Session-ID': '1bd6ceeb-fffd-456c-a09c-996053a7a08c',	
		}
		url = "http://" + host + ":" + port + "/stop"
		request = tornado.httpclient.HTTPRequest(url, method='POST', headers=headers, body='1=1')
		tornado.httpclient.AsyncHTTPClient().fetch(request, on_sended)

	def on_sended(response):
		if response.error:
			logging.error("airplay send error %s", response.error)
		else:
			logging.info("airplay send over %s",response)
			ioloop = tornado.ioloop.IOLoop.instance()
			ioloop.add_timeout(ioloop.time() + 10, stop_airplay)

	def on_send_display():
		headers = {
			#PUT /photo HTTP/1.1
			'X-Apple-AssetKey': 'F92F9B91-954E-4D63-BB9A-EEC771ADE6E8',
			'Content-Length': len(image),
			'User-Agent': 'MediaControl/1.0',
			'X-Apple-Session-ID': '1bd6ceeb-fffd-456c-a09c-996053a7a08c',	
		}
		url = "http://" + host + ":" + port + "/photo"
		request = tornado.httpclient.HTTPRequest(url, method='PUT', headers=headers, body=image)
		tornado.httpclient.AsyncHTTPClient().fetch(request, on_sended)

	stop_airplay()
	on_send_display()


def display_image(url, host, port, callback=None):
	logging.info("display image=%s, on %s:%s", url, host, port)
	def on_fetch(image):
		send_image_by_airplay(host, port, image)
		#upload_image(image)
	fetch_image(url, on_fetch)

def upload_image(image, callback=None):
	logging.info("upload image....")
	def on_upload(response):
		if response.error:
			logging.error("upload image error %s", response.error)
		else:
			logging.info("upload image success %s",response.body)
			if callback is not None:
				callback(response.body)

	filename = str(time.time() * 1000000) + ".jpg"
	token = "416521fd-cb90-34d5-beb5-1a0e0855d282"
	url = "http://pp.sohu.com/upload/api/sync?device=155828489132191744&access_token=" +  token + "&filename=" + filename
	request = tornado.httpclient.HTTPRequest(url, method='POST', body=image)
	tornado.httpclient.AsyncHTTPClient().fetch(request, on_upload)



def main():
	tornado.options.parse_command_line()
	
	#url = "http://img.itc.cn/photo/oMAER7INJZb"
	url = "http://mmbiz.qpic.cn/mmbiz/RJib8PKM3xaGcbrMueOpEPL6O7F414G7YBVhx6w6pcGCnhmFjichiajk9uQ2sTZeuMZF7QuDicfzZQxKibMKl5Yia7dA/0"
	display_image(url, '10.2.58.240', '7000')
	tornado.ioloop.IOLoop.instance().start()
	

if __name__ == "__main__":
    main()
