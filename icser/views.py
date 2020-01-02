from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
import datetime
import json
import time

import requests

# Create your views here.
output = []


def out(ClassName, Classroom, teacher, week, weekday, LessonTime, Campus, FirstDay):
    output.append({"output": "BEGIN:VEVENT"})
    output.append({"output": "SUMMARY:" + ClassName})
    output.append({"output": "DTSTART;TZID=Asia/Shanghai:" + calcStartDate(week, weekday,
                                                                           FirstDay) + "T" + calcStartTime(LessonTime)})
    output.append({"output": "DTEND;TZID=Asia/Shanghai:" + calcStartDate(week, weekday, FirstDay) + "T" + calcEndTime(
        LessonTime)})
    output.append(
        {"output": "RRULE:FREQ=WEEKLY;UNTIL=" + calcEndDate(week, weekday, FirstDay) + "T" + calcEndTime(LessonTime)})
    output.append({"output": "LOCATION:" + Campus + "  " + Classroom + "  " + teacher})
    output.append({"output": "END:VEVENT"})


def startTime(Lesson):
    TimeTable = ["080000", "085500", "095500", "105000", "114500", "133000", "142500", "152500", "162000", "183000",
                 "192500", "202000"]
    return TimeTable[Lesson - 1]


def endTime(Lesson):
    TimeTable = ["084500", "094000", "104000", "113500", "123000", "141500", "151000", "161000", "170500", "191500",
                 "201000", "210500"]
    return TimeTable[Lesson - 1]


def calcStartDate(week, weekday, FirstDay):
    if week.split("-")[0] != "1":
        FirstDay = FirstDay + datetime.timedelta(7 * int(week.split("-")[0]) - 7)
    FirstDay = FirstDay + datetime.timedelta(int(weekday) - 1)
    return FirstDay.strftime("%Y%m%d")


def calcEndDate(week, weekday, FirstDay):
    LastDay = FirstDay + datetime.timedelta(7 * int(week.split("-")[1].split("\\u546")[0]) - 7)
    LastDay = LastDay + datetime.timedelta(int(weekday))
    return LastDay.strftime("%Y%m%d")


def calcStartTime(LessonTime):
    StartLesson = int(LessonTime.split("-")[0])
    return startTime(StartLesson)


def calcEndTime(LessonTime):
    EndLesson = int(LessonTime.split("-")[1])
    return endTime(EndLesson)


def calcSemester(t):
    if t == "1":
        return "3"
    if t == "2":
        return "12"
    if t == "3":
        return "16"


def index(request):
    if request.method == "POST":
        username = request.POST.get("id", None)
        password = request.POST.get("password", None)

        headers = {
            "Host": "api.jh.zjut.edu.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/79.0.3945.88 Safari/537.36 Edg/79.0.309.54 "
        }
        FirstDay = datetime.datetime.strptime("20200217", "%Y%m%d")
        url = "http://api.jh.zjut.edu.cn/student/classZf.php?username=" + username + "&password=" + password + "&year=2019&term=12"
        content = requests.get(url, headers=headers).content.decode().encode("GBK")
        JSON = json.loads(content)
        n = 0
        output.clear()
        while JSON["status"] == "error":
            content = requests.get(url, headers=headers).content.decode().encode("GBK")
            JSON = json.loads(content)
            time.sleep(3)
            n = n + 1
            if n == 3:
                output.append({"output": "错误"})
                return render(request, "index.html", {"data": output})
        output.append({"output": "BEGIN:VCALENDAR"})
        output.append({"output": "VERSION:2.0"})
        output.append({"output": "PRODID:-//HHR"})
        for each in JSON["msg"]:
            ClassName = each["kcmc"]
            Classroom = each["cdmc"]
            Teacher = each["xm"]
            weekday = each["xqj"]
            LessonTime = each["jcor"]
            Campus = each["xqmc"]
            week = each["zcd"][:-1]
            flag = 0
            try:
                tmp = week.index("单")
            except ValueError:
                flag = 1
            if flag == 0:
                week = week[:-3]
                startWeek = int(week.split("-")[0])
                endWeek = int(week.split("-")[1])
                for i in range(startWeek, endWeek):
                    if i % 2 == 0:
                        out(ClassName, Classroom, Teacher, str(i) + "-" + str(i), weekday, LessonTime, Campus, FirstDay)
                continue
            flag = 0
            try:
                tmp = week.index("双")
            except ValueError:
                flag = 1
            if flag == 0:
                week = week[:-3]
                startWeek = int(week.split("-")[0])
                endWeek = int(week.split("-")[1])
                for i in range(startWeek, endWeek):
                    if i % 2 != 0:
                        out(ClassName, Classroom, Teacher, str(i) + "-" + str(i), weekday, LessonTime, Campus, FirstDay)
                continue
            try:
                week1 = week.split(",")[1]  # 处理形如 2-8周,10-16周 的情况
            except IndexError:
                while not ('0' <= week[-1] <= '9'):  # 剪掉后面的所有中文
                    week = week[:-1]
                week = week + "-" + week[0]  # 避免某课程只上一周导致的异常
                out(ClassName, Classroom, Teacher, week, weekday, LessonTime, Campus, FirstDay)
                continue
            week = week.split(",")[0]
            while not ('0' <= week[-1] <= '9'):  # 剪掉后面的所有中文
                week = week[:-1]
            week = week + "-" + week[0]  # 避免某课程只上一周导致的异常
            out(ClassName, Classroom, Teacher, week, weekday, LessonTime, Campus, FirstDay)
            while not ('0' <= week1[-1] <= '9'):  # 剪掉后面的所有中文
                week1 = week1[:-1]
            week1 = week1 + "-" + week1[0]  # 避免某课程只上一周导致的异常
            out(ClassName, Classroom, Teacher, week1, weekday, LessonTime, Campus, FirstDay)
        output.append({"output": "END:VCALENDAR"})
        outputString = ''
        for line in output:
            outputString = outputString + line["output"] + "\n"
        # return render(request, "index.html", {"n": output, "file": outputFile})
        response = HttpResponse(outputString)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename=' + username + '.ics'
        return response
    return render(request, "index.html", {"n": output})
