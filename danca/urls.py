from django.urls import path
from . import views
from .views import *

urlpatterns = [
    #Lotes
    path('lotes/', LoteListView.as_view(), name='list_lotes'),
    path('lotes/<int:lote_id>/', LoteDetailView.as_view(), name='detail_lote'),
    path('lotes/create/', LoteFormView.as_view(), name='create_lote'),
    path('lotes/<int:lote_id>/update/', LoteFormView.as_view(), name='update_lote'),
    path('lotes/<int:lote_id>/delete/', LoteDeleteView.as_view(), name='delete_lote'),

    #Categoria
    path('categorias/', CategoriaListView.as_view(), name='list_categorias'),
    path('categorias/<int:categoria_id>/', CategoriaDetailView.as_view(), name='detail_categoria'),
    path('categorias/create/', CategoriaFormView.as_view(), name='create_categoria'),
    path('categorias/<int:categoria_id>/update/', CategoriaFormView.as_view(), name='update_categoria'),
    path('categorias/<int:categoria_id>/delete/', CategoriaDeleteView.as_view(), name='delete_categoria'),

    # Tipo de Evento
    path('tipo-eventos/', TipoEventoListView.as_view(), name='list_tipo_eventos'),
    path('tipo-eventos/<int:tipo_evento_id>/', TipoEventoDetailView.as_view(), name='detail_tipo_evento'),
    path('tipo-eventos/create/', TipoEventoFormView.as_view(), name='create_tipo_evento'),
    path('tipo-eventos/<int:tipo_evento_id>/update/', TipoEventoFormView.as_view(), name='update_tipo_evento'),
    path('tipo-eventos/<int:tipo_evento_id>/delete/', TipoEventoDeleteView.as_view(), name='delete_tipo_evento'),
    path('evento/<int:pk>/inscritos/', EventoInscritosView.as_view(), name='evento_inscritos'),

    # Evento
    path('eventos/', EventoListView.as_view(), name='list_eventos'),
    path('eventos/<int:evento_id>/', EventoDetailView.as_view(), name='detail_evento'),
    path('eventos/create/', EventoFormView.as_view(), name='create_evento'),
    path('eventos/<int:evento_id>/update/', EventoFormView.as_view(), name='update_evento'),
    path('eventos/<int:evento_id>/delete/', EventoDeleteView.as_view(), name='delete_evento'),

    # Camisa
    path('camisas/', CamisaListView.as_view(), name='list_camisas'),
    path('camisas/<int:camisa_id>/', CamisaDetailView.as_view(), name='detail_camisa'),
    path('camisas/create/', CamisaFormView.as_view(), name='create_camisa'),
    path('camisas/<int:camisa_id>/update/', CamisaFormView.as_view(), name='update_camisa'),
    path('camisas/<int:camisa_id>/delete/', CamisaDeleteView.as_view(), name='delete_camisa'),

    # Planejamento
    path('planejamentos/', PlanejamentoListView.as_view(), name='list_planejamentos'),
    path('planejamentos/<int:planejamento_id>/', PlanejamentoDetailView.as_view(), name='detail_planejamento'),
    path('planejamentos/create/', PlanejamentoFormView.as_view(), name='create_planejamento'),
    path('planejamentos/<int:planejamento_id>/update/', PlanejamentoFormView.as_view(), name='update_planejamento'),
    path('planejamentos/<int:planejamento_id>/delete/', PlanejamentoDeleteView.as_view(), name='delete_planejamento'),
    
    # Inscricao
    path('inscricoes/', InscricaoListView.as_view(), name='list_inscricoes'),
    path('inscricoes/<int:inscricao_id>/', InscricaoDetailView.as_view(), name='detail_inscricao'),
    path('inscricoes/create/', InscricaoFormView.as_view(), name='create_inscricao'),
    path('inscricoes/<int:inscricao_id>/update/', InscricaoFormView.as_view(), name='update_inscricao'),
    path('inscricoes/<int:inscricao_id>/delete/', InscricaoDeleteView.as_view(), name='delete_inscricao'),
    path('inscricoes/<int:inscricao_id>/eventos/create/', InscricaoEventoFormView.as_view(), name='create_inscricao_evento'),
    path('inscricoes/<int:inscricao_id>/eventos/<int:inscricao_evento_id>/delete/', InscricaoEventoDeleteView.as_view(), name='delete_inscricao_evento'),

    # Profissional
    path('profissionais/', ProfissionalListView.as_view(), name='list_profissionais'),
    path('profissionais/<int:profissional_id>/', ProfissionalDetailView.as_view(), name='detail_profissional'),
    path('profissionais/create/', ProfissionalFormView.as_view(), name='create_profissional'),
    path('profissionais/<int:profissional_id>/update/', ProfissionalFormView.as_view(), name='update_profissional'),
    path('profissionais/<int:profissional_id>/delete/', ProfissionalDeleteView.as_view(), name='delete_profissional'),
    path('profissionais/<int:profissional_id>/eventos/create/', ProfissionalEventoFormView.as_view(), name='create_profissional_evento'),
    path('profissionais/<int:profissional_id>/eventos/<int:profissional_evento_id>/delete/', ProfissionalEventoDeleteView.as_view(), name='delete_profissional_evento'),

    # Entrada
    path('entrada/', EntradaListView.as_view(), name='list_entradas'),
    path('entrada/<int:entrada_id>/', EntradaDetailView.as_view(), name='detail_entrada'),
    path('entrada/create/', EntradaFormView.as_view(), name='create_entrada'),
    path('entrada/<int:entrada_id>/update/', EntradaFormView.as_view(), name='update_entrada'),
    path('entrada/<int:entrada_id>/delete/', EntradaDeleteView.as_view(), name='delete_entrada'),
    
    # Saida
    path('saida/', SaidaListView.as_view(), name='list_saidas'),
    path('saida/<int:saida_id>/', SaidaDetailView.as_view(), name='detail_saida'),
    path('saida/create/', SaidaFormView.as_view(), name='create_saida'),
    path('saida/<int:saida_id>/update/', SaidaFormView.as_view(), name='update_saida'),
    path('saida/<int:saida_id>/delete/', SaidaDeleteView.as_view(), name='delete_saida'),

    # Resumo Caixa
    path('resumo/', resumo_caixa, name='resumo_caixa'),

    # Pagamento
    path('pagamento/', PagamentoListView.as_view(), name='list_pagamentos'),
    path('pagamento/<int:pagamento_id>/', PagamentoDetailView.as_view(), name='detail_pagamento'),
    path('pagamento/create/', PagamentoFormView.as_view(), name='create_pagamento'),
    path('pagamento/<int:pagamento_id>/update/', PagamentoFormView.as_view(), name='update_pagamento'),
    path('pagamento/<int:pagamento_id>/delete/', PagamentoDeleteView.as_view(), name='delete_pagamento'),
    # path('pagamentos/relacionados/', carregar_objetos_pagamento, name='carregar_objetos_pagamento'),  # AJAX
    path('carregar_objetos_pagamento/', carregar_objetos_pagamento, name='carregar_objetos_pagamento'),
]

    


