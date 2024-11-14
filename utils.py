def error_for_list_title(list_title, lists):
    if any(list_title.lower() == lst['title'].lower() for lst in lists):
        return f'Error: {list_title} already exists.'
    elif 1 > len(list_title) or len(list_title) > 100:
        return 'Error: the list title should be between 1 and 100 characters'
    else:
        return None