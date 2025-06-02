from django import forms
from django.core.exceptions import ValidationError
from .models import Lote,Categoria,TipoEvento,Evento,Camisa,Planejamento,Inscricao, InscricaoEvento,Profissional, ProfissionalEvento, Entrada, Saida,Pagamento
from decimal import Decimal, InvalidOperation
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
import re 

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['descricao', 'valor_unitario', 'unidades', 'status']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do lote'}),
            'valor_unitario': forms.TextInput(attrs={'class': 'form-control mask-valor', 'placeholder': 'R$ 0,00'}),
            'unidades': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Quantidade'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'descricao': 'Descrição do Lote',
            'valor_unitario': 'Valor Unitário',
            'unidades': 'Quantidade de Unidades',
            'status': 'Status',
        }

    def clean_unidades(self):
        """
        Valida o campo unidades para garantir que seja maior que zero.
        """
        unidades = self.cleaned_data.get('unidades')
        if unidades is not None and unidades <= 0:
            raise ValidationError("A quantidade de unidades deve ser maior que zero.")
        return unidades


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['descricao']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição da categoria'}),
        }
        labels = {
            'descricao': 'Descrição da Categoria',
        }


class TipoEventoForm(forms.ModelForm):
    class Meta:
        model = TipoEvento
        fields = ['descricao']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do Tipo de Evento'}),
        }
        labels = {
            'descricao': 'Descrição do Tipo de Evento',
        }

    
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['descricao', 'tipo', 'data', 'quantidade_pessoas', 'valor_unitario', 'status']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do Evento'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control mask-data', 'type': 'date'}),
            'quantidade_pessoas': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Número de vagas'}),
            'valor_unitario': forms.TextInput(attrs={'class': 'form-control mask-valor', 'placeholder': 'R$ 0,00'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'descricao': 'Descrição do Evento',
            'tipo': 'Tipo de Evento',
            'data': 'Data do Evento',
            'quantidade_pessoas': 'Quantidade de Vagas',
            'valor_unitario': 'Valor Unitário',
            'status': 'Status do Evento',
        }

    def clean_quantidade_pessoas(self):
        """
        Valida o campo quantidade_pessoas para garantir que seja maior que zero.
        """
        quantidade_pessoas = self.cleaned_data.get('quantidade_pessoas')
        if quantidade_pessoas is not None and quantidade_pessoas <= 0:
            raise ValidationError("A quantidade de vagas deve ser maior que zero.")
        return quantidade_pessoas

    def clean_valor_unitario(self):
        """
        Valida o campo valor_unitario para garantir que seja maior ou igual a zero.
        """
        valor_unitario = self.cleaned_data.get('valor_unitario')
        if valor_unitario is not None and valor_unitario < 0:
            raise ValidationError("O valor unitário não pode ser negativo.")
        return valor_unitario

class CamisaForm(forms.ModelForm):
    class Meta:
        model = Camisa
        fields = ['descricao', 'tipo', 'quantidade', 'valor_unitario']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição da Camisa'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Quantidade em estoque'}),
            'valor_unitario': forms.TextInput(attrs={'class': 'form-control mask-valor', 'placeholder': 'R$ 0,00'}),
        }
        labels = {
            'descricao': 'Descrição da Camisa',
            'tipo': 'Tipo',
            'quantidade': 'Quantidade em Estoque',
            'valor_unitario': 'Valor Unitário',
        }
    def clean_quantidade(self):
        """
        Valida o campo quantidade para garantir que seja maior ou igual a zero.
        """
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is not None and quantidade < 0:
            raise ValidationError("A quantidade não pode ser negativa.")
        return quantidade

    def clean_valor_unitario(self):
        """
        Valida o campo valor_unitario para garantir que seja maior ou igual a zero.
        """
        valor_unitario = self.cleaned_data.get('valor_unitario')
        if valor_unitario is not None and valor_unitario < 0:
            raise ValidationError("O valor unitário não pode ser negativo.")
        return valor_unitario


class PlanejamentoForm(forms.ModelForm):
    class Meta:
        model = Planejamento
        fields = ['descricao', 'valor_planejado']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do Planejamento'}),
            'valor_planejado': forms.TextInput(attrs={'class': 'form-control mask-valor', 'placeholder': 'R$ 0,00'}),
        }
        labels = {
            'descricao': 'Descrição do Planejamento',
            'valor_planejado': 'Valor Planejado',
        }

    def clean_valor_planejado(self):
        """
        Valida o campo valor_planejado para garantir que seja maior ou igual a zero.
        """
        valor_planejado = self.cleaned_data.get('valor_planejado')
        if valor_planejado is not None and valor_planejado < 0:
            raise ValidationError("O valor planejado não pode ser negativo.")
        return valor_planejado




class InscricaoForm(forms.ModelForm):
    numero_parcelas = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'placeholder': 'Número de parcelas',
            'type': 'number'
        })
    )
    eventos = forms.ModelMultipleChoiceField(
        queryset=Evento.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Eventos"
    )

    class Meta:
        model = Inscricao
        fields = [
            'nome', 'cpf', 'categoria', 'cep', 'municipio', 'uf',
            'lote', 'desconto', 'numero_parcelas', 'eventos'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'uf': forms.TextInput(attrs={'class': 'form-control'}),
            'lote': forms.Select(attrs={'class': 'form-select'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'numero_parcelas': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome completo',
            'cpf': 'CPF',
            'categoria': 'Categoria',
            'cep': 'CEP',
            'municipio': 'Município',
            'uf': 'UF',
            'lote': 'Lote',
            'desconto': 'Desconto (R$)',
            'numero_parcelas': 'Número de Parcelas',
        }
        help_texts = {
            'numero_parcelas': 'Informe somente números inteiros.',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lote'].queryset = Lote.objects.all()

    def clean_desconto(self):
        desconto = self.cleaned_data.get('desconto')
        if desconto and desconto < 0:
            raise ValidationError("O desconto não pode ser negativo")
        return desconto

    def clean_numero_parcelas(self):
        numero_parcelas = self.cleaned_data.get('numero_parcelas')
        if numero_parcelas is None:
            raise ValidationError("Por favor, informe o número de parcelas")
        if not isinstance(numero_parcelas, int):
            raise ValidationError("Por favor, informe um número inteiro")
        if numero_parcelas < 1:
            raise ValidationError("O número de parcelas deve ser pelo menos 1")
        return numero_parcelas


class InscricaoEventoForm(forms.ModelForm):
    class Meta:
        model = InscricaoEvento
        fields = ['evento']
        widgets = {
            'evento': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'evento': 'Evento',
        }


class ProfissionalForm(forms.ModelForm):
    eventos = forms.ModelMultipleChoiceField(
        queryset=Evento.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Eventos"
    )

    class Meta:
        model = Profissional
        fields = ['nome','cpf' ,'valor_hora_aula', 'qt_aulas', 'funcao', 'local_partida', 'local_volta', 'eventos']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'cpf': forms.TextInput(attrs={'class': 'form-control mask-cpf', 'placeholder': 'XXX.XXX.XXX-XX'}),
            'valor_hora_aula': forms.NumberInput(attrs={'class': 'form-control', 'required': True, 'step': '0.01', 'min': '0.01'}),
            'qt_aulas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Quantidade de aulas'}),
            'funcao': forms.TextInput(attrs={'class': 'form-control'}),
            'local_partida': forms.TextInput(attrs={'class': 'form-control'}),
            'local_volta': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome completo',
            'cpf': 'CPF',
            'valor_hora_aula': 'Valor da Hora Aula',
            'qt_aulas': 'Quantidade de Aulas',
            'funcao': 'Função',
            'local_partida': 'Local de Partida',
            'local_volta': 'Local de Volta',
        }

    def clean_valor_hora_aula(self):
        valor_hora_aula = self.cleaned_data.get('valor_hora_aula')
        if valor_hora_aula is not None and valor_hora_aula < 0:
            raise ValidationError("O valor da hora aula não pode ser negativo")
        return valor_hora_aula

    def clean_qt_aulas(self):
        qt_aulas = self.cleaned_data.get('qt_aulas')
        if qt_aulas is not None and qt_aulas < 0:
            raise ValidationError("A quantidade de aulas não pode ser negativa")
        return qt_aulas

    def clean(self):
        cleaned_data = super().clean()
        # Verifica apenas se o nome está preenchido
        nome = cleaned_data.get('nome')
        if not nome:
            self.add_error('nome', 'Este campo é obrigatório.')
        return cleaned_data


class ProfissionalEventoForm(forms.ModelForm):
    class Meta:
        model = ProfissionalEvento
        fields = ['evento']
        widgets = {
            'evento': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'evento': 'Evento',
        }

class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        fields = ['descricao', 'valor', 'data']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'required': True, 'step': '0.01', 'min': '0.01'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
        }
        labels = {
            'descricao': 'Descrição',
            'valor': 'Valor (R$)',
            'data': 'Data',
        }

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor <= 0:
            raise ValidationError("O valor deve ser maior que zero")
        return valor

class SaidaForm(forms.ModelForm):
    class Meta:
        model = Saida
        fields = ['descricao', 'valor', 'data']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'required': True, 'step': '0.01', 'min': '0.01'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
        }
        labels = {
            'descricao': 'Descrição',
            'valor': 'Valor (R$)',
            'data': 'Data',
        }

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor is not None and valor <= 0:
            raise ValidationError("O valor deve ser maior que zero")
        return valor



class PagamentoForm(forms.ModelForm):
    tipo_modelo = forms.ChoiceField(
        choices=[('', 'Selecione o tipo de pagamento')] + Pagamento.TIPOS_MODELO,
        label="Tipo de Modelo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    pagamento_relacionado_id = forms.ChoiceField(
        required=False,
        label="Pagamento Relacionado",
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Modifiquei o campo 'valor_pago' para CharField
    valor_pago = forms.CharField(
        label='Valor Pago',
        widget=forms.TextInput(attrs={'class': 'form-control mask-valor', 'placeholder': 'R$ 0,00'})
    )

    class Meta:
        model = Pagamento
        fields = ['tipo_modelo', 'valor_pago','numero_parcela']
        widgets = {
            # Não é necessário alterar o widget aqui, pois 'valor_pago' foi mudado para CharField
        }
        labels = {
            'valor_pago': 'Valor Pago',
        }

    def clean_valor_pago(self):
        valor = self.cleaned_data.get('valor_pago')
        # Usando regex para remover R$, ponto e substituir vírgula por ponto
        if valor:
            valor = re.sub(r'[^0-9,]', '', valor)  # Remove qualquer coisa que não seja número ou vírgula
            valor = valor.replace(",", ".")  # Substitui vírgula por ponto

        try:
             return Decimal(valor) 
        except ValueError:
            raise forms.ValidationError("Informe um valor numérico válido.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tipo_modelo = self.data.get('tipo_modelo') or self.initial.get('tipo_modelo')
        if tipo_modelo == 'planejamento':
            self.fields['pagamento_relacionado_id'].choices = [
                (obj.id, str(obj)) for obj in Planejamento.objects.all()
            ]
        elif tipo_modelo == 'inscricao':
            self.fields['pagamento_relacionado_id'].choices = [
                (obj.id, str(obj)) for obj in Inscricao.objects.all()
            ]

    def clean(self):
        cleaned_data = super().clean()
        tipo_modelo = cleaned_data.get('tipo_modelo')
        rel_id = self.data.get('pagamento_relacionado_id')

        if tipo_modelo and rel_id:
            model_class = {
                'planejamento': Planejamento,
                'inscricao': Inscricao
            }.get(tipo_modelo)

            if model_class:
                try:
                    obj = model_class.objects.get(id=rel_id)
                    cleaned_data['content_type'] = ContentType.objects.get_for_model(model_class)
                    cleaned_data['object_id'] = obj.id
                except model_class.DoesNotExist:
                    self.add_error('pagamento_relacionado_id', 'Objeto relacionado não encontrado.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.content_type = self.cleaned_data.get('content_type')
        instance.object_id = self.cleaned_data.get('object_id')
        if commit:
            instance.save()
        return instance