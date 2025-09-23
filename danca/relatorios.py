# relatorios.py
from django.http import HttpResponse
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from django.db.models.functions import Lower
from django.contrib.contenttypes.models import ContentType
from django.db.models import Case, When, Value, DecimalField
from django.db.models.functions import Coalesce
from django.views import View
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from .models import Inscricao, Evento, Profissional, Planejamento, PedidoCamisa, Pagamento, InscricaoEvento, ProfissionalEvento
from .views import InscricaoListView
from collections import Counter


class InscricaoRelatorioDocxView(InscricaoListView):
    """ Gera relatório .docx como lista enumerada """
    def get(self, request, *args, **kwargs):
        # Remove a paginação para pegar todos os registros
        self.paginate_by = None
        queryset = self.get_queryset()

        document = Document()
        document.add_heading('Relatório de Inscrições', 0)
        document.add_paragraph(f'Gerado em: {now().strftime("%d/%m/%Y %H:%M")}')
        document.add_paragraph(f'Total de inscrições: {queryset.count()}')
        document.add_paragraph('')

        # Contador para UF
        uf_counter = Counter()

        for inscricao in queryset:
            categoria = inscricao.categoria.descricao if inscricao.categoria else 'Sem categoria'
            if inscricao.valor_restante_db <= 0:
                status = 'Pago'
            elif inscricao.valor_pago_db > 0:
                status = 'Parcial'
            else:
                status = 'Pendente'
            
            # Adiciona a UF (assumindo que o campo se chama 'uf')
            uf = getattr(inscricao, 'uf', 'Não informado') or 'Não informado'
            
            # Contabiliza a UF
            uf_counter[uf] += 1
            
            document.add_paragraph(
                f'{inscricao.nome} — {inscricao.cpf} — {categoria} — {status} — UF: {uf}',
                style='List Number'
            )

        # Adiciona seção com contagem por UF
        document.add_paragraph('')
        document.add_heading('Resumo por UF', level=1)
        
        for uf, quantidade in sorted(uf_counter.items()):
            document.add_paragraph(f'{uf}: {quantidade} inscrição(s)')

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="relatorio_inscricoes.docx"'
        document.save(response)
        return response


def evento_inscritos_docx(request, pk):
    evento = get_object_or_404(Evento, pk=pk)

    # Congressistas - removendo qualquer limitação de paginação
    inscritos = (
        InscricaoEvento.objects
        .filter(evento=evento)
        .select_related('inscricao')
        .order_by('inscricao__nome')
    )
    
    # Profissionais - removendo qualquer limitação de paginação
    profissionais = (
        ProfissionalEvento.objects
        .filter(evento=evento)
        .select_related('profissional')
        .order_by('profissional__nome')
    )

    # Contadores para UF
    uf_congressistas = Counter()
    uf_profissionais = Counter()

    # Congressistas com UF
    lista_congressistas = []
    for i in inscritos:
        uf = getattr(i.inscricao, 'uf', 'Não informado') or 'Não informado'
        lista_congressistas.append({
            'nome': i.inscricao.nome or 'Sem Cadastro',
            'cpf': i.inscricao.cpf or 'Sem Cadastro',
            'uf': uf
        })
        uf_congressistas[uf] += 1

    # Profissionais com UF
    lista_profissionais = []
    for p in profissionais:
        uf = getattr(p.profissional, 'uf', 'Não informado') or 'Não informado'
        lista_profissionais.append({
            'nome': p.profissional.nome or 'Sem Cadastro',
            'cpf': p.profissional.cpf or 'Sem Cadastro',
            'uf': uf
        })
        uf_profissionais[uf] += 1

    total_congressistas = len(lista_congressistas)
    total_profissionais = len(lista_profissionais)
    total_geral = total_congressistas + total_profissionais

    document = Document()
    document.add_heading(f'Lista - {evento.descricao}', 0)
    document.add_paragraph(f'Gerado em: {now().strftime("%d/%m/%Y %H:%M")}')
    document.add_paragraph('')

    # Congressistas
    document.add_heading('Congressistas', level=1)
    document.add_paragraph(f'Total de congressistas: {total_congressistas}')
    
    for c in lista_congressistas:
        document.add_paragraph(
            f'{c["nome"]} — {c["cpf"]} — UF: {c["uf"]}',
            style='List Number'
        )

    # Resumo UF Congressistas
    document.add_paragraph('')
    document.add_heading('Congressistas por UF', level=2)
    for uf, quantidade in sorted(uf_congressistas.items()):
        document.add_paragraph(f'{uf}: {quantidade} congressista(s)')

    document.add_paragraph('')

    # Profissionais
    document.add_heading('Profissionais', level=1)
    document.add_paragraph(f'Total de profissionais: {total_profissionais}')
    
    for p in lista_profissionais:
        document.add_paragraph(
            f'{p["nome"]} — {p["cpf"]} — UF: {p["uf"]}',
            style='List Number'
        )

    # Resumo UF Profissionais
    document.add_paragraph('')
    document.add_heading('Profissionais por UF', level=2)
    for uf, quantidade in sorted(uf_profissionais.items()):
        document.add_paragraph(f'{uf}: {quantidade} profissional(is)')

    document.add_paragraph('')
    
    # Resumo Geral por UF
    uf_geral = uf_congressistas + uf_profissionais
    document.add_heading('Total Geral por UF', level=1)
    for uf, quantidade in sorted(uf_geral.items()):
        document.add_paragraph(f'{uf}: {quantidade} participante(s)')

    document.add_paragraph('')
    document.add_paragraph(f'Total geral (congressistas + profissionais): {total_geral}')

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="evento_{evento.id}_inscritos.docx"'
    document.save(response)
    return response


class ProfissionalRelatorioDocxView(View):
    """ Gera relatório minimalista apenas com dados essenciais """
    
    def get(self, request, *args, **kwargs):
        profissionais = Profissional.objects.all().order_by('nome')
        
        document = Document()
        document.add_heading('Profissionais', 0)
        document.add_paragraph(now().strftime("%d/%m/%Y %H:%M"))
        document.add_paragraph('')

        for profissional in profissionais:
            eventos = ", ".join([e.descricao for e in profissional.eventos.all()])
            
            document.add_paragraph(
                f'{profissional.nome} • {profissional.cpf or "---"} • {eventos or "---"}'
            )

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="profissionais.docx"'
        document.save(response)
        return response


class PlanejamentoRelatorioDocxView(View):
    """ Gera relatório de planejamento com totais e formatação """
    
    def get(self, request, *args, **kwargs):
        planejamentos = Planejamento.objects.all().order_by('descricao')
        total_geral = sum(p.valor_planejado for p in planejamentos if p.valor_planejado)
        
        document = Document()
        document.add_heading('Relatório de Planejamento Financeiro', 0)
        document.add_paragraph(f'Gerado em: {now().strftime("%d/%m/%Y %H:%M")}')
        document.add_paragraph(f'Total de itens: {planejamentos.count()}')
        document.add_paragraph(f'Valor total planejado: R$ {total_geral:,.2f}')
        document.add_paragraph('')

        # Tabela principal
        table = document.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        
        # Cabeçalho
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'DESCRIÇÃO'
        hdr_cells[1].text = 'VALOR PLANEJADO'
        hdr_cells[2].text = 'STATUS'
        
        # Dados
        for planejamento in planejamentos:
            row_cells = table.add_row().cells
            row_cells[0].text = planejamento.descricao or "---"
            
            # Formata valor
            if planejamento.valor_planejado:
                row_cells[1].text = f"R$ {planejamento.valor_planejado:,.2f}"
            else:
                row_cells[1].text = "R$ 0,00"
            
            # Formata status
            status = planejamento.status
            if hasattr(planejamento, 'get_status_display'):
                status = planejamento.get_status_display()
            row_cells[2].text = str(status)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="planejamento_financeiro.docx"'
        document.save(response)
        return response


class PedidosSimplesRelatorioDocxView(View):
    """ Gera relatório minimalista ordenado por nome com resumo """
    
    def get(self, request, *args, **kwargs):
        from django.db.models.functions import Lower
        
        # Ordenar por nome completo em ordem alfabética
        pedidos = PedidoCamisa.objects.all().order_by(Lower('nome_completo'))
        
        # Preparar dados para o resumo
        resumo_por_tipo = {}  # Dicionário para agrupar por tipo de camisa
        
        for pedido in pedidos:
            # Usar o tipo da camisa (choices TIPO_CAMISA) em vez da descrição
            tipo_camisa = pedido.camisa.get_tipo_display() if pedido.camisa else "Sem tipo"
            tamanho = pedido.get_tamanho_display() if hasattr(pedido, 'get_tamanho_display') else pedido.tamanho
            cor = pedido.get_cor_display() if hasattr(pedido, 'get_cor_display') else pedido.cor
            
            # Criar chave combinando tamanho e cor
            chave = f"{tamanho} {cor}"
            
            # Inicializar o dicionário para este tipo de camisa se não existir
            if tipo_camisa not in resumo_por_tipo:
                resumo_por_tipo[tipo_camisa] = {}
            
            # Adicionar ao resumo
            if chave in resumo_por_tipo[tipo_camisa]:
                resumo_por_tipo[tipo_camisa][chave] += 1
            else:
                resumo_por_tipo[tipo_camisa][chave] = 1
        
        document = Document()
        document.add_heading('Pedidos por Ordem Alfabética', 0)
        
        # Data e hora
        data_paragraph = document.add_paragraph()
        data_run = data_paragraph.add_run(now().strftime("%d/%m/%Y %H:%M"))
        data_run.bold = True
        data_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        document.add_paragraph('')
        
        # Adicionar lista de pedidos
        document.add_heading('Lista de Pedidos', level=1)
        
        # Adicionar cabeçalho à lista
        table = document.add_table(rows=1, cols=6)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Nome'
        hdr_cells[1].text = 'Cidade'
        hdr_cells[2].text = 'Tipo Camisa'
        hdr_cells[3].text = 'Tamanho'
        hdr_cells[4].text = 'Cor'
        hdr_cells[5].text = 'Status'
        
        for pedido in pedidos:
            tamanho = pedido.get_tamanho_display() if hasattr(pedido, 'get_tamanho_display') else pedido.tamanho
            cor = pedido.get_cor_display() if hasattr(pedido, 'get_cor_display') else pedido.cor
            status = pedido.get_status_display() if hasattr(pedido, 'get_status_display') else pedido.status
            tipo_camisa = pedido.camisa.get_tipo_display() if pedido.camisa else "Sem tipo"
            descricao_camisa = pedido.camisa.descricao if pedido.camisa else "Sem descrição"
            
            # Adicionar linha à tabela
            row_cells = table.add_row().cells
            row_cells[0].text = pedido.nome_completo or ''
            row_cells[1].text = pedido.cidade or ''
            row_cells[2].text = f"{tipo_camisa} ({descricao_camisa})"
            row_cells[3].text = tamanho
            row_cells[4].text = cor
            row_cells[5].text = status
        
        document.add_paragraph('')
        
        # Adicionar resumo
        document.add_heading('Resumo por Tipo de Camisa, Tamanho e Cor', level=1)
        
        # Resumo por tipo de camisa (ordenado alfabeticamente)
        for tipo_camisa in sorted(resumo_por_tipo.keys()):
            resumo = resumo_por_tipo[tipo_camisa]
            document.add_heading(f'Camisas {tipo_camisa}', level=2)
            
            if resumo:
                # Ordenar por tamanho e depois por cor
                itens_ordenados = sorted(resumo.items(), key=lambda x: (x[0].split()[0], x[0].split()[1]))
                
                for chave, quantidade in itens_ordenados:
                    partes = chave.split()
                    tamanho = partes[0]
                    cor = ' '.join(partes[1:])
                    
                    p = document.add_paragraph()
                    p.add_run(f'{quantidade} ').bold = True
                    p.add_run(f'{tamanho} {cor}')
            else:
                document.add_paragraph('Nenhum pedido encontrado')
            
            document.add_paragraph('')
        
        # Adicionar totais
        document.add_heading('Totais Gerais', level=2)
        
        total_por_tipo = {}
        for tipo_camisa, resumo in resumo_por_tipo.items():
            total_por_tipo[tipo_camisa] = sum(resumo.values())
        
        total_geral = sum(total_por_tipo.values())
        
        for tipo_camisa, total in sorted(total_por_tipo.items()):
            p_total = document.add_paragraph()
            p_total.add_run(f'Total {tipo_camisa}: ').bold = True
            p_total.add_run(f'{total}')
        
        p_total = document.add_paragraph()
        p_total.add_run('Total Geral: ').bold = True
        p_total.add_run(f'{total_geral}').bold = True

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="pedidos_com_resumo.docx"'
        document.save(response)
        return response


class CaixaCompletoRelatorioDocxView(View):
    """ Gera relatório completo do caixa sem tabelas """
    
    def get(self, request, *args, **kwargs):
        document = Document()
        document.add_heading('Relatório Completo do Caixa', 0)
        document.add_paragraph(f'Gerado em: {now().strftime("%d/%m/%Y %H:%M")}')
        document.add_paragraph('')
        
        # ============ CÁLCULOS ============
        
        # PLANEJAMENTO
        total_planejado = Planejamento.objects.aggregate(
            total=Sum('valor_planejado')
        )['total'] or 0
        
        # PAGAMENTOS (CAIXA GERAL)
        total_entradas = Pagamento.objects.filter(
            valor_pago__gt=0
        ).aggregate(total=Sum('valor_pago'))['total'] or 0
        
        total_saidas = Pagamento.objects.filter(
            valor_pago__lt=0
        ).aggregate(total=Sum('valor_pago'))['total'] or 0
        
        total_saidas = abs(total_saidas) if total_saidas else 0
        saldo_caixa = total_entradas - total_saidas
        
        # INSCRIÇÕES
        total_inscricoes = Inscricao.objects.aggregate(
            total=Sum('valor_total')
        )['total'] or 0
        
        inscricao_content_type = ContentType.objects.get_for_model(Inscricao)
        pagamentos_inscricoes = Pagamento.objects.filter(
            content_type=inscricao_content_type,
            valor_pago__gt=0
        ).aggregate(total=Sum('valor_pago'))['total'] or 0
        
        total_inscricoes_pagas = pagamentos_inscricoes
        total_inscricoes_receber = max(total_inscricoes - pagamentos_inscricoes, 0)
        
        # CAMISAS
        total_camisas = PedidoCamisa.objects.aggregate(
            total=Sum('valor_venda')
        )['total'] or 0
        
        camisas_pagas = PedidoCamisa.objects.filter(
            status='pago'
        ).aggregate(total=Sum('valor_venda'))['total'] or 0
        
        camisas_receber = total_camisas - camisas_pagas
        
        # SALDO FUTURO PREVISTO
        saldo_futuro_previsto = saldo_caixa + total_inscricoes_receber + camisas_receber - total_planejado
        
        # ============ RELATÓRIO ============
        
        # RESUMO GERAL
        document.add_heading('Resumo Financeiro Geral', level=1)
        
        # CAIXA ATUAL
        p = document.add_paragraph()
        p.add_run('Valor no Caixa Atual: ').bold = True
        p.add_run(f'R$ {saldo_caixa:,.2f}')
        
        document.add_paragraph('')
        
        # PLANEJAMENTO
        document.add_heading('Planejamento', level=2)
        p = document.add_paragraph()
        p.add_run('Total Planejado: ').bold = True
        p.add_run(f'R$ {total_planejado:,.2f}')
        
        document.add_paragraph('')
        
        # FLUXO DE CAIXA
        document.add_heading('Fluxo de Caixa', level=2)
        p = document.add_paragraph()
        p.add_run('Total de Entradas: ').bold = True
        p.add_run(f'R$ {total_entradas:,.2f}')
        
        p = document.add_paragraph()
        p.add_run('Total de Saídas: ').bold = True
        p.add_run(f'R$ {total_saidas:,.2f}')
        
        document.add_paragraph('')
        
        # INSCRIÇÕES
        document.add_heading('Inscrições', level=2)
        p = document.add_paragraph()
        p.add_run('Valor Total das Inscrições: ').bold = True
        p.add_run(f'R$ {total_inscricoes:,.2f}')
        
        p = document.add_paragraph()
        p.add_run('Inscrições Pagas: ').bold = True
        p.add_run(f'R$ {total_inscricoes_pagas:,.2f}')
        
        p = document.add_paragraph()
        p.add_run('Total a Receber (Inscrições): ').bold = True
        p.add_run(f'R$ {total_inscricoes_receber:,.2f}')
        
        document.add_paragraph('')
        
        # CAMISAS
        document.add_heading('Camisas', level=2)
        p = document.add_paragraph()
        p.add_run('Vendas de Camisas: ').bold = True
        p.add_run(f'R$ {total_camisas:,.2f}')
        
        p = document.add_paragraph()
        p.add_run('Camisas Pagas: ').bold = True
        p.add_run(f'R$ {camisas_pagas:,.2f}')
        
        p = document.add_paragraph()
        p.add_run('Total a Receber (Camisas): ').bold = True
        p.add_run(f'R$ {camisas_receber:,.2f}')
        
        document.add_paragraph('')
        
        # PROJEÇÃO FUTURA
        document.add_heading('Projeção Futura', level=2)
        p = document.add_paragraph()
        p.add_run('Saldo Futuro Previsto: ').bold = True
        p.add_run(f'R$ {saldo_futuro_previsto:,.2f}')

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="relatorio_caixa_simples.docx"'
        document.save(response)
        return response