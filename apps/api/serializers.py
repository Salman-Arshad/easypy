from rest_framework import serializers

from apps.main.models import Execution


class ExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Execution
        fields = '__all__'


# noinspection PyAbstractClass
class RunSerializer(serializers.Serializer):
    timeframe_choices = (
        ('1m', '1m'),
        ('5m', '5m'),
        ('1h', '1h'),
        ('1d', '1d'),
    )
    signal_choices = (
        ('signals_option_0', 'signals_option_0'),
        ('signals_option_1', 'signals_option_1'),
        ('signals_option_2', 'signals_option_2'),
        ('signals_option_3', 'signals_option_3'),
        ('signals_option_4', 'signals_option_4'),
        ('signals_option_5', 'signals_option_5'),
        ('signals_option_6', 'signals_option_6'),
        ('signals_option_7', 'signals_option_7'),
        ('signals_option_8', 'signals_option_8'),
        ('signals_option_9', 'signals_option_9'),
        ('signals_option_10', 'signals_option_10'),
        ('signals_option_11', 'signals_option_11'),
        ('signals_option_12', 'signals_option_12'),
        ('signals_option_13', 'signals_option_13'),
        ('signals_option_14', 'signals_option_14'),
        ('signals_option_15', 'signals_option_15'),
        ('signals_option_16', 'signals_option_16'),
        ('signals_option_17', 'signals_option_17'),
        ('signals_option_18', 'signals_option_18'),
        ('signals_option_19', 'signals_option_19'),
        ('signals_option_20', 'signals_option_20'),
        ('signals_option_21', 'signals_option_21'),
        ('signals_option_22', 'signals_option_22'),
        ('signals_option_23', 'signals_option_23'),
        ('signals_option_24', 'signals_option_24'),
        ('signals_option_25', 'signals_option_25'),
        ('signals_option_26', 'signals_option_26'),
        ('signals_option_27', 'signals_option_27')
    )
    id = serializers.CharField()
    secret = serializers.CharField()
    symbol = serializers.CharField()
    timeframe = serializers.ChoiceField(choices=timeframe_choices)
    signal = serializers.ChoiceField(choices=signal_choices)
