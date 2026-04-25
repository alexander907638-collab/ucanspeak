from user_agents import parse as parse_ua


def parse_user_agent(ua_string: str) -> dict:
    """Возвращает {device_name, browser_name, os_name} из строки User-Agent."""
    if not ua_string:
        return {
            'device_name': 'Неизвестное устройство',
            'browser_name': '',
            'os_name': '',
        }

    ua = parse_ua(ua_string)
    browser = ua.browser.family or 'Браузер'
    os = ua.os.family or 'устройство'

    if ua.is_mobile or ua.is_tablet:
        device = f'{browser} на {os} (мобильное)'
    else:
        device = f'{browser} на {os}'

    return {
        'device_name': device,
        'browser_name': browser,
        'os_name': os,
    }


def get_client_ip(request) -> str | None:
    """Извлекает IP клиента с учётом прокси nginx."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
