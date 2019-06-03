try:
    import requests
    import sys
    import time
    from queue import Queue
    import os
    # from progress.bar import Bar
    # from progress.spinner import PixelSpinner
    import threading
    from requests.exceptions import ConnectionError
except ImportError:
    import os

    os.system('pip install -r requirements.txt')
    import requests
    import sys
    import time
    import os
    # from progress.bar import Bar
    # from progress.spinner import PixelSpinner
    import threading
    from requests.exceptions import ConnectionError


class ProgrssBar:
    class Bar:
        def __init__(self, max_value, title, char, length, unit):
            self.__title = title
            self.__char = char
            self.__len = length
            self.speed = 0
            self.__fill = 0
            self.max = max_value
            self.value = 0
            self.percent = 0
            self.unit = unit

        def string(self):
            self.percent = round(self.value / self.max * 100)
            if self.percent > 100:
                self.percent = 100
            self.__fill = round(self.percent * self.__len / 100)

            return "{} |{}{}| {}/{} ({}%) {} {}/s".format(self.__title,
                                                          self.__fill * self.__char,
                                                          (self.__len - self.__fill) * " ",
                                                          self.value, self.max, self.percent,
                                                          self.speed, self.unit)

    def __init__(self, max_value, title="Loading", char="█", length=70, unit="", multiplyer=1):
        self.bar = self.Bar(max_value, title, char, length, unit)
        self.multiplyer = multiplyer

    def set_value(self, value):
        self.bar.value = value

    def inc_value(self, increment=1):
        self.bar.value += increment

    def show_progress(self):
        def monitor_speed():
            value_start = self.bar.value
            start = time.time()
            time.sleep(1)
            self.bar.speed = int((self.bar.value - value_start) / (time.time() - start) * self.multiplyer)

        t = threading.Thread(target=monitor_speed, daemon=True)
        t.start()

        print()
        while self.bar.percent < 100:
            try:
                print(self.bar.string(), end="\r")
                time.sleep(0.1)
            except KeyboardInterrupt:
                raise NameError
        print()


class DirBruter:
    def __init__(self, target_url, wordlist_file):
        requests.packages.urllib3.disable_warnings()  # Mute SSL-Errors
        self.running = True
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
        self.__not_found_count = 0
        self.__check_redirect()
        self.__check_robots()
        self.__wordlist_count()

        self.__verify_ssl_cert()

        self.__dirs = Queue()
        self.PB = ProgrssBar(int(self.__count), unit="dirs")

    def __verify_ssl_cert(self):
        try:
            _ = requests.get(target + "/robots.txt", headers=self.__headers, verify=True)
        except requests.exceptions.SSLError:
            _ = input("[!] The SSL certificate cannot be verified. Continue? (y/n) [y]:")
            if _:
                if _ != "y":
                    print("[!] Aborting. SSL certificate not trusted.")
                    sys.exit()
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
        except:
            sys.stdout.write("[+] No robots.txt found\n")

    def __wordlist_count(self):
        for _ in self.__wordlist_list:
            self.__count += 1
        if self.__robots_path_count != 0:
            self.__count += self.__robots_path_count
        sys.stdout.write("[ ] Wordlist length: %d\n" % self.__count)

    def __urlenum(self):  # Interprets HTTP Status Codes & sorts into lists
        while self.__dirs.qsize() > 0:
            current_dir = self.__dirs.get()
            if self.running:
                try:
                    s = requests.get(target + "/" + current_dir, headers=self.__headers, verify=False, timeout=3)
                    if '404' in str(s.text):
                        self.__not_found_count = self.__not_found_count + 1
                        pass
                    else:
                        if 'Not' and 'Found' in str(s.text):
                            self.__not_found_count = self.__not_found_count + 1
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
                            self.__not_found_count = self.__not_found_count + 1
                        else:
                            self.__forbidden_directories.append(current_dir)
                    else:
                        pass
                    if str(s.status_code).startswith("3"):
                        self.__found_directories.append(current_dir)
                    else:
                        pass
                except KeyboardInterrupt:
                    pass
                except requests.exceptions.ConnectionError:
                    pass
                except requests.exceptions.Timeout:
                    pass
                except Exception as e:
                    print(e)
                    pass
                self.PB.inc_value()
            else:
                break
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
                sys.stdout.write("\n[+] Starting Directory Bruteforcer\n\n")

                for dir_ in dirs:
                    self.__dirs.put(dir_)

                # starting threads
                for onedir in range(int(sys.argv[3])):
                    t = threading.Thread(target=self.__urlenum, daemon=True)
                    t.start()
                    self.__threads.append(t)

                try:
                    self.PB.show_progress()
                except NameError:
                    raise TypeError  # print results
            except KeyboardInterrupt:
                raise TypeError
            except TypeError:
                # print results
                print("\n")
                for directory in self.__found_directories:
                    sys.stdout.write("[+] %s/%s" % (target, directory))
                    if not self.__found_directories:
                        sys.stdout.write("[+] Code 200 : 0")
                    else:
                        pass
                if self.__error500_directories:
                    for response in self.__error500_directories:
                        sys.stdout.write("[+] Code 500: %s/%s" % (target, response))
                if self.__forbidden_directories:
                    for directory in self.__forbidden_directories:
                        sys.stdout.write("[+] Forbidden: %s/%s" % (target, directory))
                sys.stdout.write("\n[+] 404 received: %d" % self.__not_found_count)

            # empty queue and wait for threads
            self.running = False
            print("\n[ ] Waiting for threads ...")
            for t in self.__threads:
                t.join()
            print("_________________________________")
            sys.exit()


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
