from django.contrib.gis.db import models

class Local(models.Model):
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=50)
    endereco = models.TextField()
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=50)
    geom = models.PointField()  # Campo geoespacial

    def __str__(self):
        return self.nome
