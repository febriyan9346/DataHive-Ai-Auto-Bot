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
        return datetime.now(self.wib).strftime('%H:%M:%S')

    def log(self, message, level="INFO"):
        time_str = self.get_wib_time()
        
        if level == "INFO":
            color = Fore.CYAN
            symbol = "[INFO]"
        elif level == "SUCCESS":
            color = Fore.GREEN
            symbol = "[SUCCESS]"
        elif level == "ERROR":
            color = Fore.RED
            symbol = "[ERROR]"
        elif level == "WARNING":
            color = Fore.YELLOW
            symbol = "[WARNING]"
        elif level == "CYCLE":
            color = Fore.MAGENTA
            symbol = "[CYCLE]"
        else:
            color = Fore.WHITE
            symbol = "[LOG]"
        
        print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")

    def print_banner(self):
        banner = f"""
{Fore.CYAN}DATAHIVE AUTO BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
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

    def load_accounts(self, filename="accounts.txt"):
        try:
            with open(filename, 'r') as f:
                tokens = [line.strip() for line in f if line.strip()]
            self.log(f"Loaded {len(tokens)} accounts successfully", "INFO")
            return tokens
        except FileNotFoundError:
            self.log(f"File {filename} Not Found.", "ERROR")
            return []

    def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"File {filename} Not Found.", "ERROR")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log("No Proxies Found.", "ERROR")
                return

            self.log(f"Loaded {len(self.proxies)} proxies successfully", "INFO")
        
        except Exception as e:
            self.log(f"Failed To Load Proxies: {e}", "ERROR")
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

    def show_menu(self):
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Select Mode:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. Run with proxy")
        print(f"2. Run without proxy{Style.RESET_ALL}")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        
        while True:
            try:
                choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}").strip()
                if choice in ['1', '2']:
                    return int(choice)
                else:
                    print(f"{Fore.RED}Invalid choice! Please enter 1 or 2.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}Program terminated by user.{Style.RESET_ALL}")
                exit(0)

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
                    
                    time_str = self.get_wib_time()
                    print(f"[{time_str}] {Fore.GREEN}[SUCCESS] Total Points: {total_points:.0f} | Today: +{gained_24h:.0f}{Style.RESET_ALL}")
                
                return data
            else:
                self.log(f"Failed Get Info: Status {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Error: {str(e)}", "ERROR")
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
                time_str = self.get_wib_time()
                print(f"[{time_str}] {Fore.GREEN}[SUCCESS] PING Success | Uptime: {uptime:.4f}{Style.RESET_ALL}")
                return True
            else:
                self.log(f"PING Failed: Status {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"PING Failed: {str(e)}", "ERROR")
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
                time_str = self.get_wib_time()
                print(f"[{time_str}] {Fore.GREEN}[SUCCESS] IP: {ip} | Country: {country}{Style.RESET_ALL}")
                return True
            else:
                self.log(f"IP Check Failed: Status {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"IP Check Failed: {str(e)}", "ERROR")
            return False

    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            hours = i // 3600
            minutes = (i % 3600) // 60
            secs = i % 60
            print(f"\r[COUNTDOWN] Next cycle in: {hours:02d}:{minutes:02d}:{secs:02d} ", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="", flush=True)

    def run(self):
        self.clear_terminal()
        self.print_banner()
        
        tokens = self.load_accounts()
        
        if not tokens:
            self.log("No Accounts Loaded.", "ERROR")
            return
        
        use_proxy_choice = self.show_menu()
        
        use_proxy = False
        rotate_proxy = False
        
        if use_proxy_choice == 1:
            use_proxy = True
            while True:
                rotate_input = input(f"{Fore.GREEN}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip().lower()
                if rotate_input in ["y", "n"]:
                    rotate_proxy = rotate_input == "y"
                    break
                else:
                    print(f"{Fore.RED}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")
        
        self.clear_terminal()
        self.print_banner()
        
        if use_proxy_choice == 1:
            self.log("Running with proxy", "INFO")
        else:
            self.log("Running without proxy", "INFO")
        
        if use_proxy:
            self.load_proxies()
        
        print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
        
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
                    self.log(f"Account #{i} Failed to get worker info", "ERROR")
                    if rotate_proxy and use_proxy:
                        proxy = self.rotate_proxy_for_account(f"account_{i}")
                    continue
                    
                worker_data = response.json()
                real_email = worker_data.get('user', {}).get('email', f'unknown{i}@email.com')
                
                server_device_id = worker_data.get('deviceId')
                if server_device_id:
                    device_info['device_id'] = server_device_id

            except Exception as e:
                self.log(f"Account #{i} Connection failed: {e}", "ERROR")
                if rotate_proxy and use_proxy:
                    proxy = self.rotate_proxy_for_account(f"account_{i}")
                continue
            
            if worker_data:
                self.log(f"Account #{i}/{len(tokens)}", "INFO")
                self.log(f"Proxy: {proxy if proxy else 'No Proxy'}", "INFO")
                self.log(f"{self.mask_email(real_email)}", "INFO")
                
                points_24h = worker_data.get('points24h', 0)
                total_points = worker_data.get('user', {}).get('points', 0)
                
                account_key = f"account_{i}"
                self.account_points[account_key] = {
                    'initial_total': total_points,
                    'initial_24h': points_24h,
                    'current_total': total_points,
                    'current_24h': points_24h
                }
                
                time_str = self.get_wib_time()
                print(f"[{time_str}] {Fore.GREEN}[SUCCESS] Login successful!{Style.RESET_ALL}")
                time.sleep(1)
                
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
                time.sleep(1)
                self.get_worker_info(token, device_info, i, real_email, proxy)
            
            if i < len(tokens):
                print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                time.sleep(2)
        
        if not active_workers:
            self.log("No Active Workers.", "ERROR")
            return
        
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        self.log(f"Setup Complete | Active Workers: {len(active_workers)}/{len(tokens)}", "INFO")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
        
        cycle = 1
        
        try:
            while True:
                self.log(f"Cycle #{cycle} Started", "CYCLE")
                print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
                
                success_count = 0
                
                for worker in active_workers:
                    worker_num = worker['num']
                    worker_token = worker['token']
                    worker_device = worker['device_info']
                    worker_email = worker['email']
                    worker_proxy = worker.get('proxy')
                    
                    self.log(f"Account #{worker_num}/{len(active_workers)}", "INFO")
                    self.log(f"Proxy: {worker_proxy if worker_proxy else 'No Proxy'}", "INFO")
                    self.log(f"{self.mask_email(worker_email)}", "INFO")
                    
                    time.sleep(1)
                    
                    uptime_ok = self.ping_uptime(worker_token, worker_device, worker_num, worker_email, worker_proxy)
                    
                    if not uptime_ok and rotate_proxy and use_proxy:
                        new_proxy = self.rotate_proxy_for_account(f"account_{worker_num}")
                        worker['proxy'] = new_proxy
                        worker_proxy = new_proxy
                        time.sleep(1)
                        uptime_ok = self.ping_uptime(worker_token, worker_device, worker_num, worker_email, worker_proxy)
                    
                    if uptime_ok:
                        time.sleep(1)
                        self.check_worker_ip(worker_token, worker_device, worker_num, worker_email, worker_proxy)
                        success_count += 1
                    
                    time.sleep(1)
                    self.get_worker_info(worker_token, worker_device, worker_num, worker_email, worker_proxy)
                    
                    if worker != active_workers[-1]:
                        print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                        time.sleep(2)
                
                print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
                self.log(f"Cycle #{cycle} Complete | Success: {success_count}/{len(active_workers)}", "CYCLE")
                print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
                
                cycle += 1
                
                wait_time = 60
                self.countdown(wait_time)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Program terminated by user.{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = DataHiveBot()
        bot.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
