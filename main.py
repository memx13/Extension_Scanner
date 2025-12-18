import requests
import threading
from queue import Queue
from colorama import Fore, Style, init
import time
import sys

# Renklendirmeyi başlat
init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.CYAN}======================================================================
    {Fore.YELLOW}SIBERTIM SENSITIVE SCANNER (SSS) - v1.0
    {Fore.WHITE}Geliştiren: @sibertim | Nesil Güvenlik Staj Projesi
{Fore.CYAN}======================================================================
{Fore.MAGENTA}DURUM KODLARI NE ANLAMA GELİR?
{Fore.GREEN}[200 OK]: {Fore.WHITE}Dosya bulundu ve ERİŞİLEBİLİR! Veri sızıntısı riski çok yüksek.
{Fore.RED}[403 FORBIDDEN]: {Fore.WHITE}Dosya orada var ama sunucu girişi engelliyor. (WAF veya İzinler)
{Fore.BLUE}[401 UNAUTHORIZED]: {Fore.WHITE}Dosya var ama giriş için kullanıcı adı/şifre lazım.
{Fore.CYAN}======================================================================
    """
    print(banner)

# --- GENİŞLETİLMİŞ WORDLIST ---
SENSITIVE_PATHS = [
    "/.env", "/.env.local", "/.env.bak", "/.git/config", "/.git/index", "/.gitignore",
    "/config.php", "/config.php.bak", "/config.php.old", "/wp-config.php", "/wp-config.php.bak",
    "/database.sql", "/backup.sql", "/db.sql", "/backup.zip", "/site.zip", "/admin/",
    "/phpinfo.php", "/.ssh/id_rsa", "/.htaccess", "/server-status", "/composer.json",
    "/Dockerfile", "/docker-compose.yml", "/.svn/entries", "/.bash_history"
]

def scan_worker(url_base, q, lock):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SiberTim-Scanner/1.0'}
    
    while not q.empty():
        path = q.get()
        target = f"{url_base}{path}"
        
        try:
            # allow_redirects=False: Sunucunun bizi ana sayfaya yönlendirmesini engelleriz, gerçek sonucu görürüz
            response = requests.get(target, headers=headers, timeout=7, allow_redirects=False)
            
            with lock:
                if response.status_code == 200:
                    print(f"{Fore.GREEN}[+] 200 OK | {Fore.WHITE}KRİTİK: {target} {Fore.GREEN}(İçerik okunabilir!)")
                elif response.status_code == 403:
                    print(f"{Fore.RED}[!] 403 FORBIDDEN | {Fore.WHITE}TESPİT EDİLDİ: {target} {Fore.RED}(Erişim engelli ama dosya mevcut!)")
                elif response.status_code == 401:
                    print(f"{Fore.BLUE}[?] 401 UNAUTHORIZED | {Fore.WHITE}DOĞRULAMA GEREKLİ: {target} {Fore.BLUE}(Giriş paneli olabilir.)")
                # 404 (Bulunamadı) durumlarını ekranı kirletmemesi için yazdırmıyoruz
                
        except Exception:
            pass
        finally:
            q.task_done()

def main():
    print_banner()
    
    target_input = input(f"{Fore.YELLOW}Hedef URL girin (Örn: https://hedefsite.com): {Style.RESET_ALL}").strip()
    
    # URL Kontrolü
    if not target_input.startswith("http"):
        print(f"{Fore.RED}Hata: URL 'http://' veya 'https://' ile başlamalıdır!")
        time.sleep(3)
        return

    url_base = target_input.rstrip("/")
    
    print(f"\n{Fore.CYAN}[*] Tarama başlatıldı... Lütfen bekleyin.\n")
    
    path_queue = Queue()
    for path in SENSITIVE_PATHS:
        path_queue.put(path)

    lock = threading.Lock()
    threads = []
    
    # 10 Thread ile hızlı tarama
    for _ in range(10):
        t = threading.Thread(target=scan_worker, args=(url_base, path_queue, lock))
        t.daemon = True
        t.start()
        threads.append(t)

    path_queue.join()
    
    print(f"\n{Fore.CYAN}======================================================================")
    print(f"{Fore.YELLOW}[*] Tarama başarıyla tamamlandı. #SiberTim")
    print(f"{Fore.CYAN}======================================================================")
    input(f"\n{Fore.WHITE}Çıkmak için ENTER tuşuna basın...")

if __name__ == "__main__":
    main()