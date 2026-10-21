import sys
import pattern_api

def main():
    print("pattern_api:", [m for m in dir(pattern_api) if not m.startswith('_')])

if __name__ == "__main__":
    main()
