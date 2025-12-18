import requests
import json
from datetime import datetime
import pytz
import time
from colorama import Fore, Back, Style, init
import uuid
import platform
import os

init(autoreset=True)

class DataHiveBot:
    def __init__(self):
        self.base_url = "https://api.datahive.ai/api"
        self.wib = pytz.timezone('Asia/Jakarta')
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.account_points = {}
        
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_device_info(self):
        return {
            "device_id": str(uuid.uuid4()),
            "os": f"{platform.system()} {platform.release()}",
            "cpu_model": "Intel Core i5",
            "cpu_arch": "x86_64",
            "cpu_count": "4"
        }

    def get_headers(self, token, device_info):
        return {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {token}",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "sec-fetch-storage-access": "active",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "x-app-version": "0.2.5",
            "x-cpu-architecture": device_info["cpu_arch"],
            "x-cpu-model": "DO-Regular",
            "x-cpu-processor-count": device_info["cpu_count"],
            "x-device-id": device_info["device_id"],
            "x-device-model": "PC x86 - Chrome 143",
            "x-device-name": "windows pc",
            "x-device-os": "Windows 7.0.0",
            "x-device-type": "extension",
            "x-s": "f",
            "x-user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "x-user-language": "en-US"
        }

    def get_wib_time(self):
        return datetime.now(self.wib).strftime('%x %X %Z')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {self.get_wib_time()} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def print_banner(self):
        banner = f"""
        {Fore.GREEN + Style.BRIGHT}DataHive {Fore.BLUE + Style.BRIGHT}Auto Farming BOT
        {Fore.WHITE + Style.DIM}Updated v0.2.5 Chrome 143 (Live Points Tracker)
        """
        print(banner)

    def mask_email(self, email):
        if "@" in email:
            local, domain = email.split('@', 1)
            if len(local) <= 6:
                hide_local = local[:2] + '*' * 3 + local[-1:]
            else:
                hide_local = local[:3] + '*' * 3 + local[-3:]
            return f"{hide_local}@{domain}"
        return email

    def print_account_info(self, account_num, email, proxy, status_color, message):
        proxy_display = f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}{Fore.CYAN + Style.BRIGHT}Proxy: {Style.RESET_ALL}{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}" if proxy else ""
        
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{self.mask_email(email)}{Style.RESET_ALL}"
            f"{proxy_display}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status: {Style.RESET_ALL}"
            f"{status_color + Style.BRIGHT}{message}{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
        )

    def load_accounts(self, filename="accounts.txt"):
        try:
            with open(filename, 'r') as f:
                tokens = [line.strip() for line in f if line.strip()]
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )
            return tokens
        except FileNotFoundError:
            self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
            return []

    def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                self.log(f"{Fore.YELLOW + Style.BRIGHT}Downloading proxies from Proxyscrape...{Style.RESET_ALL}")
                response = requests.get("https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/all.txt", timeout=30)
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate_input = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate_input in ["y", "n"]:
                    rotate = rotate_input == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate

    def get_worker_info(self, token, device_info, account_num, email, proxy=None):
        try:
            url = f"{self.base_url}/worker"
            headers = self.get_headers(token, device_info)
            proxies = {"http": proxy, "https": proxy} if proxy else None
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                points_24h = data.get('points24h', 0)
                
                if 'user' in data:
                    user = data['user']
                    total_points = user.get('points', 0)
                    
                    account_key = f"account_{account_num}"
                    if account_key not in self.account_points:
                        self.account_points[account_key] = {
                            'initial_total': total_points,
                            'initial_24h': points_24h,
                            'current_total': total_points,
                            'current_24h': points_24h
                        }
                    else:
                        self.account_points[account_key]['current_total'] = total_points
                        self.account_points[account_key]['current_24h'] = points_24h
                    
                    gained_total = total_points - self.account_points[account_key]['initial_total']
                    gained_24h = points_24h - self.account_points[account_key]['initial_24h']
                    
                    self.print_account_info(
                        account_num,
                        email,
                        proxy,
                        Fore.WHITE,
                        f"24h: {Fore.YELLOW + Style.BRIGHT}{points_24h:.2f}{Style.RESET_ALL} "
                        f"{Fore.GREEN + Style.BRIGHT}(+{gained_24h:.2f}){Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Total: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{total_points:.2f}{Style.RESET_ALL} "
                        f"{Fore.GREEN + Style.BRIGHT}(+{gained_total:.2f}){Style.RESET_ALL}"
                    )
                
                return data
            else:
                self.print_account_info(account_num, email, proxy, Fore.RED, f"Failed Get Info: Status {response.status_code}")
                return None
                
        except Exception as e:
            self.print_account_info(account_num, email, proxy, Fore.RED, f"Error: {str(e)}")
            return None

    def ping_uptime(self, token, device_info, account_num, email, proxy=None):
        try:
            url = f"{self.base_url}/ping/uptime"
            headers = self.get_headers(token, device_info)
            proxies = {"http": proxy, "https": proxy} if proxy else None
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                uptime = data.get('uptime', 0)
                self.print_account_info(
                    account_num, 
                    email, 
                    proxy, 
                    Fore.GREEN, 
                    f"PING Success | Uptime: {Fore.YELLOW + Style.BRIGHT}{uptime:.4f}{Style.RESET_ALL}"
                )
                return True
            else:
                self.print_account_info(account_num, email, proxy, Fore.RED, f"PING Failed: Status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_account_info(account_num, email, proxy, Fore.RED, f"PING Failed: {str(e)}")
            return False

    def check_worker_ip(self, token, device_info, account_num, email, proxy=None):
        try:
            url = f"{self.base_url}/network/worker-ip"
            headers = self.get_headers(token, device_info)
            proxies = {"http": proxy, "https": proxy} if proxy else None
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                ip = data.get('ip', 'Unknown')
                country = data.get('country', 'Unknown')
                self.print_account_info(
                    account_num, 
                    email, 
                    proxy, 
                    Fore.GREEN, 
                    f"IP: {Fore.WHITE + Style.BRIGHT}{ip}{Style.RESET_ALL} | "
                    f"Country: {Fore.CYAN + Style.BRIGHT}{country}{Style.RESET_ALL}"
                )
                return True
            else:
                self.print_account_info(account_num, email, proxy, Fore.RED, f"IP Check Failed: Status {response.status_code}")
                return False
                
        except Exception as e:
            self.print_account_info(account_num, email, proxy, Fore.RED, f"IP Check Failed: {str(e)}")
            return False

    def run(self):
        self.clear_terminal()
        self.print_banner()
        
        tokens = self.load_accounts()
        
        if not tokens:
            self.log(f"{Fore.RED + Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
            return
        
        use_proxy_choice, rotate_proxy = self.print_question()
        
        use_proxy = False
        if use_proxy_choice in [1, 2]:
            use_proxy = True
        
        self.clear_terminal()
        self.print_banner()
        self.log(
            f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
        )
        
        if use_proxy:
            self.load_proxies(use_proxy_choice)
        
        self.log(f"{Fore.CYAN + Style.BRIGHT}{'='*75}{Style.RESET_ALL}")
        
        active_workers = []
        
        for i, token in enumerate(tokens, 1):
            device_info = self.get_device_info()
            
            proxy = self.get_next_proxy_for_account(f"account_{i}") if use_proxy else None
            
            try:
                url = f"{self.base_url}/worker"
                headers = self.get_headers(token, device_info)
                proxies_dict = {"http": proxy, "https": proxy} if proxy else None
                response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=30)
                
                if response.status_code != 200:
                    self.log(f"{Fore.RED + Style.BRIGHT}[ Account {i} ] Failed to get worker info{Style.RESET_ALL}")
                    if rotate_proxy and use_proxy:
                        proxy = self.rotate_proxy_for_account(f"account_{i}")
                    continue
                    
                worker_data = response.json()
                real_email = worker_data.get('user', {}).get('email', f'unknown{i}@email.com')
                
                server_device_id = worker_data.get('deviceId')
                if server_device_id:
                    device_info['device_id'] = server_device_id

            except Exception as e:
                self.log(f"{Fore.RED + Style.BRIGHT}[ Account {i} ] Connection failed: {e}{Style.RESET_ALL}")
                if rotate_proxy and use_proxy:
                    proxy = self.rotate_proxy_for_account(f"account_{i}")
                continue
            
            if worker_data:
                points_24h = worker_data.get('points24h', 0)
                total_points = worker_data.get('user', {}).get('points', 0)
                
                account_key = f"account_{i}"
                self.account_points[account_key] = {
                    'initial_total': total_points,
                    'initial_24h': points_24h,
                    'current_total': total_points,
                    'current_24h': points_24h
                }
                
                self.print_account_info(
                    i,
                    real_email,
                    proxy,
                    Fore.WHITE,
                    f"24h: {Fore.YELLOW + Style.BRIGHT}{points_24h:.2f}{Style.RESET_ALL} "
                    f"{Fore.GREEN + Style.BRIGHT}(+0.00){Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{total_points:.2f}{Style.RESET_ALL} "
                    f"{Fore.GREEN + Style.BRIGHT}(+0.00){Style.RESET_ALL}"
                )
                
                active_workers.append({
                    'num': i,
                    'token': token,
                    'device_info': device_info,
                    'email': real_email,
                    'proxy': proxy
                })
                
                self.ping_uptime(token, device_info, i, real_email, proxy)
                time.sleep(1)
                self.check_worker_ip(token, device_info, i, real_email, proxy)
            
            self.log(f"{Fore.CYAN + Style.BRIGHT}{'='*75}{Style.RESET_ALL}")
            time.sleep(2)
        
        if not active_workers:
            self.log(f"{Fore.RED + Style.BRIGHT}No Active Workers.{Style.RESET_ALL}")
            return
            
        self.log(f"{Fore.GREEN + Style.BRIGHT}Active Workers: {Style.RESET_ALL}{Fore.WHITE + Style.BRIGHT}{len(active_workers)}{Style.RESET_ALL}")
        self.log(f"{Fore.CYAN + Style.BRIGHT}{'='*75}{Style.RESET_ALL}")
        
        ping_count = 0
        
        try:
            while True:
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {self.get_wib_time()} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )
                
                time.sleep(60)
                ping_count += 1
                
                total_points_session = 0
                total_points_24h = 0
                total_gained_session = 0
                total_gained_24h = 0
                
                for worker in active_workers:
                    worker_num = worker['num']
                    worker_token = worker['token']
                    worker_device = worker['device_info']
                    worker_email = worker['email']
                    worker_proxy = worker.get('proxy')
                    
                    uptime_ok = self.ping_uptime(worker_token, worker_device, worker_num, worker_email, worker_proxy)
                    
                    if not uptime_ok and rotate_proxy and use_proxy:
                        new_proxy = self.rotate_proxy_for_account(f"account_{worker_num}")
                        worker['proxy'] = new_proxy
                        worker_proxy = new_proxy
                        time.sleep(1)
                        uptime_ok = self.ping_uptime(worker_token, worker_device, worker_num, worker_mail, worker_proxy)
                    
                    if uptime_ok:
                        time.sleep(1)
                        self.check_worker_ip(worker_token, worker_device, worker_num, worker_email, worker_proxy)
                    
                    time.sleep(1)
                    worker_info = self.get_worker_info(worker_token, worker_device, worker_num, worker_email, worker_proxy)
                    if worker_info:
                        if 'user' in worker_info:
                            current_total = worker_info['user'].get('points', 0)
                            total_points_session += current_total
                            
                            account_key = f"account_{worker_num}"
                            if account_key in self.account_points:
                                gained = current_total - self.account_points[account_key]['initial_total']
                                total_gained_session += gained
                        
                        current_24h = worker_info.get('points24h', 0)
                        total_points_24h += current_24h
                        
                        account_key = f"account_{worker_num}"
                        if account_key in self.account_points:
                            gained_24h = current_24h - self.account_points[account_key]['initial_24h']
                            total_gained_24h += gained_24h
                    
                    self.log(f"{Fore.CYAN + Style.BRIGHT}{'='*75}{Style.RESET_ALL}")
                    time.sleep(2)
                
                if total_points_session > 0:
                    avg_points = total_points_session / len(active_workers)
                    avg_gained = total_gained_session / len(active_workers)
                    
                    self.log(
                        f"{Fore.GREEN + Style.BRIGHT}💰 Total Points: {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}{total_points_session:.2f}{Style.RESET_ALL} "
                        f"{Fore.GREEN + Style.BRIGHT}(+{total_gained_session:.2f}){Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}24h: {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}{total_points_24h:.2f}{Style.RESET_ALL} "
                        f"{Fore.GREEN + Style.BRIGHT}(+{total_gained_24h:.2f}){Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Avg: {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}{avg_points:.2f}{Style.RESET_ALL} "
                        f"{Fore.GREEN + Style.BRIGHT}(+{avg_gained:.2f}){Style.RESET_ALL}"
                    )
                    self.log(f"{Fore.CYAN + Style.BRIGHT}{'='*75}{Style.RESET_ALL}")
                
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {self.get_wib_time()} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Wait For 60 Seconds For Next Ping...{Style.RESET_ALL}",
                    end="\r"
                )
                
        except KeyboardInterrupt:
            print(
                f"\n{Fore.CYAN + Style.BRIGHT}[ {self.get_wib_time()} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}[ EXIT ] DataHive - BOT{Style.RESET_ALL}                                       "
            )
            
            total_pings = ping_count * len(active_workers) * 2
            
            total_gained_final = sum(
                self.account_points[f"account_{w['num']}"]['current_total'] - 
                self.account_points[f"account_{w['num']}"]['initial_total']
                for w in active_workers if f"account_{w['num']}" in self.account_points
            )
            
            self.log(
                f"{Fore.YELLOW + Style.BRIGHT}📊 Statistics:{Style.RESET_ALL}\n"
                f"{Fore.CYAN + Style.BRIGHT}   • Total Sessions: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{ping_count}{Style.RESET_ALL}\n"
                f"{Fore.CYAN + Style.BRIGHT}   • Total Accounts: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(active_workers)}{Style.RESET_ALL}\n"
                f"{Fore.CYAN + Style.BRIGHT}   • Total Pings: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{total_pings}{Style.RESET_ALL}\n"
                f"{Fore.CYAN + Style.BRIGHT}   • Total Points Gained: {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}+{total_gained_final:.2f} PTS{Style.RESET_ALL}"
            )

if __name__ == "__main__":
    try:
        bot = DataHiveBot()
        bot.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
