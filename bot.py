import requests
import json
from datetime import datetime
import pytz
import time
from colorama import Fore, Back, Style, init
import uuid
import platform
import os
import hashlib

init(autoreset=True)

class DataHiveBot:
    def __init__(self):
        self.base_url = "https://api.datahive.ai/api"
        self.wib = pytz.timezone('Asia/Jakarta')
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.account_points = {}
        self.workers_per_account = 3
        self.device_file = "devices.json"
        
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def load_device_ids(self):
        """Load saved device IDs from file"""
        if os.path.exists(self.device_file):
            try:
                with open(self.device_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_device_ids(self, devices):
        """Save device IDs to file"""
        with open(self.device_file, 'w') as f:
            json.dump(devices, f, indent=2)
    
    def generate_device_id(self, worker_key):
        """Generate device ID in python-client format like dashboard"""
        hash_part = hashlib.md5(worker_key.encode()).hexdigest()
        return f"python-client-{hash_part}"
        
    def get_device_info(self, worker_key, saved_devices):
        """Get or create device info with persistent device_id in python-client format"""
        if worker_key in saved_devices:
            device_id = saved_devices[worker_key]
            self.log(f"Using saved device: {device_id[:30]}...", "INFO")
        else:
            device_id = self.generate_device_id(worker_key)
            saved_devices[worker_key] = device_id
            self.save_device_ids(saved_devices)
            self.log(f"Created device: {device_id[:30]}...", "INFO")
        
        return {
            "device_id": device_id,
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
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "origin": "chrome-extension://abcdefghijklmnop",
            "x-app-version": "0.2.5",
            "x-cpu-architecture": device_info["cpu_arch"],
            "x-cpu-model": "DO-Regular",
            "x-cpu-processor-count": device_info["cpu_count"],
            "x-device-id": device_info["device_id"],
            "x-device-model": "PC x86 - Chrome 143",
            "x-device-name": "windows pc",
            "x-device-os": "Windows 10.0.0",
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
{Fore.CYAN}DATAHIVE AUTO BOT
{Fore.WHITE}By: FEBRIYAN
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

    def get_next_proxy_for_worker(self, worker_key):
        if worker_key not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[worker_key] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[worker_key]

    def rotate_proxy_for_worker(self, worker_key):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[worker_key] = proxy
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

    def ask_workers_count(self):
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        while True:
            try:
                count = input(f"{Fore.GREEN}How many workers per accounts : {Style.RESET_ALL}").strip()
                count = int(count)
                if 1 <= count <= 10:
                    self.workers_per_account = count
                    self.log(f"Set to {count} workers per account", "INFO")
                    return count
                else:
                    print(f"{Fore.RED}Please enter a number between 1 and 10.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input! Please enter a number.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}Program terminated by user.{Style.RESET_ALL}")
                exit(0)

    def get_worker_info(self, token, device_info, account_num, worker_num, email, proxy=None):
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

    def ping_uptime(self, token, device_info, account_num, worker_num, email, proxy=None):
        try:
            url = f"{self.base_url}/ping/uptime"
            headers = self.get_headers(token, device_info)
            proxies = {"http": proxy, "https": proxy} if proxy else None
            response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            if response.status_code == 200:
                data = response.json()
                uptime = data.get('uptime', 0)
                time_str = self.get_wib_time()
                print(f"[{time_str}] {Fore.GREEN}[SUCCESS] Worker #{worker_num} PING Success | Uptime: {uptime:.4f}{Style.RESET_ALL}")
                return True
            else:
                self.log(f"Worker #{worker_num} PING Failed: Status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Worker #{worker_num} PING Failed: {str(e)}", "ERROR")
            return False

    def check_worker_ip(self, token, device_info, account_num, worker_num, email, proxy=None):
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
                print(f"[{time_str}] {Fore.GREEN}[SUCCESS] Worker #{worker_num} IP: {ip} | Country: {country}{Style.RESET_ALL}")
                return True
            else:
                self.log(f"Worker #{worker_num} IP Check Failed: Status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Worker #{worker_num} IP Check Failed: {str(e)}", "ERROR")
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
        
        saved_devices = self.load_device_ids()
        self.log(f"Loaded {len(saved_devices)} saved device IDs", "INFO")
        
        tokens = self.load_accounts()
        if not tokens:
            self.log("No Accounts Loaded.", "ERROR")
            return
        
        self.ask_workers_count()
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
        
        self.log(f"Workers per account: {self.workers_per_account}", "INFO")
        
        if use_proxy:
            self.load_proxies()
        
        print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
        
        active_workers = []
        
        for i, token in enumerate(tokens, 1):
            try:
                temp_worker_key = f"account_{i}_temp"
                device_info_temp = self.get_device_info(temp_worker_key, saved_devices)
                
                url = f"{self.base_url}/worker"
                headers = self.get_headers(token, device_info_temp)
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    self.log(f"Account #{i} Failed to authenticate", "ERROR")
                    continue
                    
                worker_data = response.json()
                real_email = worker_data.get('user', {}).get('email', f'unknown{i}@email.com')
                
                self.log(f"Account #{i}/{len(tokens)} - {self.mask_email(real_email)}", "INFO")
                self.log(f"Setting up {self.workers_per_account} workers...", "INFO")
                
                points_24h = worker_data.get('points24h', 0)
                total_points = worker_data.get('user', {}).get('points', 0)
                
                account_key = f"account_{i}"
                self.account_points[account_key] = {
                    'initial_total': total_points,
                    'initial_24h': points_24h,
                    'current_total': total_points,
                    'current_24h': points_24h
                }
                
                for worker_idx in range(1, self.workers_per_account + 1):
                    worker_key = f"account_{i}_worker_{worker_idx}"
                    device_info = self.get_device_info(worker_key, saved_devices)
                    
                    proxy = self.get_next_proxy_for_worker(worker_key) if use_proxy else None
                    
                    try:
                        headers = self.get_headers(token, device_info)
                        proxies_dict = {"http": proxy, "https": proxy} if proxy else None
                        response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=30)
                        
                        if response.status_code != 200:
                            self.log(f"Worker #{worker_idx} Failed to initialize", "ERROR")
                            if rotate_proxy and use_proxy:
                                proxy = self.rotate_proxy_for_worker(worker_key)
                            continue
                            
                        worker_data = response.json()
                        server_device_id = worker_data.get('deviceId')
                        if server_device_id and server_device_id != device_info['device_id']:
                            self.log(f"Server assigned different ID, keeping ours", "WARNING")
                        
                        self.log(f"Worker #{worker_idx} initialized", "SUCCESS")
                        self.log(f"Device: {device_info['device_id'][:30]}...", "INFO")
                        if proxy:
                            self.log(f"Worker #{worker_idx} Proxy: {proxy}", "INFO")
                        
                        active_workers.append({
                            'account_num': i,
                            'worker_num': worker_idx,
                            'token': token,
                            'device_info': device_info,
                            'email': real_email,
                            'proxy': proxy,
                            'worker_key': worker_key
                        })
                        
                        time.sleep(1)
                        self.ping_uptime(token, device_info, i, worker_idx, real_email, proxy)
                        time.sleep(1)
                        self.check_worker_ip(token, device_info, i, worker_idx, real_email, proxy)
                        
                        if worker_idx < self.workers_per_account:
                            time.sleep(2)
                            
                    except Exception as e:
                        self.log(f"Worker #{worker_idx} Connection failed: {e}", "ERROR")
                        if rotate_proxy and use_proxy:
                            proxy = self.rotate_proxy_for_worker(worker_key)
                        continue
                
                time.sleep(1)
                self.get_worker_info(token, device_info_temp, i, 0, real_email, None)
                
                if i < len(tokens):
                    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
                    time.sleep(2)
                    
            except Exception as e:
                self.log(f"Account #{i} Setup failed: {e}", "ERROR")
                continue
        
        if not active_workers:
            self.log("No Active Workers.", "ERROR")
            return
        
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        self.log(f"Setup Complete | Active Workers: {len(active_workers)}", "INFO")
        self.log(f"Check dashboard: htps://dashboard.datahive.ai/", "SUCCESS")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
        
        cycle = 1
        
        try:
            while True:
                self.log(f"Cycle #{cycle} Started", "CYCLE")
                print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
                
                success_count = 0
                current_account = None
                
                for worker in active_workers:
                    account_num = worker['account_num']
                    worker_num = worker['worker_num']
                    worker_token = worker['token']
                    worker_device = worker['device_info']
                    worker_email = worker['email']
                    worker_proxy = worker.get('proxy')
                    worker_key = worker['worker_key']
                    
                    if current_account != account_num:
                        if current_account is not None:
                            time.sleep(1)
                            self.get_worker_info(worker_token, worker_device, current_account, 0, worker_email, None)
                            print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                        current_account = account_num
                        self.log(f"Account #{account_num} - {self.mask_email(worker_email)}", "INFO")
                    
                    self.log(f"Processing Worker #{worker_num}", "INFO")
                    if worker_proxy:
                        self.log(f"Proxy: {worker_proxy}", "INFO")
                    
                    time.sleep(1)
                    uptime_ok = self.ping_uptime(worker_token, worker_device, account_num, worker_num, worker_email, worker_proxy)
                    
                    if not uptime_ok and rotate_proxy and use_proxy:
                        new_proxy = self.rotate_proxy_for_worker(worker_key)
                        worker['proxy'] = new_proxy
                        worker_proxy = new_proxy
                        time.sleep(1)
                        uptime_ok = self.ping_uptime(worker_token, worker_device, account_num, worker_num, worker_email, worker_proxy)
                    
                    if uptime_ok:
                        time.sleep(1)
                        self.check_worker_ip(worker_token, worker_device, account_num, worker_num, worker_email, worker_proxy)
                        success_count += 1
                    
                    time.sleep(2)
                
                if active_workers:
                    last_worker = active_workers[-1]
                    time.sleep(1)
                    self.get_worker_info(last_worker['token'], last_worker['device_info'], last_worker['account_num'], 0, last_worker['email'], None)
                
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
