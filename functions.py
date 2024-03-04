from datetime import datetime,date

def filter_events(events, title_filter, date_filter):
    filtered_events = []

    for event in events:
        # Check if the event title contains the title filter (case insensitive)
        title_match = title_filter.lower() in event['title'].lower() if title_filter else True
        print(title_match)
        # Check if the event date matches the date filter
        date_match = date_filter == event['date'] if date_filter else True
        print(date_filter,date_match)
        # If both title and date match, add the event to the filtered list
        if title_match and date_match:
            filtered_events.append(event)
    return filtered_events

def edit_event(events, old_time, new_title, new_date, new_time):
    for event in events:
        if event['time'] == old_time:
            event['title'] = new_title
            event['date'] = new_date
            event['time'] = new_time
            break


def delete_event(events, time_to_delete):
    events = [event for event in events if event['time'] != time_to_delete]
    return events

