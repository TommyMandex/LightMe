#!/usr/bin/env python3
#by hossam mohamed @_wazehell
import subprocess
import os
import random
import sys
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


obfuscate_dir = "/tmp/lightme/"

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_info(text):
    print(bcolors.OKBLUE + str(text) + bcolors.ENDC)

def print_red(text):
    print(bcolors.FAIL + str(text) + bcolors.ENDC)

def print_green(text):
    print(bcolors.OKGREEN + str(text) + bcolors.ENDC)

def get_powershell_bin():
	def which_powershell():
	    try:
	        powershell_location = subprocess.check_output("which powershell", shell=True)
	    except subprocess.CalledProcessError as e:
	        try:
	            powershell_location = subprocess.check_output("which pwsh", shell=True)
	        except subprocess.CalledProcessError as e:
	            return ""
	        return "pwsh"
	    return "powershell"
	powershell_bin = which_powershell()
	if not powershell_bin:
		print_red("[*] Powershell not found trying to install .... ")
		os.system("sudo apt-get install powershell -y")
		print_info("[*] Start the script again ..")
		exit()
	powershell_bin = which_powershell()
	return powershell_bin

def InvokeObfuscationPath():
	dir_path = os.getcwd()
	path =  os.path.join(dir_path,'Invoke-Obfuscation/Invoke-Obfuscation.psd1')
	return path

def obfuscate(script,out_file):
	cmds = []
	cmds.append(get_powershell_bin())
	cmds.append('-C')
	cmds.append(f'import-module {InvokeObfuscationPath()};$ErrorActionPreference = "SilentlyContinue";Invoke-Obfuscation -ScriptPath {script} -Command "TOKEN,ALL,1" -Quiet | Out-File -Encoding ASCII {out_file}')
	data = subprocess.Popen(cmds,shell=False)
	return data,out_file

def getfiles(dir):
	data = []
	for root, dirs, files in os.walk(dir):
		for file in files:
			if file.endswith("ps1"):
				fileObject = {'fullpath':os.path.join(root,file),'filename':file}
				data.append(fileObject) if fileObject not in data else False
	return data


def obfuscate_random_script(files):
	while True:
		to_obfuscate = random.choice(files)
		obfuscated_file = os.path.join(obfuscate_dir,to_obfuscate['filename'])
		print_info("[*] obfuscate in background {} to {} ".format(to_obfuscate['filename'], obfuscated_file))
		popen, data = obfuscate(to_obfuscate['fullpath'], obfuscated_file)
		time.sleep(200)


class LightMeHTTPServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        if self.path == "/":
        	self.wfile.write("Lightme")
        else:
        	try:
	        	filename = obfuscate_dir[:-1] + self.path
	        	with open(filename, 'rb') as fh:
	        		html = fh.read()
	        		self.wfile.write(html)
        	except Exception as e:
        		self.wfile.write(b"Lightme")


def main(base_dir):
	isdir = os.path.isdir(base_dir)
	commands = []
	if not isdir:
		print_red("[-] Not Found {}".format(base_dir))
		exit()

	try:
		os.rmdir(obfuscate_dir)
		os.mkdir(obfuscate_dir)
		print_green("[+] Created Dir {}".format(obfuscate_dir)) 
	except OSError as error: 
		pass

	original_powershell_files = getfiles(base_dir)

	print_green("[*] Loaded Powershell Files {}".format(len(original_powershell_files)))

	for powershell_file in original_powershell_files:
		obfuscated_file = os.path.join(obfuscate_dir,powershell_file['filename'])
		print_green("[*] obfuscate {} to {} ".format(powershell_file['filename'], obfuscated_file))
		popen, data = obfuscate(powershell_file['fullpath'], obfuscated_file)
		commands.append(popen)

	print_red("[*] waiting for background CalledProcess's")
	time.sleep(20)

	x = threading.Thread(target=obfuscate_random_script, args=(original_powershell_files,))
	x.start()

	print_green("[+] starting http server")

	httpd = HTTPServer(('', 8000), LightMeHTTPServer)
	httpd.serve_forever()


if __name__ == '__main__':
	if len(sys.argv) > 1:
		base_dir = sys.argv[1]
		try:
			main(base_dir)
		except KeyboardInterrupt:
			print_red("[*] Closing Lightme")
			exit()
	else:
		exit()