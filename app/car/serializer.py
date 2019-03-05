#!/usr/bin/env python
# -*- coding:utf-8 -*-


# Time: 2019/2/27 10:48
__author__ = 'Peter.Fang'

from rest_framework import serializers
from .models import CarInfoManage, CarFixManage, CarFixAccManage
from app.staff.models import EmployeeManage
from app.staff.serializer import EmployeeSerializer


class CarInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarInfoManage
        fields = "__all__"

    def create(self, validated_data):
        sn = validated_data.pop('sn', None)
        car_info, created = CarInfoManage.objects.update_or_create(
            sn=sn, defaults=validated_data)
        return car_info


class FixAccSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarFixAccManage
        fields = "__all__"


class CarFixSerializer(serializers.ModelSerializer):
    car = CarInfoSerializer(read_only=True)
    # fix_acc = FixAccSerializer(many=True, read_only=True)  # 被外键的字段，添加在这就可以直接显示
    fix_man = EmployeeSerializer(read_only=True)

    class Meta:
        model = CarFixManage
        fields = "__all__"

    @staticmethod
    def _get_fix_man(name):
        try:
            print(name)
            return EmployeeManage.objects.get(name=name).id
        except Exception as e:
            print(e)
            raise

    def create(self, validated_data):
        # 由于read_only将car_id自动过滤，只能通过获取参数值，来创建car_fix
        car_info = CarFixManage(**validated_data, car_id=self.context['request'].data['car_id'],
                                fix_man_id=self._get_fix_man(self.context['request'].data['fix_man_id']))
        car_info.save()
        return car_info

    def update(self, instance, validated_data):
        print(validated_data)

        instance.car_id = self.context['request'].data['car_id']
        instance.fix_man_id = self._get_fix_man(self.context['request'].data['fix_man_id'])
        instance.save()
        return instance
