def dynPrint(data):
	sys.stdout.write("\r\x1b[K"+data.__str__())
	sys.stdout.flush()