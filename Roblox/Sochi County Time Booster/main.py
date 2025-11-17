import os
import sys
cmdWriter = sys.stdout.write
import psutil
import subprocess
import asyncio
import aiofiles
import threading
import logging
import math
import random
import typing
from re                        import compile, search
from datetime                  import datetime
from aiohttp                   import ClientSession, ClientResponse, ClientOSError, ServerDisconnectedError
from aiohttp.http_exceptions   import TransferEncodingError
from aiohttp.client_exceptions import ClientPayloadError
from urllib.parse              import quote
import colorama;               colorama.init()

def cls() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

# Exceptions

class RobloxException(Exception):
    ...

class InvalidCookie(RobloxException):
    def __init__(self, message: str = 'Invalid cookie') -> None:
        super().__init__(message)

class AccountBanned(RobloxException):
    def __init__(self, message: str = 'Account banned') -> None:
        super().__init__(message)

class RegisteredEarlier1Week(RobloxException):
    def __init__(self, message: str = 'Account registered earlier 1 week') -> None:
        super().__init__(message)

# Colors

class ANSI:
    # color
    RED    = '\033[31m'
    GREEN  = '\033[32m'
    YELLOW = '\033[33m'
    BLUE   = '\033[34m'
    PURPLE = '\033[35m'
    CYAN   = '\033[36m'
    WHITE  = '\033[37m'
    GRAY   = '\033[90m'
    PINK   = '\033[95m'
    # decor
    BOLD   = '\033[1m'
    # other
    CLEAR  = '\033[0m'

# Preload

DATE_OF_CHECK = datetime.now().strftime('%d.%m.%Y - %H.%M.%S')
os.makedirs('Results', exist_ok=True)

# Logger

os.makedirs('Logs', exist_ok=True)
logging.basicConfig(filename=os.path.join('Logs', f'log {DATE_OF_CHECK}.log'), level=logging.DEBUG, encoding='utf-8', errors='ignore')

# Settings (RM - Recovery Mode, in most cases, you only need these settings)

PATH_TO_LAUNCHER = r'%LOCALAPPDATA%\Fishstrap\Fishstrap.exe'
if not os.path.exists(PATH_TO_LAUNCHER):
    print(f'\n  [!] File: {PATH_TO_LAUNCHER} doesn\'t exists...')
    input('\n  Press Enter to close the program...')
    sys.exit()
# For Bloxstrap: %LOCALAPPDATA%\Bloxstrap\Bloxstrap.exe
# For default roblox: C:\Program Files (x86)\Roblox\Versions\version-YOUR_VERSION\RobloxPlayerBeta.exe

MULTI_ROBLOX = False # !!! Not recommended. Use Fishstrap launcher: https://github.com/fishstrap/fishstrap
# ---
RECOVERY_MODE = True # RM
MAIN_FILENAME = 'cookies_recovery.txt' if RECOVERY_MODE else 'cookies_recovered.txt'
FORCE_JOIN_IF_ALREADY_FARMING = False
CHECK_PLACE_PLAYER_IN = False
FORCE_JOIN_IF_IN_OTHER_PLACE = True
# ---
COOKIES_LIMIT_PER_ONCE = 3 # RM
WAIT_TIME_AFTER_EVERY_LAUNCH = 20
# ---
AUTO_RETRY = False # RM
RETRY_TIME = 30
# ---
MINIMUM_ACCOUNT_AGE_IN_DAYS = 7
# ---
PLACE_IDS = {
    "SC": 98968727637776 # Sochi County
}
BADGE_IDS = {
    "SC": 3926591862400476 # 1 hour played
}
PLACE_NAME = "SC"
PLACE_ID = PLACE_IDS.get(PLACE_NAME)
if not PLACE_ID:
    print(f'\n  [!] You need to specify place ID')
    input('\n  Press Enter to close the program...')
    sys.exit()
BADGE_ID = BADGE_IDS.get(PLACE_NAME)
REMOVE_COOKIES_WITH_BADGE = True
SKIP_COOKIES_WITH_BADGE = False # RM
JOIN_TO_FRIENDS = False
# ---
VOTE_PLACE = False # !!! Doesn't work, challenge bypass needed
VOTE_PLACE_LIKE = True # True: Like, False: Dislike, None: Nothing
REMOVE_COOKIES_IF_VOTED_PLACE = True
SKIP_COOKIES_IF_VOTED_PLACE = True
# ---

isRandomServerId = None
while isRandomServerId not in ('+', '-'):
    isRandomServerId = input(f'\n  [?] Enable random server IDs?\n\n  [+] Yes\n  [-] No\n\n  [<] Enter a value: ').strip()
    match isRandomServerId:
        case '+':
            RANDOM_SERVER_ID = True
        case '-':
            RANDOM_SERVER_ID = False
    cls()
    cmdWriter(ANSI.BOLD)

SHOW_ONLY_SERVERS_WHERE_FRIENDS = False
SERVERS_PER_PAGE = 50 # Don't do above 50, might be broken
SERVER_IDS_API = f'https://games.roblox.com/v1/games/{PLACE_ID}/servers/{int(SHOW_ONLY_SERVERS_WHERE_FRIENDS)}?sortOrder=1&excludeFullGames=true&limit={SERVERS_PER_PAGE}'
SERVER_IDS = {
    'static': '', # Priority (optional)
    'dynamic': None # You don't have to change that
}
AVOID_SERVER_IDS = []
# ---
processes: dict[str, subprocess.Popen] = {}

# Server IDs: https://games.roblox.com/v1/games/98968727637776/servers/1?sortOrder=1&excludeFullGames=true&limit=50
#                                                                      ^
#                                                                      | 1 - Only servers where the friends are
#                                                                      | 0 - All

# Patterns

COOKIE_PATTERN = compile(
    r'_\|(?:_|[^\s\r\n]*?\|_)\S{100,}'
)

# Functions

def create_start_files() -> None:
    START_FILES = [
        'cookies_recovery.txt',
        'cookies_recovered.txt'
    ]

    for file in START_FILES:
        os.makedirs(file, exist_ok=True)

async def remove_lines(amount: int) -> None:
    if amount:
        cmdWriter(f'\033[{amount}A\033[J')

async def get_cookies_from_file_roblox(path_to_cookies: str) -> list[str] | None:
    cookies_list = []
    try:
        with open(path_to_cookies, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                cookie = search(COOKIE_PATTERN, line.strip())
                if cookie and cookie not in cookies_list:
                    cookies_list.append(cookie.group(0))
        return cookies_list
    except Exception as e:
        logging.exception(e)

def multi_roblox():
    if not MULTI_ROBLOX:
        return

    def roblox_m():
        try:
            import win32event
        except Exception as e:
            logging.exception(e)
            return 1
        mutex_name = 'ROBLOX_singletonMutex'
        mutex = win32event.CreateMutex(None, 1, mutex_name)

        done, oof = 9e9, 0
        while done > oof:
            pass

        win32event.ReleaseMutex(mutex)

    multi_thread = threading.Thread(target=roblox_m)
    multi_thread.start()
    return 0

async def send_get_request_roblox(url: str, *, cookies: str, headers: dict = None) -> dict:
    while True:
        try:
            async with ClientSession(cookies=cookies, headers=headers) as session:
                response = await session.get(url, allow_redirects=False, timeout=5, ssl=False)
                match response.status:
                    case 200:
                        return await response.json()
                    case 204:
                        return False
                    case 302 | 401:
                        raise InvalidCookie
                    case 403:
                        raise AccountBanned
                    case _:
                        logging.debug(f'< [DEBUG] [GET_REQUEST_ROBLOX] > URL: {url} | Code: {response.status}')
                        await asyncio.sleep(5)
        except (InvalidCookie, AccountBanned):
            raise
        except (TimeoutError, ClientOSError, ConnectionResetError, ServerDisconnectedError, TransferEncodingError, ClientPayloadError) as e:
            logging.exception(f'< [GET_REQUEST_ROBLOX] > Error: {e}')
            await asyncio.sleep(5)
        except Exception as e:
            logging.exception(f'< [GET_REQUEST_ROBLOX] > Error: {e}')
            await asyncio.sleep(5)

async def send_post_request_roblox(url: str, *, returnIt: typing.Literal['HEADERS', 'JSON', 'ALL'] = 'ALL', cookies: dict, headers: dict = None, data: dict = None, json: dict = None) -> ClientResponse:
    while True:
        try:
            async with ClientSession(cookies=cookies, headers=headers) as session:
                response = await session.post(url, data=data, json=json, timeout=5, ssl=False)
                match response.status:
                    case 200 | 403:
                        match returnIt:
                            case 'HEADERS' : return response.headers
                            case 'JSON'    : return await response.json()
                            case _         : return response
                    case 401:
                        raise InvalidCookie
                    case _:
                        logging.debug(f'< [DEBUG] [POST_REQUEST_ROBLOX] > URL: {response.url} | Code: {response.status}')
                        await asyncio.sleep(5)
        except InvalidCookie:
            raise
        except (TimeoutError, ClientOSError, ConnectionResetError, ServerDisconnectedError, TransferEncodingError, ClientPayloadError) as e:
            logging.exception(f'< [POST_REQUEST_ROBLOX] > Error: {e}')
            await asyncio.sleep(5)
        except Exception as e:
            logging.exception(f'< [POST_REQUEST_ROBLOX] > Error: {e}')
            await asyncio.sleep(5)

async def vote_place(cookies: dict, place_id: str, isLike: bool | None = True):
    action = 'null' if isLike is None else 'true' if isLike else 'false'
    headers = {
        'X-CSRF-Token': await get_x_csrf_token(cookies)
    }
    return await send_post_request_roblox(f'https://apis.roblox.com/voting-api/vote/asset/{place_id}?vote={action}', cookies=cookies, headers=headers)

async def get_user_data(cookies: dict) -> dict:
    return await send_get_request_roblox('https://www.roblox.com/my/settings/json', cookies=cookies)

async def get_user_achieved_badge(user_id: int, badge_id: int, cookies: dict) -> bool:
    return bool(await send_get_request_roblox(f'https://badges.roblox.com/v1/users/{user_id}/badges/{badge_id}/awarded-date', cookies=cookies))

async def get_place_id_user_in(user_id: int, cookies: dict) -> int:
    data = {
        'userIds': [user_id]
    }
    return (await send_post_request_roblox('https://presence.roblox.com/v1/presence/users', returnIt='JSON', cookies=cookies, data=data))['userPresences'][0]['placeId']

async def get_x_csrf_token(cookies: dict) -> str:
    return (await send_post_request_roblox('https://auth.roblox.com/v2/logout', returnIt='HEADERS', cookies=cookies))['X-CSRF-Token']

async def get_auth_ticket(cookies: dict) -> str:
    return (await send_post_request_roblox('https://auth.roblox.com/v1/authentication-ticket', returnIt='HEADERS', cookies=cookies, headers={'X-CSRF-Token': await get_x_csrf_token(cookies), 'referer': 'https://www.roblox.com/hewhewhew'}))['rbx-authentication-ticket']

async def get_job_id() -> str:
    if SERVER_IDS['static']:
        return SERVER_IDS['static']

    if SERVER_IDS['dynamic'] and not RANDOM_SERVER_ID:
        return SERVER_IDS['dynamic']

    server_id = None
    data = (await send_get_request_roblox(f'https://games.roblox.com/v1/games/{PLACE_ID}/servers/{'1' if JOIN_TO_FRIENDS else '0'}?sortOrder=1&excludeFullGames=true&limit=50', cookies=None))['data']
    if RANDOM_SERVER_ID:
        while not server_id or server_id in AVOID_SERVER_IDS:
            if 0 < len(data) - 1:
                server_id = data[random.randint(0, len(data) - 1)]['id']
            else:
                server_id = data[0]['id']
    else:
        i = 0
        while not server_id or server_id in AVOID_SERVER_IDS:
            server_id = data[i]['id']
            i += 1
    cmdWriter(f'  [{ANSI.CYAN}>{ANSI.WHITE}] Server ID: {server_id}\n{'\n' if not RANDOM_SERVER_ID else ''}')
    SERVER_IDS['dynamic'] = server_id
    return server_id

async def get_child_processes(pid: int) -> list[psutil.Process]:
    try:
        parent = psutil.Process(pid)
        return parent.children(recursive=True)
    except psutil.NoSuchProcess:
        return []

async def taskkill(user_id: str) -> None:
    if user_id in processes:
        subprocess.run(
            ['taskkill', '/f', '/pid', processes[user_id]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        logging.info(f'[{processes[user_id]}] Убили процесс с ключом {user_id}')
        del processes[user_id]
    else:
        logging.error(f'[?] Не удалось убить процесс с ключом {user_id} так как его не существует')

async def launch_roblox(cookies: dict, server_id: int | str, user_id: str) -> None:
    launch_time = math.floor((datetime.now() - datetime(1970, 1, 1)).total_seconds() * 1000)
    browser_tracker_id = str(random.randint(100000, 175000)) + str(random.randint(100000, 900000))

    launch_url = f'https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGame&placeId={PLACE_ID}&gameId={server_id}&isPlayTogetherGame=true&isTeleport=true'
    encoded_launch_url = quote(launch_url)

    arguments = f'roblox-player:1+launchmode:play+gameinfo:{await get_auth_ticket(cookies)}+launchtime:{launch_time}+placelauncherurl:{encoded_launch_url}+browsertrackerid:{browser_tracker_id}+robloxLocale:en_us+gameLocale:en_us+channel:+LaunchExp:InApp'

    if sys.platform.startswith('win'):
        await taskkill(user_id)
        process = subprocess.Popen([os.path.expandvars(PATH_TO_LAUNCHER), arguments])
        logging.info(f'Запустили новый процесс, ID: {process.pid}')
        while True:
            child_processes = await get_child_processes(process.pid)
            if not child_processes:
                await asyncio.sleep(0.2)
                continue
            
            for child_process in child_processes:
                if 'robloxplayerbeta' in child_process.name().lower():
                    processes[user_id] = str(child_process.pid)
                    logging.info(f'Обнаружен процесс [{child_process.pid}]: {child_process.name()}')
            else:
                break
    return True

EXCEPTIONS = [AccountBanned, InvalidCookie, RegisteredEarlier1Week]

def exceptionsHandler(e: AccountBanned | InvalidCookie | RegisteredEarlier1Week, counter: int, indent: int, part_of_cookie: str) -> typing.Optional[dict[str, str]]:
    EXCEPTIONSS_DATA = {
        AccountBanned: {
            'cmdMessage': f'  [{ANSI.RED}>{ANSI.WHITE}] {ANSI.PINK}#{counter:<{indent}}{ANSI.WHITE}: {part_of_cookie} {ANSI.RED}>{ANSI.WHITE} Account banned\n',
            'loggerMessage': f'Cookie: {part_of_cookie} > Account banned'
        },
        InvalidCookie: {
            'cmdMessage': f'  [{ANSI.RED}>{ANSI.WHITE}] {ANSI.PINK}#{counter:<{indent}}{ANSI.WHITE}: {part_of_cookie} {ANSI.RED}>{ANSI.WHITE} Invalid cookie\n',
            'loggerMessage': f'Cookie: {part_of_cookie} > Invalid cookie'
        },
        RegisteredEarlier1Week: {
            'cmdMessage': f'  [{ANSI.RED}>{ANSI.WHITE}] {ANSI.PINK}#{counter:<{indent}}{ANSI.WHITE}: {part_of_cookie} {ANSI.RED}>{ANSI.WHITE} Reg. <{MINIMUM_ACCOUNT_AGE_IN_DAYS} days\n',
            'loggerMessage': f'Cookie: {part_of_cookie} > Reg. <{MINIMUM_ACCOUNT_AGE_IN_DAYS} days'
        }
    }
    return EXCEPTIONSS_DATA[e]

async def main():
    if not PLACE_ID:
        input(f'  [{ANSI.CYAN}>{ANSI.WHITE}] Place ID not found')
        sys.exit()

    multi_roblox_enabled = multi_roblox()

    try:
        cmdWriter(f'''
  [{ANSI.YELLOW}?{ANSI.WHITE}] Multi-Roblox: {ANSI.CYAN}{f'Enabled {ANSI.RED}(Not recommended, use Fishstrap launcher)' if multi_roblox_enabled == 0 else f'Disabled {ANSI.RED}(Module error: win32event)' if multi_roblox_enabled == 1 else 'Disabled'}{ANSI.WHITE}

  [{ANSI.YELLOW}?{ANSI.WHITE}] Limit per once: {ANSI.CYAN}{COOKIES_LIMIT_PER_ONCE}{ANSI.WHITE}

  [{ANSI.YELLOW}?{ANSI.WHITE}] Place ID: {ANSI.CYAN}{PLACE_ID}{ANSI.WHITE}
  [{ANSI.YELLOW}?{ANSI.WHITE}] Random server ID: {ANSI.CYAN}{'Enabled' if RANDOM_SERVER_ID else 'Disabled'}{ANSI.WHITE}
  [{ANSI.YELLOW}?{ANSI.WHITE}] Badge ID: {ANSI.CYAN}{BADGE_ID if BADGE_ID else 'No'}{ANSI.WHITE}
  [{ANSI.YELLOW}?{ANSI.WHITE}] Skip with badge: {ANSI.CYAN}{'Enabled' if SKIP_COOKIES_WITH_BADGE else 'Disabled'}{ANSI.WHITE}

  [{ANSI.YELLOW}?{ANSI.WHITE}] Auto-Retry: {ANSI.CYAN}{'Enabled' if AUTO_RETRY else 'Disabled'}{ANSI.WHITE}
\n''')

        cookies_buffer = []
        cookies_from_file = await get_cookies_from_file_roblox(MAIN_FILENAME)

        if not cookies_from_file:
            input(f'  [{ANSI.CYAN}>{ANSI.WHITE}] No cookies found')
            sys.exit()

        i = 0
        while i < len(cookies_from_file) or cookies_buffer:
            if i < len(cookies_from_file):
                cookie_buffer = cookies_from_file[i]
                i += 1
                cookies_buffer.append(cookie_buffer)
                cmdWriter(f'  [{ANSI.CYAN}>{ANSI.WHITE}] Added cookie in pool: {cookie_buffer[115:130]}...{cookie_buffer[-15:-1]}\n')
                if cookies_from_file and len(cookies_buffer) < COOKIES_LIMIT_PER_ONCE:
                    continue

            cmdWriter('\n')

            amount_of_cookies_in_buffer = len(cookies_buffer)
            indent = len(str(amount_of_cookies_in_buffer)) + 1
            while len(cookies_buffer) == amount_of_cookies_in_buffer or (i >= len(cookies_from_file) and cookies_buffer):
                j = 0
                counter = 0
                while j < len(cookies_buffer):
                    counter += 1
                    cookie = cookies_buffer[j]
                    j += 1
                    part_of_cookie = f'{cookie[115:130]}...{cookie[-15:-1]}'
                    cookies = {'.ROBLOSECURITY': cookie}
                    try:
                        # Получение данных о пользователе
                        user_data = await get_user_data(cookies)
                        user_id, user_name, user_display_name, user_age_in_days = int(user_data['UserId']), user_data['Name'], user_data['DisplayName'], int(user_data['AccountAgeInDays'])
                        cmdWriter(f'  [{ANSI.CYAN}>{ANSI.WHITE}] Name: {ANSI.CYAN}{user_name}{ANSI.WHITE} | Display Name: {ANSI.CYAN}{user_display_name}{ANSI.WHITE}\n')

                        # Установка оценки плейсу
                        if VOTE_PLACE:
                            response = await vote_place(cookies, PLACE_ID, VOTE_PLACE_LIKE)
                            color, value = [ANSI.GREEN, 'Yes'] if response.status == 200 else [ANSI.RED, 'No']
                            cmdWriter(f'  [{color}>{ANSI.WHITE}] Place liked: {color}{value}{ANSI.WHITE}\n')
                            logging.info(await response.json())
                            if REMOVE_COOKIES_IF_VOTED_PLACE:
                                i -= 1
                                j -= 1
                                cookies_buffer.remove(cookie)
                                cookies_from_file.remove(cookie)
                                with open(MAIN_FILENAME, 'w', encoding='utf-8', errors='ignore') as file:
                                    file.write(f'{'\n'.join(cookies_from_file)}\n')
                            if SKIP_COOKIES_IF_VOTED_PLACE:
                                continue

                        # Проверка дней с момента регистрации аккаунта
                        if user_age_in_days < MINIMUM_ACCOUNT_AGE_IN_DAYS:
                            raise RegisteredEarlier1Week

                        # Проверка бейджа
                        if BADGE_ID:
                            if await get_user_achieved_badge(user_id, BADGE_ID, cookies):
                                await taskkill(str(user_id))
                                async with aiofiles.open(f'Results\\clean_achieved_badge ({DATE_OF_CHECK}).txt', 'a', encoding='utf-8', errors='ignore') as file:
                                    await file.write(f'ID: {user_id} | Name: {user_name} | Display Name: {user_display_name} | Cookie: {cookie}\n')
                                cmdWriter(f'  [{ANSI.CYAN}>{ANSI.WHITE}] Badge: {ANSI.GREEN}Yes{ANSI.WHITE}\n')
                                if REMOVE_COOKIES_WITH_BADGE:
                                    i -= 1
                                    j -= 1
                                    cookies_buffer.remove(cookie)
                                    cookies_from_file.remove(cookie)
                                    with open(MAIN_FILENAME, 'w', encoding='utf-8', errors='ignore') as file:
                                        file.write(f'{'\n'.join(cookies_from_file)}\n')
                                    if SKIP_COOKIES_WITH_BADGE:
                                        continue
                            else:
                                cmdWriter(f'  [{ANSI.CYAN}>{ANSI.WHITE}] Badge: {ANSI.RED}No{ANSI.WHITE}\n')

                        # Проверка в каком плейсе игрок
                        if CHECK_PLACE_PLAYER_IN:
                            place_id_user_in = await get_place_id_user_in(user_id, cookies)
                            if place_id_user_in:
                                if place_id_user_in == PLACE_ID:
                                    cmdWriter(f'  [{ANSI.GREEN}>{ANSI.WHITE}] {ANSI.PINK}#{counter:<{indent}}{ANSI.WHITE}: {part_of_cookie} {ANSI.GREEN}>{ANSI.WHITE} Already farming\n')
                                    if not FORCE_JOIN_IF_ALREADY_FARMING:
                                        continue
                                else:
                                    await taskkill(str(user_id))
                                    cmdWriter(f'  [{ANSI.YELLOW}>{ANSI.WHITE}] {ANSI.PINK}#{counter:<{indent}}{ANSI.WHITE}: {part_of_cookie} {ANSI.YELLOW}>{ANSI.WHITE} In other place\n')
                                    if not FORCE_JOIN_IF_IN_OTHER_PLACE:
                                        continue

                        # Получение ID сервера
                        server_id = await get_job_id()
                        if await launch_roblox(cookies, server_id, str(user_id)):
                            cmdWriter(f'  [{ANSI.GREEN}>{ANSI.WHITE}] {ANSI.PINK}#{counter:<{indent}}{ANSI.WHITE}: {part_of_cookie} {ANSI.GREEN}>{ANSI.WHITE} Success\n\n')
                            if counter < amount_of_cookies_in_buffer:
                                for s in range(WAIT_TIME_AFTER_EVERY_LAUNCH, 0, -1):
                                    cmdWriter(f'\r  [{ANSI.YELLOW}?{ANSI.WHITE}] Next launch after {s} sec. ')
                                    await asyncio.sleep(1)
                                await remove_lines(1)
                    except Exception as e:
                        exceptionType = type(e)
                        if exceptionType in EXCEPTIONS:
                            exceptionData = exceptionsHandler(e, counter, indent, part_of_cookie)
                            i -= 1
                            cmdWriter(exceptionData['cmdMessage'])
                            logging.info(exceptionData['loggerMessage'])
                            cookies_buffer.remove(cookie)
                            cookies_from_file.remove(cookie)
                            with open(MAIN_FILENAME, 'w', encoding='utf-8', errors='ignore') as file:
                                file.write(f'{'\n'.join(cookies_from_file)}\n')
                            continue

                        cmdWriter(f'  [{ANSI.RED}>{ANSI.WHITE}] {ANSI.PINK}#{counter:<{indent}}{ANSI.WHITE}: {part_of_cookie} {ANSI.RED}>{ANSI.WHITE} Error: {e}\n')
                        logging.exception(e)
                    finally:
                        if counter < amount_of_cookies_in_buffer:
                            cmdWriter('\r   |\n')
                        else:
                            cmdWriter('\n')
                            logging.info(f'\nЗапустили все процессы... Список: {processes}')

                if AUTO_RETRY:
                    for s in range(RETRY_TIME, 0, -1):
                        cmdWriter(f'\r  [{ANSI.YELLOW}?{ANSI.WHITE}] Retrying after {s} sec. ')
                        await asyncio.sleep(1)
                    await remove_lines(1)
                else:
                    input(f'  [{ANSI.CYAN}<{ANSI.WHITE}] Press \'Enter\' to {ANSI.YELLOW}retry{ANSI.WHITE} again... ')
                    await remove_lines(2)
                cmdWriter(f'\r  [{ANSI.CYAN}>{ANSI.WHITE}] {ANSI.CYAN}Retrying...{ANSI.WHITE}\n\n')
    except Exception as e:
        cmdWriter(f'\n  [{ANSI.RED}!{ANSI.WHITE}] Error: {e}\n')
        logging.exception(e)
    finally:
        input(f'\n  [{ANSI.GREEN}<{ANSI.WHITE}] Finished! Press \'Enter\' to {ANSI.RED}close{ANSI.WHITE} console...')
        sys.exit()

if __name__ == '__main__':
    create_start_files()
    asyncio.run(main())
