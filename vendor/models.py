from django.db import models
import datetime
from customer.models import UserProfile
from super_admin.models import CompanyProfile


custom_expiry_date = datetime.datetime.now()+datetime.timedelta(days=2)
class Vendor_Account_Activation(models.Model):
    user = models.IntegerField(db_column='user_id', null=True)
    key = models.CharField(max_length=100, blank=True, null=True)
    otp = models.PositiveIntegerField()
    agent = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    expiry_date = models.DateTimeField(default=custom_expiry_date)
    email = models.CharField(max_length=50, null=True,blank=True,default='')

    class Meta:
        db_table = 'vendor_account_activation'



class company_stripe(models.Model):
    companyid = models.ForeignKey(CompanyProfile,on_delete=models.Case,db_column='company_id')
    accountid = models.CharField(db_column='account_id',max_length=100,null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    companyname = models.CharField(max_length=100,db_column='company name',null=True,blank=True)
    mobile = models.CharField(max_length=100,db_column='contact_no',null=True,blank=True)
    bankid = models.CharField(max_length=100,db_column='bank_id',null=True,blank=True)
    type = models.CharField(max_length=100,db_column='acc_type',null=True,blank=True)

    class Meta:
        db_table = 'company_details_stripe'

