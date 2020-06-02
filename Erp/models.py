import datetime

from django.db import models

# Create your models here.
from django.db.models import QuerySet, Count, Sum

from Erp.views import calcount


class Material(models.Model):
    materialId = models.AutoField(verbose_name='物料编号', primary_key=True)
    materialName = models.CharField(verbose_name='物料名称', max_length=40, null=True, blank=True)
    deploy = models.CharField(verbose_name='调配方式', max_length=40, null=True, blank=True)
    loss = models.FloatField(verbose_name='损耗率', default=0)
    preDay = models.IntegerField(verbose_name='作业提前期', default=0)
    unit = models.CharField(verbose_name='单位', max_length=40, null=True, blank=True)

    class Meta:
        db_table = "Material"
        verbose_name_plural = '物料'
        ordering = ['materialId']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Material, self).save()
        inventory = Inventory(materialId=self)
        inventory.save()

    def __str__(self):
        return self.materialName


class Deploy(models.Model):
    deployid = models.AutoField(verbose_name='调配编号', primary_key=True)
    sonId = models.ForeignKey('Erp.Material', models.CASCADE, blank=True, null=True, related_name="+",
                              verbose_name='子物料')
    fatherId = models.ForeignKey('Erp.Material', models.CASCADE, blank=True, null=True, related_name="+",
                                 verbose_name='父物料')
    areaId = models.CharField(max_length=40, null=True, blank=True, verbose_name='调配区编号')
    number = models.IntegerField(default=0, verbose_name='构成数')
    preMatrial = models.IntegerField(default=0, verbose_name='配料提前期')
    preSupplizer = models.IntegerField(default=0, verbose_name='供应商提前期')

    class Meta:
        db_table = "Deploy"
        verbose_name_plural = '调配'
        ordering = ['deployid']


class Inventory(models.Model):
    inventoryId = models.AutoField(primary_key=True, verbose_name='库存编号')
    materialId = models.ForeignKey('Erp.Material', models.CASCADE, blank=True, null=True, related_name="+",
                                   verbose_name='物料')
    materialInventory = models.IntegerField(default=0, verbose_name='工序库存')
    processInventory = models.IntegerField(default=0, verbose_name='资材库存')

    class Meta:
        db_table = "Inventory"
        verbose_name_plural = '库存'
        ordering = ['inventoryId']


class Order(models.Model):
    orderId = models.AutoField(primary_key=True, verbose_name='订单编号')
    productName = models.ForeignKey('Erp.Material', models.CASCADE, blank=True, null=True, related_name="+",
                                    verbose_name='产品名称')
    productNum = models.IntegerField(default=0, verbose_name='产品数量')
    ddl = models.DateField(verbose_name="完工日期")

    class Meta:
        db_table = "Order"
        verbose_name_plural = 'MPS'
        ordering = ['orderId']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Order, self).save()

        # 父物料的库存，看一下父物料需要多少，这样才能算出子物料的需求
        invertory = Inventory.objects.filter(materialId=self.productName).first()
        tempcount = calcount(invertory, self.productNum)
        if tempcount < 0:
            # 表示父物料的库存已经够了需求
            mrpresult = mrpResult(orderId=self, deploy=self.productName.deploy, materialId=self.productName.materialId,
                                  materialName=self.productName.materialName, count=0,
                                  fixcount=self.productNum,
                                  askDate=self.ddl - datetime.timedelta(days=self.productName.preDay),
                                  finishDate=self.ddl)
            mrpresult.save(force_insert=True)
            # 这边还需要把眼镜的库存删掉

            ttvalue = invertory.materialInventory - self.productNum
            if ttvalue < 0:
                invertory.materialInventory = 0
                invertory.processInventory += ttvalue
            else:
                invertory.materialInventory = ttvalue
            invertory.save(force_update=True)

        else:
            mrpresult = mrpResult(orderId=self, deploy=self.productName.deploy, materialId=self.productName.materialId,
                                  materialName=self.productName.materialName, count=tempcount,
                                  fixcount=self.productNum - tempcount,
                                  askDate=self.ddl - datetime.timedelta(days=self.productName.preDay),
                                  finishDate=self.ddl)
            mrpresult.save(force_insert=True)
            # 处理眼镜的库存
            invertory.materialInventory = 0
            invertory.processInventory = 0
            invertory.save(force_update=True)

            # 保存一下第一级的下达时间
            tempdate = self.ddl - datetime.timedelta(days=self.productName.preDay)

            if tempcount != 0:
                # 采用广度优先搜索算法
                # 处理下一级
                deploylist = Deploy.objects.filter(fatherId=self.productName)
                gendata = []
                # 给每个item加上时间
                for item in deploylist:
                    tt = {}
                    tt['deploy'] = item
                    tt['date'] = tempdate
                    tt['count'] = tempcount
                    gendata.append(tt)
                for item in gendata:
                    # 算出需求量
                    tempinventory = Inventory.objects.filter(materialId=item['deploy'].sonId).first()
                    itemcount = (item['count'] * item['deploy'].number) / (
                            1 - item[
                        'deploy'].sonId.loss) - tempinventory.materialInventory - tempinventory.processInventory
                    if ((item['count'] * item['deploy'].number) % (1 - item['deploy'].sonId.loss)) != 0:
                        itemcount += 1

                    if itemcount < 0:
                        mrpresult = mrpResult(orderId=self, deploy=item['deploy'].sonId.deploy,
                                              materialId=item['deploy'].sonId.materialId,
                                              materialName=item['deploy'].sonId.materialName, count=0,
                                              fixcount=((item['count'] * item['deploy'].number) / (
                                                      1 - item['deploy'].sonId.loss)),
                                              askDate=item['date'] - datetime.timedelta(
                                                  days=item['deploy'].sonId.preDay) - datetime.timedelta(
                                                  days=(item['deploy'].preMatrial + item['deploy'].preSupplizer)),
                                              finishDate=item['date'])
                        mrpresult.save(force_insert=True)
                        # 处理对应等级的库存

                        ttvalue = tempinventory.materialInventory - itemcount
                        if ttvalue < 0:
                            tempinventory.materialInventory = 0
                            tempinventory.processInventory += ttvalue
                        else:
                            tempinventory.materialInventory = ttvalue
                        tempinventory.save(force_update=True)

                    else:
                        # 库存不够
                        mrpresult = mrpResult(orderId=self, deploy=item['deploy'].sonId.deploy,
                                              materialId=item['deploy'].sonId.materialId,
                                              materialName=item['deploy'].sonId.materialName, count=itemcount,
                                              fixcount=tempinventory.materialInventory + tempinventory.processInventory,
                                              askDate=item['date'] - datetime.timedelta(
                                                  days=item['deploy'].sonId.preDay) - datetime.timedelta(
                                                  days=(item['deploy'].preMatrial + item['deploy'].preSupplizer)),
                                              finishDate=item['date'])
                        mrpresult.save(force_insert=True)
                        # 处理库存
                        tempinventory.materialInventory = 0
                        tempinventory.processInventory = 0
                        tempinventory.save(force_update=True)
                        #
                        # 处理下一级
                        if itemcount != 0:
                            ttdeploylist = Deploy.objects.filter(fatherId=item['deploy'].sonId.materialId)
                            ttempdate = item['date'] - datetime.timedelta(
                                days=item['deploy'].sonId.preDay) - datetime.timedelta(
                                days=(item['deploy'].preMatrial + item['deploy'].preSupplizer))
                            for ii in ttdeploylist:
                                ttt = {}
                                ttt['deploy'] = ii
                                ttt['date'] = ttempdate
                                ttt['count'] = itemcount
                                gendata.append(ttt)

            mrplist = mrpResult.objects.filter(orderId=self) \
                .values('materialId') \
                .annotate(resutl_count=Count('materialId'), fixcount=Sum('fixcount')) \
                .filter(resutl_count__gt=1) \
                .order_by('materialId')
            for item in mrplist:
                print(item)
                tempmrplist = mrpResult.objects.filter(orderId=self, materialId=item['materialId']).order_by('askDate')
                leftcount = item['fixcount']
                for jj in tempmrplist:
                    # 表示除了自己花费的库存外，原库存里面还剩多少库存
                    if leftcount > 0:
                        leftcount -= jj.fixcount
                        if leftcount > 0 and jj.count > 0:
                            if jj.count - leftcount > 0:
                                jj.count -= leftcount
                                jj.fixcount += leftcount
                                jj.save(force_update=True)
                                # 这个剩下的库存为0表示后来者得把自己的使用的库存吐出来
                                leftcount = 0
                            # 表示剩下的库存实际比你要的还多，所以不能全部给你
                            else:
                                leftcount -= jj.count
                                jj.fixcount += jj.count
                                jj.count = 0
                                jj.save(force_update=True)
                    else:
                        jj.count += jj.fixcount
                        jj.fixcount = 0
                        jj.save(force_update=True)

    def __str__(self):
        return str(self.orderId)


class mrpResult(models.Model):
    mrpResultId = models.AutoField(primary_key=True, verbose_name="结果ID")
    orderId = models.ForeignKey('Erp.Order', models.CASCADE, blank=True, null=True, related_name="+",
                                verbose_name='MPS编号')
    deploy = models.CharField(max_length=40, null=True, blank=True, verbose_name='调配方式')
    materialId = models.IntegerField(default=0, verbose_name="物料号")
    materialName = models.CharField(max_length=40, null=True, blank=True, verbose_name='物料名称')
    count = models.IntegerField(default=0, verbose_name="需求数量")
    fixcount = models.IntegerField(default=0, verbose_name="花费的库存")
    askDate = models.DateField(verbose_name="日程下达日期")
    finishDate = models.DateField(verbose_name="日程完成日期")

    class Meta:
        db_table = "MPSresult"
        verbose_name_plural = 'MPS结果'
        ordering = ['mrpResultId']
