from django.conf.urls import url


from backend import views

urlpatterns=[
    # url(r'add_user$',views.add_user,),

    #登录
    url(r'login/',views.login,name='login'),
    #注册
    url(r'register/',views.register,name='register'),
    url(r'logout/',views. logout,),
    #修改密码
    url(r'update_pwd/', views.update_pwd, name='update_pwd'),

    # url(r'user_detail$',views.user_detail,),
    # url(r'user_detail/(\w+)',views.user_detail,name='user_detail'),
    url(r'user_del$',views.user_del,name='user_del'),
    url(r'user_edit/(\w+)',views.user_edit,name='user_edit'),
    url(r'photoUpload/',views.photoUpload,name='photoUpload'),
    url(r'hunter_add/',views.hunter_add,name='hunter_add'),
# url(r'hunterForm/',views.hunterForm,name='hunterForm'),
    url(r'resumeCenter/',views.resumeCenter,name='resumeCenter'),
    url(r'resume_add/',views.resume_add,name='resume_add'),
    url(r'resumeCenterDelete/',views.resumeCenterDelete,name='resumeCenterDelete'),
    #显示求职者简历
    url(r'resume_show/',views.resume_show,name='resume_show'),
    #求职者添加或编辑简历
    url(r'resume_edit/(\w+)',views.resume_edit,name='resume_edit'),
    #简历删除
    url(r'resume_del/(\w+)', views.resume_del, name='resume_del'),
    url(r'education_experience_add/', views.education_experience_add, name='education_experience_add'),
    url(r'education_experience_edit/(\w+)',views.education_experience_edit,name='education_experience_edit'),
    url(r'education_experience_del/(\w+)', views.education_experience_del, name='education_experience_del'),
    url(r'work_experience_add/', views.work_experience_add, name='work_experience_add'),
    url(r'work_experience_edit/(\w+)', views.work_experience_edit, name='work_experience_edit'),
    url(r'work_experience_del/(\w+)', views.work_experience_del, name='work_experience_del'),
    url(r'project_experience_add/', views.project_experience_add, name='project_experience_add'),
    url(r'project_experience_edit/(\w+)', views.project_experience_edit, name='project_experience_edit'),
    url(r'project_experience_del/(\w+)', views.project_experience_del, name='project_experience_del'),

    url(r'send_email/',views.send_email,name='send_email'),
    url(r'allPositionSearch/',views.allPositionSearch,name='allPositionSearch'),
    url(r'positionSearch/',views.positionSearch,name='positionSearch'),
    url(r'positionCollect/',views.positionCollect,name='positionCollect'),
    url(r'positionDeliver/',views.positionDeliver,name='positionDeliver'),
    url(r'myDeliver/',views.myDeliver,name='myDeliver'),
    url(r'myCollectDelete/',views.myCollectDelete,name='myCollectDelete'),
    url(r'myCollect/',views.myCollect,name='myCollect'),
    url(r'positionDetail/',views.positionDetail,name='positionDetail'),
    url(r'positionDetailPost/(\w+)', views.positionDetailPost, name='positionDetailPost'),
    url(r'companyDetailPost/(\w+)',views.companyDetailPost,name='companyDetailPost'),#职位详情模板
    url(r'companyDetail/',views.companyDetail,name='companyDetail'),#vue
    url(r'recommendPosition/',views.recommendPosition,name='recommendPosition'),
    url(r'getFeedbackCount/', views.getFeedbackCount, name='getFeedbackCount'),
    url(r'conditionSearch/', views.conditionSearch, name='conditionSearch'),

    #企业
    url(r'company_index/',views.company_index,name='company_index'),
    url(r'company_show/',views.company_show,name='company_show'),
    url(r'companyForm/',views.companyForm,name='companyForm'),
    url(r'company_edit/(\w+)', views.company_edit, name='company_edit'),
    url(r'position_add/', views.position_add, name='position_add'),
    url(r'position_edit/(\w+)', views.position_edit, name='position_edit'),
    url(r'position_del/(\w+)', views.position_del, name='position_del'),
    url(r'getResumeCollect',views.getResumeCollect,name='getResumeCollect'),
    url(r'resumeCollect/',views.resumeCollect,name='resumeCollect'),
    url(r'resumeInterview',views.resumeInterview,name='resumeInterview'),
    url(r'getAllResume',views.getAllResume,name='getAllResume'),
    url(r'resumeSearch', views.resumeSearch, name='resumeSearch'),
    url(r'getPositionDeliverCount', views.getPositionDeliverCount, name='getPositionDeliverCount'),
    url(r'getPositionDeliver', views.getPositionDeliver, name='getPositionDeliver'),
    url('resumeManage', views.resumeManage, name='resumeManage'),
    url(r'interviewAdd', views.interviewAdd, name='interviewAdd'),
    url(r'companyInterviewAdd', views.companyInterviewAdd, name='companyInterviewAdd'),
    url(r'getInterview/',views.getInterview,name='getInterview'),
    url(r'interviewShow/',views.interviewShow,name='interviewShow'),
    url(r'resumeDetail/',views.resumeDetail,name='resumeDetail'),
    url(r'recommendResume/',views.recommendResume,name='recommendResume'),
    url(r'conditionResumeSearch/',views.conditionResumeSearch,name='conditionResumeSearch'),
    url(r'refreshReleaseTime/',views.refreshReleaseTime,name='refreshReleaseTime'),
    url(r'pausePosition/',views.pausePosition,name='pausePosition'),
url(r'interviewByWeek/',views.interviewByWeek,name='interviewByWeek'),

    #admin
    url(r'admin_index/',views.admin_index,name='admin_index'),
    url(r'positions/',views.positions,name='positions'),
    url(r'positions_del/', views.positions_del, name='positions_del'),
    url(r'position_del_admin/(\w+)', views.position_del_admin, name='position_del_admin'),
    url(r'users/',views.users,name='users'),
    url(r'users_del/', views.users_del, name='users_del'),
    url(r'hunter_edit/', views.hunter_edit, name='hunter_edit'),
    url(r'companyEditByAdmin/(\w+)', views.companyEditByAdmin, name='companyEditByAdmin'),
    url(r'adminAdd/',views.adminAdd,name='adminAdd'),
    url(r'adminEdit/(\w+)',views.adminEdit,name='adminEdit'),
    url(r'user_del/(\w+)',views.user_del,name='user_del'),
    url(r'getUserNum/',views.getUserNum,name='getUserNum'),
    url(r'getUserSex/',views.getUserSex,name='getUserSex'),
    url(r'userStatistics/',views.userStatistics,name='userStatistics'),
    url(r'educationRequirement/',views.educationRequirement,name='educationRequirement'),
    url(r'cityDistribute/',views.cityDistribute,name='cityDistribute'),
    url(r'echarts/',views.echarts,name='echarts'),
    url(r'educationAndSalary/',views.educationAndSalary,name='educationAndSalary'),
    url(r'getStatusHandel/',views.getStatusHandel,name='getStatusHandel'),
    url(r'statusToPass/',views.statusToPass,name='statusToPass'),
    url(r'statusToFail/',views.statusToFail,name='statusToFail'),
    url(r'newsAdd/', views.newsAdd, name='newsAdd'),
    url(r'newsDel/(\w+)', views.newsDel, name='newsDel'),
    url(r'newssDel/', views.newssDel, name='newssDel'),
    url(r'newsShow/', views.newsShow, name='newsShow'),
    url(r'news/', views.news, name='news'),
    url(r'newsEdit/(\w+)', views.newsEdit, name='newsEdit'),
    url(r'positionOrderByTime/', views.positionOrderByTime, name='positionOrderByTime'),
    url(r'loginTime/', views.loginTime, name='loginTime'),

#首页
    url(r'index/',views.index,name='index'),

    url(r'newsDetail/(\w+)',views.newsDetail1,name='newsDetail1'),
    url(r'newsDetail/',views.newsDetail,name='newsDetail'),
    # url(r'course/', views.course),
    url('pdf/', views.HelloPDFView.as_view(), name='pdf'),
    url('test/', views.test, name='test'),
]
