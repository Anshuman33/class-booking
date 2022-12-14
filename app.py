from flask import Flask, request, jsonify
from json import load, dump
from flask_mail import Mail, Message
from datetime import datetime, date, timedelta
import os

def saveBookings():
    global bookings
    with open("bookings.json", "w") as f:
        dump(bookings, f)
weekdays = {1:'monday',2:'tuesday',3:'wednesday',4:'thursday',5:'friday',6:'saturday', 7:'sunday'}

app = Flask(__name__)
mail = Mail(app)



with open("teacher_availability.json") as f:
    teacher = load(f)
    
if os.path.exists("bookings.json"):
    with open("bookings.json") as f:
        bookings = load(f)
else:
    bookings = {}
    saveBookings()
    


def sendMail(student_email, student_name, date, start_time, end_time):
    msg = Message('Class Booked Successfully', sender=teacher['email'], recipients=[student_email])
    msg.body = f"Student Name: {student_name}\nClass Date: {date}\nStart Time: {start_time}\nEnd Time: {end_time}"
    mail.send(msg)

def checkAvailability(day, req_start_time, req_end_time):
    print("Hello")

    if day not in teacher['availability']:
        return False
    day_avail = teacher['availability'][day]
    
    req_tstart = datetime.strptime(req_start_time, "%I %p")
    req_tend = datetime.strptime(req_end_time, "%I %p")
    
    for slot in day_avail:
        
        start_time = slot['start_time']
        end_time = slot['end_time']
        tstart = datetime.strptime(start_time, "%I %p")
        tend = datetime.strptime(end_time, "%I %p")
        if req_tstart >= tstart and req_tend <= tend:
            return True
    
    return False

def slotsCompatible(slot1, slot2):
    if(slot1[1] < slot2[0] or slot2[1] < slot1[0]):
        return True
    else :
        return False

    
def findSchedule(date, start_time, end_time):
    '''
        Finds the next available slot and returns the booking details
        returns a dictionary with date, weekday, start_time, and end_time of the booked slot
    '''
    dateStr = date.strftime("%d %M %Y")
    
    if dateStr not in bookings:
        bookings[dateStr] = []
        bookings[dateStr].append({
            "start_time" : start_time.strftime("%I %p"),
            "end_time" : end_time.strftime("%I %p")})
        print(bookings)
        saveBookings()
        return {"weekday":weekdays[date.isoweekday()],
                "date":date.strftime("%d %B %Y"), 
                "start_time":start_time.strftime("%I %p"), 
                "end_time":end_time.strftime("%I %p")
                }
    else:
        for record in bookings[dateStr]:
            rec_start_time = datetime.strptime(record["start_time"], "%I %p")
            rec_end_time = datetime.strptime(record["end_time"], "%I %p")
            if not slotsCompatible([rec_start_time,rec_end_time], [start_time, end_time]):
                # Find slot next week
                date = date + timedelta(weeks=1)
                return findSchedule(date, start_time, end_time)
        # To complete
    
@app.route("/schedule", methods=['POST'])
def schedule():
    reqParams = request.get_json()
    student_name = reqParams.get("full_name")
    email = reqParams.get("email_address")
    weekday = reqParams.get("weekday").lower()
    start_time = reqParams.get("start_time")
    end_time = reqParams.get("end_time")
    
    # Return if no slot for that weekday
    if not checkAvailability(weekday, start_time, end_time):
        return jsonify({
                "slot_confirmed": "false",
                "reason": "teacher is not available on this day"
                }), 200
    
    # Find the latest date corresponding to weekday
    currDate = date.today()
    while(weekdays[currDate.isoweekday()] != weekday):
        currDate = currDate + timedelta(days=1)
    
    # Convert start time and endtime to datetime
    start_time = datetime.strptime(start_time, "%I %p")
    end_time = datetime.strptime(end_time, "%I %p")
    
    # Find suitable schedule
    booked_slot = findSchedule(currDate, start_time, end_time)
    
    # Send mail
    # sendMail(email, student_name, booked_slot['date'], booked_slot['start_time'], booked_slot['end_time'])
    
        
    return jsonify(
            {
                "slot_confirmed": "true",
                "weekday": booked_slot['weekday'],
                "start_time": booked_slot['start_time'],
                "end_time": booked_slot['end_time'],
                "date": booked_slot['date']
            }
        ), 200
    
        
if __name__ == '__main__':
    app.run()