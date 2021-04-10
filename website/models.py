from django.db import models
from phone_field import PhoneField

# for password validation and encryption
import re
import bcrypt
from django.core.validators import validate_email

# for getting quotes
import json
from pandas_datareader import data as pdr
from datetime import date
import yfinance as yf
yf.pdr_override()
import pandas as pd
from datetime import date
import requests

# start AssignmentManager
class AssignmentManager(models.Manager):
    
    def countPriorities(self, priorities):
        # as long as priorities match index number of array then no keys are needed to reference the array in django template
        priority_count = {}
        assignments = Assignment.objects.all()
        for priority in priorities:
            count = 0
            for assignment in assignments:
                if (assignment.priority == priority):
                    count += 1
            priority_count[priority] = count
        return priority_count
    # end countPriorities()
# end AssignmentManager

# start StockManager
class StockManager(models.Manager):
    
    def updateTargetPositions(self):
        quintiles = Quintile.objects.all()
        stocks = Stock.objects.all()
        nav = NAV.objects.all()
        nav = nav[0].nav
        for stock in stocks:
            for quintile in quintiles:
                if (stock.quintile_id == quintile.id):
                    stock.weight = quintile.weight
                    stock.target_position = (quintile.weight / 100) * nav
                    stock.save()
        return
    # end updateTargetPositions()

    def yahoo_finance_rapid_api(self, symbol):
        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"

        querystring = {f"region":"US","symbols":{ symbol }}

        headers = {
            'x-rapidapi-key': "7c0c7fd098mshba615283146b103p11faaejsn835b77f547e3",
            'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        json_data= response.json()
        return json_data
    # end yahoo_finance_rapid_api

    def get_quote2(self, symbol):
        start_date= "2021-03-03"
        end_date="2021-03-03"
        today = date.today()
        data = pdr.get_data_yahoo(symbol, start=start_date, end=today)
        return data['Open']
    # end get_quote2

    def yfinance(self, symbol):
        stock = yf.Ticker(symbol)
        data = stock.info
        return data
    # end yfinance

    def iex_cloud(self, symbol):
        url = "https://sandbox.iexapis.com/stable/stock/IBM/quote?token=Tsk_45de9cdece16413a9201d79040e3711f"
        response = requests.request("GET", url)
        json_data= response.json()
        return json_data
    # end def iex_cloud(self, symbol):
# end StockManager

# start UserManager
class UserManager(models.Manager):
    def add_validator(self, post_data):
        errors = {}
        if len(post_data['first_name']) < 1:
            errors['first_name'] = "First name must be at least one character"
        
        if len(post_data['last_name']) < 1:
            errors['last_name'] = "Last name must be at least one character"

        try:
            validate_email(post_data['email'])
        except:
            errors['email'] = "Invalid email"

        # don't need this. much nicer to use validate_email function
        # EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        # if not EMAIL_REGEX.match(post_data['email']):       
        #     errors['email'] = "Invalid email address"
        else:
            exists = User.objects.filter(email=post_data['email'])
            if len(exists) > 0:
                errors['email_exists'] = "This email exists"

        if len(post_data['password']) < 1:
            errors['password'] = "Password must be at least one character"
        
        if post_data['password'] != post_data['confirm_pw']:
            errors['confirm_pw'] = "Passwords must match"

        return errors
    # end add_validator

    def login_validator(self, post_data):
        errors = {}
        
        try:
            validate_email(post_data['email'])
        except:
            errors['email'] = "Invalid email"

        # EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        # if not EMAIL_REGEX.match(post_data['email']):       
        #     errors['email'] = "Invalid email address"

        email_exists = User.objects.filter(email=post_data['email'])
        if len(email_exists) < 1:
            errors['non_existent_email'] = "Email does not exist"
        
        if len(post_data['password']) < 1:
            errors['password'] = "Password field required"
        elif len(post_data['password']) > 0:
            user = User.objects.filter(email=(post_data['email']))
            if user:
                logged_user = user[0]
                if not bcrypt.checkpw(post_data['password'].encode(), logged_user.password.encode()):
                        errors['password'] = "Invalid login"        
        return errors
    # end login_validator
    
    def update_validator(self, post_data):
        errors = {}

        if len(post_data['first_name']) < 1:
            errors['first_name'] = "First name must be at least one character"
        
        if len(post_data['last_name']) < 1:
            errors['last_name'] = "Last name must be at least one character"

        try:
            validate_email(post_data['email'])
        except:
            errors['email'] = "Invalid email"

        # EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        # if not EMAIL_REGEX.match(post_data['email']):       
        #     errors['email'] = "Invalid email address"
        
        if len(post_data['password']) < 1:
            errors['password'] = "Password must be at least one character"

        if post_data['password'] != post_data['confirm_pw']:
                errors['confirm_pw'] = "Passwords must match"

        return errors
    # end update_validator

    # start isAdmin()
    def isAdmin(self, id):
        user = User.objects.get(id=id)
        if (user.permission == "administrator"):
            return True
        else:
            return False
    # end isAdmin()

    # start canEdit()
    def isAssigned(self, analyst_id, symbol_id):
        if (Assignment.objects.filter(symbol_id=symbol_id).exists()):
            assignment = Assignment.objects.get(symbol_id=symbol_id)
            user = User.objects.get(id=analyst_id)
            if (user.permission == "administrator" or assignment.analyst_id == analyst_id ):
                return True
            else:
                return False
        else:
            return False
    # end canEdit()
# end UserManager

# *********** START MODELS *******************

# * WARNING: The order of model declarations cannot be alphabetized due to ForeignKey usage (i.e. the Quintile model must come before the Stock model, etc.) 

# start Quintile model
class Quintile(models.Model):
    quintile = models.CharField(max_length=255, blank=True, default="0")
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    # contains = a list of stocks in the quintile
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.quintile}"
# end Quintile model

# start Stock model
class Stock(models.Model):
    symbol = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    first_pt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    first_upside = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    consensus_pt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    consensus_upside = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    analysis_date = models.DateField(blank=True, null=True)
    analysis_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    summary = models.TextField(blank=True)
    # on_delete=models.PROTECT or on_delete=models.SET_DEFAULT . . . prevents a stock from being deleted when the quintile it is in is deleted (unlikely but just in case)
    quintile = models.ForeignKey(Quintile, related_name="contains", on_delete=models.PROTECT, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    target_position = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0.0)
    last_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    objects = StockManager()

    # def __init__(self, name):
    #     self.name = name

    def __str__(self):
        return f"<Stock object: {self.symbol} ({self.id})>"
# end Stock model

# start Top Idea model
class Top_Idea(models.Model):
    symbol = models.ForeignKey(Stock, related_name="top_ideas", on_delete=models.PROTECT, blank=False, null=False)
    weight = models.DecimalField(max_digits=3, decimal_places=2)
    publication_date = models.DateField()
    publication_price = models.DecimalField(max_digits=10, decimal_places=2)
    peak_date = models.DateField(null=True)
    peak_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    peak_return = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    days = models.IntegerField(null=True)
    years = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    annualized_return = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)
# end Top Idea model

# start User model
class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email= models.EmailField(max_length=254)
    phone = PhoneField(blank=True)
    password = models.CharField(max_length=255)
    permission = models.CharField(max_length=255)
    active = models.BooleanField(blank=True, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    # assigned_stocks = a list of stocks a user is assigned
    objects = UserManager()

    def __str__(self):
        return f"{self.first_name}"
# end User model

# start Assignment model
class Assignment(models.Model):
    symbol = models.OneToOneField(Stock, related_name="assigned", on_delete=models.PROTECT)
    analyst = models.ForeignKey(User, related_name="assignments", on_delete=models.PROTECT, blank=False, null=False) 
    previous_analyst = models.ForeignKey(User, related_name="previous_assignments", on_delete=models.PROTECT, blank=True, null=True) 
    date_assigned = models.DateField(blank=False)
    priority = models.IntegerField(blank=True, null=True)
    date_presented = models.DateField(blank=True, null=True)
    decision = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=255, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    objects = AssignmentManager()

    def __str__(self):
        return f"{self.symbol}"
# end Assignment model

# start Archive model
class Archive(models.Model):
    symbol = models.ForeignKey(Stock, related_name="archives", on_delete=models.PROTECT)
    archiver = models.ForeignKey(User, related_name="archived", on_delete=models.PROTECT, blank=False, null=True) 
    analyst = models.ForeignKey(User, related_name="archives", on_delete=models.PROTECT, blank=True, null=True) 
    previous_analyst = models.ForeignKey(User, related_name="previously_assigned", on_delete=models.PROTECT, blank=True, null=True) 
    date_assigned = models.DateField(blank=True)
    priority = models.IntegerField(blank=True, null=True)
    date_presented = models.DateField(blank=True, null=True)
    decision = models.CharField(max_length=255, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    # objects = ArchiveManager()
# end Archive model

# start Comment model
class Comment(models.Model):
    symbol = models.ForeignKey(Stock, related_name="comments", on_delete=models.CASCADE)
    analyst = models.ForeignKey(User, related_name="commented", on_delete=models.PROTECT) 
    comment = models.TextField(blank=True) 
    decision = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    # objects = CommentManager()

    def __str__(self):
        return f"{self.symbol}"
# end Comment model

# start NAV model
class NAV(models.Model):
    nav = models.DecimalField(max_digits=15, decimal_places=2,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
# end NAV model

