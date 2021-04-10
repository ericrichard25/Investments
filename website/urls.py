from django.urls import path     
from . import views
from django.conf.urls import url

urlpatterns = [

    # paths with no variables
    path('', views.index, name="index"),
    path('add_stock', views.add_stock, name="add_stock"),     
    path('add_user', views.add_user, name="add_user"),
    path('analyster_update/<id>', views.analyster_update, name="analyster_update"),
    path('archive/<id>', views.archive, name="archive"),
    path('batch_assign', views.batch_assign, name="batch_assign"), 
    # temp path for testing delete all stocks
    path('batch_delete', views.batch_delete, name="batch_delete"),
    path('contact', views.contact, name="contact"),	
    path('go_to', views.go_to, name="go_to"),
    path('individual_assign', views.individual_assign, name="individual_assign"), 
    path('internships', views.internships, name="internships"),
    path('investing_philosophy', views.investing_philosophy, name="investing_philosophy"),
    path('loader', views.loader, name="loader"),
    path('login', views.login, name="login"),	    
    path('login_page', views.login_page, name="login_page"),
    path('logout', views.logout, name="logout"),
    path('nav', views.nav, name="nav"),
    path('performance', views.performance, name="performance"),
    path('quintile_weights', views.quintile_weights, name="quintile_weights"),
    path('set_priority', views.set_priority, name="set_priority"),      
    path('summarizer', views.summarizer, name="summarizer"),
    path('upload', views.upload, name="upload"),    
    # end paths with no variables

    # paths with variables
    path('delete_stock/<int:id>', views.delete_stock, name="delete_stock"), 
    path('delete_user/<int:id>', views.delete_user, name="delete_user"), 
    path('comment/<symbol>', views.comment, name="comment"), 
    path('summarizer/<symbol>', views.symbol, name="symbol"), 
    path('update_user/<int:id>', views.update_user, name="update_user"), 
    path('user/<int:id>', views.user, name="user"), 
    path('update_stock/<symbol>', views.update_stock, name="update_stock"),
    # end paths with variables                  
]