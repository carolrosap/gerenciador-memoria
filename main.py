# -*- coding: utf-8 -*-
from os import listdir
from os.path import isfile, join


MM_SIZE = 0

PAGE_SIZE = 0

TLB = {}

MAIN_MEMORY = {}

LOGIC_MEMORY = {}

PROCESS_Q = []

PAGES_Q = []

PAGE_SUBSTITUTION = 0

PROCESSES_PATH = "processes/"

def read_VM():
    with open("Virtual_Memory.txt", 'r') as file:
        tmp = file.read().split("\n")[:-1]
        tmp = [clebs.split(",") for clebs in tmp]
        tmp = {clebs[0]: clebs[1:] for clebs in tmp}
        
    return tmp

def dict_to_str(VM_data):
    
    #print(VM_data)
    
    full_text = ""
    
    for line in VM_data:
        #print(line)
        full_text = full_text + line+","
        tmp = [str(clebs) + "," for clebs in VM_data[line]]
        tmp[-1] = tmp[-1][:-1]
        for address in tmp:
            full_text = full_text + address
        full_text = full_text + "\n"
        #print(full_text)
    
    #print(full_text)
    
    return full_text
    
def update_VM(process, process_pages):
    try:
        old_data = read_VM()
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
                if v_page == process + str(idx):
                    old_data[v_page] = process_pages[page]
                    red = False
                    break
                
            final_txt = final_txt + txt_tmp
            
        if red:
            with open("Virtual_Memory.txt", 'a') as file:
                file.write(final_txt)
            return
            
        final_txt = dict_to_str(old_data)
            
        with open("Virtual_Memory.txt", 'w') as file:
            file.write(final_txt)
        return
    except:
        with open("Virtual_Memory.txt", 'a') as file:
            for idx, page in enumerate(process_pages):
                file.write(process+str(idx)+ ",")
                tmp = [str(clebs) + "," for clebs in process_pages[page]]
                tmp[-1] = tmp[-1][:-1]
                for address in tmp:
                    file.write(address)
                file.write("\n")
        return

def run_process(process_to_run):
    with open(PROCESSES_PATH+process_to_run+".txt", 'r') as file:
        #print(file.read())
       
        process = file.read().replace(";", "").replace(",", "")
        process = process.split("\n")
        #print(process[1])
        
        process_pages = {clebs: [address for address in range(PAGE_SIZE)] for clebs in range(int(process[1])//PAGE_SIZE)}
        #print(process_pages)
        #print(process)
        update_VM(process[0], process_pages)
        for clebs in process[2:]:
            PROCESS_Q.append(str(process[0]) + " " + clebs)
              
        LOGIC_MEMORY[process[0]] = process_pages
        
    return PROCESS_Q

def load_address(p_id, page_address, frame_address, p_pages):
    tmp = int(page_address)
    while tmp >= PAGE_SIZE:
        tmp = tmp - PAGE_SIZE
    
    TLB[frame_address] = p_id + " " + str(int(page_address)//PAGE_SIZE)
                
    PAGES_Q.append(frame_address)
                
    print(MAIN_MEMORY[(frame_address*PAGE_SIZE)+tmp])
                
    p_pages[int(page_address)//PAGE_SIZE] = [MAIN_MEMORY[clebs] for clebs in range(frame_address*PAGE_SIZE, frame_address*PAGE_SIZE+PAGE_SIZE)]
                
    update_VM(p_id, p_pages)
    
def store_address(p_id, value, page_address, frame_address, p_pages):
    tmp = int(page_address)
    while tmp >= PAGE_SIZE:
        tmp = tmp - PAGE_SIZE
    
    TLB[frame_address] = p_id + " " + str(int(page_address)//PAGE_SIZE)
                
    PAGES_Q.append(frame_address)
                
    print(MAIN_MEMORY[(frame_address*PAGE_SIZE)+tmp])
    MAIN_MEMORY[(frame_address*PAGE_SIZE)+tmp] = value
    
                
    p_pages[int(page_address)//PAGE_SIZE][tmp] = MAIN_MEMORY[(frame_address*PAGE_SIZE)+tmp]
            
    update_VM(p_id, p_pages)
    
def sub_addres(p_id, origin_address, dest_address, frame_address, p_pages):
    tmp = int(dest_address)
    while tmp >= PAGE_SIZE:
        tmp = tmp - PAGE_SIZE
        
    TLB[frame_address] = p_id + " " + str(int(dest_address)//PAGE_SIZE)
    PAGES_Q.append(frame_address)
    #MAIN_MEMORY[(frame_address*PAGE_SIZE)+tmp] = value
    
    
    

def interpret_command(command):
   
    command = command.split(" ")
    #command[0].strip()
    print(command[0])
    
    print(LOGIC_MEMORY)
    p_pages = LOGIC_MEMORY[command[0] + " "] #VER PQ ESTAVA COM ERRO DE ESPAÇO AQUI
    
    if command[1] == "l":        
        
        for address in TLB:
            if TLB[address] == -1:
                load_address(command[0], command[2], address, p_pages)
                
                break
        
        if PAGE_SUBSTITUTION == 1:
            load_address(command[0], command[2], PAGES_Q[0], p_pages)
            del PAGES_Q[0]
            
    elif command[1] == "s":
        
        for address in TLB:
            if TLB[address] == -1:
                store_address(command[0], command[2], command[3], address, p_pages)
                            
                break
        if PAGE_SUBSTITUTION == 1:
            load_address(command[0], command[2], PAGES_Q[0], p_pages)
            del PAGES_Q[0]    
    
    #elif command[1] == "add":
        
    #elif command[1] == "sub":
    
    #elif command[1] == "sa":
     #   for address in TLB:
      #      if TLB[address] == -1:  
              
       
       
#Início

MM_SIZE = int(input("> Insira o tamanho da memória principal: "))

PAGE_SIZE = int(input("\n> Insira o tamanho das páginas: "))

PAGE_SUBSTITUTION = input("\n> Insira o algorítmo que deseja utilizar:\n1 - FIFO\n2 - LRU\n3 - Segunda chance\n")
while(PAGE_SUBSTITUTION != '1' and PAGE_SUBSTITUTION != '2' and PAGE_SUBSTITUTION != '3'):
    PAGE_SUBSTITUTION = input(" > Valor inválido, digite novamente: ")
# 1 - FIFO

MAIN_MEMORY = {clebs : 0 for clebs in range(MM_SIZE)}

TLB = {clebs: -1 for clebs in range(MM_SIZE//PAGE_SIZE)}

red = True

while red:     
    print(">--------------------\n")
    #print("|\n")
    print("\n> Processos disponíveis\n")
    
    processes = [f for f in listdir(PROCESSES_PATH) if isfile(join(PROCESSES_PATH, f))]
    
    list_proc = []
    for proc in processes:
        print("| > " + proc[:-4] + ";\n")
        list_proc.append(proc[:-4])
    
    print("> run para rodar")
    print(">--------------------\n")
    
    process_to_run = input("\n> Insira o processo que deseja executar: ")
   
    if process_to_run == "run":
        red = False
        break
 
    while(not(list_proc.__contains__(process_to_run))):    
       process_to_run = input("> Processo inválido, digite novamente: ")
        
    PROCESS_Q = run_process(process_to_run)


for proc in PROCESS_Q:
    interpret_command(proc)




