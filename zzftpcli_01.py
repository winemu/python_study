#!/usr/bin/env python3

from struct import *
import socket
import sys
import os

usage = """
Transfers files to and from a remote computer running \n
the TFTP service.

TFTP host [GET | PUT] source

  host            Specifies the local or remote host.
  GET             Transfers the file destination on the remote host to
                  the file source on the local host.
  PUT             Transfers the file source on the local host to
                  the file destination on the remote host.
  source          Specifies the file to transfer.
"""
mod='octet'.encode('utf-8')
op_tsize='tsize'.encode('utf-8')
tsize='512'.encode('utf-8')
op_read=1
op_write=2
op_data=3
op_ack=4
op_err=5
op_op_ack=6

ip=sys.argv[1]
fn=bytes(sys.argv[3].encode('utf-8'))
op_code=op_read

pkg_size = 512 + 2 + 2  #（2字节操作码+2个字节的序号+512字节数据）

port = 69
i=0
bufs =[]

#ip='192.168.1.4'
#fn='tftptest.txt'.encode('utf-8')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def tcomm():
	pack_str='!h' + str(len(fn)+1) + 's6s'
	data=pack(pack_str,op_code,fn,mod)
	s.sendto(data,(ip,port))

def tget():
	tcomm()
	size=1000
	while(size>=pkg_size):
		(data,addr) = s.recvfrom(20480)
		size=len(data)
		pack_str="!hh" + str(size-4) + "s"
		(op_code, i, buf)=unpack(pack_str,data)
		bufs.append(buf)
		data=pack("!hh",op_ack,i)
		s.sendto(data,addr)
	f=open(fn,"wb")
	for buf in bufs:
		f.write(buf)
	f.close()

def tput():
	tcomm()
	op_code=op_data
	fsize=os.path.getsize(fn)
	cnt=fsize/512
	i=0
	f=open(fn,"rb")
	(data,addr) = s.recvfrom(20480)
	while(i<cnt):
		i = i+1
		buf=f.read(512)
		pack_str='!hh' +str(len(buf)) +'s'
		print(pack_str)
		data=pack(pack_str,op_code,i,buf)
		s.sendto(data,addr)
	if(fsize % 512 ==0):
		data=pack('!hh',op_code,i +1)
		s.sendto(data,addr)
	f.close()

if(sys.argv[2].upper()=='GET'):
	op_code=op_read
	tget()
elif(sys.argv[2].upper()=='PUT'):
	op_code=op_write
	print(op_code)
	tput()
else:
	print(usage)
	exit(-1)

s.close()
