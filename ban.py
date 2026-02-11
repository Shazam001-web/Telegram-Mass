#!/usr/bin/env python3
"""
Telegram Mass Reporting Tool v3.1.7
"""

import os
import sys
import time
import random
import hashlib
import json
from datetime import datetime
import threading
import socket
import subprocess
import select
import signal

# Configuration
VERSION = "3.1.7"
CONFIG_FILE = "/data/data/com.termux/files/home/.tr_config"
SESSION_FILE = "/data/data/com.termux/files/home/.tr_session"
PROXY_LIST = "/data/data/com.termux/files/home/.tr_proxies"

class TerminalColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Progress bar colors
    PROGRESS_FILLED = '\033[42m\033[30m'  # Green background, black text
    PROGRESS_EMPTY = '\033[47m\033[30m'   # White background, black text
    PROGRESS_TEXT = '\033[97m\033[40m'    # White text, black background

class Logger:
    def __init__(self):
        self.log_file = f"/data/data/com.termux/files/home/tr_log_{int(time.time())}.log"
        
    def log(self, level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # Write to file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
            
        # Print to console
        if level == "ERROR":
            print(f"{TerminalColors.FAIL}{log_entry}{TerminalColors.ENDC}")
        elif level == "WARN":
            print(f"{TerminalColors.WARNING}{log_entry}{TerminalColors.ENDC}")
        elif level == "INFO":
            print(f"{TerminalColors.OKCYAN}{log_entry}{TerminalColors.ENDC}")
        elif level == "DEBUG":
            print(f"{TerminalColors.OKBLUE}{log_entry}{TerminalColors.ENDC}")
        else:
            print(log_entry)

class SystemCheck:
    def __init__(self):
        self.logger = Logger()
        
    def check_root(self):
        """Check for root permissions"""
        self.logger.log("DEBUG", "Initiating root permission check...")
        
        # Multiple root detection methods
        checks = [
            self._check_su_binary,
            self._check_uid,
            self._check_magisk,
            self._check_superuser_apps
        ]
        
        root_found = False
        for check in checks:
            if check():
                root_found = True
                break
                
        if not root_found:
            self.logger.log("ERROR", "Root access not detected")
            self.logger.log("INFO", "Attempting privilege escalation...")
            time.sleep(1)
            if self._attempt_privesc():
                return True
            return False
            
        self.logger.log("INFO", "Root access confirmed")
        return True
    
    def _check_su_binary(self):
        su_paths = [
            "/system/bin/su",
            "/system/xbin/su",
            "/sbin/su",
            "/vendor/bin/su",
            "/su/bin/su",
            "/magisk/.magisk"
        ]
        
        for path in su_paths:
            if os.path.exists(path):
                self.logger.log("DEBUG", f"Found SU binary at: {path}")
                return True
        return False
    
    def _check_uid(self):
        try:
            result = subprocess.run(['id'], capture_output=True, text=True, shell=True)
            if 'uid=0' in result.stdout:
                self.logger.log("DEBUG", "UID 0 (root) confirmed")
                return True
        except:
            pass
        return False
    
    def _check_magisk(self):
        magisk_paths = [
            "/data/adb/magisk",
            "/sbin/.magisk",
            "/dev/.magisk"
        ]
        
        for path in magisk_paths:
            if os.path.exists(path):
                self.logger.log("DEBUG", f"Magisk installation found at: {path}")
                return True
        return False
    
    def _check_superuser_apps(self):
        app_paths = [
            "/data/app/eu.chainfire.supersu",
            "/data/app/com.topjohnwu.magisk",
            "/data/app/com.noshufou.android.su",
            "/data/app/com.koushikdutta.superuser"
        ]
        
        for path in app_paths:
            if os.path.exists(path):
                self.logger.log("DEBUG", f"Superuser app found: {path}")
                return True
        return False
    
    def _attempt_privesc(self):
        """Simulate privilege escalation attempts"""
        self.logger.log("INFO", "Trying exploit: CVE-2021-0399")
        time.sleep(0.5)
        
        self.logger.log("INFO", "Trying exploit: DirtyPipe (CVE-2022-0847)")
        time.sleep(0.5)
        
        self.logger.log("INFO", "Trying exploit: Task Stack UAF")
        time.sleep(0.5)
        
        self.logger.log("WARN", "All privilege escalation attempts failed")
        return False
    
    def check_environment(self):
        """Check system environment"""
        self.logger.log("DEBUG", "Checking system environment...")
        
        # Check Termux
        if not os.path.exists("/data/data/com.termux/files/home"):
            self.logger.log("ERROR", "Termux environment not detected")
            return False
            
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.logger.log("ERROR", f"Python 3.8+ required (found {python_version.major}.{python_version.minor})")
            return False
            
        # Check available storage
        try:
            stat = os.statvfs('/data/data/com.termux/files/home')
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            if free_gb < 0.1:
                self.logger.log("WARN", f"Low storage space: {free_gb:.2f}GB free")
        except:
            pass
            
        self.logger.log("INFO", "Environment check passed")
        return True
    
    def check_telegram(self):
        """Check for Telegram installations"""
        self.logger.log("DEBUG", "Scanning for Telegram installations...")
        
        telegram_paths = [
            "/data/app/org.telegram.messenger",
            "/data/app/org.telegram.messenger.web",
            "/data/app/org.telegram.plus",
            "/data/app/com.telegram.messenger",
            "/data/app/com.wTelegram"
        ]
        
        found_clients = []
        for path in telegram_paths:
            if os.path.exists(path):
                client_name = path.split('/')[-1]
                found_clients.append(client_name)
                self.logger.log("DEBUG", f"Found Telegram client: {client_name}")
                
        if not found_clients:
            self.logger.log("WARN", "No Telegram installations found")
            return False
            
        self.logger.log("INFO", f"Found {len(found_clients)} Telegram client(s)")
        return True

class ProxyManager:
    def __init__(self):
        self.logger = Logger()
        self.proxies = []
        self.current_proxy = 0
        
    def load_proxies(self):
        """Load proxy list from file"""
        self.logger.log("DEBUG", "Loading proxy configuration...")
        
        # Try to load from file
        if os.path.exists(PROXY_LIST):
            try:
                with open(PROXY_LIST, 'r') as f:
                    lines = f.readlines()
                    self.proxies = [line.strip() for line in lines if line.strip()]
                self.logger.log("INFO", f"Loaded {len(self.proxies)} proxies from file")
            except:
                pass
                
        # Generate fake proxies if none loaded
        if not self.proxies:
            self._generate_proxies()
            
    def _generate_proxies(self):
        """Generate fake proxy list"""
        self.logger.log("INFO", "Generating proxy list...")
        
        proxy_types = ['socks5', 'http', 'https']
        for i in range(20):
            proxy_type = random.choice(proxy_types)
            ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            port = random.randint(8000, 65000)
            proxy = f"{proxy_type}://{ip}:{port}"
            self.proxies.append(proxy)
            
        # Save to file
        try:
            with open(PROXY_LIST, 'w') as f:
                for proxy in self.proxies:
                    f.write(proxy + "\n")
        except:
            pass
            
    def get_next_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_proxy]
        self.current_proxy = (self.current_proxy + 1) % len(self.proxies)
        return proxy
        
    def test_proxy(self, proxy):
        """Simulate proxy testing"""
        self.logger.log("DEBUG", f"Testing proxy: {proxy}")
        time.sleep(random.uniform(0.1, 0.5))
        
        # Random success/failure
        success = random.random() > 0.3
        if success:
            latency = random.uniform(50, 500)
            self.logger.log("DEBUG", f"Proxy OK - Latency: {latency:.0f}ms")
            return True
        else:
            self.logger.log("DEBUG", "Proxy failed")
            return False

class AccountManager:
    def __init__(self):
        self.logger = Logger()
        self.accounts = []
        
    def load_accounts(self):
        """Load/simulate Telegram accounts"""
        self.logger.log("DEBUG", "Loading account database...")
        
        # Simulate loading accounts from storage
        for i in range(random.randint(5, 15)):
            account_id = random.randint(1000000000, 9999999999)
            phone = f"+{random.randint(1, 999)}{random.randint(100000000, 999999999)}"
            session_hash = hashlib.md5(f"{account_id}{phone}".encode()).hexdigest()[:16]
            
            account = {
                'id': account_id,
                'phone': phone,
                'session': session_hash,
                'last_used': time.time() - random.randint(0, 86400*7),
                'status': random.choice(['active', 'limited', 'fresh'])
            }
            self.accounts.append(account)
            
        self.logger.log("INFO", f"Loaded {len(self.accounts)} accounts")
        
    def get_account_for_report(self):
        """Get account for reporting"""
        if not self.accounts:
            return None
            
        # Sort by last used
        self.accounts.sort(key=lambda x: x['last_used'])
        account = self.accounts[0]
        account['last_used'] = time.time()
        
        return account

class TelegramAPI:
    def __init__(self):
        self.logger = Logger()
        self.base_url = "https://api.telegram.org"
        self.report_endpoint = "/bot{token}/sendReport"
        
    def simulate_connection(self):
        """Simulate Telegram API connection"""
        self.logger.log("DEBUG", "Establishing connection to Telegram API...")
        
        # Simulate network handshake
        steps = [
            "Resolving hostname...",
            "Establishing TCP connection...",
            "Performing TLS handshake...",
            "Sending client hello...",
            "Receiving server hello...",
            "Exchanging keys...",
            "Connection established"
        ]
        
        for step in steps:
            time.sleep(random.uniform(0.05, 0.2))
            self.logger.log("DEBUG", step)
            
        return True
        
    def send_report(self, target, reason, account, proxy):
        """Simulate sending a report"""
        report_id = random.randint(1000000000000, 9999999999999)
        
        # Simulate API request
        request_data = {
            'target': target,
            'reason': reason,
            'account_id': account['id'],
            'session_hash': account['session'],
            'user_agent': f'Telegram-Android {random.choice(["8.7", "9.1", "9.3"])}',
            'device_model': random.choice(['SM-G998B', 'Pixel 6', 'iPhone13,3']),
            'system_version': f'Android {random.choice(["11", "12", "13"])}',
            'timestamp': int(time.time()),
            'report_id': report_id
        }
        
        # Simulate network delay
        time.sleep(random.uniform(0.1, 0.8))
        
        # Random response
        success = random.random() > 0.15  # 85% success rate
        
        if success:
            return {
                'success': True,
                'report_id': report_id,
                'response_time': random.uniform(50, 300),
                'message': 'Report submitted successfully'
            }
        else:
            return {
                'success': False,
                'error_code': random.choice([429, 500, 503, 403]),
                'error_message': random.choice([
                    'Too many requests',
                    'Internal server error',
                    'Service unavailable',
                    'Access denied'
                ]),
                'retry_after': random.randint(5, 60)
            }

class MassReporter:
    def __init__(self):
        self.logger = Logger()
        self.system = SystemCheck()
        self.proxy_manager = ProxyManager()
        self.account_manager = AccountManager()
        self.api = TelegramAPI()
        
        self.report_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.start_time = 0
        
    def show_banner(self):
        """Display tool banner"""
        os.system('clear')
        
        banner = f"""
{TerminalColors.OKCYAN}{TerminalColors.BOLD}
████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ███╗   ███╗
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
   ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██╔████╔██║
   ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║
   ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
                                                                     
               Mass Reporting System v{VERSION}
               {TerminalColors.WARNING}● Root Required ● Stealth Mode ● Multi-Proxy ●
{TerminalColors.ENDC}
"""
        print(banner)
        
    def initialize(self):
        """Initialize the tool"""
        self.logger.log("INFO", "Initializing Telegram Mass Reporting System...")
        
        # Check system
        if not self.system.check_environment():
            self.logger.log("ERROR", "System check failed")
            return False
            
        if not self.system.check_root():
            self.logger.log("ERROR", "Root access required")
            return False
            
        if not self.system.check_telegram():
            self.logger.log("WARN", "No Telegram clients found, but continuing...")
            
        # Load configurations
        self.proxy_manager.load_proxies()
        self.account_manager.load_accounts()
        
        # Test API connection
        if not self.api.simulate_connection():
            self.logger.log("ERROR", "Cannot connect to Telegram API")
            return False
            
        self.logger.log("INFO", "Initialization complete")
        return True
        
    def get_user_input(self):
        """Get target information from user"""
        print(f"\n{TerminalColors.OKGREEN}[{TerminalColors.BOLD}CONFIG{TerminalColors.ENDC}{TerminalColors.OKGREEN}]{TerminalColors.ENDC} Report Configuration\n")
        
        # Target
        target = input(f"{TerminalColors.WARNING}[?]{TerminalColors.ENDC} Target (username/user_id/link): ")
        if not target:
            target = f"user_{random.randint(1000000, 9999999)}"
            
        # Reason
        print(f"\n{TerminalColors.WARNING}[?]{TerminalColors.ENDC} Select report reason:")
        reasons = [
            "1. Spam",
            "2. Violence",
            "3. Pornography",
            "4. Child Abuse",
            "5. Illegal Content",
            "6. Copyright",
            "7. Fake Account",
            "8. Impersonation",
            "9. Terrorism",
            "10. Custom"
        ]
        
        for reason in reasons:
            print(f"   {reason}")
            
        while True:
            try:
                choice = int(input(f"\n{TerminalColors.WARNING}[>]{TerminalColors.ENDC} Choice (1-10): "))
                if 1 <= choice <= 10:
                    if choice == 10:
                        custom = input(f"{TerminalColors.WARNING}[?]{TerminalColors.ENDC} Custom reason: ")
                        reason = custom if custom else "Violation of Terms of Service"
                    else:
                        reason = reasons[choice-1].split('. ')[1]
                    break
            except:
                pass
            print(f"{TerminalColors.FAIL}[!]{TerminalColors.ENDC} Invalid choice")
            
        # Report count
        while True:
            try:
                count = int(input(f"\n{TerminalColors.WARNING}[?]{TerminalColors.ENDC} Number of reports (1-500): "))
                if 1 <= count <= 500:
                    break
            except:
                pass
            print(f"{TerminalColors.FAIL}[!]{TerminalColors.ENDC} Enter number 1-500")
            
        # Delay
        delay = 0.5
        try:
            custom_delay = float(input(f"{TerminalColors.WARNING}[?]{TerminalColors.ENDC} Delay between reports (0.1-5.0s) [0.5]: "))
            if 0.1 <= custom_delay <= 5.0:
                delay = custom_delay
        except:
            pass
            
        # Confirm
        print(f"\n{TerminalColors.OKGREEN}[{TerminalColors.BOLD}SUMMARY{TerminalColors.ENDC}{TerminalColors.OKGREEN}]{TerminalColors.ENDC}")
        print(f"   Target: {target}")
        print(f"   Reason: {reason}")
        print(f"   Reports: {count}")
        print(f"   Delay: {delay}s")
        
        confirm = input(f"\n{TerminalColors.WARNING}[?]{TerminalColors.ENDC} Start mass reporting? (y/N): ")
        return target, reason, count, delay if confirm.lower() in ['y', 'yes'] else (None, None, None, None)
        
    def show_progress(self, current, total, stats):
        """Display progress bar"""
        width = 40
        filled = int(width * current / total)
        bar = f"{TerminalColors.PROGRESS_FILLED}{'█' * filled}{TerminalColors.ENDC}"
        bar += f"{TerminalColors.PROGRESS_EMPTY}{'░' * (width - filled)}{TerminalColors.ENDC}"
        
        percent = (current / total) * 100
        
        stats_text = (f"Success: {TerminalColors.OKGREEN}{stats['success']}{TerminalColors.ENDC} | "
                      f"Failed: {TerminalColors.FAIL}{stats['failed']}{TerminalColors.ENDC} | "
                      f"Proxies: {stats['proxies']}")
                      
        print(f"\r{TerminalColors.PROGRESS_TEXT}[{current:03d}/{total:03d}]{TerminalColors.ENDC} {bar} {percent:5.1f}% | {stats_text}", end='', flush=True)
        
    def run_mass_report(self, target, reason, count, delay):
        """Execute mass reporting"""
        self.start_time = time.time()
        self.report_count = 0
        self.success_count = 0
        self.failed_count = 0
        
        print(f"\n{TerminalColors.OKGREEN}[{TerminalColors.BOLD}START{TerminalColors.ENDC}{TerminalColors.OKGREEN}]{TerminalColors.ENDC} Starting mass reporting...\n")
        
        # Statistics
        used_proxies = set()
        errors = {}
        retry_queue = []
        
        for i in range(count):
            # Get account and proxy
            account = self.account_manager.get_account_for_report()
            proxy = self.proxy_manager.get_next_proxy()
            
            if proxy not in used_proxies:
                # Test new proxy
       
