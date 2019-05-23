try:
    import requests
    import sys
    import time
    import os
    from progress.bar import Bar
    from progress.spinner import PixelSpinner
    import threading
    from requests.exceptions import ConnectionError
except ImportError:
    os.system('pip install -r requirements.txt')
    import requests
    import sys
    import time
    import os
    from progress.bar import Bar
    from progress.spinner import PixelSpinner
    import threading
    from requests.exceptions import ConnectionError


class DirBruter:
    def __init__(self, target_url, wordlist_file):
        requests.packages.urllib3.disable_warnings()  # Mute SSL-Errors

        self.__found_directories = []
        self.__redirect_directories = []
        self.__error500_directories = []
        self.__forbidden_directories = []
        self.__front_page_path = ""
        self.__front_page_error = 0
        self.__timeout = 1
        self.__headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        self.__target = target_url
        self.__wordlist = wordlist_file
        self.__wordlist_list = list(open(self.__wordlist))
        self.__threads = []
        self.__count = 0
        self.__robots_path_count = 0
        self.__Zcounter = 0

        self.__check_robots()
        self.__wordlist_count()
        self.__check_redirect()

        self.__verify_ssl_cert()

    def __verify_ssl_cert(self):
        try:
            _ = requests.get(target + "/robots.txt", headers=self.__headers, verify=True)
        except requests.exceptions.SSLError:
            _ = input("[!] The SSL certificate cannot be verified. Continue? (y):")
            if _:
                if _ != "y":
                    print("[!] Aborting. SSL certificate not trusted.")
                    exit()
            else:
                pass

    def __check_robots(self):
        try:
            sys.stdout.write("[+] Checking for a robots.txt\n")
            html = requests.get(target + "/robots.txt", headers=self.__headers, verify=False).text
            for line in html.split("\n"):
                if line.startswith("Disallow: "):
                    self.__wordlist_list.append(str(line.split(":")[1]))
                    self.__robots_path_count += 1
            sys.stdout.write("[+] Wrote contents of robots.txt into wordlist\n")
        except:  # TODO: unknown exception
            sys.stdout.write("[+] No robots.txt found")

    def __wordlist_count(self):
        for _ in self.__wordlist_list:
            self.__count += 1
        if self.__robots_path_count != 0:
            self.__count += self.__robots_path_count
        sys.stdout.write("[ ] Wordlist length: %d\n" % self.__count)

    def __urlenum(self, current_dir):  # Interprets HTTP Status Codes & sorts into lists
        try:
            s = requests.get(target + "/" + current_dir, headers=self.__headers, verify=False)
            if '404' in str(s.text):
                self.__Zcounter = self.__Zcounter + 1
                pass
            else:
                if 'Not' and 'Found' in str(s.text):
                    self.__Zcounter = self.__Zcounter + 1
                    pass
                else:
                    if str(s.status_code).startswith("2"):
                        self.__found_directories.append(current_dir)
                    else:
                        pass
            if str(s.status_code).startswith("5"):
                self.__error500_directories.append(current_dir)
            else:
                pass
            if str(s.status_code).startswith("4"):
                if s.status_code == 404:
                    self.__Zcounter = self.__Zcounter + 1
                else:
                    self.__forbidden_directories.append(current_dir)
            else:
                pass
            if str(s.status_code).startswith("3"):
                self.__found_directories.append(current_dir)
            else:
                pass
        except KeyboardInterrupt:
            print("done")
        except requests.exceptions.ConnectionError:
            sys.exit()
        except Exception as e:
            print(e)
            sys.exit()

    def __check_redirect(self):
        r = requests.get(self.__target, verify=False)
        if r.url != (self.__target + "/"):
            sys.stdout.write("[ ] You got redirected to %s\n" % (str(r.url)))
            follow_redirect = input("[ ] Want to follow? y/n : ")
            if follow_redirect == 'y':
                self.__target = r.url
                sys.stdout.write("[+] Followed redirect: %s" % self.__target)
            else:
                pass

    def run(self):  # Starts threads and prints lists
        with open(self.__wordlist) as dirs:
            try:
                sys.stdout.write("\n[+] Starting Directory Bruteforcer\n")
                bar = Bar("[+] Progress: ", fill="+", max=self.__count)
                sys.stdout.write("\n")
                for onedir in dirs:
                    try:
                        t = threading.Thread(target=self.__urlenum, args=(onedir,))
                        t.daemon = True
                        t.start()
                        self.__threads.append(t)
                        bar.next()
                        time.sleep(0.01)
                    except KeyboardInterrupt:
                        sys.stdout.write("\n[!] CTRL-C was punched, exiting...\n")
                        sys.exit()
                    except Exception as e:
                        sys.stdout.write("\n[!] Unknown Exception! exiting...\n")
                        print(e)
                        sys.exit(1)
                for t in self.__threads:
                    t.join()
                bar.finish()
                for directory in self.__found_directories:
                    sys.stdout.write("[+] %s/%s" % (target, directory))
                    if not self.__found_directories:
                        sys.stdout.write("[+] Code 200 : 0")
                    else:
                        pass
                for response in self.__error500_directories:
                    sys.stdout.write("[+] Code 500: %s/%s" % (target, response))
                for directory in self.__forbidden_directories:
                    sys.stdout.write("[+] Forbidden: %s/%s" % (target, directory))
                sys.stdout.write("[+] 404 received: %d" % self.__Zcounter)
                sys.exit()

            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(e)
            except:
                try:
                    for directory in self.__found_directories:
                        sys.stdout.write("[+] %s/%s " % (target, directory))
                    if self.__found_directories == []:
                        sys.stdout.write("\n[ ] Code 200 : 0\n")
                    else:
                        pass
                    for response in self.__error500_directories:
                        sys.stdout.write("[+] Code 500 : %s/%s" % (target, response))
                    for directory in self.__forbidden_directories:
                        sys.stdout.write("[+] Forbidden: %s/%s" % (target, directory))
                    sys.stdout.write("[+] 404 received: %d\n" % self.__Zcounter)
                    sys.exit()
                except Exception as e:
                    raise e
                except:
                    pass


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stdout.write("[-] You forgot to add an url or wordlist\n")
        sys.stdout.write("[ ] Usage: python weaver.py <example.com> <wordlist.txt>\n")
        sys.exit()

    target = sys.argv[1]
    wordlist = sys.argv[2]

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

    Bruter = DirBruter(target_url=target, wordlist_file=wordlist)
    Bruter.run()
