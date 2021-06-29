# -*- coding: utf-8 -*-
from os import listdir
from os.path import isfile, join

#classe utilizada para armazenar e manpular os dados
class Memory:
    def __init__(self, mms, psize, psubstitution):
        self.MM_SIZE = mms
        self.PAGE_SIZE = psize
        self.TLB = {clebs: -1 for clebs in range(self.MM_SIZE // self.PAGE_SIZE)}
        self.MAIN_MEMORY = {clebs: 0 for clebs in range(self.MM_SIZE)}
        self.LOGIC_MEMORY = {}
        self.PROCESS_Q = []
        self.PAGES_Q = []
        self.PAGE_SUBSTITUTION = psubstitution
        self.LOG = "              String Referência:RefStr\nLogPag\nPágina Lógica a ser Substituida:PLS\n                  Faltou Página:FP\n                          Tempo:time"
        self.PROCESSES_PATH = "processes/"
        self.VM_FILE = "Virtual_Memory.txt"
        self.LOG_FILE = "Log.txt"
        self.TOTAL_FAULTIN_PAGES = 0

        for clebs in self.TLB:
            self.LOG = self.LOG.replace("LogPag", f'                Página Física {clebs}:-\nLogPag')
        self.LOG = self.LOG.replace("\nLogPag", "")

        with open(self.VM_FILE, 'w') as file:
            file.write("")
            
            
    def run(self):
        self.LOG = self.log_ref()

        for proc in self.PROCESS_Q:
            self.interpret_command(proc)
        print(self.LOG)
        with open(self.LOG_FILE, 'w') as file:
            file.write(self.LOG)
            file.write(f"\n>----------------------------------------\n|\n| > Total de faltas de páginas: {self.TOTAL_FAULTIN_PAGES};\n|\n>----------------------------------------")

    def read_VM(self):
        with open(self.VM_FILE, 'r') as file:
            tmp = file.read().split("\n")[:-1]
            tmp = [clebs.split(",") for clebs in tmp]
            tmp = {clebs[0]: clebs[1:] for clebs in tmp}

        return tmp

    def dict_to_str(self, VM_data):
        full_text = ""

        for line in VM_data:
            full_text = full_text + line+","
            tmp = [str(clebs) + "," for clebs in VM_data[line]]
            tmp[-1] = tmp[-1][:-1]
            for address in tmp:
                full_text = full_text + address
            full_text = full_text + "\n"

        return full_text

    def update_VM(self, process, process_pages):
        try:
            old_data = self.read_VM()
            red = True
            final_txt = ""

            for idx, page in enumerate(process_pages):
                txt_tmp = process + str(idx) + ","
                tmp = [str(clebs) + "," for clebs in process_pages[page]]
                tmp[-1] = tmp[-1][:-1]
                for address in tmp:
                    txt_tmp = txt_tmp + address
                txt_tmp = txt_tmp + "\n"

                for v_page in old_data:
                    #print(v_page)
                    #print(process + str(idx))
                    if v_page == process + str(idx):
                        old_data[v_page] = process_pages[page]
                        red = False
                        break

                final_txt = final_txt + txt_tmp

            if red:
                with open(self.VM_FILE, 'a') as file:
                    file.write(final_txt)
                return

            final_txt = self.dict_to_str(old_data)

            with open(self.VM_FILE, 'w') as file:
                file.write(final_txt)
            return
        except:
            with open(self.VM_FILE, 'a') as file:
                for idx, page in enumerate(process_pages):
                    file.write(process+str(idx)+ ",")
                    tmp = [str(clebs) + "," for clebs in process_pages[page]]
                    tmp[-1] = tmp[-1][:-1]
                    for address in tmp:
                        file.write(address)
                    file.write("\n")
            return

    def run_process(self, process_to_run):
        with open(self.PROCESSES_PATH+process_to_run+".txt", 'r') as file:
            process = file.read().replace(";", "").replace(",", "")
            process = process.split("\n")

            process_pages = {clebs: [address for address in range(self.PAGE_SIZE)] for clebs in range(int(process[1])//self.PAGE_SIZE)}
            self.update_VM(process[0], process_pages)
            for clebs in process[2:]:
                self.PROCESS_Q.append(str(process[0]) + " " + clebs)
            self.LOGIC_MEMORY[process[0]] = process_pages

    def update_free_memory_log(self, p_id, page_id, frame_address):
        # LOG.find(f"{frame_address}:")
        log = self.LOG
        log_lst = log.split("\n")

        for clebs in self.TLB:
            if clebs == frame_address:
                log = log.replace(f"PF{clebs}", f"\t{p_id}_{page_id}", 1)
            elif log[log.find(f"PF{clebs}")-4] == ":" or log[log.find(f"PF{clebs}")-4] == "-":
                log = log.replace(f"PF{clebs}", f"-", 1)
            else:
                p_idx = "ERROR"
                for idx, p in enumerate(log_lst[clebs+1].split("   ")):
                    if p == f"PF{clebs}":
                        p_idx = log_lst[clebs+1].split("   ")[idx-1]
                        break
                log = log.replace(f"PF{clebs}", p_idx,1)
        self.LOG = log

    def load_address(self, p_id, page_address, frame_address, p_pages):
        tmp = int(page_address)
        while tmp >= self.PAGE_SIZE:
            tmp = tmp - self.PAGE_SIZE

        self.TLB[frame_address] = p_id + " " + str(int(page_address)//self.PAGE_SIZE)


        p_pages[int(page_address)//self.PAGE_SIZE] = [self.MAIN_MEMORY[clebs] for clebs in range(frame_address*self.PAGE_SIZE, frame_address*self.PAGE_SIZE+self.PAGE_SIZE)]

        self.update_VM(p_id, p_pages)

    def store_address(self, p_id, value, page_address, frame_address, p_pages):
        tmp = int(page_address)
        while tmp >= self.PAGE_SIZE:
            tmp = tmp - self.PAGE_SIZE

        self.TLB[frame_address] = p_id + " " + str(int(page_address)//self.PAGE_SIZE)

        self.MAIN_MEMORY[(int(frame_address)*self.PAGE_SIZE)+tmp] = value

        p_pages[int(page_address)//self.PAGE_SIZE][tmp] = self.MAIN_MEMORY[(int(frame_address)*self.PAGE_SIZE)+tmp]

        self.update_VM(p_id, p_pages)

    def log_ref(self):
        log = self.LOG

        for idx, proc in enumerate(self.PROCESS_Q):
            proc = proc.split(" ")
            log = log.replace("RefStr", f"   {proc[0]}_{int(proc[-1]) // self.PAGE_SIZE}RefStr")
            log = log.replace("-", "   P_F-")
            log = log.replace("PLS", "   P_SPLS")
            log = log.replace("FP", "   F_PFP")
            log = log.replace("time", f"    {idx+1} time")
        log = log.replace("RefStr", "")
        log = log.replace("-", "")
        log = log.replace("PLS", "")
        log = log.replace("FP", "")
        log = log.replace("time", "")

        log = log.split("\n")
        for idx, clebs in enumerate(log):
            log[idx] = clebs.replace("P_F", f"PF{clebs[clebs.find(':')-1]}")

        str = ""
        for clebs in log:
            str = str + clebs + "\n"

        return str[:-1]

    def interpret_command(self, command):
        #print(command)
        command = command.split(" ")
        p_pages = self.LOGIC_MEMORY[command[0]]

        id = command[0] + " " + str(int(command[-1]) // self.PAGE_SIZE)


        if command[1] == "l":
            fa_tmp = 0

            for address in self.TLB:
                try:
                    if self.TLB[address] == self.PAGES_Q[0]:
                        fa_tmp = address
                except:
                    pass
                if self.TLB[address] == -1 or self.TLB[address] == id:
                    self.load_address(command[0], command[2], address, p_pages)
                    self.update_free_memory_log(command[0], id.split(" ")[1], frame_address=address)

                    if id not in self.PAGES_Q and self.PAGE_SUBSTITUTION == 1:
                        self.PAGES_Q.append(id)
                    elif self.PAGE_SUBSTITUTION == 2: 
                        for i,page in enumerate(self.PAGES_Q): 
                            if page == id: 
                                del self.PAGES_Q[i] 
                        self.PAGES_Q.append(id)
                    elif id not in self.PAGES_Q and self.PAGE_SUBSTITUTION == 3:
                        self.PAGES_Q.append(id+" 1")

                        self.LOG = self.LOG.replace("P_S", self.PAGES_Q[0][:-2], 1)
                        self.LOG = self.LOG.replace("F_P", "N ", 1)
                        self.TOTAL_FAULTIN_PAGES += 1
                        return

                    self.LOG = self.LOG.replace("P_S", self.PAGES_Q[0], 1)
                    self.LOG = self.LOG.replace("F_P", "N ", 1)
                    self.TOTAL_FAULTIN_PAGES += 1
                    return

            if self.PAGE_SUBSTITUTION == 1 or self.PAGE_SUBSTITUTION == 2: 
                self.load_address(command[0], command[2], fa_tmp, p_pages)
                self.update_free_memory_log(command[0], id.split(" ")[1], fa_tmp)

                self.PAGES_Q.append(id)
                del self.PAGES_Q[0]
                self.LOG = self.LOG.replace("P_S", self.PAGES_Q[0], 1)
                self.LOG = self.LOG.replace("F_P", "Y ", 1)
                self.TOTAL_FAULTIN_PAGES += 1
                
            elif self.PAGE_SUBSTITUTION == 3:
                blue = True
                while blue:
                    for key, pages in enumerate(self.PAGES_Q):
                        if pages[-1] == "1":
                            new = self.PAGES_Q[key][:-1] + "0"

                            self.PAGES_Q.append(new)
                            del self.PAGES_Q[key]
                            break
                        elif pages[-1] == "0":
                            for address in self.TLB:
                                if self.TLB[address] == self.PAGES_Q[key][:-2]:
                                    fa_tmp = address
                                    break

                            self.load_address(command[0], command[2], fa_tmp, p_pages)
                            self.update_free_memory_log(command[0], id.split(" ")[1], fa_tmp)

                            self.PAGES_Q.append(id+" 1")
                            del self.PAGES_Q[key]
                            self.LOG = self.LOG.replace("P_S", self.PAGES_Q[key][:-2], 1)
                            self.LOG = self.LOG.replace("F_P", "Y ", 1)
                            self.TOTAL_FAULTIN_PAGES += 1
                            blue = False
                            break

        elif command[1] == "s":
            fa_tmp = 0

            for address in self.TLB:
                try:
                    if self.TLB[address] == self.PAGES_Q[0]:
                        fa_tmp = address
                except:
                    pass
                if self.TLB[address] == -1 or self.TLB[address] == id:
                    self.store_address(command[0], command[2], command[3], address, p_pages)
                    self.update_free_memory_log(command[0], id.split(" ")[1], frame_address=address)

                    if id not in self.PAGES_Q and self.PAGE_SUBSTITUTION == 1:
                        self.PAGES_Q.append(id)
                    elif self.PAGE_SUBSTITUTION == 2: 
                        for i,page in enumerate(self.PAGES_Q): 
                            if page == id: 
                                del self.PAGES_Q[i] 
                        self.PAGES_Q.append(id)
                    elif id not in self.PAGES_Q and self.PAGE_SUBSTITUTION == 3:
                        self.PAGES_Q.append(id+" 1")

                    self.LOG = self.LOG.replace("P_S", self.PAGES_Q[0][:-2], 1)
                    self.LOG = self.LOG.replace("F_P", "N ", 1)
                    self.TOTAL_FAULTIN_PAGES += 1
                    return

                self.LOG = self.LOG.replace("P_S", self.PAGES_Q[0], 1)
                self.LOG = self.LOG.replace("F_P", "N ", 1)
                self.TOTAL_FAULTIN_PAGES += 1
                return

            if self.PAGE_SUBSTITUTION == 1 or self.PAGE_SUBSTITUTION == 2:
                # print(fa_tmp)
                self.store_address(command[0], command[2], command[3], fa_tmp, p_pages)
                self.update_free_memory_log(command[0], id.split(" ")[1], fa_tmp)

                self.PAGES_Q.append(id)
                del self.PAGES_Q[0]
                self.LOG = self.LOG.replace("P_S", self.PAGES_Q[0], 1)
                self.LOG = self.LOG.replace("F_P", "Y ", 1)
                self.TOTAL_FAULTIN_PAGES += 1
            
            elif self.PAGE_SUBSTITUTION == 3:
                blue = True
                while blue:
                    for key, pages in enumerate(self.PAGES_Q):
                        if pages[-1] == "1":
                            new = self.PAGES_Q[key][:-1] + "0"

                            self.PAGES_Q.append(new)
                            del self.PAGES_Q[key]
                            break
                        elif pages[-1] == "0":
                            for address in self.TLB:
                                if self.TLB[address] == self.PAGES_Q[key][:-2]:
                                    fa_tmp = address
                                    break

                            self.store_address(command[0], command[2], command[3], fa_tmp, p_pages)
                            self.update_free_memory_log(command[0], id.split(" ")[1], fa_tmp)


                            self.PAGES_Q.append(id+" 1")
                            del self.PAGES_Q[key]
                            self.LOG = self.LOG.replace("P_S", self.PAGES_Q[key][:-2], 1)
                            self.LOG = self.LOG.replace("F_P", "Y ", 1)
                            blue = False
                            break
                
                        

mm_size = int(input("> Insira o tamanho da memória principal: "))

page_size = int(input("\n> Insira o tamanho das páginas: "))

# 1 - FIFO  \n1 - FIFO\n2 - LRU\n3 - Segunda chance\n"
print(">----------------------------------------\n|")
print("| > 1 - FIFO\n| > 2 - LRU\n| > 3 - Segunda chance")
print("|\n>----------------------------------------")
page_substitution  = input("|\n| > Insira o algorítmo que deseja utilizar: ")

#validação do algoritmo
while page_substitution != '1' and page_substitution != '2' and page_substitution != '3':
    page_substitution = input("|\n| > Valor inválido, digite novamente: ")

#novo objeto da classe memory
mem = Memory(int(mm_size), int(page_size), int(page_substitution)) 

red = True

#executa enquanto o usuário não digitar run
while red:

    print("|\n>----------------------------------------\n|")
    print("| > Processos disponíveis\n|")
    processes = [f for f in listdir(mem.PROCESSES_PATH) if isfile(join(mem.PROCESSES_PATH, f))]
    list_proc = []
    for proc in processes:
        print("| > " + proc[:-4] + ";")
        list_proc.append(proc[:-4])

    print("|\n| > 'run' para rodar os processos")
    print(">----------------------------------------")

    process_to_run = input("|\n| > Insira o processo que deseja executar: ")
    
    if process_to_run == "run":
        red = False
        break
    
    #validação do processo informado
    while(not(list_proc.__contains__(process_to_run))):  
        process_to_run = input("|\n| > Processo inválido, digite novamente: ")

    
    mem.run_process(process_to_run)
    
mem.run()

