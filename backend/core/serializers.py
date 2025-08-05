from rest_framework import serializers
from .models import CryptoCurrency, News

class CryptoCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoCurrency
        fields = '__all__'

class CryptoCurrencyMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoCurrency
        fields = ['id', 'symbol', 'name']

class NewsSerializer(serializers.ModelSerializer):
    cryptos = CryptoCurrencyMiniSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'source', 'author', 'url', 'urlToImage', 'published_at',
            'summary', 'cryptos', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'cryptos'
        ]