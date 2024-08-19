import sys
import os
import time
from selenium import webdriver
import colorama
from colorama import Fore

colorama.init(autoreset=True)

def list_user_names(entities_path):
    """List all user names from the entities directory who have cookies."""
    users_with_cookies = []
    for d in os.listdir(entities_path):
        user_path = os.path.join(entities_path, d)
        if os.path.isdir(user_path) and list_cookie_files(user_path):
            users_with_cookies.append(d)
    return users_with_cookies

def list_cookie_files(user_path):
    """List all cookie files in the user directory."""
    cookies_path = os.path.join(user_path, 'cookies')
    if not os.path.exists(cookies_path):
        return []
    return [f for f in os.listdir(cookies_path) if f.endswith('.txt')]

def prompt_for_custom_cookies():
    """Prompt user for custom cookies."""
    cookies = []
    while True:
        name = input(Fore.CYAN + 'Enter cookie name (or type "done" to finish): ' + Fore.WHITE).strip()
        if name.lower() == 'done':
            break
        value = input(Fore.CYAN + f'Enter value for {name}: ' + Fore.WHITE).strip()
        print('\n')
        cookies.append((name, value))
    return cookies

def prompt_for_option():
    """Prompt user to select the option to use cookies from a file or manually input them."""
    print(Fore.GREEN + 'Do you want to use custom cookies or select from existing files?')
    print(Fore.GREEN + '1) ' + Fore.WHITE + 'Custom Cookies')
    print(Fore.GREEN + '2) ' + Fore.WHITE + 'Existing Cookies')

    choice = input('Type option: ' + Fore.GREEN).strip()
    print('\n')
    if choice == '1':
        return 'custom', []
    elif choice == '2':
        return 'existing', []
    else:
        print(Fore.RED + 'Invalid option selected!' + Fore.WHITE)
        sys.exit(1)

def get_cookies_from_file(file_path):
    """Read cookies and URL from a file."""
    cookies = []
    url = None
    if not os.path.exists(file_path):
        print(Fore.RED + f'File does not exist: {file_path}' + Fore.WHITE)
        return url, cookies
    
    with open(file_path, 'r', encoding='utf-8') as fp:
        first_line = fp.readline().strip()
        if first_line.startswith('url='):
            url = first_line[len('url='):].strip()
        
        for line in fp:
            line = line.strip()
            if '=' in line:
                name, value = line.split('=', 1)
                cookies.append((name.strip(), value.strip()))
    
    return url, cookies

def get_domain_from_url(url):
    """Extract domain from a URL."""
    return url.split('/')[2]

def load_cookies(browser, cookies, domain):
    """Load cookies into the browser."""
    for name, value in cookies:
        browser.add_cookie({"name": name, "domain": domain, "value": value})
    browser.refresh()

def main():
    # Check if a file path argument was provided
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
        url, cookies = get_cookies_from_file(file_path)
        if not url:
            print(Fore.RED + 'No URL found in the cookie file!' + Fore.WHITE)
            sys.exit(1)
    else:
        # Normal prompt workflow
        print(Fore.GREEN + 'Select an option:')
        option, cookies = prompt_for_option()
        
        if option == 'existing':
            entities_path = 'entities'
            user_names = list_user_names(entities_path)
            
            if not user_names:
                print(Fore.RED + 'No users with cookies found!' + Fore.WHITE)
                sys.exit(1)
            
            print(Fore.GREEN + 'Available user names:')
            for idx, user in enumerate(user_names):
                print(Fore.GREEN + f'{idx + 1}) ' + Fore.WHITE + user)
            
            user_choice = int(input('Select user number: ')) - 1
            if 0 <= user_choice < len(user_names):
                user_name = user_names[user_choice]
            else:
                print(Fore.RED + 'Invalid user choice!' + Fore.WHITE)
                sys.exit(1)

            user_path = os.path.join(entities_path, user_name)
            available_files = list_cookie_files(user_path)
            
            if not available_files:
                print(Fore.RED + 'No cookie files found for the selected user!' + Fore.WHITE)
                sys.exit(1)
            
            print(Fore.GREEN + 'Available cookie files:')
            for idx, file in enumerate(available_files):
                print(Fore.GREEN + f'{idx + 1}) ' + Fore.WHITE + file.replace('.txt', ''))
            
            file_choice = int(input('Select file number: ')) - 1
            if 0 <= file_choice < len(available_files):
                selected_file = available_files[file_choice]
            else:
                print(Fore.RED + 'Invalid file choice!' + Fore.WHITE)
                sys.exit(1)

            file_path = os.path.join(user_path, 'cookies', selected_file)
            url, cookies = get_cookies_from_file(file_path)
            if not url:
                print(Fore.RED + 'No URL found in the cookie file!' + Fore.WHITE)
                sys.exit(1)
        elif option == 'custom':
            cookies = prompt_for_custom_cookies()
            print('\n')
            url = input(Fore.GREEN + 'Enter the URL to load cookies for: ' + Fore.WHITE).strip()
        else:
            print(Fore.RED + 'Invalid option!' + Fore.WHITE)
            sys.exit(1)

    if not cookies:
        print(Fore.RED + 'No cookies provided or file is empty!' + Fore.WHITE)
        sys.exit(1)

    domain = get_domain_from_url(url)
    
    browser = webdriver.Chrome()
    browser.get(url)
    load_cookies(browser, cookies, domain)
    
    # Keep the browser open for a long period to test cookies
    print(Fore.GREEN + 'Cookies loaded successfully. Keeping browser open...')
    time.sleep(99999)

if __name__ == "__main__":
    os.system('cls')
    main()
