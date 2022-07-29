from flask import Flask, request, jsonify
from json import load
from datetime import datetime, date, timedelta

weekdays = {1:'monday',2:'tuesday',3:'wednesday',4:'thursday',5:'friday',6:'saturday', 7:'sunday'}

app = Flask(__name__)

with open("teacher_availability.json") as f:
    teacher = load(f)
    
bookings = {}
print(teacher)

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
    if date in bookings:
        for record in bookings['date']:
            if not slotsCompatible(record, [start_time,end_time]):
                date = date + timedelta(weeks=1)
                return findSchedule(date)
@app.route("/schedule", methods=['POST'])
def schedule():
    response = {}
    student_name = request.form.get("full_name")
    email = request.form.get("email_address")
    weekday = request.form.get("weekday")
    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")
    
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
    
    booked_slot = findSchedule(currDate, start_time, end_time)
    
        
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