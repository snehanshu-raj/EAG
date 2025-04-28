import requests

def get_current_f1_standings():
    url = "https://ergast.com/api/f1/current/driverStandings.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        standings_list = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        
        print("Current F1 Driver Standings:")
        for driver in standings_list:
            position = driver['position']
            points = driver['points']
            driver_name = driver['Driver']['givenName'] + " " + driver['Driver']['familyName']
            nationality = driver['Driver']['nationality']
            constructor = driver['Constructors'][0]['name']
            
            print(f"{position}. {driver_name} ({nationality}) - {constructor} - {points} points")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

if __name__ == "__main__":
    get_current_f1_standings()
