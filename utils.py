def error_for_list_title(list_title, lists):
    if 1 > len(list_title) or len(list_title) > 100:
        return 'Error: the list title should be between 1 and 100 characters'
    elif any(list_title.lower() == lst['title'].lower() for lst in lists):
        return f'Error: {list_title} already exists.'
    else:
        return None

def error_for_todo_title(todo_title):
    if len(todo_title) < 1:
        return 'Please enter the title'
    elif len(todo_title) > 100:
        return 'Title cannot exceed 100 characters'
    else:
        return None

def get_list_by_id(list_id, lists):
    return next((lst for lst in lists if lst['id'] == list_id), None)

def get_todo_by_id(todo_id, todos):
    return next((todo for todo in todos if todo['id'] == todo_id), None)

def count_todos_remaining(lst):
    return sum(1 for todo in lst['todos'] if not todo['completed'])

def is_list_completed(lst):
    return len(lst['todos']) >= 1 and count_todos_remaining(lst) == 0

def is_todo_completed(todo):
    return todo['completed']

def sort_items(items, completed_callback):
    sorted_items = sorted(items, key=lambda item:item['title'].lower())

    incomplete_items = [item for item in sorted_items
                        if not completed_callback(item)]

    complete_items = [item for item in sorted_items
                        if completed_callback(item)]

    return incomplete_items + complete_items
