import os
from collections import deque

# Classe que representa um processo a ser gerenciado pelo escalonador
class Process:
    def __init__(self, pid, name, instructions):
        self.pid = pid  # Identificador único do processo
        self.name = name  # Nome do programa associado ao processo
        self.instructions = instructions  # Lista de instruções que o processo deve executar
        self.pc = 0  # Contador de Programa, indicando a próxima instrução a ser executada
        self.state = "Pronto"  # Estado inicial do processo
        self.registers = {"A": 0, "B": 0, "C": 0, "D": 0}  # Registradores do processo, inicializados em 0
        self.wait_time = 0  # Tempo de espera restante em caso de bloqueio
        self.interruptions = 0  # Contador de interrupções sofridas pelo processo
        self.executed_instructions = []  # Lista com o número de instruções executadas por quantum

    def execute_instruction(self):
        # Executa a próxima instrução, retornando-a, ou "SAIDA" se não houver mais instruções
        if self.pc < len(self.instructions):
            return self.instructions[self.pc]
        return "SAIDA"  # Indica que o processo terminou

    def __repr__(self):
        # Representação textual do processo, útil para depuração
        return f"{self.name} (PC={self.pc}, Estado={self.state})"

# Classe que implementa o escalonador de processos
class Scheduler:
    def __init__(self, quantum):
        self.quantum = quantum  # Número máximo de instruções executadas por quantum
        self.ready_queue = deque()  # Fila de processos prontos
        self.blocked_queue = []  # Lista de processos bloqueados aguardando E/S
        self.process_table = {}  # Tabela de processos ativos
        self.finished_processes = []  # Lista de processos finalizados
        self.log = []  # Log para registrar as operações do escalonador

    def load_processes(self, folder="processos"):
        # Carrega os processos a partir de arquivos no diretório especificado
        files = sorted([f for f in os.listdir(folder) if f.endswith(".txt")])
        if not files:
            raise FileNotFoundError("Nenhum arquivo de processo encontrado no diretório 'processos'.")

        for i, file in enumerate(files):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                lines = f.read().strip().split("\n")
                name = lines[0]  # Nome do programa
                instructions = lines[1:]  # Lista de instruções do programa

                process = Process(i, name, instructions)  # Cria um novo processo
                self.process_table[i] = process  # Adiciona o processo à tabela
                self.ready_queue.append(i)  # Adiciona o processo à fila de prontos
                self.log.append(f"Carregando {name}")  # Registra o carregamento no log

    def run(self):
        # Método principal que executa o escalonador usando o algoritmo Round Robin
        total_quanta = 0  # Contador total de quanta usados
        total_instructions = 0  # Contador total de instruções executadas

        while self.ready_queue or self.blocked_queue:
            self.decrement_blocked()  # Atualiza o estado dos processos bloqueados

            if not self.ready_queue:
                continue  # Aguarda até que algum processo esteja pronto para executar

            pid = self.ready_queue.popleft()  # Seleciona o próximo processo pronto

            if pid not in self.process_table:
                continue  # Ignora processos que já foram finalizados

            process = self.process_table[pid]
            process.state = "Executando"  # Atualiza o estado do processo
            self.log.append(f"Executando {process.name}")
            executed = 0  # Contador de instruções executadas neste quantum

            while executed < self.quantum and process.pc < len(process.instructions):
                if process.pc >= 21:
                    process.interruptions += 1  # Incrementa o contador de interrupções
                    self.log.append(f"{process.name} abortado: atingiu o limite de 21 instruções.")
                    self.finished_processes.append(process)
                    del self.process_table[pid]
                    break  # Sai do loop de execução do processo

                instr = process.execute_instruction()  # Obtém a próxima instrução
                process.pc += 1  # Incrementa o contador de programa
                executed += 1
                total_instructions += 1

                if instr.startswith("E/S"):
                    # Instrução de Entrada/Saída
                    process.state = "Bloqueado"
                    process.wait_time = 2  # Define o tempo de espera para desbloqueio
                    self.blocked_queue.append(pid)  # Adiciona à lista de bloqueados
                    self.log.append(f"E/S iniciada em {process.name}")
                    break

                elif instr == "SAIDA":
                    # Instrução de término do processo
                    process.interruptions += 1  # Incrementa o contador de interrupções
                    self.log.append(
                        f"{process.name} terminado. A={process.registers['A']}. "
                        f"B={process.registers['B']}. C={process.registers['C']}. D={process.registers['D']}"
                    )
                    self.finished_processes.append(process)  # Adiciona à lista de finalizados
                    del self.process_table[pid]  # Remove da tabela de processos
                    break

                elif "=" in instr:
                    # Instrução de atribuição (X=valor)
                    reg, val = instr.split("=")
                    process.registers[reg.strip()] = int(val.strip())  # Atualiza o valor do registrador

            process.executed_instructions.append(executed)  # Registra as instruções executadas

            if executed == self.quantum or process.state == "Bloqueado":
                total_quanta += 1  # Incrementa o número de quanta usados

            if pid in self.process_table and process.state == "Executando" and instr != "SAIDA":
                # Se o processo ainda está ativo, retorna ao estado Pronto
                process.state = "Pronto"
                self.ready_queue.append(pid)  # Reinsere na fila de prontos
                process.interruptions += 1  # Incrementa o contador de interrupções
                self.log.append(f"Interrompendo {process.name} após {executed} instruções")

        self.write_log(total_quanta, total_instructions)  # Gera o log final

    def decrement_blocked(self):
        # Atualiza o estado dos processos bloqueados, verificando se podem ser desbloqueados
        desbloqueados = []
        for pid in self.blocked_queue:
            process = self.process_table[pid]
            process.wait_time -= 1  # Decrementa o tempo de espera
            if process.wait_time <= 0:
                process.state = "Pronto"  # Atualiza o estado para Pronto
                desbloqueados.append(pid)

        for pid in desbloqueados:
            self.blocked_queue.remove(pid)  # Remove da lista de bloqueados
            if pid not in self.ready_queue:
                self.ready_queue.append(pid)  # Adiciona à fila de prontos

    def write_log(self, total_quanta, total_instructions):
        # Gera o arquivo de log com informações do escalonador
        all_processes = self.finished_processes + list(self.process_table.values())
        num_processes = len(all_processes)  # Considera TODOS os processos, não apenas os finalizados

        total_interruptions = sum(proc.interruptions for proc in all_processes)

        # Corrigindo a média de trocas de processo
        avg_interruptions = total_interruptions / num_processes if num_processes > 0 else 0

        avg_instructions = total_instructions / total_quanta if total_quanta > 0 else 0

        with open(f"log{self.quantum:02d}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(self.log) + "\n")
            f.write(f"MEDIA DE TROCAS: {avg_interruptions:.2f}\n")
            f.write(f"MEDIA DE INSTRUCOES: {avg_instructions:.2f}\n")
            f.write(f"QUANTUM: {self.quantum}\n")


if __name__ == "__main__":
    # Inicialização principal do programa
    if not os.path.exists("quantum.txt"):
        # Cria o arquivo de configuração do quantum, se não existir
        with open("quantum.txt", "w", encoding="utf-8") as f:
            f.write("3\n")  # Define o quantum como 3

    with open("quantum.txt", "r", encoding="utf-8") as f:
        quantum = int(f.read().strip())  # Lê o valor do quantum do arquivo

    os.makedirs("processos", exist_ok=True)  # Garante que o diretório de processos exista

    # Processos fixos para teste
    processes =  {
        1: "A=5\nB=3\nCOM\nCOM\nC=2\nCOM\nE/S\nD=10\nB=2\nCOM\nE/S\nCOM\nE/S\nCOM\nE/S\nSAIDA",
        2: "A=8\nE/S\nCOM\nCOM\nCOM\nE/S\nB=10\nC=2\nCOM\nCOM\nE/S\nCOM\nCOM\nE/S\nCOM\nCOM\nE/S\nD=3\nA=9\nB=1\nCOM\nCOM\nSAIDA",
        3: "A=8\nE/S\nCOM\nB=5\nCOM\nCOM\nC=5\nD=2\nCOM\nCOM\nA=3\nB=91\nC=10\nCOM\nD=4\nE/S\nSAIDA",
        4: "A=2\nCOM\nCOM\nE/S\nCOM\nE/S\nB=5\nE/S\nCOM\nE/S\nCOM\nC=3\nD=9\nE/S\nSAIDA",
        5: "B=3\nCOM\nE/S\nCOM\nE/S\nC=2\nE/S\nCOM\nE/S\nCOM\nE/S\nSAIDA",
        6: "A=9\nCOM\nCOM\nE/S\nB=5\nCOM\nCOM\nCOM\nCOM\nCOM\nE/S\nCOM\nCOM\nE/S\nSAIDA",
        7: "A=12\nCOM\nCOM\nE/S\nB=5\nCOM\nC=1\nD=2\nA=3\nCOM\nCOM\nCOM\nE/S\nSAIDA",
        8: "A=8\nCOM\nCOM\nA=5\nCOM\nB=10\nC=12\nD=3\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nD=1\nSAIDA",
        9: "COM\nCOM\nE/S\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nE/S\nSAIDA",
        10: "COM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nCOM\nE/S\nSAIDA",
    }


    for pid, instructions in processes.items():
        with open(f"processos/{pid:02d}.txt", "w", encoding="utf-8") as f:
            f.write(f"TESTE-{pid}\n{instructions}")

    scheduler = Scheduler(quantum)  # Cria o escalonador com o quantum definido
    scheduler.load_processes()  # Carrega os processos a partir dos arquivos
    scheduler.run()  # Executa o escalonador