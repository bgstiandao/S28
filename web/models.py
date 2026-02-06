from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名',max_length=32,db_index=True) #db_index=True 索引，加快查询速度
    email = models.EmailField(verbose_name='邮箱',max_length=32)
    mobile_phone = models.CharField(verbose_name='手机号',max_length=32)
    password = models.CharField(verbose_name='密码',max_length=32)


class PricePolicy(models.Model):
    """价格策略"""
    category_choices = [
        (1,'免费版'),
        (2, '收费版'),
        (3, '其他'),
    ]
    category = models.SmallIntegerField(verbose_name='收费类型',choices=category_choices,default=1) #默认免费版
    title = models.CharField(verbose_name='标题',max_length=32)
    price = models.PositiveIntegerField(verbose_name='价格')           #正整数

    project_num = models.PositiveIntegerField(verbose_name='项目数')
    project_member = models.PositiveIntegerField(verbose_name='项目成员数')
    project_space = models.PositiveIntegerField(verbose_name='单项目空间')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小')

    create_datetime = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)

class Transaction(models.Model):
    """交易记录"""
    status_choices = [
        (1,'未支付'),
        (2, '已支付'),
    ]

    status = models.SmallIntegerField(verbose_name='状态',choices=status_choices)

    order = models.CharField(verbose_name='订单号',max_length=64,unique=True)  #唯一索引

    user = models.ForeignKey(verbose_name='用户',to='UserInfo',on_delete=models.CASCADE)    #级联删除
    price_policy = models.ForeignKey(verbose_name='价格',to='PricePolicy',on_delete=models.CASCADE)

    count = models.IntegerField(verbose_name='数量（年）',help_text='0表示无限期')

    price = models.IntegerField(verbose_name="实际支付价格")

    start_datetime = models.DateTimeField(verbose_name='开始时间',null=True,blank=True)
    end_datetime = models.DateTimeField(verbose_name='结束时间',null=True,blank=True)

    create_datetime = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)


class Project(models.Model):
    """项目表"""
    COLOR_CHOICES = [
        (1,'#56b8eb'),
        (2,'#d7d0d7'),
        (3,'#ff7f00'),
        (4,'#ffd960'),
        (5,'#ffffb0'),
        (6,'#ffa500'),
        (7,'#ffd700'),
    ]
    name = models.CharField(verbose_name='项目名',max_length=32)
    color = models.SmallIntegerField(verbose_name='颜色',choices=COLOR_CHOICES,default=11)
    desc = models.CharField(verbose_name='项目描述',max_length=255,null=True,blank=True)
    star = models.BooleanField(verbose_name='星标',default=False)

    join_count = models.SmallIntegerField(verbose_name='参与人数',default=1)
    creator = models.ForeignKey(verbose_name='创建者',to='UserInfo',on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)


    #查询：可以省事
    #增加，删除，修改：无法完成，所以一般不用
    #project_user = models.ManyToManyField(to='UserInfo',through='ProjectUser',through_fields=('project','user'))

class ProjectUser(models.Model):
    """项目参与者"""
    project = models.ForeignKey(verbose_name="项目", to='Project', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name="参与者",to='UserInfo',on_delete=models.CASCADE)

    star = models.BooleanField(verbose_name='星标',default=False)

    create_datetime = models.DateTimeField(verbose_name="加入时间",auto_now_add=True)


class Wiki(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='标题',max_length=32)
    content = models.TextField(verbose_name='内容')

    depth = models.IntegerField(verbose_name='深度',default=1)


    #子关联 to='Wiki' 也可以写成to='self'
    parent = models.ForeignKey(verbose_name='父文章',to='Wiki',on_delete=models.CASCADE,null=True,blank=True,related_name='children')

    def __str__(self):
        return self.title

