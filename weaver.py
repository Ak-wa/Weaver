try:
    import requests,sys,time,os,signal
    from progress.bar import Bar
    from progress.spinner import PixelSpinner
    import threading
    from requests.exceptions import ConnectionError
except:
    os.system('pip install requests')
    os.system('pip install progress')
    import requests,sys,time,os,signal
    from progress.bar import Bar
    from progress.spinner import PixelSpinner
    import threading
    from requests.exceptions import ConnectionError

if len(sys.argv) <= 1:
    sys.stdout.write("[-] You forgot to add an url\n")
    sys.stdout.write("[ ] Usage: python weaver.py <example.com> <wordlist.txt>\n")
    sys.exit()
else:
	pass
if len(sys.argv) <= 2:
    sys.stdout.write("[-] You forgot to add a wordlist\n")
    sys.stdout.write("[ ] Usage: python weaver.py <example.com> <wordlist.txt>\n")
    sys.exit()
else:
	pass
found_directories = []
redirect_directories = []
error500_directories = []
forbidden_directories = []
front_page_path = ""
front_page_error = 0
timeout = 1
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
headers = {'User-Agent':user_agent}
#target = 'http://www.usnintl.com'
target = sys.argv[1]
wordlist = sys.argv[2]
threads = []

def ascii():
    print("""
           ____                      ,
          /---.'.__             ____//
               '--.\           /.---'
          _______  \\         //
        /.------.\  \|      .'/  ______
       //  ___  \ \ ||/|\  //  _/_----.\__
      |/  /.-.\  \ \:|< >|// _/.'..\   '--'
         //   \'. | \'.|.'/ /_/ /  \\
        //     \ \_\/" ' ~\-'.-'    \\
       //       '-._| :H: |'-.__     \\
      //           (/'==='\)'-._\     ||
      ||                        \\    \|
      ||                         \\    '
      |/                          \\
             Weaver v.1.0          ||
                                   ||
                                   \\
                                    '
""")

count = 0
for line in open(wordlist).readlines(): count += 1
sys.stdout.write("[ ] Wordlist length: %d\n"%count)
Zcounter = 0
def urlenum(current_dir): # Interprets HTTP Status Codes & sorts into lists
        try:
            global Zcounter
            s = requests.get(target+"/"+current_dir,headers=headers)
            if str('FrontPage Error') in str(s.text):
                global front_page_path
                global front_page_error
                front_page_error = 1
                front_page_path = current_dir
            else:
                if '404' in str(s.text):
                    Zcounter = Zcounter +1
                    pass
                else:
                    if 'Not' and 'Found' in str(s.text):
                        Zcounter = Zcounter + 1
                        pass
                    else:
                        if str(s.status_code).startswith("2"):
                            found_directories.append(current_dir)
                        else:
                            pass
                if str(s.status_code).startswith("5"):
                    error500_directories.append(current_dir)
                else:
                    pass
                if str(s.status_code).startswith("4"):
                    if s.status_code == 404:
                        Zcounter = Zcounter + 1
                    else:
                        forbidden_directories.append(current_dir)
                else:
                    pass
                if str(s.status_code).startswith("3"):
                    found_directories.append(current_dir)
                else:
                    pass
        except KeyboardInterrupt:
            print("done")
        except requests.exceptions.ConnectionError:
            sys.exit()
        except Exception as e:
            print(e)
            sys.exit()
            print("Crash #1")
def dirBruter(): # Starts threads and prints lists
    with open(wordlist) as dirs:
        try:
            sys.stdout.write("\n[+] Starting Directory Bruteforcer\n")
            bar = Bar("[+] Progress: ",fill="+",max=count)
            sys.stdout.write("\n")
            #spinner = PixelSpinner('[+] Bruteforcing ')
            for onedir in dirs:
                try:
                    t = threading.Thread(target=urlenum,args=(onedir,))
                    t.daemon = True
                    t.start()
                    threads.append(t)
                    #spinner.next()
                    bar.next()
                    time.sleep(0.01)
                except KeyboardInterrupt:
                    sys.stdout.write("\n[!] CTRL-C was punched, exiting...\n")
                    sys.exit()
                except Exception as e:
                    sys.stdout.write("\n[!] Unknown Exception! exiting...\n")
                    print(e)
                    sys.exit()
                    sys.exit(1)
            for t in threads:
                t.join()
            bar.finish()
            for directory in found_directories:
                sys.stdout.write("[+] %s/%s"%(target,directory))
                if not found_directories:
                    sys.stdout.write("[+] Code 200 : 0")
                else:
                    pass
            for response in error500_directories:
                sys.stdout.write("[+] Code 500: %s/%s" % (target,response))
            for directory in forbidden_directories:
                sys.stdout.write("[+] Forbidden: %s/%s" %(target,directory))
            sys.stdout.write("[+] 404 received: %d" % Zcounter)
            if front_page_error == 1:
                sys.stdout.write("[+] Frontpage error found on: %s"%front_page_path)
            else:
                pass
            sys.exit()
            
        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            sys.stdout.write(e)
        except:
            try:
                for directory in found_directories:
                    sys.stdout.write("[+] %s/%s "%(target,directory))
                if found_directories == []:
                    sys.stdout.write("\n[ ] Code 200 : 0\n")
                else:
                    pass
                for response in error500_directories:
                    sys.stdout.write("[+] Code 500 : %s/%s" % (target,response))
                for directory in forbidden_directories:
                    sys.stdout.write("[+] Forbidden: %s/%s" % (target,directory))
                sys.stdout.write("[+] 404 received: %d\n" % Zcounter)
                if front_page_error == 1:
                    sys.stdout.write("[+] Frontpage error found on: %s"%front_page_path)
                    sys.stdout.write("[+] You might want to read this: https://www.exploit-db.com/exploits/19897")
                else:
                    pass
                sys.exit()
            except Exception as e:
                raise e
            except:
                pass
                
def check_redirect():
    global target
    r = requests.get(target)
    if r.url != (target+"/"):
        sys.stdout.write("[ ] You got redirected to %s\n" % (str(r.url)))
        follow_redirect = input("[ ] Want to follow? y/n : ")
        if follow_redirect == 'y':
            target = r.url
            sys.stdout.write("[+] Followed redirect: %s" % target)
        else:
            pass
check_redirect()
ascii()
dirBruter()
