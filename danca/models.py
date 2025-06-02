from datetime import timedelta
from django.db import models
from .constants import STATUS_EVENTO, TAMANHO_CAMISA, TIPO_CAMISA, STATUS_LOTE
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Sum
from datetime import date, timedelta



class Lote(models.Model):
    descricao = models.CharField(max_length=255)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidades = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_LOTE, default='ativo')

    def __str__(self):
        return f"{self.descricao} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-id']

class Categoria(models.Model):
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.descricao
    
    class Meta:
        ordering = ['-id']

class TipoEvento(models.Model):
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.descricao
    
    class Meta:
        ordering = ['-id']

class Evento(models.Model):
    descricao = models.CharField(max_length=100)
    tipo = models.ForeignKey(TipoEvento, on_delete=models.CASCADE)
    data = models.DateField(null=True, blank=True)
    quantidade_pessoas = models.IntegerField(null=True, blank=True, help_text='Número máximo de vagas disponíveis')
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Valor unitário do evento')
    contador_inscricoes = models.IntegerField(default=0, editable=False, verbose_name="Inscrições")
    status = models.CharField(max_length=20, choices=STATUS_EVENTO, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.descricao} - {self.tipo.descricao}"
    
    def get_vagas_disponiveis(self):
        """Retorna o número de vagas disponíveis para o evento"""
        if self.quantidade_pessoas is None:
            return None
        return max(0, self.quantidade_pessoas - self.contador_inscricoes)
    
    def atualizar_contador_inscricoes(self):
        """Atualiza o contador de inscrições baseado nas inscrições ativas"""
        novo_contador = self.inscricao_eventos.count()
        if self.contador_inscricoes != novo_contador:
            self.contador_inscricoes = novo_contador
            super().save(update_fields=['contador_inscricoes'])
    
    def save(self, *args, **kwargs):
        """Atualiza o contador de inscrições ao salvar o evento"""
        # Salva primeiro para garantir que o ID exista
        super().save(*args, **kwargs)
        
        # Atualiza o contador apenas se o evento já existir no banco
        if self.id:
            self.atualizar_contador_inscricoes()
    
    class Meta:
        ordering = ['-data', '-id']
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"


class Camisa(models.Model):
    descricao = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CAMISA, default='unissex')
    quantidade = models.IntegerField(default=0)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.descricao} - {self.get_tipo_display()}"

    class Meta:
        verbose_name = "Camisa"
        verbose_name_plural = "Camisas"
        ordering = ['tipo', '-data_atualizacao']

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario if self.quantidade and self.valor_unitario else 0


class Planejamento(models.Model):
    descricao = models.CharField(max_length=100)   
    valor_planejado = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)    
      

    def __str__(self):
        return self.descricao    
    class Meta:
        ordering = ['-id']
        verbose_name = "Planejamento"
        verbose_name_plural = "Planejamentos"
    
    @property
    def valor_pago(self):
        content_type = ContentType.objects.get_for_model(self)
        total_pago = Pagamento.objects.filter(
            content_type=content_type,
            object_id=self.id
        ).aggregate(total=Sum('valor_pago'))['total'] or 0
        return total_pago

    @property
    def valor_restante(self):
        return (self.valor_planejado or 0) - self.valor_pago

    @property
    def status(self):
        if self.valor_restante <= 0:
            return "Pago"
        elif self.valor_pago > 0:
            return "Parcial"
        return "Pendente"



class Inscricao(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    cep = models.CharField(max_length=9, null=True, blank=True)
    municipio = models.CharField(max_length=100, null=True, blank=True)
    uf = models.CharField(max_length=2, null=True, blank=True)
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    numero_parcelas = models.IntegerField(default=1)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    valor_parcela = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    eventos = models.ManyToManyField(Evento, through='InscricaoEvento', related_name='inscricao_eventos')

    def calcular_valor_total(self):
        """
        Calcula o valor total com base nos eventos associados, considerando desconto e lote.
        """
        valor_base = sum(evento.valor_unitario for evento in self.eventos.all())
        valor_com_desconto = valor_base - self.desconto
        valor_final = valor_com_desconto + self.lote.valor_unitario
        return valor_final

    def calcular_valor_parcela(self):
        """
        Calcula o valor de cada parcela com base no valor total e no número de parcelas.
        """
        if self.numero_parcelas > 0:
            return self.valor_total / self.numero_parcelas
        return 0

    def save(self, *args, **kwargs):
        """
        Salva a instância e calcula o valor total após salvar.
        """
        # Salva a instância para garantir que ela tenha um ID
        super().save(*args, **kwargs)

        # Atualiza o valor total após salvar e associar os eventos
        self.valor_total = self.calcular_valor_total()
        self.valor_parcela = self.calcular_valor_parcela()
        super().save(update_fields=['valor_total', 'valor_parcela'])
    

    def __str__(self):
        return f"{self.nome} - {self.categoria.descricao}"

    class Meta:
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"
        ordering = ['-id']
    
    @property
    def valor_pago(self):
        content_type = ContentType.objects.get_for_model(self)
        total_pago = Pagamento.objects.filter(
            content_type=content_type,
            object_id=self.id
        ).aggregate(total=Sum('valor_pago'))['total'] or 0
        return total_pago

    @property
    def valor_restante(self):
        return self.valor_total - self.valor_pago
    
    @property
    def status(self):
        if self.valor_restante <= 0:
            return "Pago"
        elif self.valor_pago > 0:
            return "Parcial"
        return "Pendente"
    
    @property
    def proximo_pagamento(self):
        content_type = ContentType.objects.get_for_model(self)
        proximo = Pagamento.objects.filter(
            content_type=content_type,
            object_id=self.id,
            data_proximo_pagamento__isnull=False
        ).order_by('data_proximo_pagamento').first()

        if proximo:
            return proximo.data_proximo_pagamento  # Retorna como objeto de data
        return None

class InscricaoEvento(models.Model):
    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE, related_name='inscricao_evento_set')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Evento da Inscrição"
        verbose_name_plural = "Eventos das Inscrições"
        unique_together = [['inscricao', 'evento']]

    def __str__(self):
        return f"{self.inscricao.nome} - {self.evento.descricao}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.evento.atualizar_contador_inscricoes()
        
        self.inscricao.valor_total = self.inscricao.calcular_valor_total()
        self.inscricao.valor_parcela = self.inscricao.calcular_valor_parcela()
        self.inscricao.save(update_fields=['valor_total', 'valor_parcela'])


    def delete(self, *args, **kwargs):
        evento = self.evento
        inscricao = self.inscricao
        super().delete(*args, **kwargs)
        evento.atualizar_contador_inscricoes()
        
        inscricao.valor_total = inscricao.calcular_valor_total()
        inscricao.valor_parcela = inscricao.calcular_valor_parcela()
        inscricao.save(update_fields=['valor_total', 'valor_parcela'])


class Profissional(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    valor_hora_aula = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qt_aulas = models.IntegerField(null=True, blank=True)
    funcao = models.CharField(max_length=100, null=True, blank=True)
    local_partida = models.CharField(max_length=100, null=True, blank=True)
    local_volta = models.CharField(max_length=100, null=True, blank=True)
    eventos = models.ManyToManyField(Evento, through='ProfissionalEvento', related_name='profissionais_eventos')

    def calcular_cache(self):
        if self.valor_hora_aula is not None and self.qt_aulas is not None:
            return self.valor_hora_aula * self.qt_aulas
        return None

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"
        ordering = ['-id']


class ProfissionalEvento(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='profissional_evento_set')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Evento do Profissional"
        verbose_name_plural = "Eventos dos Profissionais"
        unique_together = [['profissional', 'evento']]

    def __str__(self):
        return f"{self.profissional.nome} - {self.evento.descricao}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.evento.atualizar_contador_inscricoes()

    def delete(self, *args, **kwargs):
        evento = self.evento
        super().delete(*args, **kwargs)
        evento.atualizar_contador_inscricoes()


class Entrada(models.Model):
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()   
   
    
    def __str__(self):
        return f"Entrada - {self.descricao} - R$ {self.valor}"
    
    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ['-data']


class Saida(models.Model):
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()   
    
    def __str__(self):
        return f"Saída - {self.descricao} - R$ {self.valor}"
    
    class Meta:
        verbose_name = "Saída"
        verbose_name_plural = "Saídas"
        ordering = ['-data']


class Pagamento(models.Model):
    TIPOS_MODELO = [
        ('planejamento', 'Planejamento'),
        ('inscricao', 'Inscrição'),
    ]
    tipo_modelo = models.CharField(max_length=20, choices=TIPOS_MODELO)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    pagamento_relacionado = GenericForeignKey('content_type', 'object_id')

    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateField(auto_now_add=True)
    data_proximo_pagamento = models.DateField(null=True, blank=True)  
    numero_parcela =models.IntegerField()

    def save(self, *args, **kwargs):
        # Garante que data_pagamento não seja None
        if not self.data_pagamento:
            self.data_pagamento = date.today()

        # Calcula a data do próximo pagamento apenas para inscrições
        if self.tipo_modelo == 'inscricao':
            self.data_proximo_pagamento = self.data_pagamento + timedelta(days=30)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo_modelo} - {self.pagamento_relacionado} - Parcela {self.numero_parcela}"

    
    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-data_pagamento']
        get_latest_by = 'data_pagamento'  # Define o campo para o método latest