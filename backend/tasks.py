
# coding:utf-8
import datetime

from celery.decorators import task
import time
# coding:utf-8
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.core.mail import send_mail

from backend.models import Position, CompanyResume, HunterPosition
from talentRecruitment.settings import EMAIL_FROM


@periodic_task(run_every=crontab())
def some_task():
    print('periodic task test!!!!!')
    time.sleep(5)
    print('success')
    return True
#到达过期时间，暂停职位招聘
@periodic_task(run_every=crontab(minute=0, hour=0))
def deletePositionTask():
    now = datetime.datetime.now()
    positions = Position.objects.filter(expiry_date__lt=now, is_delete='0')
    for position in positions:
        position.is_delete = '2'
        position.save()
    return True

#简历收藏
@periodic_task(run_every=crontab(minute=0, hour=0))
def collectResumeDeleteTask():
    start_date = datetime.datetime.now()
    other_date = start_date - datetime.timedelta(days=60)
    companyResumes = CompanyResume.objects.filter(collect_time__lt=other_date, is_collect='1')
    if companyResumes:
        for companyResume in companyResumes:
            if companyResume.status == '无':
                companyResume.delete()
            else:
                companyResume.is_collect = '0'
                companyResume.collect_time = ''
                companyResume.save()
    return True

#职位收藏
@periodic_task(run_every=crontab(minute=0, hour=0))
def collectPositionDeleteTask():
    start_date = datetime.datetime.now()
    other_date = start_date - datetime.timedelta(days=60)
    print(other_date)
    hunterPositions = HunterPosition.objects.filter(collect_time__lt=other_date, is_collect='1')
    if hunterPositions:
        for hunterPosition in hunterPositions:
            if hunterPosition.status == '无':
                hunterPosition.delete()
            else:
                hunterPosition.is_collect = '0'
                hunterPosition.collect_time = ''
                hunterPosition.save()
    return True
#异步任务
@task
def sendmail(title,ret,fro,email):
    print('start send email to %s' % email)
    send_mail(title, ret, fro, [email], fail_silently=False)
    time.sleep(5)  # 休息5秒
    print('success')
    return True


#每隔三天刷新职位发布时间
@periodic_task(run_every=crontab(minute=0, hour=0, day_of_month='3-31/3'))
def refreshReleaseTime():
    positions=Position.objects.filter(is_delete='0')
    for position in positions:
        position.release_time=time.timezone
        position.save()
    return True