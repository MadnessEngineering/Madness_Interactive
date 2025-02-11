#!/usr/bin/env python3
import argparse

from AppKit import NSPoint
from AppKit import NSSize
from AppKit import NSWorkspace


def get_attribute_value(element, attribute):
    """Safely get an attribute value."""
    try:
        value = AXUIElementCopyAttributeValue(element, attribute, None)
        if isinstance(value, tuple):
            return value[1] if len(value) > 1 else value[0]
        return value
    except Exception:
        return None


def get_available_attributes(element):
    """Get list of available attributes for an element."""
    try:
        result = AXUIElementCopyAttributeNames(element, None)
        if isinstance(result, tuple):
            return result[1] if len(result) > 1 else []
        return []
    except Exception:
        return []


def format_value(value):
    """Format a value for display."""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    elif isinstance(value, (NSPoint, NSSize)):
        return str(value)
    elif hasattr(value, '__len__'):
        return f"[{len(value)} items]"
    else:
        return f"<{type(value).__name__}>"


def explore_element(element, indent="", max_depth=4, current_depth=0):
    """Explore and print all information about an element."""
    if current_depth > max_depth:
        return

    try:
        attrs = get_available_attributes(element)
        if not attrs:
            return

        # Get role and title first for better readability
        role = get_attribute_value(element, 'AXRole')
        title = get_attribute_value(element, 'AXTitle')

        # Print element header
        print(f"\n{indent}{'=' * 20}")
        print(f"{indent}Role: {role}")
        if title:
            print(f"{indent}Title: {title}")

        # Print other interesting attributes
        interesting_attrs = [
            'AXDescription', 'AXValue', 'AXEnabled', 'AXFocused',
            'AXSelected', 'AXHelp', 'AXSubrole'
        ]

        for attr in attrs:
            if attr in interesting_attrs:
                value = get_attribute_value(element, attr)
                if value is not None:
                    print(f"{indent}{attr}: {format_value(value)}")

        print(f"{indent}{'=' * 20}")

        # Handle children
        if current_depth < max_depth:
            children = get_attribute_value(element, 'AXChildren')
            if children and hasattr(children, '__iter__'):
                for child in children:
                    explore_element(child, indent + "  ", max_depth, current_depth + 1)

    except Exception as e:
        print(f"{indent}Error: {e}")


def get_all_windows():
    """Get all visible windows from all applications."""
    windows = []
    workspace = NSWorkspace.sharedWorkspace()
    apps = workspace.runningApplications()

    for app in apps:
        try:
            pid = app.processIdentifier()
            app_name = app.localizedName()
            app_ref = AXUIElementCreateApplication(pid)

            # Try to get the windows
            app_windows = get_attribute_value(app_ref, 'AXWindows')
            if app_windows:
                for window in app_windows:
                    title = get_attribute_value(window, 'AXTitle')
                    if title:  # Only include windows with titles
                        windows.append({
                            'app_name': app_name,
                            'window_title': title,
                            'pid': pid
                        })
        except Exception:
            continue

    return windows


def find_window_by_title(search_title):
    """Find a specific window by its title."""
    windows = get_all_windows()

    # First try exact match
    for window in windows:
        if window['window_title'].lower() == search_title.lower():
            return window

    # Then try partial match
    for window in windows:
        if search_title.lower() in window['window_title'].lower():
            return window

    return None


def list_windows():
    """List all visible windows."""
    windows = get_all_windows()

    print("\nAvailable Windows:")
    print("=" * 50)

    # Group windows by application
    apps = {}
    for window in windows:
        app_name = window['app_name']
        if app_name not in apps:
            apps[app_name] = []
        apps[app_name].append(window['window_title'])

    # Print grouped windows
    for app_name, titles in sorted(apps.items()):
        print(f"\n{app_name}:")
        for title in sorted(titles):
            print(f"  - {title}")


def inspect_window(window_info):
    """Inspect a specific window's hierarchy."""
    app_ref = AXUIElementCreateApplication(window_info['pid'])

    # Get all windows and find the matching one
    windows = get_attribute_value(app_ref, 'AXWindows')
    if windows:
        for window in windows:
            title = get_attribute_value(window, 'AXTitle')
            if title == window_info['window_title']:
                print(f"\nInspecting window: {title} ({window_info['app_name']})")
                print("=" * 50)
                explore_element(window, max_depth=4)
                return

    print("Window not found or no longer available.")


def main():
    parser = argparse.ArgumentParser(description='Inspect GUI elements of macOS windows')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list', action='store_true', help='List all available windows')
    group.add_argument('--window', type=str, help='Inspect a specific window by title (partial match supported)')
    parser.add_argument('--max-depth', type=int, default=4, help='Maximum depth to explore (default: 4)')

    args = parser.parse_args()

    if args.list:
        list_windows()
    elif args.window:
        window = find_window_by_title(args.window)
        if window:
            inspect_window(window)
        else:
            print(f"No window found matching: {args.window}")


if __name__ == "__main__":
    main()
