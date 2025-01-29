# README - Sistema de Escalonador de Tarefas

## Descrição do Sistema
Este projeto implementa um escalonador de tarefas de tempo compartilhado baseado no algoritmo Round Robin. O sistema simula a execução de processos simples em um ambiente computacional com recursos limitados, incluindo:

- Quatro registradores de uso geral (A, B, C, D).
- Um contador de programa (PC).
- Estados dos processos: **Pronto**, **Executando** ou **Bloqueado**.

### Principais funcionalidades
1. **Carregamento de Processos**:
   - Processos são lidos de arquivos com até 21 instruções.
   - Instruções suportadas: atribuição, entrada/saída (E/S), comando (COM) e término (SAIDA).

2. **Execução com Round Robin**:
   - Cada processo recebe um quantum de instruções a serem executadas por vez.
   - Caso não finalize durante o quantum, o processo retorna à fila de prontos.
   - Processos bloqueados aguardam o tempo especificado antes de retornar à fila de prontos.

3. **Geração de Logs**:
   - Os logs documentam o comportamento do sistema e incluem métricas como média de trocas e instruções por quantum.

## Estrutura do Código
O código é dividido em duas classes principais:

1. **Process**:
   - Representa um processo com atributos como identificador (PID), estado, contador de programa e registradores.

2. **Scheduler**:
   - Implementa o escalonador, com funções para carregar processos, executar instruções, gerenciar filas de prontos e bloqueados, e gerar logs.

## Resultados e Análise dos Logs
Foram realizados testes com diferentes valores de quantum, gerando logs para cada um. Abaixo, apresentamos os resultados principais.

### Tabela de Desempenho
| Quantum | Média de Trocas | Média de Instruções |
|---------|------------------|--------------------------|
| 2       | 6.00             | 1.99                    |
| 3       | 4.00             | 2.62                    |
| 4       | 2.80             | 3.34                    |
| 5       | 2.20             | 3.83                    |
| 6       | 2.00             | 4.03                    |
| 7       | 1.60             | 4.36                    |
| 8       | 1.60             | 4.49                    |
| 9       | 1.50             | 4.62                    |
| 10      | 1.40             | 4.76                    |
| 11      | 1.20             | 5.06                    |

### Gráficos
**Trocas de Processos por Quantum**:
Conforme o quantum aumenta, o número de trocas diminui exponencialmente, indicando menos interrupções.

**Instruções Executadas por Quantum**:
O aumento do quantum permite que mais instruções sejam executadas antes de uma troca, alcançando maior eficiência.

### Conclusões
- **Quantum Ideal**: Valores entre 6 e 8 oferecem um bom equilíbrio entre a média de trocas e instruções executadas.
- **Impacto do Quantum**: Quantums muito pequenos causam muitas interrupções, enquanto quantums muito grandes retardam a resposta para processos bloqueados ou prontos.

## Arquivos Gerados
- **Código-fonte**: `escalonador.py`
- **Logs**: `log02.txt` até `log11.txt`
- **Processos**: `01.txt` até `10.txt`

## Autoria
Desenvolvido como parte da disciplina de Sistemas Operacionais, sob orientação do prof. Elinaldo Santos de Góes Júnior.

Universidade Estadual de Feira de Santana (UEFS)

