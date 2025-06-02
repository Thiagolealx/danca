from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, DeleteView, DetailView
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.db.models.functions import Lower
from .models import Lote, Categoria, TipoEvento, Evento, Camisa,Planejamento,Inscricao, InscricaoEvento, Profissional, ProfissionalEvento, Entrada, Saida,Pagamento
from .form import LoteForm,CategoriaForm,TipoEventoForm,EventoForm,CamisaForm,PlanejamentoForm,InscricaoForm, InscricaoEventoForm, ProfissionalForm, ProfissionalEventoForm, EntradaForm, SaidaForm, PagamentoForm
from django.shortcuts import redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.views.decorators.http import require_GET
from datetime import date
from django.db.models import OuterRef, Subquery
from django.contrib.contenttypes.models import ContentType
from datetime import date, timedelta




def index(request):
    return render(request, 'index.html')


#@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name="dispatch")
class LoteListView(ListView):
    model = Lote
    paginate_by = 10
    template_name = "lote/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Lote.objects.filter(descricao__icontains=query).order_by(Lower('descricao'))
        return Lote.objects.all().order_by(Lower('descricao'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['create_url'] = reverse('create_lote')
        return context

#@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name="dispatch")
class LoteDetailView(TemplateView):
    template_name = "lote/lote.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lote = get_object_or_404(Lote, id=self.kwargs['lote_id'])
        context['lote'] = lote
        return context

#@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name="dispatch")
class LoteFormView(View):
    form_class = LoteForm
    template_name = "lote/form.html"

    def get(self, request, lote_id=None):
        form = self.form_class()
        titulo = "Novo Lote" if not lote_id else "Editar Lote"
        if lote_id:
            lote = get_object_or_404(Lote, id=lote_id)
            form = self.form_class(instance=lote)
        return render(request, self.template_name, {
            "form": form,
            "titulo": titulo,
        })

    def post(self, request, lote_id=None):
        form = self.form_class(request.POST)
        msg = 'Lote criado com sucesso'

        if lote_id:
            lote = get_object_or_404(Lote, id=lote_id)
            form = self.form_class(request.POST, instance=lote)
            msg = 'Lote modificado com sucesso'
    
        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect('list_lotes')

#@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name="dispatch")
class LoteDeleteView(DeleteView):  
    model = Lote
    pk_url_kwarg = "lote_id"    

    def get_success_url(self):
        messages.success(self.request, "Lote removido com sucesso")
        return reverse_lazy('list_lotes')

# CRUD de Categoria

@method_decorator(never_cache, name="dispatch")
class CategoriaListView(ListView):
    model = Categoria
    paginate_by = 10
    template_name = "categoria/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Categoria.objects.filter(descricao__icontains=query).order_by(Lower('descricao'))
        return Categoria.objects.all().order_by(Lower('descricao'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['create_url'] = reverse('create_categoria')  
        return context


@method_decorator(never_cache, name="dispatch")
class CategoriaDetailView(TemplateView):
    template_name = "categoria/categoria.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categoria = get_object_or_404(Categoria, id=self.kwargs['categoria_id'])
        context['categoria'] = categoria
        return context

@method_decorator(never_cache, name="dispatch")
class CategoriaFormView(View):
    form_class = CategoriaForm
    template_name = "categoria/form.html"

    def get(self, request, categoria_id=None):
        form = self.form_class()
        titulo = "Nova Categoria" if not categoria_id else "Editar Categoria"        
        if categoria_id:
            categoria = get_object_or_404(Categoria, id=categoria_id)
            form = self.form_class(instance=categoria)
        return render(request, self.template_name, {
            "form": form,
            "titulo": titulo,           
        })

    def post(self, request, categoria_id=None):
        form = self.form_class(request.POST)
        msg = 'Categoria criada com sucesso'

        if categoria_id:
            categoria = get_object_or_404(Categoria, id=categoria_id)
            form = self.form_class(request.POST, instance=categoria)
            msg = 'Categoria modificado com sucesso'
    
        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect('list_categorias')

#@method_decorator(login_required, name='dispatch')
@method_decorator(never_cache, name="dispatch")
class CategoriaDeleteView(DeleteView):  
    model = Categoria
    pk_url_kwarg = "categoria_id"    

    def get_success_url(self):
        messages.success(self.request, "Categoria removida com sucesso")
        return reverse_lazy('list_categorias')


@method_decorator(never_cache, name="dispatch")
class TipoEventoListView(ListView):
    model = TipoEvento
    paginate_by = 10
    template_name = "tipo_evento/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return TipoEvento.objects.filter(descricao__icontains=query).order_by(Lower('descricao'))
        return TipoEvento.objects.all().order_by(Lower('descricao'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['create_url'] = reverse('create_tipo_evento')  
        return context


@method_decorator(never_cache, name="dispatch")
class TipoEventoDetailView(TemplateView):
    template_name = "tipo_evento/tipo_evento.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo_evento = get_object_or_404(TipoEvento, id=self.kwargs['tipo_evento_id'])
        context['tipo_evento'] = tipo_evento
        return context


@method_decorator(never_cache, name="dispatch")
class TipoEventoFormView(View):
    form_class = TipoEventoForm
    template_name = "tipo_evento/form.html"

    def get(self, request, tipo_evento_id=None):
        form = self.form_class()
        if tipo_evento_id:
            tipo_evento = get_object_or_404(TipoEvento, id=tipo_evento_id)
            form = self.form_class(instance=tipo_evento)
        return render(request, self.template_name, {"form": form})

    def post(self, request, tipo_evento_id=None):
        form = self.form_class(request.POST)
        msg = 'Tipo de Evento criado com sucesso'

        if tipo_evento_id:
            tipo_evento = get_object_or_404(TipoEvento, id=tipo_evento_id)
            form = self.form_class(request.POST, instance=tipo_evento)
            msg = 'Tipo de Evento modificado com sucesso'
    
        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect('list_tipo_eventos')


@method_decorator(never_cache, name="dispatch")
class TipoEventoDeleteView(DeleteView):  
    model = TipoEvento
    pk_url_kwarg = "tipo_evento_id"    

    def get_success_url(self):
        messages.success(self.request, "Tipo de Evento removido com sucesso")
        return reverse_lazy('list_tipo_eventos')


# CRUD de Evento

@method_decorator(never_cache, name="dispatch")
class EventoListView(ListView):
    model = Evento
    paginate_by = 10
    template_name = "evento/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Evento.objects.filter(descricao__icontains=query).order_by(Lower('descricao'))
        return Evento.objects.all().order_by(Lower('descricao'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['create_url'] = reverse('create_evento')  
        return context


@method_decorator(never_cache, name="dispatch")
class EventoDetailView(TemplateView):
    template_name = "evento/evento.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evento = get_object_or_404(Evento, id=self.kwargs['evento_id'])
        context['evento'] = evento
        return context


@method_decorator(never_cache, name="dispatch")
class EventoFormView(View):
    form_class = EventoForm
    template_name = "evento/form.html"

    def get(self, request, evento_id=None):
        form = self.form_class()
        titulo = "Novo Evento" if not evento_id else "Editar Evento"
        if evento_id:
            evento = get_object_or_404(Evento, id=evento_id)
            form = self.form_class(instance=evento)
        return render(request, self.template_name, {
            "form": form,
            "titulo": titulo,
        })

    def post(self, request, evento_id=None):
        form = self.form_class(request.POST)
        msg = 'Evento criado com sucesso'

        if evento_id:
            evento = get_object_or_404(Evento, id=evento_id)
            form = self.form_class(request.POST, instance=evento)
            msg = 'Evento modificado com sucesso'
        
        if form.is_valid():
            evento = form.save()
            evento.atualizar_contador_inscricoes()
            messages.success(request, msg)
            return redirect('list_eventos')


@method_decorator(never_cache, name="dispatch")
class EventoDeleteView(DeleteView):  
    model = Evento
    pk_url_kwarg = "evento_id"    

    def get_success_url(self):
        messages.success(self.request, "Evento removido com sucesso")
        return reverse_lazy('list_eventos')


# CRUD de Camisa

@method_decorator(never_cache, name="dispatch")
class CamisaListView(ListView):
    model = Camisa
    paginate_by = 10
    template_name = "camisa/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Camisa.objects.filter(descricao__icontains=query).order_by('tipo')
        return Camisa.objects.all().order_by('tipo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['create_url'] = reverse('create_camisa')
        return context


@method_decorator(never_cache, name="dispatch")
class CamisaDetailView(TemplateView):
    template_name = "camisa/camisa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camisa = get_object_or_404(Camisa, id=self.kwargs['camisa_id'])
        context['camisa'] = camisa
        return context


@method_decorator(never_cache, name="dispatch")
class CamisaFormView(View):
    form_class = CamisaForm
    template_name = "camisa/form.html"

    def get(self, request, camisa_id=None):
        form = self.form_class()
        if camisa_id:
            camisa = get_object_or_404(Camisa, id=camisa_id)
            form = self.form_class(instance=camisa)
        return render(request, self.template_name, {"form": form})

    def post(self, request, camisa_id=None):
        form = self.form_class(request.POST)
        msg = 'Camisa criada com sucesso'

        if camisa_id:
            camisa = get_object_or_404(Camisa, id=camisa_id)
            form = self.form_class(request.POST, instance=camisa)
            msg = 'Camisa modificada com sucesso'
    
        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect('list_camisas')


@method_decorator(never_cache, name="dispatch")
class CamisaDeleteView(DeleteView):  
    model = Camisa
    pk_url_kwarg = "camisa_id"    

    def get_success_url(self):
        messages.success(self.request, "Camisa removida com sucesso")
        return reverse_lazy('list_camisas')


@method_decorator(never_cache, name="dispatch")
class PlanejamentoListView(ListView):
    model = Planejamento
    paginate_by = 20
    template_name = "planejamento/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Planejamento.objects.filter(descricao__icontains=query).order_by(Lower('descricao'))
        return Planejamento.objects.all().order_by(Lower('descricao'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_planejado'] = Planejamento.objects.aggregate(total=Sum('valor_planejado'))['total'] or 0
        context['q'] = self.request.GET.get('q', '')
        context['create_url'] = reverse('create_planejamento')
        return context


@method_decorator(never_cache, name="dispatch")
class PlanejamentoDetailView(TemplateView):
    template_name = "planejamento/planejamento.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        planejamento = get_object_or_404(Planejamento, id=self.kwargs['planejamento_id'])
        context['planejamento'] = planejamento
        return context


@method_decorator(never_cache, name="dispatch")
class PlanejamentoFormView(View):
    form_class = PlanejamentoForm
    template_name = "planejamento/form.html"

    def get(self, request, planejamento_id=None):
        form = self.form_class()
        titulo = "Novo Planejamento" if not planejamento_id else "Editar Planejamento"
        if planejamento_id:
            planejamento = get_object_or_404(Planejamento, id=planejamento_id)
            form = self.form_class(instance=planejamento)
        return render(request, self.template_name, {
            "form": form,
            "titulo": titulo,
        })

    def post(self, request, planejamento_id=None):
        form = self.form_class(request.POST)
        msg = 'Planejamento criado com sucesso'

        if planejamento_id:
            planejamento = get_object_or_404(Planejamento, id=planejamento_id)
            form = self.form_class(request.POST, instance=planejamento)
            msg = 'Planejamento modificado com sucesso'
    
        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect('list_planejamentos')


@method_decorator(never_cache, name="dispatch")
class PlanejamentoDeleteView(DeleteView):
    model = Planejamento
    pk_url_kwarg = "planejamento_id"

    def get_success_url(self):
        messages.success(self.request, "Planejamento removido com sucesso")
        return reverse_lazy('list_planejamentos')



@method_decorator(never_cache, name="dispatch")
class InscricaoListView(ListView):
    model = Inscricao
    paginate_by = 25
    template_name = "inscricao/list.html"

    def get_queryset(self):
        ordering = self.request.GET.get('ordering', 'nome')  # Ordena por 'nome' por padrão
        status = self.request.GET.get('status')  # Obtém o filtro de status
        proximo_pagamento = self.request.GET.get('proximo_pagamento')  # Filtro por próximo pagamento
        inscricoes = Inscricao.objects.all()

        # Filtra por status, se fornecido
        if status:
            if status == 'pago':
                inscricoes = inscricoes.filter(valor_restante__lte=0)
            elif status == 'parcial':
                inscricoes = inscricoes.filter(valor_pago__gt=0, valor_restante__gt=0)
            elif status == 'pendente':
                inscricoes = inscricoes.filter(valor_pago=0)
        
         # Filtra por próximo pagamento, se fornecido
        if proximo_pagamento == 'hoje':
            inscricoes = inscricoes.filter(
                pagamento__data_proximo_pagamento=date.today()
            )
        elif proximo_pagamento == 'atrasado':
            inscricoes = inscricoes.filter(
                pagamento__data_proximo_pagamento__lt=date.today()
            )
        elif proximo_pagamento == 'futuro':
            inscricoes = inscricoes.filter(
                pagamento__data_proximo_pagamento__gt=date.today()
            )
        
        proximo_pagamento_subquery = Pagamento.objects.filter(
            content_type=ContentType.objects.get_for_model(Inscricao),
            object_id=OuterRef('id'),
            data_proximo_pagamento__isnull=False
        ).order_by('data_proximo_pagamento').values('data_proximo_pagamento')[:1]

        # Anota o campo data_proximo_pagamento no queryset
        inscricoes = Inscricao.objects.annotate(
            data_proximo_pagamento=Subquery(proximo_pagamento_subquery)
        )

        # Verifica se o ordering é data_proximo_pagamento ou valor_restante
        if ordering == 'data_proximo_pagamento':
            return inscricoes.order_by('data_proximo_pagamento')
        elif ordering == '-data_proximo_pagamento':
            return inscricoes.order_by('-data_proximo_pagamento')
        elif ordering == 'valor_restante':
            return inscricoes.order_by('valor_restante')
        elif ordering == '-valor_restante':
            return inscricoes.order_by('-valor_restante')

        return inscricoes.order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ordering'] = self.request.GET.get('ordering', 'nome')
        queryset = self.get_queryset()

        # Corrigindo a forma de calcular os totais
        total_pago = sum(inscricao.valor_pago for inscricao in queryset)
        total_total = queryset.aggregate(total=Sum('valor_total'))['total'] or 0
        total_a_receber = total_total - total_pago

        # Adiciona o total de inscrições
        total_inscricoes = Inscricao.objects.count()

        context.update({
            'q': self.request.GET.get('q', ''),
            'status': self.request.GET.get('status', ''),
            'proximo_pagamento': self.request.GET.get('proximo_pagamento', ''),
            'create_url': reverse('create_inscricao'),
            'total_pago': total_pago,
            'total_a_receber': total_a_receber,
            'total_inscricoes': total_inscricoes,
        })
        return context

@method_decorator(never_cache, name="dispatch")
class InscricaoDetailView(TemplateView):
    template_name = "inscricao/incricao.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inscricao = get_object_or_404(Inscricao, id=self.kwargs['inscricao_id'])
        context['inscricao'] = inscricao
        return context

@method_decorator(never_cache, name="dispatch")
class InscricaoFormView(View):
    form_class = InscricaoForm
    template_name = "inscricao/form.html"

    def get(self, request, inscricao_id=None):
        form = self.form_class()
        eventos = Evento.objects.all()
        inscricao = None

        if inscricao_id:
            inscricao = get_object_or_404(Inscricao, id=inscricao_id)
            form = self.form_class(instance=inscricao)

        # Certifique-se de que o queryset do lote está carregado
        form.fields['lote'].queryset = Lote.objects.all()

        return render(request, self.template_name, {
            "form": form,
            "eventos": eventos,
            "inscricao": inscricao,
        })

    def post(self, request, inscricao_id=None):
        inscricao = None
        if inscricao_id:
            inscricao = get_object_or_404(Inscricao, id=inscricao_id)
            form = self.form_class(request.POST, instance=inscricao)
        else:
            form = self.form_class(request.POST)

        if form.is_valid():
            inscricao = form.save(commit=False)
            inscricao.save()

            # Associa os eventos selecionados
            eventos_ids = request.POST.getlist('eventos')
            eventos = Evento.objects.filter(id__in=eventos_ids)
            
            # Verifica se há vagas suficientes para cada evento
            for evento in eventos:
                if evento.quantidade_pessoas is not None:
                    if evento.quantidade_pessoas <= 0:
                        raise ValidationError(f"O evento '{evento.descricao}' não tem vagas disponíveis.")

            inscricao.eventos.set(eventos)

            # Atualiza o valor total e o valor da parcela
            inscricao.valor_total = inscricao.calcular_valor_total()
            inscricao.valor_parcela = inscricao.calcular_valor_parcela()
            inscricao.save(update_fields=['valor_total', 'valor_parcela'])

            messages.success(request, "Inscrição salva com sucesso!")
            return redirect('list_inscricoes')

        return render(request, self.template_name, {
            "form": form,
            "eventos": Evento.objects.all(),
            "inscricao": inscricao,
        })

@method_decorator(never_cache, name="dispatch")
class InscricaoDeleteView(DeleteView):
    model = Inscricao
    pk_url_kwarg = "inscricao_id"

    def get_success_url(self):
        messages.success(self.request, "Inscrição removida com sucesso")
        return reverse_lazy('list_inscricoes')

@method_decorator(never_cache, name="dispatch")
class InscricaoEventoFormView(View):
    form_class = InscricaoEventoForm
    template_name = "inscricao/form_evento.html"

    def get(self, request, inscricao_id):
        form = self.form_class()
        eventos = Evento.objects.all()
        inscricao = get_object_or_404(Inscricao, id=inscricao_id)
        eventos = inscricao.eventos.all()  # Recupera os eventos associados      
            
        return render(request, self.template_name, {
            "form": form,
            "inscricao": inscricao,
            'eventos': eventos,
        })

    def post(self, request, inscricao_id):
        form = self.form_class(request.POST)
        inscricao = get_object_or_404(Inscricao, id=inscricao_id)
        msg = 'Evento adicionado à inscrição com sucesso'

        if form.is_valid():
            inscricao = form.save(commit=False)
            
            # Ainda não salva no banco
            eventos_ids = request.POST.getlist('eventos')
            eventos = Evento.objects.filter(id__in=eventos_ids)
            
            inscricao.valor_total = sum(evento.valor_unitario for evento in eventos) - inscricao.desconto + inscricao.lote.valor_unitario
            inscricao.valor_parcela = inscricao.calcular_valor_parcela()

            inscricao.save()  # Agora sim, já com valores certos
            inscricao.eventos.set(eventos)

            # Atualiza o contador de inscrições
            for evento in eventos:
                evento.atualizar_contador_inscricoes()

            return redirect('list_inscricoes')

@method_decorator(never_cache, name="dispatch")
class InscricaoEventoDeleteView(DeleteView):
    model = InscricaoEvento
    pk_url_kwarg = "inscricao_evento_id"

    def get_success_url(self):
        inscricao_id = self.kwargs['inscricao_id']
        inscricao = get_object_or_404(Inscricao, id=inscricao_id)
        
        # Recalcular valor total da inscrição após remover o evento
        inscricao.valor_total = inscricao.calcular_valor_total()
        inscricao.save()
        
        # Atualiza o contador de inscrições para o evento associado
        inscricao_evento = self.object
        inscricao_evento.evento.atualizar_contador_inscricoes()
        
        messages.success(self.request, "Evento removido da inscrição com sucesso")
        return reverse('detail_inscricao', kwargs={'inscricao_id': inscricao_id})

@method_decorator(never_cache, name="dispatch")
class InscricaoCreateView(View):
    def get(self, request):
        form = InscricaoForm()
        return render(request, 'inscricao_form.html', {'form': form})

    def post(self, request):
        form = InscricaoForm(request.POST)
        if form.is_valid():
            # Salva a inscrição sem os eventos
            inscricao = form.save(commit=False)
            inscricao.save()

            # Associa os eventos selecionados
            eventos = form.cleaned_data['eventos']
            inscricao.eventos.set(eventos)

            # Atualiza o valor total e o valor da parcela
            inscricao.valor_total = inscricao.calcular_valor_total()
            inscricao.valor_parcela = inscricao.calcular_valor_parcela()
            inscricao.save(update_fields=['valor_total', 'valor_parcela'])

            return redirect('list_inscricoes')  # Redireciona para a lista de inscrições
        return render(request, 'inscricao_form.html', {'form': form})

@method_decorator(never_cache, name="dispatch")
class EventoInscritosView(DetailView):
    model = Evento
    template_name = "evento/inscritos.html"
    context_object_name = "evento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtém todas as inscrições associadas a este evento
        inscritos = InscricaoEvento.objects.filter(evento=self.object).select_related('inscricao')
        
        # Cria uma lista de inscritos com informações relevantes
        lista_inscritos = []
        for inscricao_evento in inscritos:
            inscricao = inscricao_evento.inscricao
            lista_inscritos.append({
                'nome': inscricao.nome,
                'cpf': inscricao.cpf,
            })

        # Obtém todos os profissionais associados a este evento
        profissionais = ProfissionalEvento.objects.filter(evento=self.object).select_related('profissional')
        
        # Cria uma lista de profissionais com informações relevantes
        lista_profissionais = []
        for profissional_evento in profissionais:
            profissional = profissional_evento.profissional
            lista_profissionais.append({
                'nome': profissional.nome,
                'cpf': profissional.cpf,  # <- Adiciona o CPF aqui
            })
        
        context['inscritos'] = lista_inscritos
        context['profissionais'] = lista_profissionais
        context['total_inscritos'] = len(lista_inscritos)
        context['total_profissionais'] = len(lista_profissionais)
        return context


@method_decorator(never_cache, name="dispatch")
class ProfissionalListView(ListView):
    model = Profissional
    paginate_by = 10
    template_name = "profissional/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Profissional.objects.filter(nome__icontains=query).order_by(Lower('nome'))
        return Profissional.objects.all().order_by(Lower('nome'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['create_url'] = reverse('create_profissional')
        return context


@method_decorator(never_cache, name="dispatch")
class ProfissionalDetailView(TemplateView):
    template_name = "profissional/profissional.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profissional = get_object_or_404(Profissional, id=self.kwargs['profissional_id'])
        context['profissional'] = profissional
        return context


@method_decorator(never_cache, name="dispatch")
class ProfissionalFormView(View):
    form_class = ProfissionalForm
    template_name = "profissional/form.html"

    def get(self, request, profissional_id=None):
        form = self.form_class()
        profissional = None
        if profissional_id:
            profissional = get_object_or_404(Profissional, id=profissional_id)
            form = self.form_class(instance=profissional)
        eventos = Evento.objects.all()
        return render(request, self.template_name, {
            "form": form,
            "profissional": profissional,
            "eventos": eventos,
            "titulo": "Editar Profissional" if profissional else "Novo Profissional"
        })

    def post(self, request, profissional_id=None):
        profissional = None
        if profissional_id:
            profissional = get_object_or_404(Profissional, id=profissional_id)
            form = self.form_class(request.POST, instance=profissional)
        else:
            form = self.form_class(request.POST)

        if form.is_valid():
            profissional = form.save(commit=False)
            profissional.save()

            # Associa os eventos selecionados
            eventos_ids = request.POST.getlist('eventos')
            profissional.eventos.set(eventos_ids)

            messages.success(request, "Profissional salvo com sucesso!")
            return redirect('list_profissionais')

        return render(request, self.template_name, {
            "form": form,
            "profissional": profissional,
            "eventos": Evento.objects.all(),
            "titulo": "Editar Profissional" if profissional else "Novo Profissional"
        })


@method_decorator(never_cache, name="dispatch")
class ProfissionalDeleteView(DeleteView):
    model = Profissional
    pk_url_kwarg = "profissional_id"

    def get_success_url(self):
        messages.success(self.request, "Profissional removido com sucesso")
        return reverse_lazy('list_profissionais')


@method_decorator(never_cache, name="dispatch")
class ProfissionalEventoFormView(View):
    form_class = ProfissionalEventoForm
    template_name = "profissional/form_evento.html"

    def get(self, request, profissional_id):
        form = self.form_class()
        eventos = Evento.objects.all()
        profissional = get_object_or_404(Profissional, id=profissional_id)
        eventos = profissional.eventos.all()
        
        return render(request, self.template_name, {
            "form": form,
            "profissional": profissional,
            'eventos': eventos,
        })

    def post(self, request, profissional_id):
        form = self.form_class(request.POST)
        profissional = get_object_or_404(Profissional, id=profissional_id)
        msg = 'Evento adicionado ao profissional com sucesso'

        if form.is_valid():
            profissional_evento = form.save(commit=False)
            profissional_evento.profissional = profissional
            profissional_evento.save()

            # Atualiza o contador de inscrições para o evento
            profissional_evento.evento.atualizar_contador_inscricoes()

            messages.success(request, msg)
            return redirect('list_profissionais')


@method_decorator(never_cache, name="dispatch")
class ProfissionalEventoDeleteView(DeleteView):
    model = ProfissionalEvento
    pk_url_kwarg = "profissional_evento_id"

    def get_success_url(self):
        profissional_id = self.kwargs['profissional_id']
        profissional = get_object_or_404(Profissional, id=profissional_id)
        
        # Atualiza o contador de inscrições para o evento associado
        profissional_evento = self.object
        profissional_evento.evento.atualizar_contador_inscricoes()
        
        messages.success(self.request, "Evento removido do profissional com sucesso")
        return reverse('detail_profissional', kwargs={'profissional_id': profissional_id})

@method_decorator(never_cache, name="dispatch")
class EntradaListView(ListView):
    model = Entrada
    paginate_by = 10
    template_name = "entrada/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Entrada.objects.filter(descricao__icontains=query).order_by('-data')
        return Entrada.objects.all().order_by('-data')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_entrada'] = Entrada.objects.aggregate(total=Sum('valor'))['total'] or 0
        context['q'] = self.request.GET.get('q', '')
        context['total_entradas'] = sum(entrada.valor for entrada in context['object_list'])
        return context

@method_decorator(never_cache, name="dispatch")
class EntradaDetailView(TemplateView):
    template_name = "entrada/entrada.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entrada = get_object_or_404(Entrada, id=self.kwargs['entrada_id'])
        context['entrada'] = entrada
        return context

@method_decorator(never_cache, name="dispatch")
class EntradaFormView(View):
    form_class = EntradaForm
    template_name = "entrada/form.html"

    def get(self, request, entrada_id=None):
        form = self.form_class()
        titulo = "Nova Entrada" if not entrada_id else "Editar Entrada"
        if entrada_id:
            entrada = get_object_or_404(Entrada, id=entrada_id)
            form = self.form_class(instance=entrada)
        return render(request, self.template_name, {"form": form,"titulo": titulo,})

    def post(self, request, entrada_id=None):
        form = self.form_class(request.POST)
        msg = 'Entrada criada com sucesso'

        if entrada_id:
            entrada = get_object_or_404(Entrada, id=entrada_id)
            form = self.form_class(request.POST, instance=entrada)
            msg = 'Entrada modificada com sucesso'
    
        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect('list_entradas')

@method_decorator(never_cache, name="dispatch")
class EntradaDeleteView(DeleteView):  
    model = Entrada
    pk_url_kwarg = "entrada_id"    

    def get_success_url(self):
        messages.success(self.request, "Entrada removida com sucesso")
        return reverse_lazy('list_entradas')

@method_decorator(never_cache, name="dispatch")
class SaidaListView(ListView):
    model = Saida
    paginate_by = 10
    template_name = "saida/list.html"

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Saida.objects.filter(descricao__icontains(query)).order_by('-data') # type: ignore
        return Saida.objects.all().order_by('-data')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_saida'] = Saida.objects.aggregate(total=Sum('valor'))['total'] or 0
        context['q'] = self.request.GET.get('q', '')
        context['total_saidas'] = sum(saida.valor for saida in context['object_list'])
        return context

@method_decorator(never_cache, name="dispatch")
class SaidaDetailView(TemplateView):
    template_name = "saida/saida.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        saida = get_object_or_404(Saida, id=self.kwargs['saida_id'])
        context['saida'] = saida
        return context

@method_decorator(never_cache, name="dispatch")
class SaidaFormView(View):
    form_class = SaidaForm
    template_name = "saida/form.html"

    def get(self, request, saida_id=None):
        form = self.form_class()
        titulo = "Nova Saída" if not saida_id else "Editar Saída"
        if saida_id:
            saida = get_object_or_404(Saida, id=saida_id)
            form = self.form_class(instance=saida)
        return render(request, self.template_name, {"form": form,"titulo": titulo,})

    def post(self, request, saida_id=None):
        form = self.form_class(request.POST)
        msg = 'Saída criada com sucesso'

        if saida_id:
            saida = get_object_or_404(Saida, id=saida_id)
            form = self.form_class(request.POST, instance=saida)
            msg = 'Saída modificada com sucesso'
    
        if form.is_valid():
            form.save()
            messages.success(request, msg)
            return redirect('list_saidas')

@method_decorator(never_cache, name="dispatch")
class SaidaDeleteView(DeleteView):  
    model = Saida
    pk_url_kwarg = "saida_id"    

    def get_success_url(self):
        messages.success(self.request, "Saída removida com sucesso")
        return reverse_lazy('list_saidas')

def resumo_caixa(request):
    # Entradas e saídas
    total_entradas = Entrada.objects.aggregate(total=Sum('valor'))['total'] or 0
    total_saidas = Saida.objects.aggregate(total=Sum('valor'))['total'] or 0

    # Total inscricoes pagas (somando os pagamentos com tipo_modelo='inscricao')
    ct_inscricao = ContentType.objects.get_for_model(Inscricao)
    total_pago_inscricoes = Pagamento.objects.filter(content_type=ct_inscricao).aggregate(total=Sum('valor_pago'))['total'] or 0

    # Total a receber de inscrições (valor_total - valor_pago)
    total_valor_inscricoes = Inscricao.objects.aggregate(total=Sum('valor_total'))['total'] or 0
    total_a_receber = total_valor_inscricoes - total_pago_inscricoes

    # Total camisas (considerado como entrada)
    total_camisas = Camisa.objects.aggregate(total=Sum('valor_unitario'))['total'] or 0

    # Total planejado e total pago em planejamentos
    total_planejamentos = Planejamento.objects.aggregate(total=Sum('valor_planejado'))['total'] or 0
    ct_planejamento = ContentType.objects.get_for_model(Planejamento)
    total_pago_planejamento = Pagamento.objects.filter(content_type=ct_planejamento).aggregate(total=Sum('valor_pago'))['total'] or 0

    # Valor a pagar = planejado - pago
    total_a_pagar = total_planejamentos - total_pago_planejamento

    # Saldo em caixa = entradas + inscrições pagas + camisas - saídas - pagamentos de planejamento
    saldo_caixa = (total_entradas + total_pago_inscricoes + total_camisas) - (total_saidas + total_pago_planejamento)

     # Cálculo da estimativa
    saldo_futuro_previsto = (saldo_caixa + total_a_receber) - (total_planejamentos - total_saidas)

    context = {
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'total_inscricoes': total_pago_inscricoes,  # Total recebido das inscrições
        'total_a_receber': total_a_receber,
        'total_planejamentos': total_planejamentos,
        'total_pago_planejamento': total_pago_planejamento,
        'total_a_pagar': total_a_pagar,
        'total_camisas': total_camisas,
        'saldo_caixa': saldo_caixa,
        'saldo_futuro_previsto': saldo_futuro_previsto,
    }

    return render(request, 'resumo/resumo_caixa.html', context)

# Lista de Pagamentos
@method_decorator(never_cache, name="dispatch")
class PagamentoListView(ListView):
    model = Pagamento
    paginate_by = 35
    template_name = "pagamento/list.html"

    def get_queryset(self):
        queryset = Pagamento.objects.all().order_by('-id')
        filtro = self.request.GET.get('q', '').strip().lower()

        if filtro:
            # Busca os objetos relacionados que contenham o texto
            planejamentos = Planejamento.objects.filter(descricao__icontains=filtro)
            inscricoes = Inscricao.objects.filter(nome__icontains=filtro)

            # Monta a lista de conteúdo genérico
            content_type_planejamento = ContentType.objects.get_for_model(Planejamento)
            content_type_inscricao = ContentType.objects.get_for_model(Inscricao)

            queryset = queryset.filter(
                models.Q(content_type=content_type_planejamento, object_id__in=planejamentos.values_list('id', flat=True)) |
                models.Q(content_type=content_type_inscricao, object_id__in=inscricoes.values_list('id', flat=True))
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtro = self.request.GET.get('q', '')
        context['pagamento_relacionado'] = filtro
        context['search_url'] = self.request.path
        context['create_url'] = reverse('create_pagamento')
        return context
           




# Criar e Editar Pagamento
@method_decorator(never_cache, name="dispatch")
class PagamentoFormView(View):
    form_class = PagamentoForm
    template_name = "pagamento/form.html"

    def get(self, request, pagamento_id=None):
        if pagamento_id:
            pagamento = get_object_or_404(Pagamento, pk=pagamento_id)
            form = self.form_class(instance=pagamento)
            titulo = "Editar Pagamento"
        else:
            pagamento = None
            form = self.form_class()
            titulo = "Novo Pagamento"
        return render(request, self.template_name, {
            "form": form,
            "titulo": titulo,
            "pagamento": pagamento,
        })

    def post(self, request, pagamento_id=None):
        if pagamento_id:
            pagamento = get_object_or_404(Pagamento, pk=pagamento_id)
            form = self.form_class(request.POST, instance=pagamento)
        else:
            pagamento = None
            form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Pagamento salvo com sucesso!")
            return redirect('list_pagamentos')
        else:
            print("Formulário inválido:", form.errors)

        titulo = "Editar Pagamento" if pagamento_id else "Novo Pagamento"
        return render(request, self.template_name, {
            "form": form,
            "titulo": titulo,
            "pagamento": pagamento,
        })


# Detalhamento do Pagamento
@method_decorator(never_cache, name="dispatch")
class PagamentoDetailView(TemplateView):
    template_name = "pagamento/pagamento.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pagamento = get_object_or_404(Pagamento, id=self.kwargs['pagamento_id'])
        context['pagamento'] = pagamento
        return context


# Remover Pagamento
@method_decorator(never_cache, name="dispatch")
class PagamentoDeleteView(DeleteView):
    model = Pagamento
    pk_url_kwarg = "pagamento_id"

    def get_success_url(self):
        messages.success(self.request, "Pagamento removido com sucesso")
        return reverse_lazy('list_pagamentos')


# Carregar objetos relacionados com AJAX
@require_GET
def carregar_objetos_pagamento(request):
    tipo = request.GET.get('tipo_modelo')
    termo = request.GET.get('q', '')

    if tipo == 'planejamento':
        objetos = Planejamento.objects.filter(descricao__icontains=termo)
    elif tipo == 'inscricao':
        objetos = Inscricao.objects.filter(nome__icontains=termo)
    else:
        objetos = []

    data = {
        'objetos': [{'id': obj.id, 'descricao': str(obj)} for obj in objetos]
    }
    return JsonResponse(data)

def pagamentos_list(request):
    pagamentos = Pagamento.objects.all()
    tipo_modelo = request.GET.get('tipo_modelo')
    pagamento_relacionado = request.GET.get('pagamento_relacionado')

    if tipo_modelo:
        pagamentos = pagamentos.filter(tipo_modelo=tipo_modelo)

    if pagamento_relacionado:
        pagamentos = pagamentos.filter(pagamento_relacionado_id=pagamento_relacionado)

    # Popula opções para pagamento_relacionado conforme tipo_modelo
    if tipo_modelo == 'planejamento':
        pagamentos_relacionados = Planejamento.objects.all()
    elif tipo_modelo == 'inscricao':
        pagamentos_relacionados = Inscricao.objects.all()
    else:
        pagamentos_relacionados = []

    context = {
        'page_obj': pagamentos,
        'pagamentos_relacionados': pagamentos_relacionados,
        'create_url': reverse('create_pagamento'),
    }
    return render(request, 'pagamentos.html', context)


def listar_pagamentos(request):
    pagamentos = Pagamento.objects.all()

    tipo_modelo = request.GET.get('tipo_modelo')
    pagamento_relacionado = request.GET.get('pagamento_relacionado')

    if tipo_modelo:
        pagamentos = pagamentos.filter(tipo_modelo=tipo_modelo)

    if pagamento_relacionado:
        pagamentos = pagamentos.filter(pagamento_relacionado__id=pagamento_relacionado)

    paginator = Paginator(pagamentos, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'pagamentos/lista.html', {
        'page_obj': page_obj,
    })

