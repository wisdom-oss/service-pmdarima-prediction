
def convert_timeframe(timeframe: str):
    num_rows = 0

    match timeframe:
        case "one day": num_rows = 24
        case "one week": num_rows = 24*7
        case "one month": num_rows = 24*7*30
        case "three months": num_rows  = 24*7*30*3
        case "six months": num_rows  = 24*7*30*6
        case "one year": num_rows  = 24*7*30*12

    print("re-do function to accurately depict correct months later")
    return num_rows